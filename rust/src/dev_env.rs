use pyo3::prelude::*;
use std::io::{BufRead, BufReader};
use std::process::{Command, Stdio};

fn call_command_realtime(command: &str, args: &[&str]) -> PyResult<()> {
    let command_str = format!("{} {}", command, args.join(" "));
    println!("正在执行命令: {}", command_str);

    let mut child = Command::new(command)
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| {
            eprintln!("执行命令`{}`时出错: {}", command_str, e);
            pyo3::exceptions::PyException::new_err("Failed to execute command")
        })?;

    // 实时输出 stdout
    if let Some(stdout) = child.stdout.take() {
        let reader = BufReader::new(stdout);
        for line in reader.lines() {
            match line {
                Ok(line) => println!("{}", line),
                Err(e) => eprintln!("读取 stdout 时出错: {}", e),
            }
        }
    }

    // 实时输出 stderr
    if let Some(stderr) = child.stderr.take() {
        let reader = BufReader::new(stderr);
        for line in reader.lines() {
            match line {
                Ok(line) => eprintln!("{}", line),
                Err(e) => eprintln!("读取 stderr 时出错: {}", e),
            }
        }
    }

    // 等待子进程结束
    let status = child.wait().map_err(|e| {
        eprintln!("等待子进程结束时出错: {}", e);
        pyo3::exceptions::PyException::new_err("Failed to wait for child process")
    })?;

    if !status.success() {
        return Err(pyo3::exceptions::PyException::new_err(
            "Failed to install toolchain",
        ));
    }

    println!("命令`{}`执行成功", command_str);
    Ok(())
}

#[pyfunction]
pub fn setup_rust_env() -> PyResult<()> {
    println!("正在设置 Rust 环境...");

    call_command_realtime(
        "rustup",
        ["toolchain", "install", "stable-x86_64-pc-windows-msvc"].as_ref(),
    )?;

    call_command_realtime(
        "rustup",
        ["set", "default-host", "x86_64-pc-windows-msvc"].as_ref(),
    )?;

    println!("Rust 环境设置完成");
    Ok(())
}
