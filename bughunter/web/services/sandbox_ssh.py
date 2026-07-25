"""SSH client wrapper for sandbox command execution.

Provides single-shot SSH command execution and readiness checks
using paramiko, isolated from the Docker lifecycle management.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class CommandResult:
    """Result of a command executed via SSH."""

    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    duration_ms: int = 0
    truncated: bool = False


# Maximum output size before truncation (256 KB).
_MAX_OUTPUT_BYTES = 256 * 1024


def ssh_exec(
    host: str,
    port: int,
    user: str,
    password: str,
    command: str,
    timeout: int = 30,
) -> CommandResult:
    """Execute a single command over SSH and return the result.

    Parameters
    ----------
    host:
        SSH host address.
    port:
        SSH port.
    user:
        SSH username.
    password:
        SSH password.
    command:
        Shell command to execute.
    timeout:
        Maximum seconds to wait for the command to finish.

    Returns
    -------
    CommandResult with stdout, stderr, exit_code, and duration.
    """
    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    start = time.monotonic()
    try:
        client.connect(
            hostname=host,
            port=port,
            username=user,
            password=password,
            timeout=min(timeout, 10),
            look_for_keys=False,
            allow_agent=False,
        )

        _stdin, _stdout, _stderr = client.exec_command(command, timeout=timeout)

        raw_out = _stdout.read(_MAX_OUTPUT_BYTES)
        raw_err = _stderr.read(_MAX_OUTPUT_BYTES)
        exit_code = _stdout.channel.recv_exit_status()

        elapsed = int((time.monotonic() - start) * 1000)

        truncated = len(raw_out) >= _MAX_OUTPUT_BYTES or len(raw_err) >= _MAX_OUTPUT_BYTES

        return CommandResult(
            stdout=raw_out.decode("utf-8", errors="replace"),
            stderr=raw_err.decode("utf-8", errors="replace"),
            exit_code=exit_code,
            duration_ms=elapsed,
            truncated=truncated,
        )
    except paramiko.AuthenticationException:
        elapsed = int((time.monotonic() - start) * 1000)
        return CommandResult(
            stderr="SSH authentication failed",
            exit_code=-1,
            duration_ms=elapsed,
        )
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        return CommandResult(
            stderr=f"SSH error: {exc}",
            exit_code=-1,
            duration_ms=elapsed,
        )
    finally:
        client.close()


def ssh_check_ready(
    host: str,
    port: int,
    user: str,
    password: str,
    retries: int = 15,
    delay: float = 1.0,
) -> bool:
    """Poll until SSH is accepting connections.

    Returns True if a connection succeeds within the retry window.
    """
    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for attempt in range(retries):
        try:
            client.connect(
                hostname=host,
                port=port,
                username=user,
                password=password,
                timeout=3,
                look_for_keys=False,
                allow_agent=False,
            )
            client.close()
            return True
        except Exception:
            if attempt < retries - 1:
                time.sleep(delay)
    return False
