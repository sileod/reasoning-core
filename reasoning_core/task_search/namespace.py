"""The filesystem a worker sees, fixed so it does not describe the machine it ran on.

A trial used to be handed its own host paths: the checkout under someone's home, a runs
directory named after the cluster share. Those reach the model, so they reach trajectories,
and two runs of the same trial on two machines then differ in ways that have nothing to do
with the work. Here the worktree is always `/workspace` and the trial's scratch space is
always `/runtime`, whatever they are outside.

Nothing in this module knows about task search, plans, or trials. It is the mapping between
a pair of host directories and the paths a sandboxed process is given for them, plus the
bubblewrap arguments that make the mapping true -- so it can move to whatever owns the
namespace: this repository's wrapper today, Harness Link if it grows a sandbox mode.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import sys

# Bubblewrap cannot create a top-level mount point on a read-only root -- `--bind X
# /workspace` fails with "Can't mkdir /workspace" -- so the fixed tree lives under one
# existing directory that is replaced with a tmpfs and rebuilt. /home is that directory:
# on a shared machine it otherwise exposes every colleague's home, so covering it is worth
# doing for its own sake, and what a worker gets instead is three fixed names.
SANDBOX_ROOT = PurePosixPath("/home")
WORKSPACE = SANDBOX_ROOT / "workspace"
RUNTIME = SANDBOX_ROOT / "runtime"
HOME = SANDBOX_ROOT / "task-search"
USER = "task-search"
HOSTNAME = "task-search"

# Where a process is told to put things, in sandbox paths. The host directories behind
# them are `host_directories()`, which the caller creates before launching: bubblewrap
# will happily bind a directory that does not exist yet and give the worker an empty one.
RUNTIME_SUBDIRS = {
    "XDG_CONFIG_HOME": "config",
    "XDG_DATA_HOME": "data",
    "XDG_CACHE_HOME": "cache",
    "XDG_STATE_HOME": "state",
    "TMPDIR": "tmp",
    "MPLCONFIGDIR": "matplotlib",
}
HOME_SUBDIR = "home"


@dataclass(frozen=True)
class Namespace:
    """One trial's two host directories and the fixed paths they appear at."""

    worktree: Path
    runtime_root: Path

    def __post_init__(self):
        object.__setattr__(self, "worktree", Path(self.worktree).resolve())
        object.__setattr__(self, "runtime_root", Path(self.runtime_root).resolve())

    def workspace(self, *parts):
        return WORKSPACE.joinpath(*parts)

    def runtime(self, *parts):
        return RUNTIME.joinpath(*parts)

    def translate(self, host_path):
        """The sandbox path for something under the worktree or the runtime root.

        Raises for anything else rather than guessing: a path this does not own is one the
        worker should not have been given, and returning it unchanged would leak the host
        silently, which is the failure this module exists to prevent.
        """
        host_path = Path(host_path).resolve()
        for root, inside in ((self.worktree, WORKSPACE), (self.runtime_root, RUNTIME)):
            if host_path == root:
                return inside
            if root in host_path.parents:
                return inside / host_path.relative_to(root)
        raise ValueError(f"path is outside the sandbox namespace: {host_path}")

    def host_directories(self):
        """Host directories to create before launching."""
        return (
            self.runtime_root / HOME_SUBDIR,
            *(self.runtime_root / name for name in RUNTIME_SUBDIRS.values()),
        )

    def environment(self, *, home=True):
        """Where the worker is told to put things, in its own paths."""
        variables = {"HOME": str(HOME)} if home else {}
        for name, subdir in RUNTIME_SUBDIRS.items():
            variables[name] = str(self.runtime(subdir))
        return variables

    def binds(self, owned_path, *, home=True):
        """Bubblewrap arguments placing the two host directories at their fixed paths.

        `owned_path` is the only part of the worktree a worker may write, and is bound
        after the read-only worktree so it wins. Sources are host paths -- bubblewrap
        resolves them in the namespace it starts from -- and only destinations are fixed.

        `home=False` leaves the real home alone, for a harness that authenticates through
        its own installation there. That also keeps /home as it is, since a home under it
        would otherwise lose everything the tmpfs covers.
        """
        owned = (self.worktree / owned_path).resolve()
        if self.worktree not in owned.parents:
            raise ValueError(f"owned path escapes worktree: {owned_path}")
        # The tmpfs both hides the real occupants of SANDBOX_ROOT and makes it writable
        # inside the namespace, which is the only reason the three binds below can create
        # their mount points at all. It does not hide the operator's own home: on a cluster
        # $HOME is usually elsewhere, and the interpreter and harnesses live inside it, so
        # it has to stay readable. `require_free_root` is what keeps the two facts apart.
        return (
            "--tmpfs", str(SANDBOX_ROOT),
            "--ro-bind", str(self.worktree), str(WORKSPACE),
            "--bind", str(owned), str(self.workspace(owned_path)),
            "--bind", str(self.runtime_root), str(RUNTIME),
            *(("--bind", str(self.runtime_root / HOME_SUBDIR), str(HOME)) if home else ()),
            "--chdir", str(WORKSPACE),
        )


def require_free_root():
    """Fail loudly if this machine keeps something the run needs under SANDBOX_ROOT.

    The fixed tree is built by replacing that directory with a tmpfs, which is safe here
    because $HOME, the interpreter and the harnesses all live elsewhere. On a machine whose
    users are under /home it would hide the very things the worker runs on, and a wave that
    dies at step zero everywhere is a worse way to learn that than one clear sentence.
    """
    root = Path(SANDBOX_ROOT)
    for path, what in ((Path.home(), "the home directory"),
                       (Path(sys.executable), "the interpreter")):
        path = path.resolve()
        if path == root or root in path.parents:
            raise RuntimeError(
                f"{what} is under {root}, which the sandbox replaces with a tmpfs: {path}. "
                "Pick a different namespace.SANDBOX_ROOT for this machine."
            )
