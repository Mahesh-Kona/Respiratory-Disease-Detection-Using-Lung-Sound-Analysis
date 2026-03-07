"""Minimal imghdr compatibility module for Python 3.13+.

Streamlit (and some other libraries) still import the standard-library
imghdr module, which was removed in newer Python versions.

This file provides a small subset of the original interface, just enough
for Streamlit's image handling: the ``what`` function.
"""

from __future__ import annotations

from typing import Optional, Union, BinaryIO


def _test_jpeg(h: bytes) -> Optional[str]:
    if h.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    return None


def _test_png(h: bytes) -> Optional[str]:
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    return None


def _test_gif(h: bytes) -> Optional[str]:
    if h.startswith(b"GIF87a") or h.startswith(b"GIF89a"):
        return "gif"
    return None


def _test_bmp(h: bytes) -> Optional[str]:
    if h.startswith(b"BM"):
        return "bmp"
    return None


_TESTS = (_test_jpeg, _test_png, _test_gif, _test_bmp)


def what(file: Union[str, BinaryIO], h: Optional[bytes] = None) -> Optional[str]:
    """Guess the type of an image.

    Parameters
    ----------
    file: str or binary file object
        Filename or an open file-like object.
    h: bytes, optional
        Optional header bytes. If not provided, the function will read
        up to 32 bytes from the file.
    """

    if h is None:
        close_after = False
        if hasattr(file, "read"):
            f = file  # type: ignore[assignment]
        else:
            f = open(file, "rb")  # type: ignore[arg-type]
            close_after = True
        try:
            h = f.read(32)
        finally:
            if close_after:
                f.close()

    for test in _TESTS:
        res = test(h)
        if res is not None:
            return res
    return None
