"""Process isolation and resource controls for task-search runs."""

import json
import os
from pathlib import Path
import shutil
import subprocess


def _write_json(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def _resource_command(command, resource_limits):
    if not resource_limits.get("enabled"):
        return command
    return [
        resource_limits["executable"],
        "--user",
        "--scope",
        "--quiet",
        "--collect",
        "-p",
        f"MemoryMax={resource_limits['memory_max']}",
        "-p",
        f"TasksMax={resource_limits['tasks_max']}",
        "-p",
        f"CPUQuota={resource_limits['cpu_quota']}",
        "--",
        *command,
    ]


def _resolve_resource_limits(
    mode,
    *,
    systemd_run_bin="systemd-run",
    memory_max="8G",
    tasks_max=512,
    cpu_quota="400%",
):
    if mode == "none":
        return {"enabled": False, "mode": mode}
    executable = shutil.which(systemd_run_bin)
    true_executable = shutil.which("true")
    error = None
    if executable and true_executable:
        probe = subprocess.run(
            [
                executable,
                "--user",
                "--scope",
                "--quiet",
                "--collect",
                "-p",
                f"MemoryMax={memory_max}",
                "-p",
                f"TasksMax={tasks_max}",
                "-p",
                f"CPUQuota={cpu_quota}",
                "--",
                true_executable,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        if probe.returncode == 0:
            version = subprocess.check_output(
                [executable, "--version"], text=True
            ).splitlines()[0]
            return {
                "enabled": True,
                "mode": mode,
                "name": "systemd-run user scope",
                "version": version,
                "executable": executable,
                "memory_max": memory_max,
                "tasks_max": tasks_max,
                "cpu_quota": cpu_quota,
            }
        error = probe.stderr.strip() or f"exit code {probe.returncode}"
    elif not executable:
        error = f"command not found: {systemd_run_bin}"
    else:
        error = "command not found: true"
    if mode == "required":
        raise RuntimeError(f"resource limits unavailable: {error}")
    return {"enabled": False, "mode": mode, "reason": error}


def _public_resource_limits(resource_limits):
    fields = {
        "enabled",
        "mode",
        "name",
        "version",
        "memory_max",
        "tasks_max",
        "cpu_quota",
    }
    return {key: value for key, value in resource_limits.items() if key in fields}


# What a sandboxed process needs whatever it is doing: where to find programs, how to
# decode bytes, how the interpreter loads its own libraries, and how to reach the network
# through this site's TLS and proxy settings. Deliberately about the shape of a Unix
# process and not about any vendor -- a provider credential is passed in by name.
BASE_ENV_NAMES = (
    "PATH",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "TERM",
    "LD_LIBRARY_PATH",
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "REQUESTS_CA_BUNDLE",
    "CURL_CA_BUNDLE",
    "NODE_EXTRA_CA_CERTS",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "no_proxy",
    # For `systemd-run --user`, which wraps bwrap from the outside and needs the session
    # bus to reach the user manager; without these a strict run dies at "Failed to connect
    # to bus". They are not a way back into the host from inside: bwrap mounts a tmpfs over
    # /run, so both the runtime directory and the bus socket are gone by the time the
    # worker starts.
    "DBUS_SESSION_BUS_ADDRESS",
    "XDG_RUNTIME_DIR",
)

# The name a worker sees itself under. Fixed so that nothing a worker writes can carry the
# operator's login, and paired with --hostname for the same reason.
SANDBOX_USER = "task-search"
SANDBOX_HOSTNAME = "task-search"


def _minimal_environment(passthrough=()):
    """Build an environment from an allowlist rather than subtracting from the operator's.

    Inheriting os.environ handed every trial the whole login session: seven API keys where
    one is needed, this machine's ssh and dbus addresses, and the config paths that made
    mini read the host's own ~/.config/mini-swe-agent/.env. A wave that calls itself
    reproducible cannot be reading the operator's dotfiles, so the default is nothing and
    each name that goes in is one somebody chose.

    HOME and the XDG directories are not set here: they are bound into the trial runtime by
    `_sandbox_command`, so the worker and the validation subprocess get the same answer.
    """
    environment = {
        name: os.environ[name]
        for name in (*BASE_ENV_NAMES, *passthrough)
        if name in os.environ
    }
    environment["USER"] = SANDBOX_USER
    environment["LOGNAME"] = SANDBOX_USER
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def _check_sandbox_location(path, label):
    path = Path(path).resolve()
    for hidden in (Path("/tmp"), Path("/run")):
        if path == hidden or hidden in path.parents:
            raise ValueError(
                f"{label} cannot be under {hidden} because strict runs hide host {hidden}: {path}"
            )


def _sandbox_command(
    command,
    *,
    worktree,
    owned_path,
    runtime_root,
    bwrap_bin="bwrap",
    writable_overlays=(),
    synthetic_home=True,
):
    """Wrap a worker so only its owned repository directory is writable."""
    executable = shutil.which(bwrap_bin)
    if executable is None:
        raise RuntimeError(
            f"bubblewrap executable not found: {bwrap_bin!r}; "
            "strict task-search runs require bubblewrap"
        )
    worktree = Path(worktree).resolve()
    owned = (worktree / owned_path).resolve()
    if worktree not in owned.parents:
        raise ValueError(f"owned path escapes worktree: {owned_path}")
    runtime_root = Path(runtime_root).resolve()
    for path, label in ((worktree, "worktree"), (runtime_root, "runtime root")):
        _check_sandbox_location(path, label)
    runtime_dirs = {
        # HOME last mattered because everything else was already redirected here except it:
        # a harness that resolves its own config through the home directory read the
        # operator's. XDG_CONFIG_HOME is named rather than left to default to $HOME/.config
        # so the redirect holds for tools that read it directly.
        "HOME": runtime_root / "home",
        "XDG_CONFIG_HOME": runtime_root / "config",
        "XDG_DATA_HOME": runtime_root / "data",
        "XDG_CACHE_HOME": runtime_root / "cache",
        "XDG_STATE_HOME": runtime_root / "state",
        "TMPDIR": runtime_root / "tmp",
        "MPLCONFIGDIR": runtime_root / "matplotlib",
    }
    if not synthetic_home:
        # AGY reads its own authenticated installation out of the real home, and
        # `_agy_writable_overlays` binds those paths in. Redirecting HOME would point it at
        # an empty directory. Said plainly rather than worked around: an AGY trial is the
        # one kind that still sees the operator's home.
        runtime_dirs.pop("HOME")
    for path in runtime_dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    wrapped = [
        executable,
        "--die-with-parent",
        "--new-session",
        "--unshare-pid",
        "--unshare-ipc",
        "--unshare-uts",
        "--hostname",
        SANDBOX_HOSTNAME,
        "--unshare-cgroup-try",
        "--cap-drop",
        "ALL",
        "--ro-bind",
        "/",
        "/",
        # Do not expose host daemon and desktop sockets. Read-only socket files
        # can still be connected to, so a read-only root alone is insufficient.
        "--tmpfs",
        "/run",
        "--tmpfs",
        "/tmp",
        # Bun/OpenCode needs live device and proc mounts. Replacing the
        # read-only recursive binds also avoids a Bun startup crash.
        "--dev",
        "/dev",
        "--proc",
        "/proc",
        "--bind",
        str(owned),
        str(owned),
        "--bind",
        str(runtime_root),
        str(runtime_root),
        "--chdir",
        str(worktree),
    ]
    for source, target in writable_overlays:
        source = Path(source).resolve()
        target = Path(target).resolve()
        if runtime_root != source and runtime_root not in source.parents:
            raise ValueError(f"writable overlay is outside runtime root: {source}")
        if not source.exists() or not target.exists():
            raise ValueError(
                f"writable overlay endpoint does not exist: {source} -> {target}"
            )
        wrapped.extend(("--bind", str(source), str(target)))
    for name, value in runtime_dirs.items():
        wrapped.extend(("--setenv", name, str(value)))
    wrapped.extend(("--setenv", "PYTHONDONTWRITEBYTECODE", "1"))
    wrapped.extend(
        ("--setenv", "TASK_SEARCH_SPEC", str(runtime_root / "trial_spec.json"))
    )
    wrapped.extend(command)
    return wrapped


def _agy_writable_overlays(runtime_root):
    """Give AGY disposable tool state without opening its authenticated home.

    AGY rewrites ``bin/agentapi`` before every terminal call. The authenticated
    config, settings, conversations, and the rest of its installation stay on the
    read-only root. Its background-task logs similarly live under ``brain``; map
    that artifact tree to the trial runtime so a worker can inspect a long command.
    """
    home = Path.home() / ".gemini" / "antigravity-cli"
    helper_target = home / "bin" / "agentapi"
    brain_target = home / "brain"
    if not helper_target.is_file():
        raise RuntimeError(f"AGY terminal helper is missing: {helper_target}")
    if not brain_target.is_dir():
        raise RuntimeError(f"AGY artifact directory is missing: {brain_target}")
    helper_source = Path(runtime_root) / "agy-agentapi"
    brain_source = Path(runtime_root) / "agy-brain"
    helper_source.touch(mode=0o700)
    brain_source.mkdir(exist_ok=True)
    return ((helper_source, helper_target), (brain_source, brain_target))


def _run_validation(
    worktree,
    commands,
    log_path,
    *,
    owned_path,
    runtime_root,
    bwrap_bin,
    resource_limits,
    timeout_seconds,
    credential_env_names=(),
):
    results = []
    # Candidate code gets no credential, named or not: it is the one process here with no
    # reason to reach a provider.
    environment = _minimal_environment()
    with log_path.open("w") as log:
        for command in commands:
            log.write(f"$ {command}\n")
            log.flush()
            sandboxed = _sandbox_command(
                ["/bin/bash", "-c", command],
                worktree=worktree,
                owned_path=owned_path,
                runtime_root=runtime_root,
                bwrap_bin=bwrap_bin,
            )
            sandboxed = _resource_command(sandboxed, resource_limits)
            try:
                completed = subprocess.run(
                    sandboxed,
                    cwd=worktree,
                    env=environment,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=timeout_seconds,
                )
                exit_code = completed.returncode
                timed_out = False
            except subprocess.TimeoutExpired:
                log.write(f"TIMEOUT after {timeout_seconds} seconds\n")
                log.flush()
                exit_code = 124
                timed_out = True
            results.append(
                {
                    "command": command,
                    "exit_code": exit_code,
                    "timed_out": timed_out,
                }
            )
            if exit_code:
                break
    return results
