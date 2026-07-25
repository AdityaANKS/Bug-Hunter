"""Bug Hunter CLI main entry point with REPL and sub-commands."""

# ruff: noqa: E402

from __future__ import annotations

import asyncio
import os
import sys
import time
from typing import Optional


def _configure_windows_console() -> None:
    """Force UTF-8 console I/O on Windows for reliable Unicode output."""
    if sys.platform != "win32":
        return

    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass


_configure_windows_console()

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from bughunter import __version__
from bughunter.agent.constraint_policy import validate_action_constraints
from bughunter.agent.input_analysis import extract_task_constraints
from bughunter.agent.think_filter import format_think_tags, strip_think_tags
from bughunter.config.settings import (
    apply_provider_preset,
    list_providers,
    load_config,
    save_config,
    set_config_value,
)
from bughunter.i18n import _
from bughunter.orchestrator import run_agent_task
from bughunter.repl_runner import run_repl_call
from bughunter.target_state.store import (
    apply_target_state_to_agent,
    clear_target_state,
    diff_target_state_snapshots,
    get_target_state_preview,
    list_target_snapshots,
    load_target_state,
    rollback_target_state,
)

# === Stream Output Renderer ===
# at the top of the file imports after,app before definition


class TerminalStreamSink:
    """CLI terminal stream renderer.

    Implements StreamSink protocol for real-time terminal output.
    """

    def __init__(self, console: "Console", show_thinking: bool = True) -> None:
        """Initialize the terminal sink.

        Args:
            console: Rich Console instance
            show_thinking: Whether to show thinking content
        """
        self._console = console
        self._show_thinking = show_thinking
        self._status_printed = False
        self._in_thinking = False
        self._thinking_started = False

    def on_status(self, message: str) -> None:
        """Display status message like 'Thinking...'."""
        if not self._show_thinking:
            # Only show "Thinking..." when thinking is hidden
            self._console.print(f"[dim]{message}[/dim] ", end="", soft_wrap=True)
        # When show_thinking=True, skip "Thinking..." — we'll show actual tokens
        self._status_printed = True

    def on_thinking_token(self, token: str) -> None:
        """Receive thinking token — stream it live with visual styling."""
        if not self._show_thinking:
            return
        if not self._thinking_started:
            # Print thinking header on first token
            self._console.print()
            self._console.print("[dim yellow]💭 Reasoning:[/]")
            self._thinking_started = True
            self._in_thinking = True
            self._status_printed = False
        self._console.print(f"[dim yellow]{token}[/]", end="", soft_wrap=True)

    def on_content_token(self, token: str) -> None:
        """Receive content token."""
        # Transition from thinking → content
        if self._in_thinking:
            self._console.print()  # End thinking line
            self._console.print("[dim]─── Response ───[/]")
            self._in_thinking = False
            self._thinking_started = False
        elif self._status_printed:
            self._console.print()  # Wrap to new line after "Thinking..."
            self._status_printed = False
        self._console.print(token, end="", soft_wrap=True)

    def on_tool_call(self, tool_name: str, args: str) -> None:
        """Display tool call notification."""
        if self._in_thinking:
            self._console.print()  # End thinking line before tool call
            self._in_thinking = False
            self._thinking_started = False
        self._console.print()
        self._console.print(f"[bold cyan]→ callTool: {tool_name}[/] {args[:100]}")
        self._status_printed = False

    def on_tool_result(self, result_summary: str) -> None:
        """Display tool result summary."""
        self._console.print()
        if len(result_summary) > 200:
            result_summary = result_summary[:200] + "..."
        self._console.print(f"[dim]→ ToolResult: {result_summary}[/]")

    def on_stream_end(self) -> None:
        """Handle stream end."""
        if self._status_printed:
            self._status_printed = False
        self._in_thinking = False
        self._thinking_started = False
        self._console.print()

app = typer.Typer(
    name="bughunter",
    help="Bug Hunter - AI-powered security research assistant (run 'bughunter tui' for the TUI workbench)",
    no_args_is_help=False,
    add_completion=False,
)

console = Console()
err_console = Console(stderr=True)


# Banner

ASCII_LOGO = (
    "  ____              _   _             _            \n"
    " | __ ) _   _  __ _| | | |_   _ _ __ | |_ ___ _ __ \n"
    " |  _ \\| | | |/ _` | |_| | | | | '_ \\| __/ _ \\ '__|\n"
    " | |_) | |_| | (_| |  _  | |_| | | | | ||  __/ |   \n"
    " |____/ \\__,_|\\__, |_| |_|\\__,_|_| |_|\\__\\___|_|   \n"
    "          |___/                                    \n"
)

BANNER_SUBTITLE = f"Bug Hunter v{__version__} - AI-powered security research assistant"


def _print_banner() -> None:
    logo = Text(ASCII_LOGO, style="bold red")
    subtitle = Text(BANNER_SUBTITLE)
    console.print(logo)
    console.print(subtitle)
    console.print()


def _print_agent_output(output: str, config) -> None:
    """Print agent output with think-tag filtering based on config."""
    from rich.markup import escape as rich_escape

    formatted = format_think_tags(output, show=config.session.show_thinking)
    if formatted:
        # LLM output may contain Rich-style brackets like [/TOOL_CALL] which
        # cause MarkupError.  Escape before printing so they render literally.
        console.print(rich_escape(formatted))
    elif not config.session.show_thinking:
        # Check if the original output had thinking content that was stripped
        stripped = strip_think_tags(output)
        had_thinking = (stripped != output) and not stripped
        if had_thinking:
            console.print("[dim](LLM returned only hidden reasoning and no visible answer.)[/dim]")


def _make_solve_event_printer(target_console):
    """Return an on_event callback that prints solve-engine progress live."""

    def on_event(kind: str, payload: dict) -> None:
        if kind == "reason":
            decision = payload.get("decision") or {}
            complete_flag = decision.get("complete")
            if complete_flag is not None and complete_flag is not False:
                # Complete completed / complete_rejected
                # Goal achieved
                pass
            elif decision.get("intents"):
                target_console.print(
                    f"[cyan]◆ Reason:[/cyan] propose {len(decision['intents'])} newExploration direction"
                )
            else:
                target_console.print("[dim]◆ Reason: No new direction is added yet[/dim]")
        elif kind == "completed":
            target_console.print("[green]✓ Reason: Goal achieved[/green]")
        elif kind == "explore_start":
            target_console.print(
                f"[yellow]▶ Explore {payload['intent_id']}:[/yellow] {payload['description'][:90]}"
            )
        elif kind == "conclude":
            target_console.print(
                f"[green]＋ Fact {payload.get('fact', '')}:[/green] {payload.get('desc', '')[:90]}"
            )
        elif kind == "hallucination":
            target_console.print(
                f"[red]⚠ Illusion interception {payload['intent_id']}:[/red] claimed flag No real evidence, rejected"
            )
        elif kind == "complete_rejected":
            target_console.print(f"[red]⚠ rejectComplete:[/red] {payload.get('reason', '')[:90]}")
        elif kind == "abandon":
            target_console.print(f"[red]✗ give up {payload['intent_id']}[/red]")

    return on_event


# REPL


def _prepare_repl_target(
    agent, requested_target: str, current_target: Optional[str], current_phase: str
) -> tuple[str, str, bool]:
    """Prepare REPL state for a target switch and optionally restore history."""
    target = requested_target.strip()
    if not target:
        return current_target or "", current_phase, False

    if current_target and current_target != target:
        console.print(
            f"[dim][*] Target switch: {current_target} -> {target}, resetting session context[/]"
        )
        agent.reset_context()
        current_phase = agent.session_state.phase.value

    restore_result = apply_target_state_to_agent(agent, target)
    current_phase = restore_result.phase or agent.session_state.phase.value
    return target, current_phase, restore_result.restored


async def _run_repl_agent_call(agent, *, call, after_result) -> None:
    """Run a REPL agent call and hand each result back to a caller hook."""
    await run_repl_call(call=call, after_result=after_result)


