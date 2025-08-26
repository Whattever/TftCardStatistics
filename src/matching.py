from typing import Tuple, Optional, Dict, Any, List

import cv2
import numpy as np


def load_template_bgr(path: str) -> np.ndarray:
    """
    Load an image from disk as BGR (for OpenCV).
    Raises FileNotFoundError if path is invalid or image can't be read.
    """
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read template image: {path}")
    return img


def match_template(
    scene_bgr: np.ndarray,
    template_bgr: np.ndarray,
    method: int = cv2.TM_CCOEFF_NORMED,
    threshold: float = 0.9,
) -> Optional[Dict[str, Any]]:
    """
    Perform template matching and return best match if above threshold.

    Returns None if no match is found.
    Otherwise returns dict with keys:
      - score: float
      - top_left: (x, y)
      - bottom_right: (x2, y2)
      - center: (cx, cy)
    """
    if scene_bgr.size == 0 or template_bgr.size == 0:
        return None

    scene_gray = cv2.cvtColor(scene_bgr, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(scene_gray, template_gray, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # For normalized methods where higher is better
    top_left = max_loc
    score = max_val

    h, w = template_gray.shape[:2]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    center = (top_left[0] + w // 2, top_left[1] + h // 2)

    if score < threshold:
        return None

    return {
        "score": float(score),
        "top_left": top_left,
        "bottom_right": bottom_right,
        "center": center,
    }


def draw_match_bbox(image_bgr: np.ndarray, top_left: Tuple[int, int], bottom_right: Tuple[int, int]) -> np.ndarray:
    """
    Draw a rectangle on a copy of image and return it.
    """
    vis = image_bgr.copy()
    cv2.rectangle(vis, top_left, bottom_right, (0, 255, 0), 2)
    return vis


def load_templates_from_dir(template_dir: str, valid_exts: Optional[Tuple[str, ...]] = None) -> List[Tuple[str, np.ndarray]]:
    """
    Load all templates from a directory.

    Returns list of (filename, image_bgr). Skips files that cannot be read.
    """
    import os

    if valid_exts is None:
        valid_exts = (".png", ".jpg", ".jpeg", ".bmp", ".webp")

    if not os.path.isdir(template_dir):
        raise FileNotFoundError(f"Template directory does not exist: {template_dir}")

    loaded: List[Tuple[str, np.ndarray]] = []
    for name in sorted(os.listdir(template_dir)):
        path = os.path.join(template_dir, name)
        if not os.path.isfile(path):
            continue
        _, ext = os.path.splitext(name.lower())
        if ext not in valid_exts:
            continue
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None or img.size == 0:
            continue
        loaded.append((name, img))
    return loaded


