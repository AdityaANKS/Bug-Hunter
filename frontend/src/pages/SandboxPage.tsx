import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { execSandboxCommand, startSandbox, stopSandbox } from "../api/web";
import { useSandboxSessionsQuery } from "../hooks/queries";
import type { SandboxCommandResult, SandboxSession } from "../types/api";

interface TerminalEntry {
  id: number;
  type: "command" | "stdout" | "stderr" | "system" | "meta";
  text: string;
  exitCode?: number;
  durationMs?: number;
}

const QUICK_COMMANDS = [
  { label: "nmap version", cmd: "nmap -V" },
  { label: "System info", cmd: "uname -a" },
  { label: "Network info", cmd: "ip addr show" },
  { label: "Installed tools", cmd: "which nmap nikto sqlmap gobuster" },
  { label: "Disk usage", cmd: "df -h" },
  { label: "Process list", cmd: "ps aux" },
];

export function SandboxPage() {
  const queryClient = useQueryClient();
  const sessionsQuery = useSandboxSessionsQuery();
  const [activeSession, setActiveSession] = useState<SandboxSession | null>(null);
  const [commandInput, setCommandInput] = useState("");
  const [history, setHistory] = useState<TerminalEntry[]>([]);
  const [cmdHistory, setCmdHistory] = useState<string[]>([]);
  const [cmdHistoryIdx, setCmdHistoryIdx] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const outputRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  let entryId = useRef(0);

  // Auto-scroll terminal output
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [history]);

  // Focus input when session is active
  useEffect(() => {
    if (activeSession?.status === "running" && inputRef.current) {
      inputRef.current.focus();
    }
  }, [activeSession?.status]);

  // Sync session status from polling
  useEffect(() => {
    if (!sessionsQuery.data || !activeSession) return;
    const updated = sessionsQuery.data.find((s) => s.session_id === activeSession.session_id);
    if (updated && updated.status !== activeSession.status) {
      setActiveSession(updated);
    }
  }, [sessionsQuery.data, activeSession?.session_id]);

  const pushEntry = useCallback(
    (type: TerminalEntry["type"], text: string, meta?: Partial<TerminalEntry>) => {
      entryId.current += 1;
      setHistory((prev) => [...prev.slice(-499), { id: entryId.current, type, text, ...meta }]);
    },
    [],
  );

  async function handleStart() {
    setIsStarting(true);
    pushEntry("system", "⏳ Starting Kali Linux sandbox...");
    try {
      const session = await startSandbox();
      setActiveSession(session);
      void queryClient.invalidateQueries({ queryKey: ["sandbox-sessions"] });
      if (session.status === "running") {
        pushEntry("system", `✅ Sandbox ready — container ${session.container_id} on SSH port ${session.ssh_port}`);
        pushEntry("system", "Type commands below to execute them in the Kali Linux sandbox.");
      } else {
        pushEntry("system", `❌ Sandbox failed to start — status: ${session.status}`);
      }
    } catch (err) {
      pushEntry("system", `❌ Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsStarting(false);
    }
  }

  async function handleStop() {
    if (!activeSession) return;
    pushEntry("system", "⏳ Stopping sandbox...");
    try {
      await stopSandbox(activeSession.session_id);
      setActiveSession((prev) => (prev ? { ...prev, status: "stopped" } : null));
      void queryClient.invalidateQueries({ queryKey: ["sandbox-sessions"] });
      pushEntry("system", "🛑 Sandbox stopped and container removed.");
    } catch (err) {
      pushEntry("system", `❌ Error stopping: ${err instanceof Error ? err.message : String(err)}`);
    }
  }

  async function handleExec(cmd: string) {
    if (!activeSession || !cmd.trim()) return;
    const trimmed = cmd.trim();

    // Update command history
    setCmdHistory((prev) => [...prev.filter((c) => c !== trimmed), trimmed]);
    setCmdHistoryIdx(-1);
    setCommandInput("");

    pushEntry("command", `$ ${trimmed}`);
    setIsLoading(true);

    try {
      const result: SandboxCommandResult = await execSandboxCommand(
        activeSession.session_id,
        trimmed,
      );

      if (result.stdout) {
        pushEntry("stdout", result.stdout);
      }
      if (result.stderr) {
        pushEntry("stderr", result.stderr);
      }

      const exitLabel = result.exit_code === 0 ? "✓" : `✗ exit ${result.exit_code}`;
      pushEntry("meta", `${exitLabel}  (${result.duration_ms}ms)${result.truncated ? "  [output truncated]" : ""}`, {
        exitCode: result.exit_code,
        durationMs: result.duration_ms,
      });
    } catch (err) {
      pushEntry("stderr", `Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleExec(commandInput);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (cmdHistory.length === 0) return;
      const nextIdx = cmdHistoryIdx < cmdHistory.length - 1 ? cmdHistoryIdx + 1 : cmdHistoryIdx;
      setCmdHistoryIdx(nextIdx);
      setCommandInput(cmdHistory[cmdHistory.length - 1 - nextIdx] || "");
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (cmdHistoryIdx <= 0) {
        setCmdHistoryIdx(-1);
        setCommandInput("");
      } else {
        const nextIdx = cmdHistoryIdx - 1;
        setCmdHistoryIdx(nextIdx);
        setCommandInput(cmdHistory[cmdHistory.length - 1 - nextIdx] || "");
      }
    }
  }

  const isRunning = activeSession?.status === "running";

  return (
    <div className="sandbox-page">
      {/* Header */}
      <section className="sandbox-header">
        <div className="sandbox-header-left">
          <span className={`sandbox-status-dot ${isRunning ? "running" : activeSession ? "stopped" : ""}`} />
          <strong>Kali Linux Sandbox</strong>
          {activeSession && (
            <span className="sandbox-meta">
              {activeSession.container_id && <code>{activeSession.container_id}</code>}
              {isRunning && <span className="sandbox-port">SSH :{activeSession.ssh_port}</span>}
            </span>
          )}
        </div>
        <div className="sandbox-header-actions">
          {!isRunning ? (
            <button
              type="button"
              className="primary-btn"
              onClick={handleStart}
              disabled={isStarting}
            >
              {isStarting ? "Starting…" : "Start Sandbox"}
            </button>
          ) : (
            <button
              type="button"
              className="danger-btn"
              onClick={handleStop}
            >
              Stop Sandbox
            </button>
          )}
        </div>
      </section>

      {/* Quick commands */}
      {isRunning && (
        <section className="sandbox-toolbar">
          {QUICK_COMMANDS.map((qc) => (
            <button
              key={qc.cmd}
              type="button"
              className="sandbox-quick-btn"
              disabled={isLoading}
              onClick={() => void handleExec(qc.cmd)}
              title={qc.cmd}
            >
              {qc.label}
            </button>
          ))}
        </section>
      )}

      {/* Terminal output */}
      <div className="sandbox-terminal" ref={outputRef} onClick={() => inputRef.current?.focus()}>
        {history.length === 0 && !isRunning && (
          <div className="sandbox-placeholder">
            <p>🐉 <strong>Kali Linux Sandbox</strong></p>
            <p>Start a sandbox to get an isolated Kali Linux environment with pre-installed security tools.</p>
            <p>Available tools: <code>nmap</code>, <code>nikto</code>, <code>sqlmap</code>, <code>gobuster</code>, <code>whois</code>, <code>curl</code>, and more.</p>
          </div>
        )}
        {history.map((entry) => (
          <div key={entry.id} className={`sandbox-entry sandbox-entry-${entry.type}`}>
            <pre>{entry.text}</pre>
          </div>
        ))}
        {isLoading && (
          <div className="sandbox-entry sandbox-entry-system">
            <pre>⏳ Executing...</pre>
          </div>
        )}
      </div>

      {/* Command input */}
      <div className={`sandbox-input-bar ${!isRunning ? "disabled" : ""}`}>
        <span className="sandbox-prompt">$</span>
        <input
          ref={inputRef}
          type="text"
          className="sandbox-command-input"
          placeholder={isRunning ? "Type a command and press Enter…" : "Start a sandbox first…"}
          value={commandInput}
          onChange={(e) => setCommandInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={!isRunning || isLoading}
          autoComplete="off"
          spellCheck={false}
        />
        <button
          type="button"
          className="sandbox-send-btn"
          disabled={!isRunning || isLoading || !commandInput.trim()}
          onClick={() => void handleExec(commandInput)}
          title="Execute"
        >
          ▶
        </button>
      </div>
    </div>
  );
}