def _run_repl() -> None:
    """Run the interactive REPL loop."""
    from bughunter.agent.core import AgentCore
    from bughunter.mcp.lifecycle import MCPLifecycleManager

    _print_banner()

    config = load_config()
    if not config.llm.api_key:
        console.print(_("cli.no_api_key"))
        console.print(_("cli.choose_provider"))
        console.print(_("cli.set_env_var"))
        console.print()
        console.print(_("cli.offline_mode"))

    # Initialize MCP lifecycle manager
    mcp_manager = MCPLifecycleManager(config)
    started = mcp_manager.start_enabled_servers()
    console.print(_("cli.mcp_registered", count=started))
    # Report any servers that failed to attach so the user knows immediately
    for srv_name, srv_state in mcp_manager.registry.get_all_servers().items():
        if srv_state.health_status in ("degraded", "unavailable") and srv_state.execution_mode in ("placeholder",):
            err_msg = getattr(srv_state, "error", "") or ""
            if err_msg:
                console.print(f"[yellow]  ⚠ {srv_name}: {err_msg[:120]}[/yellow]")

    # Initialize agent
    agent = AgentCore(config, mcp_manager)

    # Display provider status
    console.print(f"[bold green][+] Primary LLM:[/] {config.llm.provider} ({config.llm.model})")
    if config.llm.fallback_providers:
        for fb in config.llm.fallback_providers:
            key_count = 1 + len(fb.api_keys)
            model_label = fb.model or config.llm.model
            console.print(
                f"[bold blue][+] Fallback LLM:[/] {fb.name} "
                f"({key_count} key{'s' if key_count > 1 else ''}, model: {model_label})"
            )
    # Auto-start Kali sandbox if configured
    sandbox_started = False
    if getattr(config.safety, 'sandbox_auto_start', True):
        try:
            import threading

            from bughunter.agent.builtin_tools import _SANDBOX_SESSION_ID, _get_sandbox_manager

            sandbox_mgr = _get_sandbox_manager()
            console.print("[bold cyan][+] Kali Sandbox:[/] Starting in background...")

            def _bg_sandbox_start():
                nonlocal sandbox_started
                import asyncio
                import logging
                # Suppress paramiko's noisy SSH banner errors during startup retries.
                # Paramiko's transport thread writes directly to stderr, so we need
                # to temporarily redirect it in addition to setting log levels.
                logging.getLogger("paramiko").setLevel(logging.CRITICAL)
                logging.getLogger("paramiko.transport").setLevel(logging.CRITICAL)
                try:
                    loop = asyncio.new_event_loop()
                    session = loop.run_until_complete(sandbox_mgr.start_sandbox(_SANDBOX_SESSION_ID))
                    loop.close()
                except Exception:
                    return
                try:
                    if session.status == "running":
                        sandbox_started = True
                        console.print(
                            f"[bold green][+] Kali Sandbox:[/] Ready "
                            f"(container={session.container_name}, ssh_port={session.ssh_port})"
                        )
                    else:
                        console.print(f"[yellow][!] Kali Sandbox:[/] Failed to start (status: {session.status})")
                except Exception as e:
                    console.print(f"[yellow][!] Kali Sandbox:[/] {e}")

            threading.Thread(target=_bg_sandbox_start, daemon=True).start()
        except Exception as e:
            console.print(f"[yellow][!] Kali Sandbox auto-start skipped:[/] {e}")

    console.print(_("cli.welcome"))
    console.print()

    # Track current target
    current_target: Optional[str] = None
    current_phase: str = "Ready"
    exit_requested = False
    auto_mode_active = False
    _last_ctrlc_time = 0.0
    last_auto_input: str = ""

    # Initialize prompt_toolkit session for multi-line paste & command history support
    _prompt_session = None
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.formatted_text import ANSI
        from prompt_toolkit.history import InMemoryHistory

        _prompt_session = PromptSession(history=InMemoryHistory())
    except Exception:
        _prompt_session = None

    while True:
        try:
            # Build prompt string
            prompt_parts = []
            if current_target:
                prompt_parts.append(f"[bold cyan]{current_target}[/]")
            prompt_parts.append(f"[dim]{current_phase}[/]")
            if auto_mode_active:
                prompt_parts.append("[bold yellow]AUTO[/]")
            prompt_str = " | ".join(prompt_parts) if prompt_parts else "bughunter"

            # Read input (supports pasting long multi-line prompts via prompt_toolkit bracketed paste)
            with console.capture() as capture:
                console.print(f"bughunter {prompt_str}> ", end="")
            prompt_ansi_str = capture.get()

            if _prompt_session is not None:
                try:
                    user_input = _prompt_session.prompt(ANSI(prompt_ansi_str)).strip()
                except (KeyboardInterrupt, EOFError):
                    raise
                except Exception:
                    user_input = console.input(f"bughunter {prompt_str}> ").strip()
            else:
                user_input = console.input(f"bughunter {prompt_str}> ").strip()

            if not user_input:
                if last_auto_input:
                    user_input = last_auto_input
                    console.print(f"[dim]↻ Resuming auto pentest: {last_auto_input[:60]}...[/]")
                else:
                    continue

            # Handle built-in commands
            cmd_lower = user_input.lower()

            if cmd_lower in ("exit", "quit", "q"):
                console.print(_("cli.bye"))
                break

            elif cmd_lower in ("paste", "multiline", ":::"):
                console.print("[bold cyan][+] Multi-line Input Mode[/bold cyan]")
                console.print("[dim]    Paste or type your long prompt below. Type 'END' on a new line or press Enter twice when finished.[/dim]")
                collected_lines = []
                while True:
                    try:
                        line = console.input("[dim]... [/dim]")
                        if line.strip().upper() in ("END", "EOF", ":::"):
                            break
                        if not line.strip() and collected_lines and not collected_lines[-1].strip():
                            break
                        collected_lines.append(line)
                    except (KeyboardInterrupt, EOFError):
                        break
                user_input = "\n".join(collected_lines).strip()
                if not user_input:
                    continue
                cmd_lower = user_input.lower()

            elif cmd_lower == "help":
                _print_help()
                continue

            elif cmd_lower == "status":
                _print_status(agent, mcp_manager, current_target, current_phase, config)
                continue

            elif cmd_lower.startswith("target "):
                current_target, current_phase, restored_loaded = _prepare_repl_target(
                    agent,
                    user_input[7:].strip(),
                    current_target,
                    current_phase,
                )
                if restored_loaded:
                    console.print(_("cli.target_restored", target=current_target))
                console.print(_("cli.target_set", target=current_target))
                continue

            elif cmd_lower == "clear":
                current_target = None
                current_phase = "Ready"
                auto_mode_active = False
                last_auto_input = ""
                agent.reset_context()
                console.print(_("cli.conversation_cleared"))
                continue

            elif cmd_lower == "tools":
                tools = mcp_manager.list_available_tools()
                if tools:
                    console.print(_("cli.available_tools"))
                    for tool in tools:
                        console.print(f"  - {tool}")
                else:
                    console.print(_("cli.no_tools"))
                continue

            elif cmd_lower.startswith("report"):
                report_target = user_input[len("report") :].strip() or current_target
                if not report_target:
                    console.print(_("cli.no_target_for_report"))
                    continue

                report_path = _generate_report_for_target(
                    report_target,
                    current_session=agent.session_state
                    if agent.session_state.target == report_target
                    else None,
                    report_format=config.session.report_format,
                )
                console.print(_("cli.report_generated", path=report_path))
                continue

            elif cmd_lower.startswith("sandbox"):
                sandbox_args = user_input[len("sandbox"):].strip()
                _handle_sandbox_command(sandbox_args, console)
                continue

            elif cmd_lower == "findings":
                _print_findings(agent, console)
                continue

            elif cmd_lower == "pool":
                _print_model_pool(config, console)
                continue

            elif cmd_lower == "subagents":
                _print_subagent_status(agent, console)
                continue

            elif cmd_lower == "config":
                _print_config(config, console)
                continue

            elif cmd_lower.startswith("budget"):
                budget_arg = user_input[len("budget"):].strip().lower()
                if budget_arg == "off" or budget_arg == "0":
                    config.session.scan_time_budget = 0
                    console.print("[green]✓[/] Time budget disabled (unlimited).")
                elif budget_arg.isdigit():
                    mins = int(budget_arg)
                    config.session.scan_time_budget = mins
                    console.print(
                        f"[green]✓[/] Time budget set to [bold]{mins} minutes[/].\n"
                        f"  Quick: {int(mins*0.2)}m → Standard: {int(mins*0.4)}m "
                        f"→ Deep: {int(mins*0.3)}m → Report: {int(mins*0.1)}m"
                    )
                else:
                    current = getattr(config.session, "scan_time_budget", 0)
                    if current > 0:
                        console.print(
                            f"[bold]⏱️  Time budget:[/] {current} minutes\n"
                            f"  Quick: {int(current*0.2)}m → Standard: {int(current*0.4)}m "
                            f"→ Deep: {int(current*0.3)}m → Report: {int(current*0.1)}m\n"
                            f"  Tool timeouts: quick={config.session.scan_tool_timeout_quick}s, "
                            f"standard={config.session.scan_tool_timeout_standard}s, "
                            f"deep={config.session.scan_tool_timeout_deep}s"
                        )
                    else:
                        console.print(
                            "[bold]⏱️  Time budget:[/] unlimited (no deadline)\n"
                            "  Set with: [cyan]budget 30[/] (minutes) or say "
                            "[cyan]pentest target.com in 30 minutes[/]"
                        )
                continue
            elif cmd_lower.startswith("persistent"):
                explicit_target = user_input[len("persistent") :].strip()
                persistent_target = explicit_target or current_target
                if not persistent_target:
                    console.print(
                        "[!] Set a target first with [bold]target <host>[/] or run [bold]persistent <host>[/]."
                    )
                    continue

                current_target, current_phase, restored_loaded = _prepare_repl_target(
                    agent,
                    persistent_target,
                    current_target,
                    current_phase,
                )
                persistent_target = current_target
                if restored_loaded:
                    console.print(_("cli.target_restored", target=persistent_target))

                from bughunter.agent.core import PersistentCycleResult

                rounds_per_cycle = config.session.persistent_rounds_per_cycle
                max_cycles = config.session.persistent_max_cycles
                auto_report = config.session.persistent_auto_report

                console.print(
                    Panel(
                        f"Target: [bold]{persistent_target}[/]\n"
                        f"Rounds per cycle: [bold]{rounds_per_cycle}[/]\n"
                        f"Max cycles: [bold]{max_cycles}[/]\n"
                        f"Auto report: {'[green]on[/]' if auto_report else '[yellow]off[/]'}",
                        title="Persistent Pentest",
                        border_style="cyan",
                    )
                )

                persistent_prompt = (
                    f"Perform an authorized persistent penetration test against {persistent_target}. "
                    "This target is in scope and explicitly authorized."
                )

                all_cycle_results: list[PersistentCycleResult] = []

                def _on_persistent_step(round_num: int, cycle_num: int, result) -> None:
                    console.print(f"[dim]-- Cycle {cycle_num} | Round {round_num} --[/]")
                    # TerminalStreamSink Real-time streaming display, callback does not print repeatedly
                    console.print()
                    nonlocal current_target, current_phase
                    if result.target:
                        current_target = result.target
                    if result.phase:
                        current_phase = result.phase

                def _on_persistent_cycle(
                    cycle_num: int, cycle_result: PersistentCycleResult
                ) -> None:
                    all_cycle_results.append(cycle_result)
                    console.print(
                        Panel(
                            f"Cycle {cycle_num} completed\n"
                            f"   Total findings: {cycle_result.total_findings}\n"
                            f"   New findings: {cycle_result.new_findings}\n"
                            f"   Report: {cycle_result.report_path or 'not generated'}",
                            title=f"Cycle {cycle_num}",
                            border_style="green" if cycle_result.new_findings == 0 else "red",
                        )
                    )
                    console.print()

                try:

                    async def _run_persistent():
                        sink = TerminalStreamSink(console, config.session.show_thinking)
                        return await agent.persistent_pentest(
                            user_input=persistent_prompt,
                            target=persistent_target,
                            rounds_per_cycle=rounds_per_cycle,
                            max_cycles=max_cycles,
                            auto_report=auto_report,
                            on_cycle_step=_on_persistent_step,
                            on_cycle_complete=_on_persistent_cycle,
                            stream_sink=sink,
                        )

                    asyncio.run(_run_persistent())
                    if auto_report and not all_cycle_results:
                        partial_report = _generate_report_for_target(
                            persistent_target,
                            current_session=agent.session_state,
                            report_format=config.session.report_format,
                        )
                        console.print(_("cli.partial_report", path=partial_report))
                except KeyboardInterrupt:
                    console.print(f"\n{_('persistent.interrupted_message')}")
                    if agent.session_state.findings:
                        try:
                            final_report = _generate_report_for_target(
                                persistent_target,
                                current_session=agent.session_state,
                                report_format=config.session.report_format,
                            )
                            console.print(_("persistent.final_report", path=final_report))
                        except Exception as exc:
                            console.print(_("persistent.failed_final_report", exc=exc))

                # Summary
                tf = len(agent.session_state.findings)
                console.print(
                    _("persistent.finished_summary", cycles=len(all_cycle_results), findings=tf)
                )
                continue

            elif cmd_lower == "think":
                # Toggle think tag display
                config.session.show_thinking = not config.session.show_thinking
                state_str = (
                    "[green]shown[/]" if config.session.show_thinking else "[yellow]hidden[/]"
                )
                console.print(f"[*] Thinking visibility: {state_str}")
                console.print(_("cli.thinking_toggle_hint"))
                continue

            elif cmd_lower == "think on":
                config.session.show_thinking = True
                console.print(_("cli.thinking_shown"))
                continue

            elif cmd_lower == "think off":
                config.session.show_thinking = False
                console.print(_("cli.thinking_hidden"))
                continue

            # Handle auto mode persistence: exit auto mode on explicit commands
            if auto_mode_active and user_input.lower().strip() in (
                "chat", "manual", "exit auto", "Single-turn", "Manual",
            ):
                auto_mode_active = False
                last_auto_input = ""
                console.print(_("cli.auto_mode_exited"))
                is_auto_mode = False
            elif auto_mode_active:
                is_auto_mode = True
            else:
                # Route to agent and detect whether this should be an autonomous loop
                is_auto_mode = _should_auto_pentest(user_input, current_target)

            # Detect target switch and reset context if the user mentions a new target
            new_target = _extract_target_from_input(user_input)
            if new_target and current_target and new_target != current_target:
                console.print(_("cli.target_switch", from_target=current_target, to_target=new_target))
                current_target = new_target
                current_phase = "Recon"
                agent.reset_context()
                # Reset auto mode on target switch
                auto_mode_active = False
                last_auto_input = ""

            # Save last auto input for resume on empty Enter
            if is_auto_mode:
                last_auto_input = user_input

            try:
                if is_auto_mode:
                    # Autonomous pentest loop
                    console.print(_("cli.enter_auto_mode"))
                    console.print()

                    # Parse time budget from input: "pentest X in 30 minutes"
                    time_budget = _extract_time_budget(user_input)
                    if time_budget > 0:
                        console.print(
                            f"[bold cyan]⏱️  Time Budget:[/] {time_budget} minutes "
                            f"(Quick {int(time_budget*0.2)}m → Standard {int(time_budget*0.4)}m "
                            f"→ Deep {int(time_budget*0.3)}m → Report {int(time_budget*0.1)}m)"
                        )
                        console.print()

                    # Go by defaultTargetdrive solve engine;engine=rounds Fallback to the old fixedroundCount loop
                    if getattr(config.session, "engine", "solve") == "solve":
                        async def _run_auto():
                            sink = TerminalStreamSink(console, config.session.show_thinking)

                            async def call():
                                return await agent.solve(
                                    user_input,
                                    target=current_target,
                                    max_steps=config.session.solve_max_steps,
                                    max_intents=config.session.solve_max_intents,
                                    max_tool_rounds=config.session.solve_max_tool_rounds,
                                    stream_sink=sink,
                                    on_event=_make_solve_event_printer(console),
                                    time_budget_minutes=time_budget,
                                )

                            async def after_result(result):
                                board = agent.context.state.board.get_summary()
                                done = board.get("completed")
                                console.print()
                                console.print(
                                    Panel(
                                        f"{'✅ Goal achieved' if done else '⊘ Not achieved'} — "
                                        f"facts={board.get('facts', 0)} intents={board.get('intents', 0)}\n"
                                        f"reason: {board.get('complete_reason') or 'ExploreEnd'}",
                                        title="Solve",
                                        border_style="green" if done else "yellow",
                                    )
                                )

                            await _run_repl_agent_call(agent, call=call, after_result=after_result)

                        asyncio.run(_run_auto())
                        auto_mode_active = True
                        console.print(_("cli.auto_mode_hint"))
                        continue

                    async def _run_auto():
                        sink = TerminalStreamSink(console, config.session.show_thinking)
                        async def call():
                            def on_step(round_num, result):
                                nonlocal current_target, current_phase
                                console.print(f"[dim]-- Round {round_num} --[/]")
                                console.print()
                                if result.target:
                                    current_target = result.target
                                if result.phase:
                                    current_phase = result.phase

                            return await agent.auto_pentest(
                                user_input,
                                target=current_target,
                                max_rounds=config.session.max_rounds,
                                on_step=on_step,
                                stream_sink=sink,
                                time_budget_minutes=time_budget,
                            )

                        async def after_result(results):
                            if results:
                                total_findings = len(agent.session_state.findings)
                                total_steps = len(agent.session_state.executed_steps)
                                console.print()
                                console.print(
                                    Panel(
                                        f"{_('auto_pentest.finished')}\n"
                                        f"{_('auto_pentest.rounds', rounds=len(results))}\n"
                                        f"{_('auto_pentest.steps', steps=total_steps)}\n"
                                        f"{_('auto_pentest.findings', findings=total_findings)}",
                                        title=_("auto_pentest.title"),
                                        border_style="green" if total_findings == 0 else "red",
                                    )
                                )

                                if any(
                                    token in user_input.lower()
                                    for token in (
                                        "Output",
                                        "Save",
                                        "write to",
                                        "Export",
                                        "save",
                                        "write",
                                        "export",
                                    )
                                ):
                                    _auto_save_recon_report(agent, user_input, config)

                        await _run_repl_agent_call(agent, call=call, after_result=after_result)

                    asyncio.run(_run_auto())
                    auto_mode_active = True
                    console.print(_("cli.auto_mode_hint"))

                else:
                    # Single-turn chat
                    async def _run_agent():
                        sink = TerminalStreamSink(console, config.session.show_thinking)
                        async def call():
                            return await agent.chat(user_input, target=current_target, stream_sink=sink)

                        async def after_result(result):
                            nonlocal current_target, current_phase
                            if result:
                                if result.target:
                                    current_target = result.target
                                if result.phase:
                                    current_phase = result.phase
                                # Comment out: streamingOutputPassed TerminalStreamSink Real-time display without repeated printing
                                # if result.output:
                                #     _print_agent_output(result.output, config)

                        await _run_repl_agent_call(agent, call=call, after_result=after_result)

                    asyncio.run(_run_agent())

            except KeyboardInterrupt:
                if is_auto_mode:
                    auto_mode_active = False
                    console.print()
                    console.print(_("cli.interrupted"))
                    console.print(_("cli.auto_resume_hint"))
                else:
                    console.print(f"\n{_('cli.interrupted')}")
            except Exception as e:
                # Escape Rich markup chars in exception message to prevent MarkupError
                from rich.markup import escape as rich_escape

                console.print(_("cli.error", msg=rich_escape(str(e))))

        except KeyboardInterrupt:
            now = time.monotonic()
            if exit_requested and (now - _last_ctrlc_time) < 3.0:
                console.print(_("cli.bye"))
                break
            exit_requested = True
            _last_ctrlc_time = now
            console.print(f"\n{_('cli.press_again')}")
        except EOFError:
            break

    # Cleanup — suppress SIGINT to prevent re-trigger during threading shutdown
    import signal

    signal.signal(signal.SIGINT, signal.SIG_IGN)
    mcp_manager.stop_all()
    console.print("[dim]MCP services stopped.[/]")
    # Cleanup sandbox
    if sandbox_started:
        try:
            from bughunter.agent.builtin_tools import _SANDBOX_SESSION_ID, _get_sandbox_manager
            _get_sandbox_manager().stop_sandbox(_SANDBOX_SESSION_ID)
            console.print("[dim]Kali sandbox stopped.[/]")
        except Exception:
            pass


