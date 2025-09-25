from pathlib import Path

from pycmd2.config import TomlConfigMixin


class TodoConfig(TomlConfigMixin):
    """Todo configuration."""

    TITLE = "Todo"

    _DATA_DIR = Path.home() / ".pycmd2" / "office" / "todo"

    def data_dir(self) -> Path:
        """Data directory.

        Returns:
            Path: data directory
        """
        return self._DATA_DIR


conf = TodoConfig()

if not conf.data_dir().exists():
    conf.data_dir().mkdir(parents=True)
