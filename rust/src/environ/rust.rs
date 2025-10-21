use std::path;

use crate::system::{self, call_command};
use pyo3::prelude::*;
use std::env::current_dir;
use tklog::info;
use which::which;

#[cfg(windows)]
fn _install_rustup_windows() -> PyResult<()> {
    let current_dir = current_dir().expect("无法获取当前目录");
    let rustup_path = path::Path::new(&current_dir).join("rustup-init.exe");

    if rustup_path.exists() {
        info!("rustup-init.exe 已经存在");
    } else {
        info!("正在下载 rustup-init.exe...");

        call_command(
            "wget",
            ["https://win.rustup.rs", "-O", "rustup-init.exe"].as_ref(),
        )?;

        info!(format!(
            "下载完成，文件保存在: {}",
            path::Path::new(&current_dir)
                .join("rustup-init.exe")
                .display()
        ));
    }

    info!("安装 rustup 环境...");
    call_command(&rustup_path.display().to_string(), [].as_ref())?;

    Ok(())
}

#[cfg(unix)]
fn _install_rustup_unix() -> PyResult<()> {
    let current_dir = current_dir().expect("无法获取当前目录");

    info!("正在下载 rustup-init.exe...");
    call_command(
        "curl",
        [
            "--proto",
            "'=https'",
            "--tlsv1.2",
            "-sSf",
            "https://sh.rustup.rs",
            "|",
            "sh",
        ]
        .as_ref(),
    )?;

    info!(format!(
        "下载完成，文件保存在: {}",
        path::Path::new(&current_dir)
            .join("rustup-init.exe")
            .display()
    ));
}

fn _setup_rust_env() -> PyResult<()> {
    info!("设置 Rust 环境...");

    let versions = vec!["stable", "nightly"];
    let platform = std::env::consts::OS;
    let compiler = match platform {
        "windows" => "msvc",
        "linux" => "gnu",
        "macos" => "apple-darwin",
        other => {
            return Err(pyo3::exceptions::PyException::new_err(format!(
                "不支持的平台: {}",
                other
            )));
        }
    };

    for version in versions {
        call_command(
            "rustup",
            [
                "toolchain",
                "install",
                format!("{}-x86_64-pc-{}-{}", version, platform, compiler).as_str(),
            ]
            .as_ref(),
        )?;
    }

    call_command(
        "rustup",
        ["set", "default-host", "x86_64-pc-windows-msvc"].as_ref(),
    )?;

    println!("Rust 环境设置完成");

    Ok(())
}

#[pyfunction]
pub fn setup_rust_env() -> PyResult<()> {
    system::init_log();

    info!("检查 rustup 环境...");

    _install_rustup_windows()?;

    match which("rustup") {
        Ok(_) => {
            info!("Rustup 已经安装");
        }
        Err(_) => {
            info!("Rustup 未安装，正在安装...");

            #[cfg(windows)]
            {
                _install_rustup_windows()?;
            }

            #[cfg(unix)]
            {
                _install_rustup_unix()?;
            }
        }
    }

    _setup_rust_env()?;

    Ok(())
}
