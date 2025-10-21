use colored::*;
use pyo3::prelude::*;
use std::{
    io::BufRead,
    process::{Command, Stdio},
};

use tklog::{error, info};

/// 调用命令并实时输出结果
///
/// # Arguments
/// * command - 命令
/// * args - 参数
///
/// # Returns
/// None
///
/// # Examples
/// ```rust
/// call_command("rustup", ["toolchain", "install", "stable-x86_64-pc-windows-msvc"])
/// ```
pub fn call_command(command: &str, args: &[&str]) -> PyResult<()> {
    let command_str = format!("{} {}", command, args.join(" "));
    info!(format!("正在执行命令 `{}`", command_str.green()));

    let mut child = Command::new(command)
        .args(args)
        .stdin(Stdio::inherit()) // 继承父进程的stdin，允许用户输入
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| {
            error!(format!(
                "执行命令 `{}` 时出错: {}",
                command_str.red(),
                e.to_string().red()
            ));

            match e.kind() {
                // 命令未找到
                std::io::ErrorKind::NotFound => {
                    pyo3::exceptions::PyException::new_err(format!("命令未找到: {}", command))
                }

                // 权限被拒绝
                std::io::ErrorKind::PermissionDenied => pyo3::exceptions::PyException::new_err(
                    format!("权限被拒绝，无法执行命令: {}", command_str.red().bold()),
                ),

                _ => {
                    // Windows 错误代码 193 表示不是有效的 Win32 应用程序
                    if let Some(193) = e.raw_os_error() {
                        if std::path::Path::new(command).exists() {
                            error!(format!(
                                "文件存在，但不是有效的 Win32 应用程序: {}, 尝试删除...",
                                command_str.red().bold()
                            ));

                            // 尝试删除可能损坏的文件
                            match std::fs::remove_file(command) {
                                Ok(()) => info!("文件删除成功。"),
                                Err(e) => match e.kind() {
                                    std::io::ErrorKind::NotFound => {
                                        error!(format!("错误：文件 '{}' 未找到。", command))
                                    }
                                    std::io::ErrorKind::PermissionDenied => {
                                        error!(format!("错误：没有权限删除 '{}'。", command))
                                    }
                                    _ => error!(format!("删除文件时发生未知错误: {}", e)),
                                },
                            }
                        }

                        pyo3::exceptions::PyException::new_err(format!(
                            "不是有效的 Win32 应用程序: {}",
                            command_str
                        ))
                    } else {
                        // 其他错误
                        pyo3::exceptions::PyException::new_err(format!("执行命令时未知错误: {}", e))
                    }
                }
            }
        })?;

    // 实时输出 stdout
    if let Some(stdout) = child.stdout.take() {
        let reader = std::io::BufReader::new(stdout);
        for line in reader.lines() {
            match line {
                Ok(line) => info!(line.blue()),
                Err(e) => error!(format!("读取 stdout 时出错: {}", e.to_string().red())),
            }
        }
    }

    // 实时输出 stderr
    if let Some(stderr) = child.stderr.take() {
        let reader = std::io::BufReader::new(stderr);
        for line in reader.lines() {
            match line {
                Ok(line) => info!(line),
                Err(e) => error!(format!("读取 stderr 时出错: {}", e.to_string().red())),
            }
        }
    }

    // 等待子进程结束
    let status = child.wait().map_err(|e| {
        error!(format!("等待子进程结束时出错: {}", e.to_string().red()));
        pyo3::exceptions::PyException::new_err("Failed to wait for child process")
    })?;

    if !status.success() {
        return Err(pyo3::exceptions::PyException::new_err(
            "Failed to install toolchain",
        ));
    }

    info!(format!("命令`{}`执行成功", command_str.green().bold()));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_call_command() {
        call_command(
            "rustup",
            ["toolchain", "install", "stable-x86_64-pc-windows-msvc"].as_ref(),
        )
        .unwrap();
    }

    #[test]
    fn test_call_invalid_command() {
        let result = call_command("invalid_command", [].as_ref());
        assert!(result.is_err());
    }
}
