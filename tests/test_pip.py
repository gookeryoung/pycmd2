import os


def test_pip_download(typer_runner, dir_tests):
    os.chdir(dir_tests)

    from pycmd2.pip.pip_download import cli

    result = typer_runner.invoke(cli.app, ["lxml"])
    assert result.exit_code == 0

    files = list(dir_tests.glob("packages/lxml-*.whl"))
    assert len(files) == 1
