use pyo3::prelude::*;

mod dirs;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn show_version() -> PyResult<String> {
    Ok(format!("pycmd2 version: {}", env!("CARGO_PKG_VERSION")))
}

/// A Python module implemented in Rust.
#[pymodule]
fn _pycmd2(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(show_version, m)?)?;
    m.add_function(wrap_pyfunction!(dirs::list_dirs, m)?)?;
    Ok(())
}
