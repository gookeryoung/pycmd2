"""
功能: Backup files and folders as zip file in destination folder, automatic remove
dump files when reached max count.
命令: folderback.exe -f [FILES ...] -d [DESTINATION] -c [CONFIG] -n [COUNT]
"""

import argparse
import pathlib
import sys
import threading
import time
import zipfile


def remove_dump(src: pathlib.Path, dst: pathlib.Path, max_zip: int) -> None:
    """Recursively remove dump zip files in folder dst, archived from src."""
    zip_paths = [
        filepath for filepath in dst.rglob("*.zip") if src.stem in str(filepath)
    ]
    zip_files = sorted(zip_paths, key=lambda fn: str(fn)[-19:-4])
    if len(zip_files) > max_zip:
        print(f"remove oldest zip file: [{zip_files[0]}].")
        zip_files[0].unlink()
        remove_dump(src, dst, max_zip)


def zip_target(src: pathlib.Path, dst: pathlib.Path, max_zip: int) -> None:
    """Zip single file or files in folder from src into dst folder."""
    files = [str(src)] if src.is_file() else [str(_) for _ in src.rglob("*")]
    timestamp = time.strftime("_%Y%m%d_%H%M%S")
    target_path = dst / (src.stem + timestamp + ".zip")
    zip_file = zipfile.ZipFile(target_path, "w")

    print(f"compressing [{src}] into [{dst}]...")
    for file in files:
        zip_file.write(file, arcname=file.replace(str(src.parent), ""))
    remove_dump(src, dst, max_zip)


def main():
    doc = {
        "files": "files or folders to be archived",
        "config": "load folders from config file",
        "destination": "destination folder",
        "count": "max backup count",
    }

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f", dest="files", type=str, nargs="+", help=doc["files"]
    )
    group.add_argument("-c", dest="config", type=str, help=doc["config"])
    parser.add_argument(
        "-d",
        dest="destination",
        type=str,
        required=True,
        help=doc["destination"],
    )
    parser.add_argument(
        "-n",
        dest="count",
        type=int,
        required=True,
        default=5,
        help=doc["count"],
    )

    args = parser.parse_args()
    opt_files, opt_config = args.files, args.config

    if opt_config:
        path_config = pathlib.Path(sys.argv[0]).parent / opt_config
        if path_config.exists():
            print(f"scanning config file [{path_config}]...")
            with open(str(path_config), encoding="utf-8") as f:
                content = [line.strip() for line in f.readlines()]
                targets = [
                    pathlib.Path(fn)
                    for fn in content
                    if pathlib.Path(fn).exists()
                ]
        else:
            print(f"config file {path_config} is not valid.")
            sys.exit(-1)
    elif opt_files:
        targets = [
            pathlib.Path(f) for f in opt_files if pathlib.Path(f).exists()
        ]
    else:
        print("invalid arguments.")
        parser.print_help(sys.stdout)
        sys.exit(-1)

    if not len(targets):
        print("no valid file found.")
        sys.exit(-1)

    max_count = args.count
    path_dst_folder = pathlib.Path(args.destination)
    if not path_dst_folder.exists():
        print(f"creating destination folder: {path_dst_folder}")
        path_dst_folder.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    for target in targets:
        print(f"start processing target [{target}]...")
        thread = threading.Thread(
            target=zip_target, args=(target, path_dst_folder, max_count)
        )
        thread.start()
        thread.join()
    print(
        f"total targets: {len(targets)}.\ntime used:{time.perf_counter() - t0:.4f}s."
    )
