use colored::*;
use pyo3::prelude::*;
use std::io::{BufRead, BufReader};
use std::process::{Command, Stdio};

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
/// call_command_realtime("rustup", ["toolchain", "install", "stable-x86_64-pc-windows-msvc"])
/// ```
pub fn call_command_realtime(command: &str, args: &[&str]) -> PyResult<()> {
    let command_str = format!("{} {}", command, args.join(" "));
    println!("正在执行命令: `{}`", command_str.green());

    let mut child = Command::new(command)
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| {
            eprintln!(
                "执行命令 `{}` 时出错: {}",
                command_str.red(),
                e.to_string().red()
            );
            pyo3::exceptions::PyException::new_err("Failed to execute command")
        })?;

    // 实时输出 stdout
    if let Some(stdout) = child.stdout.take() {
        let reader = BufReader::new(stdout);
        for line in reader.lines() {
            match line {
                Ok(line) => println!("{}", line.blue()),
                Err(e) => eprintln!("读取 stdout 时出错: {}", e.to_string().red()),
            }
        }
    }

    // 实时输出 stderr
    if let Some(stderr) = child.stderr.take() {
        let reader = BufReader::new(stderr);
        for line in reader.lines() {
            match line {
                Ok(line) => eprintln!("{}", line.yellow()),
                Err(e) => eprintln!("读取 stderr 时出错: {}", e.to_string().red()),
            }
        }
    }

    // 等待子进程结束
    let status = child.wait().map_err(|e| {
        eprintln!("等待子进程结束时出错: {}", e.to_string().red());
        pyo3::exceptions::PyException::new_err("Failed to wait for child process")
    })?;

    if !status.success() {
        return Err(pyo3::exceptions::PyException::new_err(
            "Failed to install toolchain",
        ));
    }

    println!("命令`{}`执行成功", command_str.green());
    Ok(())
}

#[test]
fn test_call_command_realtime() {
    assert_eq!(
        call_command_realtime(
            "rustup",
            ["toolchain", "install", "stable-x86_64-pc-windows-msvc"].as_ref(),
        )
        .unwrap(),
        ()
    )
}
