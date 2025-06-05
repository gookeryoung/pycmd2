import os
from pathlib import Path

import PySide2


def setup_pyside2_env() -> None:
    """初始化 PySide2 环境."""
    qt_dir = Path(PySide2.__file__).parent
    plugin_path = qt_dir / "plugins" / "platforms"
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugin_path)
