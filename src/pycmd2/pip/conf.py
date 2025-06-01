from pycmd2.common.cli import get_client
from pycmd2.common.settings import get_settings

cli = get_client()

settings = get_settings(
    "pip",
    default_config=dict(
        trusted_pip_url=[
            "--trusted-host",
            "pypi.tuna.tsinghua.edu.cn",
            "-i",
            "https://pypi.tuna.tsinghua.edu.cn/simple/",
        ],
        dest_dir=str(cli.CWD / "packages"),
    ),
)
