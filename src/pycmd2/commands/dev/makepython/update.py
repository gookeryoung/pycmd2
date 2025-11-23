from __future__ import annotations

import contextlib
import datetime
import logging
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from typing import Generator

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)

__all__ = ("update_build_date",)


class _Config:
    """配置常量类."""

    # 文件相关常量
    SRC_DIR_NAME: Final[str] = "src"
    INIT_FILENAME: Final[str] = "__init__.py"
    BACKUP_SUFFIX: Final[str] = ".bak"
    TEMP_SUFFIX: Final[str] = ".tmp"

    # 日期格式常量
    DATE_FORMAT: Final[str] = "%Y-%m-%d"
    DATE_PATTERN: Final[str] = r"\d{4}-\d{2}-\d{2}"

    # 正则表达式模式
    BUILD_DATE_VAR: Final[str] = "__build_date__"

    # 编码相关
    PRIMARY_ENCODING: Final[str] = "utf-8"
    FALLBACK_ENCODING: Final[str] = "latin-1"


@dataclass
class _ParseResult:
    """解析结果类."""

    needs_update: bool
    new_content: str = ""


@contextlib.contextmanager
def _managed_backup(file_path: Path) -> Generator[Path, None, None]:
    """管理备份文件的生命周期.

    Args:
        file_path: 要备份的文件路径

    Yields:
        Path: 备份文件路径

    Raises:
        OSError: 文件操作失败
    """
    backup_file = None
    try:
        # 使用时间戳避免备份文件名冲突
        timestamp = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        backup_suffix = f"{_Config.BACKUP_SUFFIX}.{timestamp}"
        backup_file = file_path.with_suffix(file_path.suffix + backup_suffix)

        shutil.copy2(file_path, backup_file)
        logger.debug(f"创建备份文件: {backup_file}")
        yield backup_file
    except OSError:
        logger.exception(f"备份操作失败: {file_path}")
        raise
    finally:
        # 只有在正常完成时才清理备份文件
        if backup_file and backup_file.exists():
            try:
                backup_file.unlink()
                logger.debug(f"清理备份文件: {backup_file}")
            except OSError as e:
                logger.warning(f"删除备份文件失败: {backup_file}, {e}")
        else:
            logger.info(f"备份文件不存在: {backup_file}, 跳过清理")


def _update_file_build_date(file_path: Path, build_date: str, pattern: re.Pattern) -> bool:
    """更新单个文件的构建日期.

    Args:
        file_path: 文件路径
        build_date: 新的构建日期
        pattern: 正则表达式模式

    Returns:
        bool: 是否成功更新
    """
    # 读取文件内容
    original_content = _read_file_content(file_path)
    if original_content is None:
        return False

    # 解析和验证内容
    parse_result = _parse_and_validate_content(file_path, original_content, build_date, pattern)
    if not parse_result.needs_update:
        return False

    # 执行文件更新
    return _perform_file_update(file_path, parse_result.new_content, build_date)


def _read_file_content(file_path: Path) -> str | None:
    """读取文件内容.

    Args:
        file_path: 文件路径

    Returns:
        str | None: 文件内容, 失败时返回 None
    """
    try:
        with file_path.open("r", encoding=_Config.PRIMARY_ENCODING) as f:
            return f.read()
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with file_path.open("r", encoding=_Config.FALLBACK_ENCODING) as f:
                content = f.read()
            logger.warning(f"文件 {file_path} 使用 {_Config.FALLBACK_ENCODING} 编码读取")
        except OSError:
            logger.exception(f"读取文件失败: {file_path}")
            return None
        else:
            return content
    except OSError:
        logger.exception(f"读取文件失败: {file_path}")
        return None


