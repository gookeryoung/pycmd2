import os


def setup_pyside2_env():
    """初始化 PySide2 环境"""
    import PySide2

    qt_dir = os.path.dirname(PySide2.__file__)
    plugin_path = os.path.join(qt_dir, "plugins", "platforms")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
