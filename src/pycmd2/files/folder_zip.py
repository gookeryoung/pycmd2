"""
功能: 压缩目录下的所有文件/文件夹, 默认为当前目录
命令: folderzip.exe [DIRECTORIES ...]
特性: 使用内置压缩工具
"""

import pathlib
import shutil

from pycmd2.common.cli import setup_client

cli = setup_client(help="pdf 分割工具.")


IGNORE_DIRS = [".git", ".idea", ".vscode", "__pycache__"]
IGNORE_FILES = [".gitignore"]
IGNORE = [*IGNORE_DIRS, *IGNORE_FILES]
IGNORE_EXT = [".zip", ".rar", ".7z", ".tar", ".gz"]


def zip_folder(folder: pathlib.Path) -> None:
    shutil.make_archive(str(folder), "zip", folder)
    print(f"[*] 压缩{'目录'}[{folder.name}]")


@cli.app.command()
def main():
    dirs = list(d for d in cli.cwd.iterdir() if d.is_dir())
    cli.run(zip_folder, dirs)
