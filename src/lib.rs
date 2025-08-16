use fast_blurhash::compute_dct;
use fast_blurhash::convert::Rgb;
use fast_blurhash::decode as _fast_blurhash_decode;

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;

use std::panic::{catch_unwind, AssertUnwindSafe};

const MIN_COMPONENTS: usize = 1;
const MAX_COMPONENTS: usize = 9;

type Rgba = [u8; 4];

fn _run_with_py_errors<T, F>(operation: F, context: &'static str) -> PyResult<T>
where
    F: FnOnce() -> PyResult<T>,
{
    let result = catch_unwind(AssertUnwindSafe(operation));

    match result {
        Ok(Ok(value)) => Ok(value),
        Ok(Err(e)) => Err(e),
        Err(panic) => {
            let message = panic
                .downcast_ref::<String>()
                .map(|s| s.as_str())
                .or_else(|| panic.downcast_ref::<&str>().copied())
                .unwrap_or(context);
            Err(PyRuntimeError::new_err(message.to_string()))
        }
    }
}

fn _to_chunks<T, const N: usize>(slice: &[T]) -> Option<&[[T; N]]> {
    let (chunks, remainder) = slice.as_chunks::<N>();
    if remainder.is_empty() {
        Some(chunks)
    } else {
        None
    }
}

fn _check_dimensions(width: usize, height: usize) -> PyResult<()> {
    if width == 0 || height == 0 {
        return Err(PyValueError::new_err(
            "width and height must be greater than 0",
        ));
    }
    Ok(())
}

fn _check_components(x_components: usize, y_components: usize) -> PyResult<()> {
    if x_components < MIN_COMPONENTS
        || x_components > MAX_COMPONENTS
        || y_components < MIN_COMPONENTS
        || y_components > MAX_COMPONENTS
    {
        return Err(PyValueError::new_err(
            "x_components and y_components must be in the range [1, 9]",
        ));
    }
    Ok(())
}

fn _check_punch(punch: f32) -> PyResult<()> {
    if punch < 1.0 {
        return Err(PyValueError::new_err("punch must be greater than 1"));
    }
    Ok(())
}

fn encode_rgb(
    pixels: &[u8],
    x_components: usize,
    y_components: usize,
    width: usize,
    height: usize,
) -> PyResult<String> {
    _check_dimensions(width, height)?;
    _check_components(x_components, y_components)?;
    let rgb = _to_chunks::<u8, 3>(pixels).ok_or(PyValueError::new_err(
        "pixels length does not match width * height",
    ))?;

    if rgb.len() != (width * height) {
        return Err(PyValueError::new_err(
            "pixels length does not match width * height",
        ));
    }
    let dct = compute_dct::<Rgb>(rgb, width, height, x_components, y_components);
    Ok(dct.into_blurhash())
}

fn encode_rgba(
    pixels: &[u8],
    x_components: usize,
    y_components: usize,
    width: usize,
    height: usize,
) -> PyResult<String> {
    _check_dimensions(width, height)?;
    _check_components(x_components, y_components)?;
    let rgba = _to_chunks::<u8, 4>(pixels).ok_or(PyValueError::new_err(
        "pixels length does not match width * height",
    ))?;
    if rgba.len() != (width * height) {
        return Err(PyValueError::new_err(
            "pixels length does not match width * height",
        ));
    }
    let dct = compute_dct::<Rgba>(rgba, width, height, x_components, y_components);
    Ok(dct.into_blurhash())
}

#[pyfunction]
fn encode(
    pixels: &[u8],
    x_components: usize,
    y_components: usize,
    width: usize,
    height: usize,
    space: u8,
) -> PyResult<String> {
    match space {
        3 => _run_with_py_errors(
            || encode_rgb(pixels, x_components, y_components, width, height),
            "Error occurred during blurhash encoding",
        ),
        4 => _run_with_py_errors(
            || encode_rgba(pixels, x_components, y_components, width, height),
            "Error occurred during blurhash encoding",
        ),
        _ => Err(PyValueError::new_err("space must be 3 (RGB) or 4 (RGBA)")),
    }
}

#[pyfunction]
fn decode(blurhash: &str, width: usize, height: usize, punch: f32) -> PyResult<Vec<u8>> {
    _run_with_py_errors(
        || -> PyResult<Vec<u8>> {
            _check_punch(punch)?;
            let dct = _fast_blurhash_decode(blurhash, punch)
                .or_else(|e| Err(PyValueError::new_err(e.to_string())))?;

            let pixels = dct
                .to_rgb8(width, height)
                .into_iter()
                .flatten()
                .collect::<Vec<_>>();
            Ok(pixels)
        },
        "Error occurred during blurhash decoding",
    )
}

#[pymodule]
fn _fast_blurhash(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encode, m)?)?;
    m.add_function(wrap_pyfunction!(decode, m)?)?;
    Ok(())
}
