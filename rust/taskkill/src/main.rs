use std::env;
use std::process::Command;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        eprintln!("用法: taskk <进程名>");
        std::process::exit(1);
    }

    let process_name = &args[1];

    #[cfg(windows)]
    {
        // Windows 平台使用 taskkill 命令
        match kill_process_windows(process_name) {
            Ok(_) => println!("成功终止匹配 '{}' 的进程", process_name),
            Err(e) => {
                eprintln!("终止进程时出错: {}", e);
                std::process::exit(1);
            }
        }
    }

    #[cfg(not(windows))]
    {
        // Unix-like 平台使用 kill 和 pgrep 命令
        match kill_process_unix(process_name) {
            Ok(count) => println!("成功终止 {} 个匹配 '{}' 的进程", count, process_name),
            Err(e) => {
                eprintln!("终止进程时出错: {}", e);
                std::process::exit(1);
            }
        }
    }
}

#[cfg(windows)]
fn kill_process_windows(process_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    let output = Command::new("taskkill")
        .args(&["/f", "/im", process_name])
        .output()?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        if stderr.contains("INFO") {
            // INFO级别的消息，表示没有找到进程，这不是错误
            println!("未找到匹配 '{}' 的进程", process_name);
            return Ok(());
        }
        return Err(format!("taskkill 命令失败: {}", stderr).into());
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    print!("执行结果: {}", stdout);
    Ok(())
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
