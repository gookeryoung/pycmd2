use pyo3::{PyResult, pyfunction};
use std::{fs, path};

#[pyfunction]
pub fn grep(pattern: &str, path: &str) -> PyResult<String> {
    let filepath = path::Path::new(path);

    if !filepath.exists() {
        return Err(pyo3::exceptions::PyFileNotFoundError::new_err(format!(
            "{} 文件不存在",
            path
        )));
    }

    let mut match_contents = String::new();
    if filepath.is_file() {
        // 使用 fs::read 并手动处理 UTF-8 转换，忽略无效编码的文件
        match fs::read_to_string(path) {
            Ok(contents) => {
                for line in contents.lines() {
                    if line.contains(pattern) {
                        match_contents.push_str(line);
                        match_contents.push('\n');
                    }
                }
            }
            Err(_) => {
                // 如果无法读取为UTF-8，则跳过该文件但不中断操作
                eprintln!("警告：无法读取文件 {} 作为UTF-8文本", path);
            }
        }
    } else if filepath.is_dir() {
        for entry in fs::read_dir(path)? {
            let path = entry?.path();
            if path.is_file() {
                println!("在文件中查找匹配: {}", path.display());
                // 同样处理目录中的每个文件
                match fs::read_to_string(&path) {
                    Ok(contents) => {
                        for line in contents.lines() {
                            if line.contains(pattern) {
                                match_contents.push_str(line);
                                match_contents.push('\n');
                            }
                        }
                    }
                    Err(_) => {
                        // 如果无法读取为UTF-8，则跳过该文件但不中断操作
                        eprintln!("警告：无法读取文件 {:?} 作为UTF-8文本", path);
                    }
                }
            }
        }
    } else {
        return Err(pyo3::exceptions::PyValueError::new_err(format!(
            "{} 不是一个文件或目录",
            path
        )));
    }

    Ok(match_contents)
}