def _parse_and_validate_content(file_path: Path, content: str, build_date: str, pattern: re.Pattern) -> _ParseResult:
    """解析和验证文件内容.

    Args:
        file_path: 文件路径
        content: 文件内容
        build_date: 新的构建日期
        pattern: 正则表达式模式

    Returns:
        _ParseResult: 解析结果
    """
    try:
        # 查找匹配项
        match = pattern.search(content)
        if not match:
            logger.debug(f"文件 {file_path} 中未找到 {_Config.BUILD_DATE_VAR} 定义, 跳过")
            return _ParseResult(needs_update=False)

        # 验证现有日期格式
        current_date = match.group(4)
        if not _validate_date_format(current_date):
            logger.warning(f"文件 {file_path} 中的日期格式无效: {current_date}, 跳过")
            return _ParseResult(needs_update=False)

        # 验证新日期格式
        if not _validate_date_format(build_date):
            logger.error(f"新的构建日期格式无效: {build_date}")
            return _ParseResult(needs_update=False)

        # 构造新内容
        quote = match.group(3) or ""  # 获取原引号(可能为空)
        new_line = f"{match.group(1)}{match.group(2)} = {quote}{build_date}{quote}{match.group(5)}"
        new_content = pattern.sub(new_line, content, count=1)

        # 检查是否需要更新
        if new_content == content:
            logger.debug(f"文件 {file_path} 构建日期已是最新, 无需更新")
            return _ParseResult(needs_update=False)

        return _ParseResult(needs_update=True, new_content=new_content)

    except (re.error, ValueError) as e:
        msg = f"数据处理错误: {file_path}, {e.__class__.__name__}: {e}"
        logger.exception(msg)
        return _ParseResult(needs_update=False)


def _perform_file_update(file_path: Path, new_content: str, build_date: str) -> bool:
    """执行文件更新操作.

    Args:
        file_path: 文件路径
        new_content: 新的文件内容
        build_date: 构建日期

    Returns:
        bool: 是否成功更新

    Raises:
        OSError: 文件操作失败
    """
    try:
        with _managed_backup(file_path):
            # 原子性写入
            temp_file = file_path.with_suffix(file_path.suffix + _Config.TEMP_SUFFIX)
            try:
                with temp_file.open("w", encoding=_Config.PRIMARY_ENCODING) as f:
                    f.write(new_content)
                    f.flush()
                    os.fsync(f.fileno())  # 强制写入磁盘

                # 原子性移动
                shutil.move(str(temp_file), str(file_path))

            except OSError:
                # 清理临时文件
                if temp_file.exists():
                    with contextlib.suppress(OSError):
                        temp_file.unlink()
                raise
            else:
                logger.info(f"更新文件: {file_path}, {_Config.BUILD_DATE_VAR} -> {build_date}")
                return True

    except OSError as e:
        msg = f"文件操作失败: {file_path}, {e.__class__.__name__}: {e}"
        logger.exception(msg)
        return False


def _validate_date_format(date_str: str) -> bool:
    """验证日期格式是否正确.

    Args:
        date_str: 日期字符串

    Returns:
        bool: 是否为有效的 YYYY-MM-DD 格式
    """
    try:
        datetime.datetime.strptime(date_str, _Config.DATE_FORMAT)  # noqa: DTZ007
    except ValueError:
        return False
    else:
        return True


def _validate_config() -> bool:
    """验证配置的有效性.

    Returns:
        bool: 配置是否有效
    """
    # 验证日期格式
    test_date = datetime.datetime.now(tz=datetime.timezone.utc).strftime(_Config.DATE_FORMAT)
    if not _validate_date_format(test_date):
        logger.error(f"日期格式配置无效: {_Config.DATE_FORMAT}")
        return False

    # 验证正则表达式模式
    try:
        pattern = _get_build_date_pattern()
        # 测试模式是否有效
        test_content = f"{_Config.BUILD_DATE_VAR} = '{test_date}'"
        if not pattern.search(test_content):
            logger.error("正则表达式模式配置无效")
            return False
    except re.error:
        logger.exception("正则表达式编译失败")
        return False

    return True