def _print_help() -> None:
    """Print REPL help."""
    help_text = f"""
 [bold]{_("help.commands")}[/]:
  {_("help.target")}
  {_("help.status")}
  {_("help.tools")}
  {_("help.report")}
  {_("help.think")}
  {_("help.think_on_off")}
  {_("help.persistent")}
  {_("help.persistent_host")}
  {_("help.findings")}
  {_("help.pool")}
  [cyan]subagents[/]        — Show active/completed sub-agent status
  {_("help.config")}
  {_("help.budget")}
  {_("help.clear")}
  [cyan]paste[/] or [cyan]multiline[/] — Enter multi-line prompt paste mode
  {_("help.chat")}
  {_("help.help")}
  {_("help.exit")}

 [bold]{_("help.sandbox_section")}[/]:
  {_("help.sandbox")}
  {_("help.sandbox_start")}
  {_("help.sandbox_stop")}
  {_("help.sandbox_exec")}

 [bold]{_("help.auto_mode")}[/]:
  {_("help.auto_mode_desc")}
  {_("help.auto_mode_example")}
  {_("help.auto_mode_stays")}

 [bold]{_("help.persistent_mode")}[/]:
  {_("help.persistent_mode_desc")}
  {_("help.persistent_cli")}
  {_("help.persistent_repl")}

 [bold]{_("help.examples")}[/]:
  {_("help.example_pentest")}
  {_("help.example_scan")}
  {_("help.example_vuln")}
  {_("help.example_exploit")}
  {_("help.example_report")}
"""
    console.print(Panel(help_text, title=_("help.title"), border_style="cyan"))


def _print_status(agent, mcp_manager, target, phase, config) -> None:
    """Print current session status."""
    think_state = "[green]shown[/]" if config.session.show_thinking else "[yellow]hidden[/]"
    findings_count = len(agent.session_state.findings) if hasattr(agent, 'session_state') else 0
    pool = config.llm.model_pool
    primary_model = pool[0].name if pool else config.llm.model
    pool_count = len(pool)

    # Sandbox status
    try:
        from bughunter.agent.builtin_tools import _sandbox_manager
        if _sandbox_manager is not None:
            sessions = _sandbox_manager.list_sessions()
            running = [s for s in sessions if s.status == "running"]
            sandbox_state = f"[green]running ({len(running)} container{'s' if len(running) != 1 else ''})[/]" if running else "[yellow]stopped[/]"
        else:
            sandbox_state = "[dim]not initialized[/]"
    except Exception:
        sandbox_state = "[dim]not initialized[/]"

    console.print(
        Panel(
            f"{_('status.target', target=target or 'Not set')}\n"
            f"{_('status.phase', phase=phase)}\n"
            f"{_('status.mcp_services', count=mcp_manager.running_count())}\n"
            f"{_('status.tools', count=len(mcp_manager.list_available_tools()))}\n"
            f"{_('status.thinking', state=think_state)}\n"
            f"{_('status.sandbox', state=sandbox_state)}\n"
            f"{_('status.model_pool', primary=primary_model, count=pool_count)}\n"
            f"{_('status.findings', count=findings_count)}",
            title=_("status.title"),
            border_style="green",
        )
    )


