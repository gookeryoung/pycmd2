use pyo3::prelude::*;

mod dirs;
mod environ;
mod system;

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
    let y = {
        let x = 3;
        x + 1
    };
    Ok(format!(
        "y={}\nsum={}, add={}",
        y,
        (a + b).to_string(),
        add()
    ))
}

#[pyfunction]
fn version_info() -> PyResult<String> {
    Ok(format!("_pycmd2 v{}", env!("CARGO_PKG_VERSION")))
}

#[pyfunction]
fn add() -> String {
    let x = 3;
    let y = x;
    let mut s = String::from("hello");
    s.push_str("test");
    println!("s = {}", s);
    format!("{} + {} = {}", x, y, x + y)
}

/// A Python module implemented in Rust.
#[pymodule]
fn _pycmd2(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(version_info, m)?)?;

    // dirs
    m.add_function(wrap_pyfunction!(dirs::list_entries, m)?)?;
    m.add_function(wrap_pyfunction!(dirs::list_names, m)?)?;

    // demos
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(environ::rust::setup_rust_env, m)?)?;

    Ok(())
}
