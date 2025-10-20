use pyo3::prelude::*;
use std::process::Command;

#[pyfunction]
pub fn setup_rust_env() -> PyResult<()> {
    println!("正在设置 Rust 环境...");

    // 安装指定的工具链
    let output = Command::new("rustup")
        .args(["toolchain", "install", "stable-x86_64-pc-windows-msvc"])
        .output();

    println!("调用命令: {:?}", output);

    match output {
        Ok(output) => {
            if output.status.success() {
                println!("成功安装 stable-x86_64-pc-windows-msvc 工具链");
            } else {
                let stderr = String::from_utf8_lossy(&output.stderr);
                eprintln!("安装工具链时出错: {}", stderr);
                return Err(pyo3::exceptions::PyException::new_err(
                    "Failed to install toolchain",
                ));
            }
        }
        Err(e) => {
            eprintln!("执行 rustup 命令时出错: {}", e);
            return Err(pyo3::exceptions::PyException::new_err(
                "Failed to execute rustup command",
            ));
        }
    }

    // 设置默认主机
    let output = Command::new("rustup")
        .args(["set", "default-host", "x86_64-pc-windows-msvc"])
        .output();

    match output {
        Ok(output) => {
            if output.status.success() {
                println!("成功设置默认主机为 x86_64-pc-windows-msvc");
            } else {
                let stderr = String::from_utf8_lossy(&output.stderr);
                eprintln!("设置默认主机时出错: {}", stderr);
                return Err(pyo3::exceptions::PyException::new_err(
                    "Failed to set default host",
                ));
            }
        }
        Err(e) => {
            eprintln!("执行 rustup set 命令时出错: {}", e);
            return Err(pyo3::exceptions::PyException::new_err(
                "Failed to execute rustup set command",
            ));
        }
    }

    println!("Rust 环境设置完成");
    Ok(())
}
