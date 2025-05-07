import os

import PySide2


def setup_gui_env():
    qt_dir = os.path.dirname(PySide2.__file__)
    plugin_path = os.path.join(qt_dir, "plugins", "platforms")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
