import logging

logger = logging.getLogger(__name__)


class BaseEnvTool:
    """环境工具基类."""

    desc = ""

    def run(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, ARG002
        """运行."""
        if self.desc:
            logger.info(f"[green bold]{self.desc}")
