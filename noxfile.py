from __future__ import annotations

import nox


@nox.session()
def pre_commit(session):
    session.run("poetry", "run", "pre-commit", "run", "--all-files", external=True)


@nox.session()
def test(session):
    session.run(
        "poetry",
        "run",
        "pytest",
        "--cov=pyartifactory",
        "--cov-branch",
        "--cov-report=xml",
        external=True,
    )
