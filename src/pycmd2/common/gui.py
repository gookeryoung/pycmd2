from __future__ import annotations

import logging
import os
from pathlib import Path

import PySide2

logger = logging.getLogger(__name__)


def setup_pyside2_env(*, enable_high_dpi: bool = False) -> None:
    """初始化 PySide2 环境."""
    qt_dir = Path(PySide2.__file__).parent
    plugin_path = qt_dir / "plugins" / "platforms"
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugin_path)

    if enable_high_dpi:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
