use pyo3::prelude::*;

mod dev_env;
mod dirs;

/// 格式化输出两个数字之和为字符串
///
/// # Arguments
/// * a - 第一个数字
/// * b - 第二个数字
///
/// # Returns
/// 两个数字之和的字符串
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
    m.add_function(wrap_pyfunction!(dev_env::setup_rust_env, m)?)?;
    Ok(())
}
