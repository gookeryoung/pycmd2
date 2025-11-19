use pyo3::prelude::*;
use pyo3::{PyResult, pyfunction};
use std::{fs, path};

/// 表示单个匹配结果的结构体
#[pyclass]
#[derive(Debug, Clone)]
pub struct MatchResult {
    /// 文件路径
    #[pyo3(get)]
    pub file_path: String,
    /// 行号
    #[pyo3(get)]
    pub line_number: usize,
    /// 匹配的行内容
    #[pyo3(get)]
    pub line_content: String,
}

#[pymethods]
impl MatchResult {
    fn __repr__(&self) -> String {
        format!(
            "MatchResult(file_path='{}', line_number={}, line_content='{}')",
            self.file_path, self.line_number, self.line_content
        )
    }
}

/// Grep搜索结果列表
#[pyclass]
pub struct GrepResults {
    #[pyo3(get)]
    pub matches: Vec<MatchResult>,
}

#[pymethods]
impl GrepResults {
    fn __repr__(&self) -> String {
        format!(
            "GrepResults(matches=[{}])",
            self.matches
                .iter()
                .map(|m| format!("{:?}", m))
                .collect::<Vec<_>>()
                .join(", ")
        )
    }

    fn __str__(&self) -> String {
        self.matches
            .iter()
            .map(|m| format!("[{}]@{}:`{}`\n", m.file_path, m.line_number, m.line_content))
            .collect::<String>()
    }

    fn __len__(&self) -> usize {
        self.matches.len()
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<MatchResult> {
        if !slf.matches.is_empty() {
            Some(slf.matches.remove(0))
        } else {
            None
        }
    }
}

#[pyfunction]
pub fn grep(pattern: &str, path: &str) -> PyResult<GrepResults> {
    let filepath = path::Path::new(path);

    if !filepath.exists() {
        return Err(pyo3::exceptions::PyFileNotFoundError::new_err(format!(
            "{} 文件不存在",
            path
        )));
    }

    let mut results = GrepResults {
        matches: Vec::new(),
    };

    if filepath.is_file() {
        match fs::read_to_string(path) {
            Ok(contents) => {
                for (line_num, line) in contents.lines().enumerate() {
                    if line.contains(pattern) {
                        results.matches.push(MatchResult {
                            file_path: path.to_string(),
                            line_number: line_num + 1,
                            line_content: line.to_string(),
                        });
                    }
                }
            }
            Err(_) => {
                eprintln!("警告：无法读取文件 {} 作为UTF-8文本", path);
            }
        }
    } else if filepath.is_dir() {
        for entry in fs::read_dir(path)? {
            let path = entry?.path();
            if path.is_file() {
                let path_str = match path.to_str() {
                    Some(s) => s.to_string(),
                    None => continue,
                };

                match fs::read_to_string(&path) {
                    Ok(contents) => {
                        for (line_num, line) in contents.lines().enumerate() {
                            if line.contains(pattern) {
                                results.matches.push(MatchResult {
                                    file_path: path_str.clone(),
                                    line_number: line_num + 1,
                                    line_content: line.to_string(),
                                });
                            }
                        }
                    }
                    Err(_) => {
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

    Ok(results)
}
