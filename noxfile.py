"""noxfile.py is used to run the tests."""

from typing import Final

import nox

XDIST_WORKERS: Final[int] = 10
PYTHON_VERSIONS: Final[list[str]] = ["3.10.0", "3.11.4", "3.12.0", "3.13.0"]

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True


@nox.session(tags=["tests"], python=PYTHON_VERSIONS)
@nox.parametrize("group", ["--group=dev", "--all-groups"])
def tests(session: nox.Session, group: str) -> None:
    """Run the tests."""
    session.run_install(
        "uv",
        "sync",
        group,
        "--frozen",
        "--active",
        f"--python={session.python}",
    )
    session.run("pytest", "tests", f"-n={XDIST_WORKERS}")


@nox.session(tags=["lint"], python=PYTHON_VERSIONS)
@nox.parametrize("group", ["--group=dev", "--all-groups"])
def lint(session: nox.Session, group: str) -> None:
    """Run the linter."""
    session.run_install(
        "uv",
        "sync",
        group,
        "--frozen",
        "--active",
        f"--python={session.python}",
    )
    session.run("ruff", "check", "tests", "fast_blurhash")
    session.run("ruff", "format", "--check", "tests", "fast_blurhash")


@nox.session(tags=["mypy"], python=PYTHON_VERSIONS)
@nox.parametrize("group", ["--group=dev", "--all-groups"])
def mypy(session: nox.Session, group: str) -> None:
    """Run the type checker."""
    session.run_install(
        "uv",
        "sync",
        group,
        "--frozen",
        "--active",
        f"--python={session.python}",
    )
    session.run("mypy", "tests", "fast_blurhash")
