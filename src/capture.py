from typing import Tuple, Optional

import numpy as np
from mss import mss
from PIL import Image


def grab_fullscreen(monitor_index: int = 1) -> np.ndarray:
    """
    Capture a full-screen screenshot as a NumPy array in BGR order compatible with OpenCV.

    On Windows with mss, monitor indexes usually start at 1. Index 1 is the primary display.
    Returns an array shaped (H, W, 3), dtype=uint8.
    """
    with mss() as sct:
        monitor = sct.monitors[monitor_index]
        img = sct.grab(monitor)
        # mss returns BGRA
        arr = np.asarray(img, dtype=np.uint8)
        # Drop alpha channel -> BGR
        bgr = arr[:, :, :3]
        return bgr.copy()


def crop_region(image_bgr: np.ndarray, region_xywh: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Crop a rectangular region from a BGR image.

    region_xywh: (x, y, width, height)
    Returns a new array view copy of the region in BGR order.
    """
    x, y, w, h = region_xywh
    x2, y2 = x + w, y + h
    x = max(0, x)
    y = max(0, y)
    x2 = min(image_bgr.shape[1], x2)
    y2 = min(image_bgr.shape[0], y2)
    if x >= x2 or y >= y2:
        return image_bgr[0:0, 0:0, :]
    return image_bgr[y:y2, x:x2, :].copy()


def grab_region(region_xywh: Tuple[int, int, int, int], monitor_index: int = 1) -> np.ndarray:
    """
    Convenience method: capture full screen then crop the region.
    """
    screen = grab_fullscreen(monitor_index=monitor_index)
    return crop_region(screen, region_xywh)


