import numpy as np
from paddleocr import PaddleOCR

from app.services.utils.image_processing_utils import (
    extract_image_contours,
    match_contour_ocr_result,
    run_ocr,
)

_ocr_model = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="en",
)


def get_booths_from_map(image: np.ndarray) -> dict:
    extracted_booth_data = extract_image_contours(image)
    ocr_data = run_ocr(_ocr_model, extracted_booth_data["booth_text_img"])
    booths = match_contour_ocr_result(extracted_booth_data["booth_contours"], ocr_data)

    return booths
