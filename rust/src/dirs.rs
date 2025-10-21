use pyo3::{PyResult, pyfunction};

/// 列出指定路径下的所有目录
///
/// # Arguments
/// * path - 目录路径
///
/// # Returns
/// 包含目录路径的字符串列表
///
/// # Examples
/// ```python
/// from pycmd2._pycmd2 import list_dirs
///
/// list_dirs("C:\\")
/// ```
///
#[pyfunction]
pub fn list_dirs(path: &str) -> PyResult<Vec<String>> {
    let paths = std::fs::read_dir(path)?;
    let mut dirs = Vec::new();

    for path in paths {
        let dir_entry = path?;
        dirs.push(dir_entry.path().display().to_string());
    }

    Ok(dirs)
}