def _handle_sandbox_command(args: str, console) -> None:
    """Handle sandbox REPL commands (start/stop/exec/status)."""
    import asyncio

    from rich.table import Table

    from bughunter.agent.builtin_tools import _SANDBOX_SESSION_ID, _get_sandbox_manager

    manager = _get_sandbox_manager()

    if not args or args.lower() == "status":
        # Show sandbox status
        sessions = manager.list_sessions()
        if not sessions:
            console.print("[dim]No sandbox sessions. Use [cyan]sandbox start[/] to launch one.[/]")
            return
        table = Table(title="Kali Sandbox Sessions", border_style="cyan")
        table.add_column("Session ID", style="bold")
        table.add_column("Status")
        table.add_column("Container")
        table.add_column("SSH Port")
        table.add_column("Created")
        for s in sessions:
            status_style = "green" if s.status == "running" else "yellow" if s.status == "starting" else "red"
            table.add_row(
                s.session_id,
                f"[{status_style}]{s.status}[/]",
                s.container_name or "-",
                str(s.ssh_port) if s.ssh_port else "-",
                s.created_at[:19] if s.created_at else "-",
            )
        console.print(table)
        return

    if args.lower() == "start":
        console.print("[*] Starting Kali Linux sandbox...")
        try:
            session = asyncio.run(manager.start_sandbox(_SANDBOX_SESSION_ID))
            if session.status == "running":
                console.print(
                    f"[green]✓[/] Sandbox started: container=[bold]{session.container_name}[/] "
                    f"ssh_port=[bold]{session.ssh_port}[/]"
                )
            else:
                console.print(f"[red]✗[/] Sandbox failed to start (status: {session.status})")
        except Exception as e:
            console.print(f"[red]✗[/] Error starting sandbox: {e}")
        return

    if args.lower() == "stop":
        console.print("[*] Stopping sandbox...")
        try:
            ok = manager.stop_sandbox(_SANDBOX_SESSION_ID)
            if ok:
                console.print("[green]✓[/] Sandbox stopped.")
            else:
                console.print("[yellow]![/] No running sandbox session found.")
        except Exception as e:
            console.print(f"[red]✗[/] Error stopping sandbox: {e}")
        return

    # Anything else is a command to execute in the sandbox
    command = args
    console.print(f"[dim]sandbox $ {command}[/]")
    try:
        session = asyncio.run(manager.start_sandbox(_SANDBOX_SESSION_ID))
        if session.status != "running":
            console.print("[red]✗[/] Sandbox is not running. Use [cyan]sandbox start[/] first.")
            return
        result = asyncio.run(manager.execute_command(_SANDBOX_SESSION_ID, command, timeout=60))
        if result is None:
            console.print("[red]✗[/] Command execution failed.")
            return
        console.print(f"[dim]exit_code: {result.exit_code} | duration: {result.duration_ms}ms[/]")
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[red]{result.stderr}[/]")
        if not result.stdout and not result.stderr:
            console.print("[dim](no output)[/]")
    except Exception as e:
        console.print(f"[red]✗[/] Sandbox exec error: {e}")


def _print_findings(agent, console) -> None:
    """Print all findings from the current session."""
    from rich.table import Table

    findings = agent.session_state.findings if hasattr(agent, 'session_state') else []
    if not findings:
        console.print("[dim]No findings in the current session.[/]")
        return

    table = Table(title=f"Session Findings ({len(findings)})", border_style="red")
    table.add_column("#", style="bold", width=3)
    table.add_column("Severity", width=10)
    table.add_column("Title", min_width=30)
    table.add_column("Category", width=15)
    table.add_column("Target", width=20)

    for i, f in enumerate(findings, 1):
        severity = getattr(f, 'severity', 'unknown') if hasattr(f, 'severity') else f.get('severity', 'unknown') if isinstance(f, dict) else 'unknown'
        title = getattr(f, 'title', str(f)[:60]) if hasattr(f, 'title') else f.get('title', str(f)[:60]) if isinstance(f, dict) else str(f)[:60]
        category = getattr(f, 'category', '-') if hasattr(f, 'category') else f.get('category', '-') if isinstance(f, dict) else '-'
        target = getattr(f, 'target', '-') if hasattr(f, 'target') else f.get('target', '-') if isinstance(f, dict) else '-'

        sev_lower = str(severity).lower()
        sev_style = (
            "red bold" if sev_lower in ("critical", "high")
            else "yellow" if sev_lower == "medium"
            else "green" if sev_lower == "low"
            else "dim"
        )
        table.add_row(str(i), f"[{sev_style}]{severity}[/]", title, category, target)

    console.print(table)


def _print_model_pool(config, console) -> None:
    """Print the AI model pool configuration."""
    from rich.table import Table

    pool = config.llm.model_pool
    if not pool:
        console.print(f"[dim]No model pool configured. Current model: [bold]{config.llm.model}[/][/]")
        return

    table = Table(title=f"AI Model Pool ({len(pool)} models)", border_style="cyan")
    table.add_column("Tier", width=5, style="bold")
    table.add_column("Name", min_width=15)
    table.add_column("Provider", width=12)
    table.add_column("Model", min_width=20)
    table.add_column("Role", width=10)
    table.add_column("Status", width=10)

    for entry in sorted(pool, key=lambda e: e.tier):
        enabled_str = "[green]enabled[/]" if entry.enabled else "[red]disabled[/]"
        tier_style = "bold green" if entry.tier == 1 else "bold yellow" if entry.tier == 2 else "dim"
        table.add_row(
            f"[{tier_style}]T{entry.tier}[/]",
            entry.name,
            entry.provider,
            entry.model,
            entry.role,
            enabled_str,
        )

    console.print(table)
    # Show active primary
    enabled_pool = [e for e in pool if e.enabled]
    if enabled_pool:
        primary = sorted(enabled_pool, key=lambda e: e.tier)[0]
        console.print(f"[dim]Active primary: [bold]{primary.name}[/] ({primary.model})[/]")


def _print_subagent_status(agent, console) -> None:
    """Print the status of active and completed sub-agents."""
    from rich.panel import Panel

    sub_manager = getattr(agent, "sub_agent_manager", None)
    if sub_manager is None:
        console.print("[dim]Sub-agent manager not initialized.[/]")
        console.print("[dim]Configure model_pool in config.yaml to enable sub-agents.[/]")
        return

    summary = sub_manager.get_status_summary()
    available = sub_manager.available_models()

    # Show available models for sub-agents
    if available:
        model_list = ", ".join(f"[bold]{m.name}[/]" for m in available)
        header = f"Available models: {model_list}\n\n"
    else:
        header = "[yellow]⚠ No models available in pool. Add model_pool entries to config.yaml.[/]\n\n"

    console.print(
        Panel(
            header + summary,
            title="🤖 Sub-Agent Status",
            border_style="cyan",
        )
    )


def _print_config(config, console) -> None:
    """Print current LLM configuration summary."""
    from rich.table import Table

    table = Table(title="LLM Configuration", border_style="cyan")
    table.add_column("Setting", style="bold", width=20)
    table.add_column("Value", min_width=30)

    table.add_row("Provider", config.llm.provider or "-")
    table.add_row("Model", config.llm.model or "-")
    table.add_row("Base URL", config.llm.base_url or "-")
    table.add_row("API Key", "[green]configured[/]" if config.llm.api_key else "[red]not set[/]")
    table.add_row("Temperature", str(getattr(config.llm, 'temperature', '-')))
    table.add_row("Max Tokens", str(getattr(config.llm, 'max_tokens', '-')))
    table.add_row("Model Pool", f"{len(config.llm.model_pool)} models" if config.llm.model_pool else "not configured")

    console.print(table)


def _generate_report_for_target(
    target: str,
    *,
    current_session=None,
    report_format: str = "markdown",
) -> str:
    """Generate a report for a target using the best available source data."""
    from bughunter.agent.context import SessionState
    from bughunter.report.generator import generate_report, generate_report_from_target_state
    from bughunter.target_state.store import load_target_state

    if current_session is not None and (
        current_session.findings or current_session.executed_steps or current_session.notes
    ):
        path = generate_report(current_session, report_format=report_format)
        return str(path)

    state = load_target_state(target)
    if state:
        path = generate_report_from_target_state(state)
        return str(path)

    session = SessionState(target=target)
    path = generate_report(session, report_format=report_format)
    return str(path)


def _append_cli_constraints(
    prompt: str,
    only_port: Optional[int],
    only_host: Optional[str],
    only_path: Optional[str],
    blocked_host: Optional[str] = None,
    blocked_path: Optional[str] = None,
) -> str:
    constraints = []
    if only_port is not None:
        constraints.append(f"Only test port {only_port}")
    if only_host:
        constraints.append(f"Only test host {only_host}")
    if only_path:
        constraints.append(f"Only test path {only_path}")
    if blocked_host:
        constraints.append(f"Blocked host {blocked_host}")
    if blocked_path:
        constraints.append(f"Blocked path {blocked_path}")
    if not constraints:
        return prompt
    return f"{prompt} {' '.join(constraints)}."


def _append_cli_constraints_compat(
    prompt: str,
    only_port: Optional[int],
    only_host: Optional[str],
    only_path: Optional[str],
    blocked_host: Optional[str],
    blocked_path: Optional[str],
) -> str:
    """Append scope constraints while preserving older monkeypatch call shapes."""
    try:
        return _append_cli_constraints(
            prompt, only_port, only_host, only_path, blocked_host, blocked_path
        )
    except TypeError as exc:
        if "positional" not in str(exc) and "argument" not in str(exc):
            raise
        return _append_cli_constraints(prompt, only_port, only_host, only_path)


def _append_action_constraints(
    prompt: str, allow_actions: Optional[str], block_actions: Optional[str]
) -> str:
    constraints = []
    if allow_actions:
        constraints.append(f"Only allowed actions: {allow_actions}")
    if block_actions:
        constraints.append(f"Blocked actions: {block_actions}")
    if not constraints:
        return prompt
    return f"{prompt} {' '.join(constraints)}."


async def _run_cli_orchestrated_task(
    *,
    command: str,
    target: str,
    resume: bool,
    snapshot: Optional[str],
    runner,
):
    """Run a CLI task through the shared orchestrator helpers."""
    from bughunter.agent.core import AgentCore
    from bughunter.mcp.lifecycle import MCPLifecycleManager

    config = load_config()
    mcp_manager = MCPLifecycleManager(config)
    mcp_manager.start_enabled_servers()
    agent = AgentCore(config, mcp_manager)

    # Auto-start Kali sandbox for CLI tasks
    sandbox_active = False
    if getattr(config.safety, 'sandbox_auto_start', True):
        try:
            from bughunter.agent.builtin_tools import _SANDBOX_SESSION_ID, _get_sandbox_manager
            sandbox_mgr = _get_sandbox_manager()
            console.print("[bold cyan][+] Kali Sandbox:[/] Starting...")
            session = await sandbox_mgr.start_sandbox(_SANDBOX_SESSION_ID)
            if session.status == "running":
                sandbox_active = True
                console.print(
                    f"[bold green][✓] Kali Sandbox:[/] Ready "
                    f"(container={session.container_name}, ssh_port={session.ssh_port})"
                )
            else:
                console.print(f"[yellow][!] Kali Sandbox:[/] Failed (status: {session.status})")
        except Exception as e:
            console.print(f"[yellow][!] Kali Sandbox:[/] {e}")

    try:

        def on_restored(restore_result) -> None:
            console.print(
                f"[*] Restored saved target state: [bold]{restore_result.target or target}[/]"
            )

        return await run_agent_task(
            agent=agent,
            command=command,
            target=target,
            resume=resume,
            snapshot_id=snapshot,
            on_restored=on_restored,
            runner=lambda shared_agent: runner(shared_agent, config),
        )
    finally:
        import signal

        signal.signal(signal.SIGINT, signal.SIG_IGN)
        mcp_manager.stop_all()
        # Cleanup sandbox
        if sandbox_active:
            try:
                from bughunter.agent.builtin_tools import _SANDBOX_SESSION_ID, _get_sandbox_manager
                _get_sandbox_manager().stop_sandbox(_SANDBOX_SESSION_ID)
            except Exception:
                pass


