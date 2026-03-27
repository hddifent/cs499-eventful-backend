import numpy as np
from paddleocr import PaddleOCR

from app.services.utils.image_processing_utils import (
    extract_image_bw,
    match_contour_ocr_result,
    run_ocr,
)

_ocr_model = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="en",
    det_db_unclip_ratio=1.2,
    det_db_box_thresh=0.6,
)


def get_booths_from_map(image: np.ndarray) -> dict:
    extracted_booth_data = extract_image_bw(image)
    ocr_data = run_ocr(_ocr_model, extracted_booth_data)
    booths = match_contour_ocr_result(ocr_data)

    return booths
