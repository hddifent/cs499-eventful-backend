import cv2
from paddleocr import PaddleOCR
import numpy as np

from dataclasses import dataclass

from app.services.utils.booth_validator import try_format_booth_number, validate_booth_number

@dataclass
class _ContourObjectGroup:
    base: np.ndarray
    holes: list[np.ndarray]

def _percent256(p: float):
    return int(256 * p)

def _graypercent256(p: float, channels: int):
    return np.array([_percent256(p)] * channels)

def _num_between(n: float, lower: float, upper: float):
    return lower <= n <= upper

def _remove_outliers_zscore(data, threshold: float = 3):
    data = np.array(data)
    mean = np.mean(data)
    std = np.std(data)
    mask = np.abs(data - mean) <= threshold * std
    return data[mask]

def _get_1cnl_base_black(shape: tuple[int, int], dtype: np.dtype = np.dtype('uint8')):
    return np.zeros(shape, dtype)

def _get_leveled_hierarchy(h):
    levels_array = []
    current_level_queue = [0]
    next_level = []

    while True:
        visited = []
        while len(current_level_queue) > 0:
            h_index = current_level_queue.pop(0)
            visited.append(int(h_index))
            n, _, c, _ = h[0][h_index]
            if n != -1: current_level_queue.append(n)
            if c != -1: next_level.append(c)
        
        levels_array.append(visited)

        if len(next_level) == 0: break

        current_level_queue = next_level.copy()
        next_level = []
    
    return levels_array

def _get_contour_groups(c, h, bases: list[int]):
    list_contours_group = []

    for i in bases:
        contours_group = []
        indexes_group = []
        checking_index = h[0][i][2] # Opposite hierarchy level.

        while True:
            if checking_index == -1: break

            # We want the outline to be in the same hierarchy level.
            # If there's none, consider that it has no inner outline.
            inner_index = h[0][checking_index][2]
            if inner_index != -1:
                contours_group.append(c[inner_index])
                indexes_group.append(int(inner_index))
            
            checking_index = h[0][checking_index][0] # Next neighbor
        
        list_contours_group.append(_ContourObjectGroup(c[i], contours_group))
    
    return list_contours_group

def _get_contour_group_area(group: _ContourObjectGroup):
    area = cv2.contourArea(group.base)
    for c in group.holes:
        area -= cv2.contourArea(c)
    return area

def extract_image_contours(image: np.ndarray):
    # Image Metadata -----------------------------------------------------------------------------------
    image_pixels = image.shape[0] * image.shape[1]
    image_shape = (image.shape[0], image.shape[1])

    # Get BW mask --------------------------------------------------------------------------------------
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # TODO This might be the make or break
    lower_bound = _graypercent256(0.85, 1)
    upper_bound = _graypercent256(1, 1)
    bw_mask = cv2.inRange(grayscale_image, lower_bound, upper_bound)

    # Get contours -------------------------------------------------------------------------------------
    contours, hierarchy = cv2.findContours(bw_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    index_by_level = _get_leveled_hierarchy(hierarchy)

    # Filter white areas -------------------------------------------------------------------------------
    # Level 0-outer to 1-inner Pair (method=0)
    mask_0 = _get_1cnl_base_black(image_shape)
    cv2.drawContours(mask_0, contours, -1, (255,), -1)
    mask_0_selection = cv2.bitwise_and(mask_0, bw_mask)

    drawing_method = 0 if cv2.mean(mask_0_selection) != (0, 0, 0, 0) else 1

    contour_group = _get_contour_groups(contours, hierarchy, index_by_level[drawing_method])

    # Filter reasonable areas --------------------------------------------------------------------------
    raw_contour_group_area = [_get_contour_group_area(g) for g in contour_group]

    small_area_threshold = (1 / 10000.0) * image_pixels
    large_area_threshold = (1 /   100.0) * image_pixels
    contour_group_area = [a for a in raw_contour_group_area if _num_between(a, small_area_threshold, large_area_threshold)]
    contour_group_area = _remove_outliers_zscore(contour_group_area)

    area_threshold_lower = min(contour_group_area)
    area_threshold_upper = max(contour_group_area)
    contours_group_reasonable = [g for g in contour_group if _num_between(_get_contour_group_area(g), area_threshold_lower, area_threshold_upper)]
    contour_group_bases = [g.base for g in contours_group_reasonable]

    # Get "OCR-able" text area -------------------------------------------------------------------------
    boxes_image_bw = _get_1cnl_base_black(image_shape)
    cv2.fillPoly(boxes_image_bw, pts=contour_group_bases, color=(255,))
    selected_area_text = cv2.bitwise_and(boxes_image_bw, cv2.bitwise_not(bw_mask))
    selected_area_text = cv2.bitwise_not(selected_area_text)
    selected_area_text = cv2.merge([selected_area_text, selected_area_text, selected_area_text])

    return {
        "booth_contours": contour_group_bases, # For UI Rendering
        "booth_text_img": selected_area_text,  # For OCR Scanning
    }

def run_ocr(ocr_model: PaddleOCR, image: np.ndarray):
    result = ocr_model.predict(image)

    if not result or len(result) == 0:
        return {
            "texts": [],
            "scores": [],
            "boxes": []
        }

    data = result[0]

    return {
        "texts": data["rec_texts"],
        "scores": data["rec_scores"],
        "boxes": data["rec_boxes"]
    }

def match_contour_ocr_result(contours: list[np.ndarray], ocr_data: dict, booth_number_format: str = "$##"):
    matched = {}
    zipped_results = list(zip(ocr_data["texts"], ocr_data["scores"], ocr_data["boxes"]))

    for (text, score, box) in zipped_results:
        if score < 0.7: continue

        formatted = try_format_booth_number(text, booth_number_format)
        if not validate_booth_number(formatted, booth_number_format):
            continue

        x1, y1, x2, y2 = box
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        center = (cx, cy)

        for contour in contours:
            inside = cv2.pointPolygonTest(contour, center, False)
            if inside >= 0:
                x, y, w, h = cv2.boundingRect(contour)
                matched[formatted] = {
                    "bounding_box": ((x, y), (x + w, y + h))
                }
                break

    return matched