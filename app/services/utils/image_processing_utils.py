import cv2
import numpy as np
from paddleocr import PaddleOCR

from app.services.utils.booth_validator import try_format_booth_number, validate_booth_number


def _percent256(p: float):
    return int(256 * p)


def _graypercent256(p: float, channels: int):
    return np.array([_percent256(p)] * channels)


def extract_image_bw(image: np.ndarray):
    # Get BW mask --------------------------------------------------------------------------------------
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    lower_bound = _graypercent256(0.85, 1)
    upper_bound = _graypercent256(1, 1)
    bw_mask = cv2.inRange(grayscale_image, lower_bound, upper_bound)

    return cv2.merge([bw_mask, bw_mask, bw_mask])


def run_ocr(ocr_model: PaddleOCR, image: np.ndarray):
    result = ocr_model.predict(image)

    if not result or len(result) == 0:
        return {"texts": [], "scores": [], "boxes": []}

    data = result[0]

    return {"texts": data["rec_texts"], "scores": data["rec_scores"], "boxes": data["rec_boxes"]}


def match_contour_ocr_result(ocr_data: dict, booth_number_format: str = "$##"):
    matched = {}
    zipped_results = list(zip(ocr_data["texts"], ocr_data["scores"], ocr_data["boxes"]))

    for text, score, box in zipped_results:
        if score < 0.7:
            continue

        formatted = try_format_booth_number(text, booth_number_format)
        if not validate_booth_number(formatted, booth_number_format):
            continue

        x1, y1, x2, y2 = box
        scaling = 1.1

        dw, dh = (x2 - x1) * (scaling - 1) / 2, (y2 - y1) * (scaling - 1) / 2

        matched[formatted] = {
            "bounding_box": (
                (int(x1 - dw), int(y1 - dh)),
                (int(x2 + dw), int(y2 + dh)),
            )
        }

    return matched