def _get_build_date_pattern() -> re.Pattern:
    """获取构建日期匹配的正则表达式模式.

    Returns:
        re.Pattern: 正则表达式模式
    """
    return re.compile(
        r"^(\s*)"  # 分组1: 缩进
        rf"({_Config.BUILD_DATE_VAR})\s*=\s*"  # 分组2: 变量名
        r"([\"']?)"  # 分组3: 引号类型
        rf"({_Config.DATE_PATTERN})"  # 分组4: 原日期
        r"\3"  # 闭合引号(引用分组3)
        r"(\s*(#.*)?)$",  # 分组5: 尾部空格和注释
        flags=re.MULTILINE | re.IGNORECASE,
    )


def _cleanup_temp_files(directory: Path) -> None:
    """清理可能残留的临时文件.

    Args:
        directory: 要清理的目录路径
    """
    try:
        for temp_file in directory.rglob(f"*{_Config.TEMP_SUFFIX}"):
            try:
                temp_file.unlink()
                logger.debug(f"清理临时文件: {temp_file}")
            except OSError as e:  # noqa: PERF203
                logger.warning(f"清理临时文件失败: {temp_file}, {e}")
    except OSError as e:
        logger.warning(f"扫描临时文件失败: {directory}, {e}")


def _log_update_summary(updated_count: int, skipped_count: int, failed_count: int = 0) -> None:
    """记录更新结果汇总.

    Args:
        updated_count: 成功更新的文件数量
        skipped_count: 跳过的文件数量
        failed_count: 处理失败的文件数量
    """
    total_files = updated_count + skipped_count + failed_count

    if updated_count > 0:
        logger.info(f"构建日期更新完成, 共更新 {updated_count} 个文件")
    if skipped_count > 0:
        logger.info(f"跳过 {skipped_count} 个文件(未找到 __build_date__ 定义或无需更新)")
    if failed_count > 0:
        logger.error(f"处理失败 {failed_count} 个文件")

    if total_files == 0:
        logger.warning(f"未找到任何 {_Config.INIT_FILENAME} 文件进行处理")
    else:
        logger.info(f"处理完成: 总计 {total_files} 个文件, 成功 {updated_count}, 跳过 {skipped_count}, 失败 {failed_count}")


def update_build_date() -> None:
    """更新构建日期.

    遍历 src 目录下的所有 __init__.py 文件, 更新其中的 __build_date__ 变量。

    使用原子性操作确保文件更新的安全性, 并在失败时自动恢复。
    处理完成后会清理可能残留的临时文件。
    """
    # 验证配置
    if not _validate_config():
        logger.error("配置验证失败, 终止更新操作")
        return

    # 检查 src 目录是否存在
    src_dir = cli.cwd / _Config.SRC_DIR_NAME
    if not src_dir.exists():
        logger.warning(f"{_Config.SRC_DIR_NAME} 目录不存在, 无法更新构建日期")
        return

    # 先清理可能残留的临时文件
    logger.debug("清理可能残留的临时文件...")
    _cleanup_temp_files(src_dir)

    try:
        init_files = list(src_dir.rglob(_Config.INIT_FILENAME))
    except OSError:
        logger.exception(f"扫描 {_Config.INIT_FILENAME} 文件失败")
        return

    if not init_files:
        logger.warning(f"未找到任何 {_Config.INIT_FILENAME} 文件进行处理")
        return

    logger.info(f"找到 {len(init_files)} 个 {_Config.INIT_FILENAME} 文件需要处理")

    updated_files = 0
    skipped_files = 0
    failed_files = 0

    pattern = _get_build_date_pattern()
    build_date = datetime.datetime.now(datetime.timezone.utc).strftime(_Config.DATE_FORMAT)

    # 验证生成的日期格式
    if not _validate_date_format(build_date):
        logger.error(f"生成的构建日期格式无效: {build_date}")
        return

    # 按路径排序, 确保处理顺序的一致性
    init_files.sort()

    for init_file in init_files:
        try:
            if _update_file_build_date(init_file, build_date, pattern):
                updated_files += 1
            else:
                skipped_files += 1
        except Exception as e:  # noqa: PERF203
            logger.exception(f"处理文件失败: {init_file}, {e.__class__.__name__}")
            failed_files += 1

    _log_update_summary(updated_files, skipped_files, failed_files)

    # 最终清理临时文件
    _cleanup_temp_files(src_dir)
