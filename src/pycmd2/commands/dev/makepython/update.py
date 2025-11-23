import datetime
import logging
import re
import shutil
from pathlib import Path

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)

__all__ = ("update_build_date",)


def _restore_backup_file(file_path: Path, backup_file: Path) -> None:
    """恢复备份文件.

    Args:
        file_path: 文件路径
        backup_file: 备份文件路径

    Raises:
        OSError: 恢复失败
    """
    try:
        shutil.copy2(backup_file, file_path)
        logger.info(f"已恢复文件: {file_path}")
    except OSError as e:
        logger.exception(f"恢复文件失败: {file_path}, {e.__class__.__name__}")
        raise


def _create_backup_file(file_path: Path) -> Path:
    """创建文件备份.

    Args:
        file_path: 文件路径

    Returns:
        Path: 备份文件路径
    """
    backup_file = file_path.with_suffix(file_path.suffix + ".bak")
    shutil.copy2(file_path, backup_file)
    return backup_file


def _update_file_build_date(file_path: Path, build_date: str, pattern: re.Pattern) -> bool:
    """更新单个文件的构建日期.

    Args:
        file_path: 文件路径
        build_date: 新的构建日期
        pattern: 正则表达式模式

    Returns:
        bool: 是否成功更新
    """
    backup_file = None
    try:
        # 创建备份
        backup_file = _create_backup_file(file_path)

        with file_path.open("r+", encoding="utf-8") as f:
            content = f.read()

            # 查找匹配项
            match = pattern.search(content)
            if not match:
                logger.debug(f"文件 {file_path} 中未找到 __build_date__ 定义, 跳过")
                return False

            # 构造新行 - 修正分组索引
            # 分组1: 缩进, 分组2: 变量名, 分组3: 引号, 分组4: 原日期, 分组5: 尾部
            quote = match.group(3) or ""  # 获取原引号(可能为空)
            new_line = f"{match.group(1)}{match.group(2)} = {quote}{build_date}{quote}{match.group(5)}"
            new_content = pattern.sub(new_line, content, count=1)

            # 检查是否需要更新
            if new_content == content:
                logger.debug(f"文件 {file_path} 构建日期已是最新, 无需更新")
                return False

            # 回写文件
            f.seek(0)
            f.write(new_content)
            f.truncate()
            f.flush()  # 确保写入磁盘

            logger.info(f"更新文件: {file_path}, __build_date__ -> {build_date}")

            return True

    except OSError as e:
        msg = f"文件操作失败: {file_path}, {e.__class__.__name__}: {e}"
        logger.exception(msg)
        # 恢复备份
        if backup_file and backup_file.exists():
            try:
                _restore_backup_file(file_path, backup_file)
            except OSError:
                logger.exception(f"恢复备份文件失败: {backup_file}")
        return False
    except (re.error, ValueError) as e:
        msg = f"数据处理错误: {file_path}, {e.__class__.__name__}: {e}"
        logger.exception(msg)
        return False
    finally:
        # 清理备份文件
        if backup_file and backup_file.exists():
            try:
                backup_file.unlink()
            except OSError as e:
                logger.warning(f"删除备份文件失败: {backup_file}, {e}")


def _get_build_date_pattern() -> re.Pattern:
    """获取构建日期匹配的正则表达式模式.

    Returns:
        re.Pattern: 正则表达式模式
    """
    return re.compile(
        r"^(\s*)"  # 分组1: 缩进
        r"(__build_date__)\s*=\s*"  # 分组2: 变量名
        r"([\"']?)"  # 分组3: 引号类型
        r"(\d{4}-\d{2}-\d{2})"  # 分组4: 原日期
        r"\3"  # 闭合引号(引用分组3)
        r"(\s*(#.*)?)$",  # 分组5: 尾部空格和注释
        flags=re.MULTILINE | re.IGNORECASE,
    )


def _log_update_summary(updated_count: int, skipped_count: int) -> None:
    """记录更新结果汇总.

    Args:
        updated_count: 成功更新的文件数量
        skipped_count: 跳过的文件数量
    """
    if updated_count > 0:
        logger.info(f"构建日期更新完成, 共更新 {updated_count} 个文件")
    if skipped_count > 0:
        logger.info(f"跳过 {skipped_count} 个文件(未找到 __build_date__ 定义或无需更新)")
    if updated_count == 0 and skipped_count == 0:
        logger.warning("未找到任何 __init__.py 文件进行处理")


def update_build_date() -> None:
    """更新构建日期.

    遍历 src 目录下的所有 __init__.py 文件, 更新其中的 __build_date__ 变量。
    """
    # 检查 src 目录是否存在
    src_dir = cli.cwd / "src"
    if not src_dir.exists():
        logger.warning("src 目录不存在, 无法更新构建日期")
        return

    init_files = list(src_dir.rglob("__init__.py"))
    if not init_files:
        logger.warning("未找到任何 __init__.py 文件进行处理")
        return

    updated_files = 0
    skipped_files = 0

    pattern = _get_build_date_pattern()
    build_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    for init_file in init_files:
        if _update_file_build_date(init_file, build_date, pattern):
            updated_files += 1
        else:
            skipped_files += 1

    _log_update_summary(updated_files, skipped_files)
