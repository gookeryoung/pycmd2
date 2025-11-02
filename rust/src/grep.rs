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
        let contents = fs::read_to_string(path)?;
        for line in contents.lines() {
            if line.contains(pattern) {
                match_contents.push_str(line);
            }
        }
    } else if filepath.is_dir() {
        for entry in fs::read_dir(path)? {
            let path = entry?.path();
            if path.is_file() {
                println!("Search in file: {}", path.display());
                let contents = fs::read_to_string(path)?;
                for line in contents.lines() {
                    if line.contains(pattern) {
                        match_contents.push_str(line);
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
