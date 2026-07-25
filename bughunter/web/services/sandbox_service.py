"""Sandbox lifecycle manager for Kali Linux Docker containers.

Manages ephemeral Kali containers via the Docker SDK, providing
start/stop/exec operations accessed through the Web UI API.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from uuid import uuid4

from bughunter.web.services.sandbox_ssh import CommandResult, ssh_check_ready, ssh_exec

logger = logging.getLogger(__name__)

# ── Container defaults ──────────────────────────────────────────────

_IMAGE_NAME = "bughunter-kali-sandbox:latest"
_CONTAINER_PREFIX = "bughunter-sandbox-"
_SSH_USER = "agentuser"
_SSH_PASSWORD = "bughunter_sandbox_2024"
_SSH_CONTAINER_PORT = 22
_MEM_LIMIT = "2g"
_CPU_PERIOD = 100_000
_CPU_QUOTA = 100_000  # 100 % of one core
_MAX_LIFETIME_SECONDS = 3600  # 1 hour


class SandboxSession:
    """In-memory representation of an active sandbox session."""

    def __init__(
        self,
        session_id: str,
        container_id: str = "",
        status: str = "starting",
        host: str = "127.0.0.1",
        ssh_port: int = 0,
        container_name: str = "",
    ) -> None:
        self.session_id = session_id
        self.container_id = container_id
        self.status = status
        self.host = host
        self.ssh_port = ssh_port
        self.container_name = container_name
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.last_activity: str | None = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "container_id": self.container_id,
            "status": self.status,
            "host": self.host,
            "ssh_port": self.ssh_port,
            "container_name": self.container_name,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
        }


class SandboxManager:
    """Manage Kali Linux sandbox Docker containers."""

    def __init__(self) -> None:
        self._sessions: dict[str, SandboxSession] = {}
        self._docker_client = None
        self._reaper_task: asyncio.Task | None = None

    # ── Docker client (lazy) ────────────────────────────────────────

    def _get_docker(self):
        """Lazily initialise the Docker client."""
        if self._docker_client is None:
            import docker

            self._docker_client = docker.from_env()
        return self._docker_client

    # ── Public API ──────────────────────────────────────────────────

    async def start_sandbox(self, session_id: str | None = None) -> SandboxSession:
        """Start a new Kali sandbox container.

        Returns the SandboxSession with connection details.
        If a container with the same name already exists, reuses it.
        """
        if session_id is None:
            session_id = f"sandbox_{uuid4().hex[:12]}"

        # Prevent duplicate sessions
        if session_id in self._sessions:
            existing = self._sessions[session_id]
            if existing.status == "running":
                return existing

        session = SandboxSession(session_id=session_id)
        self._sessions[session_id] = session

        try:
            client = self._get_docker()
            container_name = f"{_CONTAINER_PREFIX}{session_id}"
            container = None

            # Try to find an existing container with this name
            try:
                container = client.containers.get(container_name)
                container.reload()
                container_status = container.status  # "running", "exited", "created", etc.
                logger.info(
                    "Found existing container %s (status: %s)", container_name, container_status
                )
                if container_status == "exited" or container_status == "created":
                    # Restart the stopped container
                    container.start()
                    container.reload()
                elif container_status == "running":
                    pass  # Already running, reuse it
                else:
                    # Unknown state — remove and recreate
                    container.remove(force=True)
                    container = None
            except Exception:
                # Container doesn't exist — will create below
                container = None

            if container is None:
                # Create a new container
                import platform
                run_kwargs = dict(
                    detach=True,
                    name=container_name,
                    ports={f"{_SSH_CONTAINER_PORT}/tcp": None},  # random host port
                    mem_limit=_MEM_LIMIT,
                    cpu_period=_CPU_PERIOD,
                    cpu_quota=_CPU_QUOTA,
                    remove=False,
                    cap_add=["NET_ADMIN"],
                )
                # /dev/net/tun is only available on Linux hosts
                if platform.system() != "Windows":
                    run_kwargs["devices"] = ["/dev/net/tun:/dev/net/tun"]
                container = client.containers.run(_IMAGE_NAME, **run_kwargs)
                container.reload()

            # Get port mapping
            port_bindings = container.attrs["NetworkSettings"]["Ports"]
            host_port_info = port_bindings.get(f"{_SSH_CONTAINER_PORT}/tcp")

            if not host_port_info:
                raise RuntimeError("Container started but no SSH port mapping found")

            ssh_port = int(host_port_info[0]["HostPort"])

            session.container_id = container.short_id
            session.container_name = container_name
            session.ssh_port = ssh_port

            # Wait for SSH readiness in a thread to avoid blocking the event loop
            ready = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ssh_check_ready("127.0.0.1", ssh_port, _SSH_USER, _SSH_PASSWORD),
            )

            if ready:
                session.status = "running"
                logger.info(
                    "Sandbox %s started: container=%s, ssh_port=%d",
                    session_id,
                    container.short_id,
                    ssh_port,
                )
            else:
                session.status = "error"
                logger.error("Sandbox %s: SSH not ready after retries", session_id)

        except Exception as exc:
            session.status = "error"
            logger.exception("Failed to start sandbox %s: %s", session_id, exc)

        # Start the reaper if not running
        self._ensure_reaper()

        return session

    def stop_sandbox(self, session_id: str) -> bool:
        """Stop and remove a sandbox container."""
        session = self._sessions.get(session_id)
        if session is None:
            return False

        try:
            client = self._get_docker()
            try:
                container = client.containers.get(session.container_name)
                container.stop(timeout=5)
                container.remove(force=True)
            except Exception:
                # Container may already be gone
                pass

            session.status = "stopped"
            logger.info("Sandbox %s stopped", session_id)
        except Exception as exc:
            logger.exception("Error stopping sandbox %s: %s", session_id, exc)
            session.status = "error"

        return True

    async def execute_command(
        self, session_id: str, command: str, timeout: int = 30
    ) -> CommandResult | None:
        """Execute a command inside a sandbox via SSH."""
        session = self._sessions.get(session_id)
        if session is None or session.status != "running":
            return None

        # Run SSH exec in a thread to avoid blocking
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: ssh_exec(
                session.host,
                session.ssh_port,
                _SSH_USER,
                _SSH_PASSWORD,
                command,
                timeout=timeout,
            ),
        )

        session.last_activity = datetime.now(timezone.utc).isoformat()
        return result

    def get_status(self, session_id: str) -> SandboxSession | None:
        """Get the status of a sandbox session."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[SandboxSession]:
        """Return all tracked sessions."""
        return list(self._sessions.values())

    # ── Reaper ──────────────────────────────────────────────────────

    def _ensure_reaper(self) -> None:
        """Start the background reaper task if not already running."""
        if self._reaper_task is None or self._reaper_task.done():
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    self._reaper_task = loop.create_task(self._reap_loop())
            except RuntimeError:
                pass

    async def _reap_loop(self) -> None:
        """Periodically kill containers older than max lifetime."""
        while True:
            await asyncio.sleep(60)
            try:
                self._reap_expired()
            except Exception:
                logger.exception("Reaper error")

    def _reap_expired(self) -> None:
        """Kill containers that have exceeded their maximum lifetime."""
        now = datetime.now(timezone.utc)
        to_reap = []

        for session_id, session in self._sessions.items():
            if session.status != "running":
                continue
            try:
                created = datetime.fromisoformat(session.created_at)
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                age = (now - created).total_seconds()
                if age > _MAX_LIFETIME_SECONDS:
                    to_reap.append(session_id)
            except Exception:
                continue

        for session_id in to_reap:
            logger.info("Reaping expired sandbox: %s", session_id)
            self.stop_sandbox(session_id)

    # ── Cleanup on shutdown ─────────────────────────────────────────

    def stop_all(self) -> None:
        """Stop all running sandbox containers. Called on app shutdown."""
        for session_id in list(self._sessions.keys()):
            session = self._sessions[session_id]
            if session.status == "running":
                self.stop_sandbox(session_id)