# Lithium€Lithium€ Sub-commands Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€


@app.command()
def run(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    scope: str = typer.Option("full", help="Test scope: full, web, api, mobile"),
    output: Optional[str] = typer.Option(None, help="Output report file path"),
    # [Added] 2026-06-10 Nyaecho - TUINatural language driven: Allowpass --prompt incomingCustomHintWord coverage automatically generatedprompt
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restrict testing to a single path"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Explicitly blocked path"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
) -> None:
    """Run a full authorized pentest workflow."""
    config = load_config()
    if not config.llm.api_key:
        err_console.print("[!] Configure an LLM API key first.")
        raise typer.Exit(1)

    console.print(f"[*] Target: [bold]{target}[/] | Scope: [bold]{scope}[/]")

    task_prompt = prompt if prompt else (
        f"Perform an authorized {scope} pentest against {target}. "
        "This target is in scope and explicitly authorized."
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("run", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    board_holder: dict = {}

    async def _run():
        async def runner(agent, shared_config):
            sink = TerminalStreamSink(console, shared_config.session.show_thinking)
            # Go by defaultTargetdrive solve engine;engine=rounds Fallback to the old fixedroundCount loop
            if getattr(shared_config.session, "engine", "solve") == "solve":
                result = await agent.solve(
                    task_prompt,
                    target=target,
                    max_steps=shared_config.session.solve_max_steps,
                    max_intents=shared_config.session.solve_max_intents,
                    max_tool_rounds=shared_config.session.solve_max_tool_rounds,
                    stream_sink=sink,
                    on_event=_make_solve_event_printer(console),
                )
                board_holder["board"] = agent.context.state.board.get_summary()
                return result
            return await agent.auto_pentest(
                task_prompt,
                target=target,
                max_rounds=shared_config.session.max_rounds,
                on_step=lambda r, res: (
                    _print_agent_output(f"[dim]Round {r}[/]: {res.output[:200]}...", shared_config)
                    if res.output
                    else None
                ),
                stream_sink=sink,
            )

        result = await _run_cli_orchestrated_task(
            command="run",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )
        return result

    orchestrated = asyncio.run(_run())
    if board_holder.get("board"):
        board = board_holder["board"]
        status = "✅ Goal achieved" if board.get("completed") else "⊘ Not achieved"
        console.print(
            f"\n[bold]{status}[/bold] — facts={board.get('facts', 0)} "
            f"intents={board.get('intents', 0)} reason: {board.get('complete_reason') or 'ExploreEnd'}"
        )
    else:
        total_findings = orchestrated.summary["findings_count"]
        console.print(_("cli.pentest_finished", findings=total_findings))


@app.command()
def solve(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    goal: Optional[str] = typer.Option(
        None, "--goal", help="Success condition, e.g. 'capture the flag' / 'get a shell'"
    ),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom task description (overrides auto-generated)"
    ),
    max_steps: int = typer.Option(
        40, "--max-steps", help="Safety cap on explore steps (NOT a fixed workflow length)"
    ),
    max_intents: int = typer.Option(3, "--max-intents", help="Max new intents per reason step"),
    max_tool_rounds: int = typer.Option(
        4, "--max-tool-rounds", help="Max tool-calling rounds per intent exploration"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(None, "--snapshot", help="Resume from a snapshot id"),
) -> None:
    """Goal-driven solve loop — runs until the goal is met or the exploration frontier is exhausted.

    Unlike `run`, this has no fixed round count. It searches a Fact/Intent graph
    from the target toward the goal and stops on success or when no path remains.
    """
    config = load_config()
    if not config.llm.api_key:
        err_console.print("[!] Configure an LLM API key first.")
        raise typer.Exit(1)

    resolved_goal = goal or "turn up flag / get shell / Confirmand verifyHighvalueVulnerability"
    task_prompt = prompt or (
        f"right {target} AuthorizePenetration Testing. This is explicit authorization、within rangeTarget.Target(goal):{resolved_goal}."
    )
    console.print(f"[*] Target: [bold]{target}[/] | Goal: [bold]{resolved_goal}[/]")

    on_event = _make_solve_event_printer(console)
    holder: dict = {}

    async def _run():
        async def runner(agent, shared_config):
            sink = TerminalStreamSink(console, shared_config.session.show_thinking)
            result = await agent.solve(
                task_prompt,
                target=target,
                goal=resolved_goal,
                max_steps=max_steps,
                max_intents=max_intents,
                max_tool_rounds=max_tool_rounds,
                stream_sink=sink,
                on_event=on_event,
            )
            holder["board"] = agent.context.state.board.get_summary()
            return result

        return await _run_cli_orchestrated_task(
            command="solve",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )

    asyncio.run(_run())
    board = holder.get("board") or {}
    status = "✅ Goal achieved" if board.get("completed") else "⊘ Not achieved"
    console.print(
        f"\n[bold]{status}[/bold] — facts={board.get('facts', 0)} "
        f"intents={board.get('intents', 0)} reason: {board.get('complete_reason') or 'ExploreEnd'}"
    )


@app.command()
def persistent(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    rounds: int = typer.Option(
        0, "--rounds", "-r", help="Rounds per cycle (0=use config, default 100)"
    ),
    cycles: int = typer.Option(0, "--cycles", "-c", help="Max cycles (0=use config, default 10)"),
    no_report: bool = typer.Option(
        False, "--no-report", help="Disable auto report after each cycle"
    ),
    # [Added] 2026-06-10 Nyaecho - TUINatural language driven: Allowpass --prompt incomingCustomHintWord coverage automatically generatedprompt
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restrict testing to a single path"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Explicitly blocked path"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
) -> None:
    """Run a persistent authorized pentest across multiple cycles."""
    from bughunter.agent.core import PersistentCycleResult

    config = load_config()
    if not config.llm.api_key:
        err_console.print("[!] Configure an LLM API key first.")
        raise typer.Exit(1)

    # Resolve parameters (CLI override -> config defaults)
    rounds_per_cycle = rounds if rounds > 0 else config.session.persistent_rounds_per_cycle
    max_cycles = cycles if cycles > 0 else config.session.persistent_max_cycles
    auto_report = config.session.persistent_auto_report and not no_report

    console.print(
        Panel(
            f"Target: [bold]{target}[/]\n"
            f"Rounds per cycle: [bold]{rounds_per_cycle}[/]\n"
            f"Max cycles: [bold]{max_cycles}[/] {'(unlimited)' if max_cycles == 0 else ''}\n"
            f"Auto report: {'[green]on[/]' if auto_report else '[yellow]off[/]'}\n"
            f"Max total rounds: [bold]{rounds_per_cycle * max_cycles if max_cycles > 0 else 'unlimited'}[/]",
            title="Persistent Pentest",
            border_style="cyan",
        )
    )

    task_prompt = prompt if prompt else (
        f"Perform an authorized persistent penetration test against {target}. "
        "This target is in scope and explicitly authorized."
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("persistent", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    # Track stats
    all_cycle_results: list[PersistentCycleResult] = []
    interrupted = False

    def _on_cycle_step(round_num: int, cycle_num: int, result) -> None:
        """Real-time output for each step within a cycle."""
        console.print(f"[dim]-- Cycle {cycle_num} | Round {round_num} --[/]")
        # TerminalStreamSink Real-time streaming display, callback does not print repeatedly
        console.print()

    def _on_cycle_complete(cycle_num: int, cycle_result: PersistentCycleResult) -> None:
        """Callback after each cycle completes."""
        all_cycle_results.append(cycle_result)
        console.print(
            Panel(
                f"Cycle {cycle_num} completed\n"
                f"   Steps executed: {cycle_result.total_steps}\n"
                f"   Total findings: {cycle_result.total_findings}\n"
                f"   New findings: {cycle_result.new_findings}\n"
                f"   Report: {cycle_result.report_path or 'not generated'}",
                title=f"Cycle {cycle_num} Result",
                border_style="green" if cycle_result.new_findings == 0 else "red",
            )
        )
        console.print()

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            return await agent.persistent_pentest(
                user_input=task_prompt,
                target=target,
                rounds_per_cycle=rounds_per_cycle,
                max_cycles=max_cycles,
                auto_report=auto_report,
                on_cycle_step=_on_cycle_step,
                on_cycle_complete=_on_cycle_complete,
                stream_sink=sink,
            )

        return await _run_cli_orchestrated_task(
            command="persistent",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )

    try:
        orchestrated = asyncio.run(_run())
    except KeyboardInterrupt:
        interrupted = True
        console.print("\n[!] User interrupted persistent pentest")
        orchestrated = None

    summary = (
        orchestrated.summary
        if orchestrated
        else {
            "findings_count": 0,
            "executed_steps": 0,
        }
    )
    total_findings = summary["findings_count"]
    total_steps = summary["executed_steps"]
    completed_cycles = len(all_cycle_results)

    console.print()
    console.print(
        Panel(
            f"{'Interrupted by user' if interrupted else 'Testing completed'}\n\n"
            f"  Completed cycles: [bold]{completed_cycles}[/]\n"
            f"  Steps executed: [bold]{total_steps}[/]\n"
            f"  Findings: [bold]{total_findings}[/]",
            title="Persistent Pentest Summary",
            border_style="red" if total_findings > 0 else "green",
        )
    )

    if auto_report and all_cycle_results:
        console.print("\n[bold]Cycle Reports[/]:")
        for cr in all_cycle_results:
            if cr.report_path and "failed" not in str(cr.report_path).lower():
                console.print(f"  Cycle {cr.cycle_num}: {cr.report_path}")


@app.command()
def recon(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    # [Added] 2026-06-10 Nyaecho - TUINatural language driven: Allowpass --prompt incomingCustomHintWord coverage automatically generatedprompt
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restrict testing to a single path"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Explicitly blocked path"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
) -> None:
    """Run reconnaissance only."""
    task_prompt = prompt if prompt else f"Perform authorized reconnaissance against {target} without exploitation."
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("recon", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            # TerminalStreamSink Already shown in real-time streaming without duplication console.print
            return await agent.chat(task_prompt, target=target, stream_sink=sink)

        await _run_cli_orchestrated_task(
            command="recon",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )

    asyncio.run(_run())


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    ports: Optional[str] = typer.Option(None, help="Port range, e.g. 80,443,8080"),
    # [Added] 2026-06-10 Nyaecho - TUINatural language driven: Allowpass --prompt incomingCustomHintWord coverage automatically generatedprompt
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restrict testing to a single path"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Explicitly blocked path"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
) -> None:
    """Run vulnerability scanning only."""
    port_hint = f", focusing on ports {ports}" if ports else ""
    task_prompt = prompt if prompt else f"Perform authorized vulnerability scanning against {target}{port_hint} without exploitation."
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("scan", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            # TerminalStreamSink Already shown in real-time streaming without duplication console.print
            return await agent.chat(task_prompt, target=target, stream_sink=sink)

        await _run_cli_orchestrated_task(
            command="scan",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )

    asyncio.run(_run())


@app.command()
def exploit(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    cve: Optional[str] = typer.Option(None, help="Specific CVE to exploit"),
    cmd: str = typer.Option("id", help="Command to execute for verification"),
    # [Added] 2026-06-10 Nyaecho - TUINatural language driven: Allowpass --prompt incomingCustomHintWord coverage automatically generatedprompt
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restrict testing to a single path"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Explicitly blocked path"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
) -> None:
    """Run exploitation only."""
    cve_hint = f" using {cve}" if cve else ""
    task_prompt = prompt if prompt else (
        f"Attempt authorized exploitation against {target}{cve_hint} and verify with command: {cmd}"
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("exploit", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            # TerminalStreamSink Already shown in real-time streaming without duplication console.print
            return await agent.chat(task_prompt, target=target, stream_sink=sink)

        await _run_cli_orchestrated_task(
            command="exploit",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )

    asyncio.run(_run())


@app.command()
def report(
    session: str = typer.Argument(
        ..., help="Path to session JSON file or target when used with --target"
    ),
    target_mode: bool = typer.Option(
        False, "--target", help="Interpret argument as target and generate report from target state"
    ),
) -> None:
    """Generate a report from a session file or target state."""
    if target_mode:
        from bughunter.report.generator import generate_report_from_target_state

        state = load_target_state(session)
        if not state:
            err_console.print(f"[!] Target state not found: {session}")
            raise typer.Exit(1)
        generate_report_from_target_state(state)
    else:
        from bughunter.report.generator import generate_report_from_file

        generate_report_from_file(session)
    console.print("[+] Report generated")


# Lithium€Lithium€ Config sub-command group Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€

config_app = typer.Typer(help="Manage configuration")
app.add_typer(config_app, name="config")


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key in dot notation, e.g. llm.api_key"),
    value: str = typer.Argument(..., help="Config value"),
) -> None:
    """Set a config value."""
    set_config_value(key, value)
    console.print(
        f"[+] Set {key} = {'***' if 'key' in key.lower() or 'pass' in key.lower() else value}"
    )


@config_app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Config key in dot notation"),
) -> None:
    """Get a config value."""
    config = load_config()
    parts = key.split(".")
    obj = config
    for part in parts:
        obj = getattr(obj, part)
    value = obj if not hasattr(obj, "model_dump") else obj.model_dump()
    if isinstance(value, str) and ("key" in key.lower() or "pass" in key.lower()):
        value = value[:8] + "..." if len(value) > 8 else "***"
    console.print(f"{key} = {value}")


@config_app.command("list")
def config_list() -> None:
    """List all configuration values."""
    import yaml as _yaml

    config = load_config()
    raw = config.model_dump(mode="json")
    console.print(_yaml.dump(raw, default_flow_style=False, allow_unicode=True))


@config_app.command("provider")
def config_provider(
    name: Optional[str] = typer.Argument(
        None, help="Provider name to switch to (e.g. minimax, deepseek)"
    ),
    list_all: bool = typer.Option(False, "--list", "-l", help="List all available providers"),
) -> None:
    """View or switch the configured LLM provider."""
    if list_all or name is None:
        providers = list_providers()
        current_config = load_config()
        current_provider = current_config.llm.provider

        console.print("[bold]Available LLM Providers[/]")
        console.print()
        for p in providers:
            is_current = p["provider"] == current_provider
            marker = " [green](current)[/]" if is_current else ""
            console.print(f"  [bold cyan]{p['provider']}[/]{marker}")
            console.print(f"    Label: {p['label']}")
            console.print(f"    URL:  [dim]{p['base_url']}[/]")
            console.print(f"    Model: [dim]{p['default_model']}[/]")
            console.print()

        # Show active fallback providers
        if current_config.llm.fallback_providers:
            console.print("[bold]Active Fallback Providers[/]")
            console.print()
            for fb in current_config.llm.fallback_providers:
                key_count = 1 + len(fb.api_keys)
                model_label = fb.model or current_config.llm.model
                console.print(f"  [bold blue]{fb.name}[/] (priority {fb.priority})")
                console.print(f"    URL:   [dim]{fb.base_url}[/]")
                console.print(f"    Model: [dim]{model_label}[/]")
                console.print(f"    Keys:  {key_count} configured")
                console.print()

        console.print("[dim]Use bughunter config provider <name> to switch providers.[/]")
        return

    # Switch provider
    from bughunter.config.schema import PROVIDER_PRESETS, LLMProvider

    # Validate provider name
    try:
        provider_enum = LLMProvider(name.lower())
    except ValueError:
        console.print(f"[!] Unknown provider: [bold]{name}[/]")
        console.print(f"    Available: {', '.join(p.value for p in LLMProvider)}")
        console.print("    Tip: use [bold]custom[/] for a manual base_url and model.")
        raise typer.Exit(1)

    config = load_config()
    config = apply_provider_preset(config, name.lower())
    save_config(config)

    preset = PROVIDER_PRESETS.get(provider_enum, {})
    label = preset.get("label", name)
    console.print(f"[+] Switched LLM provider to [bold cyan]{label}[/]")
    console.print(f"    Base URL: [dim]{config.llm.base_url}[/]")
    console.print(f"    Model:    [dim]{config.llm.model}[/]")

    if not config.llm.api_key:
        console.print()
        console.print(
            "[yellow]Set an API key first: [bold]bughunter config set llm.api_key <your-key>[/][/]"
        )


# Lithium€Lithium€ Init command Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€


@app.command()
def init() -> None:
    """Initialize Bug Hunter config."""
    from bughunter.config.settings import ensure_dirs

    ensure_dirs()

    config = load_config()
    save_config(config)
    console.print(_("cli.init.config_created"))
    console.print(_("cli.init.dirs_initialized"))
    console.print(_("cli.init.dir_sessions"))
    console.print(_("cli.init.dir_kb"))
    console.print(_("cli.init.dir_skills"))
    console.print()
    console.print(_("cli.init.next_steps"))
    console.print(_("cli.init.step_provider"))
    console.print(_("cli.init.step_api_key"))
    console.print(_("cli.init.step_cli"))
    console.print(_("cli.init.step_tui"))


# Lithium€Lithium€ Doctor command Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€


@app.command()
def doctor() -> None:
    """Inspect the Bug Hunter runtime environment."""
    import shutil

    from bughunter.web.services.mcp_service import get_mcp_diagnostics

    console.print("[bold]Bug Hunter Environment Check[/]")
    console.print()

    # Check Python
    console.print(f"  Python: [green]{sys.version.split()[0]}[/]")

    # Check Node.js
    node_path = shutil.which("node")
    if node_path:
        import subprocess

        try:
            result = subprocess.run(
                [node_path, "--version"], capture_output=True, text=True, timeout=5
            )
            console.print(f"  Node.js: [green]{result.stdout.strip()}[/]")
        except Exception:
            console.print("  Node.js: [yellow]check failed[/]")
    else:
        console.print("  Node.js: [red]not installed[/] (required for some MCP services)")

    # Check npx
    npx_path = shutil.which("npx")
    console.print(
        f"  npx: [{'green' if npx_path else 'red'}]{'installed' if npx_path else 'missing'}[/]"
    )

    # Check uvx
    uvx_path = shutil.which("uvx")
    console.print(
        f"  uvx: [{'green' if uvx_path else 'yellow'}]{'installed' if uvx_path else 'missing'}[/]"
    )

    # Check nmap
    nmap_path = shutil.which("nmap")
    console.print(
        f"  nmap: [{'green' if nmap_path else 'yellow'}]{'installed' if nmap_path else 'optional/missing'}[/]"
    )

    # Check config
    config = load_config()
    console.print()
    console.print("[bold]LLM Config[/]:")
    has_key = bool(config.llm.api_key)
    console.print(f"  Provider: [bold cyan]{config.llm.provider}[/]")
    console.print(
        f"  API Key: [{'green' if has_key else 'red'}]{'configured' if has_key else 'not set'}[/]"
    )
    console.print(f"  Base URL: [dim]{config.llm.base_url}[/]")
    console.print(f"  Model: [dim]{config.llm.model}[/]")

    # Check MCP servers
    console.print()
    console.print("[bold]MCP Services[/]:")
    mcp_diag = get_mcp_diagnostics()
    console.print(f"  Registered: [bold]{mcp_diag.total_services}[/] services")
    console.print(f"  Tools: [bold]{mcp_diag.tool_count}[/] exposed")

    for item in mcp_diag.services:
        status = "[green]enabled[/]" if item.enabled else "[dim]disabled[/]"
        priority_label = {0: "P0", 1: "P1", 2: "P2"}.get(item.priority, "??")
        running = "[green]running[/]" if item.running else "[yellow]registered[/]"
        capability = "[green]exec[/]" if item.can_execute else "[yellow]schema-only[/]"
        console.print(
            f"  {item.name}: {status} [{priority_label}] {running} mode={item.execution_mode} {capability} tools={item.tool_count}"
        )
        if item.error:
            label = item.last_error_type or "error"
            console.print(f"    [red]{label}[/]: {item.error}")

    console.print(
        "[dim]doctor shows MCP registration state and exposed tools. fetch/memory run in local mode; most other services are still placeholders.[/]"
    )
    console.print(
        "[yellow]python_execute is a high-risk experimental capability. It is not a strong sandbox; use it only in authorized or controlled environments.[/]"
    )
    console.print(
        "[dim]The knowledge-base update flow is live; retrieval enhancements can continue independently.[/]"
    )

    console.print()
    if has_key:
        console.print("[green]Environment ready. Run [bold]bughunter[/] to start.[/]")
    else:
        console.print(
            "[yellow]Set an API key first: [bold]bughunter config set llm.api_key <key>[/][/]"
        )


# Lithium€Lithium€ KB command Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€

kb_app = typer.Typer(help="Security knowledge base commands")
app.add_typer(kb_app, name="kb")

target_state_app = typer.Typer(help="Manage target history state")
app.add_typer(target_state_app, name="target-state")

plugins_app = typer.Typer(help="Inspect and run vulnerability detection plugins")
app.add_typer(plugins_app, name="plugins")


def _parse_kv_options(pairs: Optional[list[str]]) -> dict[str, object]:
    """Bundle --option key=value(repeatable) resolves to dict,value Priority press JSON parse."""
    import json as _json

    options: dict[str, object] = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise typer.BadParameter(f"Expected key=value, got: {pair}")
        key, _, raw = pair.partition("=")
        key = key.strip()
        raw = raw.strip()
        try:
            options[key] = _json.loads(raw)
        except (ValueError, TypeError):
            options[key] = raw
    return options


@plugins_app.command("list")
def plugins_list(
    stage: Optional[str] = typer.Option(None, "--stage", help="Filter by stage"),
    tag: Optional[str] = typer.Option(None, "--tag", help="Filter by tag"),
) -> None:
    """List registered detection plugins."""
    from rich.table import Table

    from bughunter.plugins import registry

    plugin_classes = registry.list()
    if stage:
        try:
            plugin_classes = registry.by_stage(stage)
        except ValueError:
            err_console.print(f"[!] Unknown stage: {stage}")
            raise typer.Exit(1) from None
    if tag:
        tag_set = {p.plugin_id for p in registry.by_tag(tag)}
        plugin_classes = [p for p in plugin_classes if p.plugin_id in tag_set]

    if not plugin_classes:
        console.print("[yellow]No plugins match the filter.[/yellow]")
        return

    table = Table(title="Bug Hunter Plugins", show_lines=False)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Stages")
    table.add_column("Risk")
    table.add_column("Destructive", justify="center")
    for plugin_cls in sorted(plugin_classes, key=lambda p: p.plugin_id):
        meta = plugin_cls.metadata()
        table.add_row(
            meta["plugin_id"],
            meta["name"],
            ", ".join(meta["stages"]),
            meta["default_risk"],
            "⚠️" if meta["destructive"] else "-",
        )
    console.print(table)


@plugins_app.command("info")
def plugins_info(plugin_id: str = typer.Argument(..., help="Plugin id")) -> None:
    """Show full metadata for a single plugin."""
    import json as _json

    from bughunter.plugins import registry

    plugin_cls = registry.get(plugin_id)
    if plugin_cls is None:
        err_console.print(f"[!] Plugin not found: {plugin_id}")
        raise typer.Exit(1)
    console.print_json(_json.dumps(plugin_cls.metadata(), ensure_ascii=False))


@plugins_app.command("run")
def plugins_run(
    plugin_id: str = typer.Argument(..., help="Plugin id to run"),
    target: str = typer.Option("", "--target", help="Target host/IP/URL"),
    stage: str = typer.Option("discovery", "--stage", help="Plugin stage"),
    option: Optional[list[str]] = typer.Option(
        None, "--option", "-o", help="Plugin option key=value (repeatable, value parsed as JSON)"
    ),
    input_file: Optional[str] = typer.Option(
        None, "--input", help="JSON file merged into plugin options"
    ),
    allow_destructive: bool = typer.Option(
        False, "--allow-destructive", help="Permit destructive plugins"
    ),
    session_file: Optional[str] = typer.Option(
        None, "--session", help="Merge findings into this SessionState JSON and save it"
    ),
    as_json: bool = typer.Option(False, "--json", help="Print the raw PluginResult as JSON"),
) -> None:
    """Run a plugin against supplied data (builtin plugins only analyze provided input)."""
    import json as _json
    from pathlib import Path

    from rich.table import Table

    from bughunter.plugins import PluginContext, PluginStage, create_builtin_runtime
    from bughunter.plugins.integration import merge_plugin_results_into_session

    try:
        stage_value = PluginStage(stage)
    except ValueError:
        err_console.print(f"[!] Unknown stage: {stage}")
        raise typer.Exit(1) from None

    options = _parse_kv_options(option)
    if input_file:
        path = Path(input_file)
        if not path.exists():
            err_console.print(f"[!] Input file not found: {input_file}")
            raise typer.Exit(1)
        try:
            payload = _json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            err_console.print(f"[!] Failed to read input file: {exc}")
            raise typer.Exit(1) from None
        if isinstance(payload, dict):
            options.update(payload)
        else:
            options["input"] = payload

    config = load_config()
    runtime = create_builtin_runtime(config)
    context = PluginContext(
        target=target,
        stage=stage_value,
        options=options,
        allow_destructive=allow_destructive,
    )

    result = asyncio.run(runtime.execute(plugin_id, context))

    if as_json:
        console.print_json(result.model_dump_json())
    else:
        if result.skipped:
            console.print(f"[yellow]⊘ Skipped[/yellow] ({result.error_type}): {result.error}")
        elif result.error:
            console.print(f"[red]✗ Error[/red] ({result.error_type}): {result.error}")
        for message in result.messages:
            console.print(f"  [dim]{message}[/dim]")
        if result.findings:
            table = Table(title=f"{plugin_id} findings", show_lines=True)
            table.add_column("Risk", style="magenta", no_wrap=True)
            table.add_column("Title")
            table.add_column("Type")
            table.add_column("Confidence", justify="right")
            for finding in result.findings:
                table.add_row(
                    finding.risk.value,
                    finding.title,
                    finding.vuln_type or "-",
                    f"{finding.confidence:.2f}",
                )
            console.print(table)
        elif not result.error:
            console.print("[green]✓[/green] Plugin ran; no findings.")

    if session_file:
        session_path = Path(session_file)
        from bughunter.agent.context import SessionState

        session = SessionState.load(session_path) if session_path.exists() else SessionState()
        added = merge_plugin_results_into_session(session, result)
        session.save(session_path)
        console.print(f"[+] Merged {added} finding(s) into {session_file}")


@kb_app.command("update")
def kb_update() -> None:
    """Update the knowledge base."""
    console.print("[*] Updating knowledge base...")
    from bughunter.kb.store import KnowledgeStore
    from bughunter.kb.updater import seed_knowledge_base

    store = KnowledgeStore()
    before_stats = store.get_stats()
    seed_knowledge_base(store)
    after_stats = store.get_stats()

    before_total = sum(before_stats.values())
    after_total = sum(after_stats.values())
    delta = after_total - before_total
    category_summary = ", ".join(f"{cat}={count}" for cat, count in sorted(after_stats.items()))

    console.print(f"[+] Knowledge base updated: +{delta} entries")
    console.print(f"    Categories: {category_summary or 'empty'}")


@kb_app.command("status")
def kb_status() -> None:
    """Show the knowledge base retrieval backend status."""
    from bughunter.kb.retriever import KnowledgeRetriever, RetrieverStatus
    from bughunter.kb.store import KnowledgeStore

    store = KnowledgeStore()
    retriever = KnowledgeRetriever(store=store)
    status = retriever.get_status()
    detail = retriever.get_status_detail()
    stats = store.get_stats()
    total = sum(stats.values())
    category_summary = ", ".join(f"{cat}={count}" for cat, count in sorted(stats.items()))

    if status == RetrieverStatus.CHROMADB_ACTIVE:
        line = "[green]✓ Knowledge base active (ChromaDB semantic retrieval)[/green]"
    elif status == RetrieverStatus.KEYWORD_FALLBACK:
        line = "[yellow]⚠ Knowledge base degraded to keyword mode (chromadb not installed)[/yellow]"
    else:
        line = "[red]✗ Knowledge base disabled (no data available)[/red]"

    console.print(
        Panel(
            f"{line}\n"
            f"Backend: [bold]{status.value}[/]\n"
            f"Detail: {detail or 'n/a'}\n"
            f"Entries: [bold]{total}[/] ({category_summary or 'empty'})\n"
            f"Semantic search: run [bold]pip install bughunter\\[kb][/] to enable ChromaDB",
            title="KB Status",
            border_style="cyan",
        )
    )


@target_state_app.command("list")
def target_state_list(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
) -> None:
    """List target snapshots."""
    snapshots = list_target_snapshots(target)
    if not snapshots:
        console.print(f"[-] No snapshots found for: {target}")
        raise typer.Exit(1)

    console.print(f"[bold]Target snapshots[/]: {target}")
    for item in snapshots[:20]:
        console.print(
            f"  {item['snapshot_id']} | v{item.get('schema_version', 1)} | {item['last_command']} | "
            f"steps={item['executed_steps']} verified={item['verified_findings']} pending={item['pending_findings']}"
        )


@target_state_app.command("preview")
def target_state_preview_cmd(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    snapshot_id: Optional[str] = typer.Option(
        None, "--snapshot", help="Preview a specific snapshot id"
    ),
) -> None:
    """Show a resume preview for the target state."""
    preview = get_target_state_preview(target, snapshot_id=snapshot_id)
    if not preview:
        console.print(f"[-] No target state found: {target}")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"Target: [bold]{preview['target']}[/]\n"
            f"Schema: [bold]v{preview['schema_version']}[/]\n"
            f"Phase: [bold]{preview['phase'] or 'unknown'}[/]\n"
            f"Resume strategy: [bold]{preview['resume_strategy'] or 'none'}[/]\n"
            f"Reason: {preview['resume_reason'] or 'n/a'}\n"
            f"Findings: {preview['verified_count']} verified / {preview['pending_count']} pending / {preview['findings_count']} total",
            title="Target Preview",
            border_style="cyan",
        )
    )

    if preview.get("priority_targets"):
        console.print("[bold]Priority targets[/]:")
        for item in preview["priority_targets"][:5]:
            console.print(f"  - {item}")
    if preview.get("priority_recon_assets"):
        console.print("[bold]Priority recon assets[/]:")
        for item in preview["priority_recon_assets"][:5]:
            console.print(f"  - {item}")
    if preview.get("next_actions"):
        console.print("[bold]Next actions[/]:")
        for item in preview["next_actions"][:5]:
            console.print(f"  - {item}")


@target_state_app.command("diff")
def target_state_diff_cmd(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    from_snapshot_id: str = typer.Argument(..., help="Base snapshot id"),
    to_snapshot_id: Optional[str] = typer.Option(
        None, "--to", help="Compare against another snapshot or current state"
    ),
) -> None:
    """Show differences between two target-state snapshots."""
    diff = diff_target_state_snapshots(target, from_snapshot_id, to_snapshot_id=to_snapshot_id)
    if not diff:
        console.print(f"[-] Unable to diff target state: {target}")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"Target: [bold]{diff['target']}[/]\n"
            f"From: [bold]{diff['from_snapshot_id']}[/] -> To: [bold]{diff['to_snapshot_id']}[/]\n"
            f"Schema: v{diff['schema_version_from']} -> v{diff['schema_version_to']}\n"
            f"Resume strategy: {diff['resume_strategy_from'] or 'none'} -> {diff['resume_strategy_to'] or 'none'}",
            title="Target Diff",
            border_style="magenta",
        )
    )

    for title, items in (
        ("Added findings", diff.get("added_findings", [])),
        ("Removed findings", diff.get("removed_findings", [])),
        ("Updated findings", diff.get("updated_findings", [])),
        ("Added recon assets", diff.get("added_recon_assets", [])),
        ("Removed recon assets", diff.get("removed_recon_assets", [])),
        ("Added steps", diff.get("added_steps", [])),
        ("Removed steps", diff.get("removed_steps", [])),
        ("Added notes", diff.get("added_notes", [])),
        ("Removed notes", diff.get("removed_notes", [])),
    ):
        if items:
            console.print(f"[bold]{title}[/]:")
            for item in items[:10]:
                console.print(f"  - {item}")


@target_state_app.command("rollback")
def target_state_rollback_cmd(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    snapshot_id: str = typer.Argument(..., help="Snapshot id to restore"),
) -> None:
    """Rollback target state to a snapshot."""
    path = rollback_target_state(target, snapshot_id)
    if not path:
        console.print(f"[-] Snapshot not found: {snapshot_id}")
        raise typer.Exit(1)
    console.print(f"[+] Rolled back target state: {target}")
    console.print(f"    Snapshot: {snapshot_id}")


@target_state_app.command("clear")
def target_state_clear_cmd(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
) -> None:
    """Clear target state."""
    ok = clear_target_state(target)
    if not ok:
        console.print(f"[-] No target state found: {target}")
        raise typer.Exit(1)
    console.print(f"[+] Cleared target state: {target}")


# Default command (no sub-command -> REPL)

# Lithium€Lithium€ Auto-pentest detection Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€Lithium€


def _should_auto_pentest(user_input: str, current_target: Optional[str]) -> bool:
    """Determine if user input should trigger autonomous pentest loop.

    Triggers when:
    - User explicitly asks for a full pentest with a target
    - User mentions a target plus action keywords like "Penetration Testing" or "hit"
    - User asks to solve a CTF / find a flag with a target
    - User asks for information gathering / recon / OSINT with a target
    - A target is present + multi-step intent indicators
    """
    input_lower = user_input.lower()

    # Explicit auto-mode triggers
    auto_keywords = [
        "Penetration Testing",
        "conductPentest",
        "DoPentest",
        "hit",
        "Comprehensive testing",
        "pentest",
        "full test",
        "auto",
        "Autonomous Pentest Mode",
        "autonomous mode",
        "find the flag",
        "turn upflag",
        "takeflag",
        "get flag",
        "find flag",
        "solve challenge",
        "Do the questions",
        "challenge",
        "challenge",
        "ctf",
        "weak password",
        "blasting",
        "bypass",
        "bypass",
        "brute",
        "gather",
        "collect",
        "Reconnaissance",
        "reconnaissance",
        "recon",
        "reconnaissance",
        "social eng",
        "osint",
        "intelligence",
        "intelligence",
        "AnalysisTarget",
        "TargetAnalysis",
        "asset discovery",
        "directory scan",
        "detection",
        "Explore",
        "investigate",
        "investigate",
        "enumerate",
        "comprehensiveAnalysis",
        "depthAnalysis",
        "detailedAnalysis",
        "full scan",
        "subdomain",
        "subdomain",
    ]

    # Single-step queries should NOT trigger auto mode
    single_step_keywords = [
        "Generate report",
        "report",
        "help",
        "Help",
    ]

    # If it's clearly a single-step query, don't auto-loop
    # But if it also has auto keywords, still go auto (e.g. "collectInfoandGenerate report")
    if any(kw in input_lower for kw in single_step_keywords) and not any(
        kw in input_lower for kw in auto_keywords
    ):
        return False

    # If it has auto-mode keywords, trigger auto loop
    if any(kw in input_lower for kw in auto_keywords):
        # Must have a target (either in input or already set)
        has_target = bool(current_target) or bool(_extract_target_from_input(user_input))
        return has_target

    # Fallback: has target + multi-step intent -> auto
    has_target = bool(current_target) or bool(_extract_target_from_input(user_input))
    if has_target:
        multi_step_indicators = [
            "and",
            "Then",
            "Output",
            "Save",
            "write to",
            "Export",
            "all",
            "all",
            "whole",
            "detailed",
        ]
        if any(ind in input_lower for ind in multi_step_indicators):
            return True

    return False


def _extract_target_from_input(user_input: str) -> Optional[str]:
    """Extract target from user input string."""
    import re

    # Try to find URL (with optional port)
    url_match = re.search(r"(https?://[a-zA-Z0-9][-a-zA-Z0-9.:]*)", user_input)
    if url_match:
        return url_match.group(1).rstrip("/")
    # Try to find IP address
    ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", user_input)
    if ip_match:
        return ip_match.group(1)
    # Try to find domain
    domain_match = re.search(r"([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)", user_input)
    if domain_match:
        return domain_match.group(1)
    return None


def _extract_time_budget(user_input: str) -> int:
    """Extract a time budget from natural language input.

    Matches patterns like:
      - "pentest target.com in 30 minutes"
      - "scan 10.10.10.1 in 15 min"
      - "hack example.com in 1 hour"
      - "budget 20"
      - "in 45m"

    Returns minutes as int, or 0 if no budget found.
    """
    import re

    text = user_input.lower().strip()

    # Direct budget command: "budget 30"
    budget_match = re.search(r'\bbudget\s+(\d+)', text)
    if budget_match:
        return int(budget_match.group(1))

    # "in X minutes/min/m"
    min_match = re.search(r'\bin\s+(\d+)\s*(?:minutes?|mins?|m)\b', text)
    if min_match:
        return int(min_match.group(1))

    # "in X hours/hr/h"
    hr_match = re.search(r'\bin\s+(\d+)\s*(?:hours?|hrs?|h)\b', text)
    if hr_match:
        return int(hr_match.group(1)) * 60

    # "within X minutes"
    within_match = re.search(r'\bwithin\s+(\d+)\s*(?:minutes?|mins?|m)\b', text)
    if within_match:
        return int(within_match.group(1))

    return 0


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Open the classic CLI/REPL by default."""
    if ctx.invoked_subcommand is None:
        _run_repl()


def _auto_save_recon_report(agent, user_input: str, config) -> None:
    """Auto-save a recon report after auto_pentest completes when user requested file output."""
    import re
    from datetime import datetime

    try:
        state = agent.session_state
        target = state.target or "unknown"

        # Determine output path
        # Check if user specified a path
        path_match = re.search(
            r"(?:Savearrive|write to|Outputarrive|Exportarrive|save to|write to|output to|export to)\s*([^\s,,]+)",
            user_input,
            re.IGNORECASE,
        )
        if path_match:
            output_path = path_match.group(1)
        else:
            safe_name = re.sub(r"[^\w]", "_", target)[:30]
            date_str = datetime.now().strftime("%Y%m%d_%H%M")
            output_path = str(config.session.output_dir / f"{safe_name}_recon_{date_str}.md")

        from bughunter.report.generator import generate_report

        generate_report(
            state,
            output_path,
            report_format=config.session.report_format,
        )

        console.print(f"\n[+] Recon report saved: {output_path}")

    except Exception as e:
        console.print(f"\n[!] Failed to auto-save report: {e}")


@app.command()
def repl() -> None:
    """Start the classic natural-language REPL."""
    _run_repl()


@app.command()
def tui(
    target: Optional[str] = typer.Option(
        None,
        "--target",
        "-t",
        help="Pre-fill the authorized target for the TUI.",
    ),
    mode: str = typer.Option(
        "standard",
        "--mode",
        "-m",
        help="Pre-fill check mode: quick, standard, deep, continuous.",
    ),
    only_port: Optional[int] = typer.Option(
        None,
        "--only-port",
        help="Pre-fill a single allowed test port.",
    ),
    only_host: Optional[str] = typer.Option(
        None,
        "--only-host",
        help="Pre-fill a single allowed host.",
    ),
    only_path: Optional[str] = typer.Option(
        None,
        "--only-path",
        help="Pre-fill a single allowed path.",
    ),
    blocked_host: Optional[str] = typer.Option(
        None,
        "--blocked-host",
        help="Pre-fill an explicitly blocked host.",
    ),
    blocked_path: Optional[str] = typer.Option(
        None,
        "--blocked-path",
        help="Pre-fill an explicitly blocked path.",
    ),
    allow_actions: Optional[str] = typer.Option(
        None,
        "--allow-actions",
        help="Pre-fill comma-separated allowed actions.",
    ),
    block_actions: Optional[str] = typer.Option(
        None,
        "--block-actions",
        help="Pre-fill comma-separated blocked actions.",
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume target history."),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Render the launch summary and exit without starting a task.",
    ),
    once: bool = typer.Option(
        False,
        "--once",
        help="Render the TUI dashboard once and exit (useful for smoke tests).",
    ),
) -> None:
    """Open the terminal UI workbench."""
    from bughunter.cli.tui import (
        MODES,
        build_state_from_options,
        build_task_draft,
        render_task_summary,
        run_tui,
    )

    if mode not in MODES:
        err_console.print("[!] Unknown TUI mode. Use one of: quick, standard, deep, continuous")
        raise typer.Exit(1)

    state = build_state_from_options(
        target=target or "",
        mode=mode,  # type: ignore[arg-type]
        only_host=only_host or "",
        only_port=only_port,
        only_path=only_path or "",
        blocked_host=blocked_host or "",
        blocked_path=blocked_path or "",
        allow_actions=allow_actions,
        block_actions=block_actions,
        resume=resume,
    )

    if dry_run:
        console.out(render_task_summary(build_task_draft(state)), end="")
        return

    if once and target:
        from bughunter.cli.tui import render_tui_home

        console.out(render_tui_home(state), end="")
        return

    run_tui(once=once, initial_state=state)


@app.command()
def web(
    host: str = typer.Option(
        "127.0.0.1", "--host", help="Web server host (default: localhost only)"
    ),
    port: int = typer.Option(7788, "--port", help="Web server port"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Validate and print launch info without starting the server"
    ),
    allow_remote: bool = typer.Option(
        False, "--allow-remote", help="Explicitly allow binding the Web UI to a non-local address"
    ),
) -> None:
    """Run the local Web UI."""
    if host != "127.0.0.1":
        if not allow_remote:
            err_console.print(
                "[!] Refusing to bind the Web UI to a non-local address without --allow-remote."
            )
            raise typer.Exit(1)
        console.print(
            "[yellow]Warning: keep the Web UI bound to 127.0.0.1 unless you know what you're doing.[/]"
        )

    from bughunter.web.app import FASTAPI_AVAILABLE

    console.print(
        Panel(
            f"Host: [bold]{host}[/]\n"
            f"Port: [bold]{port}[/]\n"
            f"FastAPI: [{'green' if FASTAPI_AVAILABLE else 'yellow'}]{'installed' if FASTAPI_AVAILABLE else 'missing'}[/]\n"
            f"URL: [bold]http://{host}:{port}[/]",
            title="Bug Hunter Web UI",
            border_style="cyan",
        )
    )

    if dry_run:
        console.print("[green]Web UI dry-run completed.[/]")
        return

    if not FASTAPI_AVAILABLE:
        err_console.print(
            "[!] FastAPI is missing. Install with [bold]pip install bughunter[web][/]."
        )
        raise typer.Exit(1)

    try:
        import uvicorn
    except ImportError:
        err_console.print(
            "[!] uvicorn is missing. Install with [bold]pip install bughunter[web][/]."
        )
        raise typer.Exit(1)

    from bughunter.web.app import create_app

    uvicorn.run(create_app(), host=host, port=port, log_level="info")


if __name__ == "__main__":
    app()
