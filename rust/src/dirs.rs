use pyo3::pyfunction;

/// Lists all directories in the given path.
/// # Arguments
/// * `path` - A string slice that holds the path to list directories from.
///
/// # Returns
/// A vector of strings containing the names of all directories in the given path.
#[pyfunction]
pub fn list_dirs(path: &str) -> Result<Vec<String>, std::io::Error> {
    let paths = std::fs::read_dir(path)?;
    let mut dirs = Vec::new();

    for path in paths {
        let dir_entry = path?;
        dirs.push(dir_entry.path().display().to_string());
    }

    Ok(dirs)
}
