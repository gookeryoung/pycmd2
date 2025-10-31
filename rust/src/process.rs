use pyo3::prelude::*;
use std::process::Command;

#[pyfunction]
pub fn kill_process(process_name: &str) -> PyResult<()> {
    #[cfg(windows)]
    {
        // Windows 平台使用 taskkill 命令
        match kill_process_windows(process_name) {
            Ok(_) => {
                println!("成功终止匹配 '{}' 的进程", process_name);
                Ok(())
            }
            Err(e) => {
                return Err(pyo3::exceptions::PyProcessLookupError::new_err(format!(
                    "无法终止进程: {}",
                    e
                )));
            }
        }
    }

    #[cfg(not(windows))]
    {
        // Unix-like 平台使用 kill 和 pgrep 命令
        match kill_process_unix(process_name) {
            Ok(count) => {
                println!("成功终止 {} 个匹配 '{}' 的进程", count, process_name);
                Ok(())
            }
            Err(e) => {
                return Err(pyo3::exceptions::PyProcessLookupError::new_err(format!(
                    "无法终止进程: {}",
                    e
                )));
            }
        }
    }
}

#[cfg(windows)]
fn kill_process_windows(process_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    let output = Command::new("taskkill")
        .args(&["/F", "/IM", format!("{}*", process_name).as_str()])
        .output()?;

    if !output.status.success() {
        // 尝试使用GBK编码解析stderr
        let stderr = decode_windows_output(&output.stderr);
        if stderr.contains("INFO") {
            // INFO级别的消息，表示没有找到进程，这不是错误
            println!("Process not found: '{}' ", process_name);
            return Ok(());
        }
        return Err(format!("taskkill command failed: {}", stderr).into());
    }

    // 使用正确的编码处理stdout
    let stdout = decode_windows_output(&output.stdout);
    println!("执行结果: {}", stdout);
    Ok(())
}

#[cfg(windows)]
fn decode_windows_output(bytes: &[u8]) -> String {
    // 尝试使用GBK编码解析（Windows中文系统常用编码）
    match encoding_rs::GBK.decode_without_bom_handling_and_without_replacement(bytes) {
        Some(s) => s.to_string(),
        None => {
            // 如果GBK解码失败，则回退到UTF-8并替换无效字符
            String::from_utf8_lossy(bytes).to_string()
        }
    }
}

#[cfg(not(windows))]
fn kill_process_unix(process_name: &str) -> Result<u32, Box<dyn std::error::Error>> {
    // 使用 pgrep 查找匹配的进程 ID
    let output = Command::new("pgrep").arg(process_name).output()?;

    if !output.status.success() {
        // pgrep 没有找到匹配的进程
        println!("未找到匹配 '{}' 的进程", process_name);
        return Ok(0);
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let mut count = 0;

    for line in stdout.lines() {
        if let Ok(pid) = line.trim().parse::<u32>() {
            // 使用 kill 命令终止进程
            let kill_output = Command::new("kill")
                .arg("-9")
                .arg(pid.to_string())
                .output()?;

            if kill_output.status.success() {
                println!("成功终止进程 PID: {}", pid);
                count += 1;
            } else {
                let stderr = String::from_utf8_lossy(&kill_output.stderr);
                eprintln!("无法终止进程 PID {}: {}", pid, stderr);
            }
        }
    }

    Ok(count)
}
