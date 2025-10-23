use pyo3::{PyResult, pyfunction};

#[pyfunction]
pub fn grep(pattern: &str, path: &str) -> PyResult<String> {
    println!("Searching for {} in {}", pattern, path);

    if !std::path::Path::new(path).exists() {
        return Err(pyo3::exceptions::PyFileNotFoundError::new_err(format!(
            "{} 文件不存在",
            path
        )));
    }

    let contents = std::fs::read_to_string(path)?;
    let mut match_contents = String::new();
    for line in contents.lines() {
        if line.contains(pattern) {
            match_contents.push_str(line);
        }
    }

    return Ok(match_contents);
}
