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
/// from pycmd2._pycmd2 import list_entries
///
/// list_entries("C:\\")
/// ```
///
#[pyfunction]
pub fn list_entries(path: &str) -> PyResult<Vec<String>> {
    let paths = std::fs::read_dir(path)?;
    let mut dirs = Vec::new();

    for path in paths {
        let dir_entry = path?;
        dirs.push(dir_entry.path().display().to_string());
    }

    Ok(dirs)
}

/// 列出指定路径下的所有目录名称
///
/// # Arguments
/// * path - 目录路径
///
/// # Returns
/// 仅包含目录名称的字符串列表
///
/// # Examples
/// ```python
/// from pycmd2._pycmd2 import list_names
///
/// list_names("C:\\")
/// ```
#[pyfunction]
pub fn list_names(path: &str) -> PyResult<Vec<String>> {
    let paths = std::fs::read_dir(path)?;
    let mut names = Vec::new();

    for path in paths {
        let dir_entry = path?;
        names.push(dir_entry.file_name().to_string_lossy().to_string());
    }

    Ok(names)
}
