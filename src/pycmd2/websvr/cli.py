from __future__ import annotations

import logging
import os
import pathlib
import subprocess
import sys
import time
from typing import Optional

import typer
import webview

DIST_DIR = pathlib.Path(__file__).parent / "frontend" / "dist"
FRONTEND_DIR = pathlib.Path(__file__).parent / "frontend"
NODE_MODULES_DIR = FRONTEND_DIR / "node_modules"

assert DIST_DIR.exists(), "找不到前端构建目录"
assert FRONTEND_DIR.exists(), "找不到前端目录"
assert NODE_MODULES_DIR.exists(), "找不到 node_modules 目录"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer()


def get_yarn_executable_path() -> str:
    """获取 Yarn 的可执行文件路径."""
    if sys.platform == "win32":
        return "yarn.cmd"

    return "yarn"


def get_npm_executable_path() -> str:
    """获取 NPM 的可执行文件路径."""
    if sys.platform == "win32":
        return "npm.cmd"

    return "npm"


def is_development_mode() -> bool:
    """检查是否为开发模式."""
    # 检查是否有 --dev 参数
    if "--dev" in sys.argv:
        return True

    # 检查是否存在 dist 目录
    if not DIST_DIR.exists():
        return True

    # 检查是否在开发环境中运行（通过检查环境变量）
    return os.getenv("PYCMD2_WEBVIEW_DEV") == "1"


def start_vite_dev_server() -> Optional[subprocess.Popen]:
    """启动 Vite 开发服务器.

    Returns:
        Optional[subprocess.Popen]: 返回启动的开发服务器进程对象，如果启动失败则返回None
    """
    os.chdir(FRONTEND_DIR)

    try:
        # 检查是否安装了依赖
        if not (FRONTEND_DIR / "node_modules").exists():
            subprocess.run(
                [get_yarn_executable_path(), "install"]
                if (FRONTEND_DIR / "yarn.lock").exists()
                else [get_npm_executable_path(), "install"],
                cwd=FRONTEND_DIR,
                check=True,
            )

        # 启动开发服务器
        dev_server = subprocess.Popen(
            [get_yarn_executable_path(), "dev"]
            if (FRONTEND_DIR / "yarn.lock").exists()
            else [get_npm_executable_path(), "run", "dev"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # 等待服务器启动
        time.sleep(5)
    except (subprocess.SubprocessError, OSError):
        logger.exception("启动 Vite 开发服务器失败")
        return None
    else:
        return dev_server


@app.command("run", help="开发模式, 启动 Vite 构建工具并启动 WebView 应用, 默认别名: d")
def run(
    *,
    dev: bool = typer.Option(False, "--dev", "-d", help="开发模式"),
) -> None:
    """开发模式, 启动 Vite 构建工具并启动 WebView 应用, 默认别名: d."""
    if dev:
        logger.info("启动开发模式...")
        os.environ["PYCMD2_WEBVIEW_DEV"] = "1"
        start_vite_dev_server()
    else:
        logger.info("启动生产模式...")

    start_webview()


def start_webview() -> None:
    """启动 WebView 应用."""
    dev_server = None  # 初始化为None，确保在异常情况下也能正确处理

    if is_development_mode():
        url_path = "http://localhost:5173"

        dev_server = start_vite_dev_server()
        if not dev_server:
            logger.error("无法启动 Vite 开发服务器, 退出...")
            return
    else:
        # 生产模式：加载构建后的静态文件
        url_path = DIST_DIR / "index.html"

        # 使用显式检查而不是assert（在-O模式下会被忽略）
        if not url_path.exists():
            logger.error(f"找不到构建后的文件 {url_path}")
            logger.error("请先构建前端应用, 或者使用 --dev 参数运行开发模式")
            return

        # 将文件路径转换为file:// URL格式
        dev_server = None

    try:
        # 创建窗口并连接到开发服务器或加载本地文件
        webview.create_window(
            title="我的全栈应用",
            url=str(url_path) if dev_server is None else "http://localhost:5173",
            width=1200,
            height=800,
        )

        # 启动 WebView
        webview.start(debug=False)  # 显式设置debug=False，避免在生产环境中输出过多日志
    except Exception:
        logger.exception("启动 WebView 失败")
    finally:
        logger.info("清理资源")
        # 无论正常退出还是异常退出，都清理资源
        if dev_server and dev_server.poll() is None:
            logger.info("正在关闭 Vite 开发服务器...")

            # 尝试优雅地终止进程
            try:
                # 在Windows上，使用terminate()可能不会终止子进程，因此需要专门处理
                if sys.platform == "win32":
                    # 在Windows上，子进程可能不会被terminate()终止，需要使用taskkill命令
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(dev_server.pid)],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    # 在Unix-like系统上，发送SIGTERM信号
                    dev_server.terminate()

                try:
                    # 等待进程结束，设置超时
                    dev_server.wait(timeout=10)  # 增加超时时间到10秒
                    logger.info("Vite 开发服务器已正常关闭")
                except subprocess.TimeoutExpired:
                    logger.warning("Vite 开发服务器未能正常关闭, 强制终止")
                    # 如果进程仍未结束，则强制杀死
                    if sys.platform != "win32":
                        dev_server.kill()
                    dev_server.wait()  # 确保进程被清理
                    logger.info("Vite 开发服务器已强制关闭")
            except ProcessLookupError:
                # 进程可能已经结束
                logger.info("Vite 开发服务器进程已不存在")
            except Exception:
                logger.exception("关闭 Vite 开发服务器时出错")
