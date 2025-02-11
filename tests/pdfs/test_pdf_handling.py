import os
import pytest
import fitz  # PyMuPDF
from data.models import Series, SeriesContainer, ContainerRow, StampContainer, Stamp
from pdfs.pdf_handling import print_to_pdf

@pytest.fixture
def series_container():
    series_data = {
        "name": "Test Series",
        "year": 2025,
        "stamps": [
            {"height": 2.0, "width": 1.0},
            {"height": 2.0, "width": 1.5},
            {"height": 2.0, "width": 2.0},
            {"height": 2.0, "width": 2.5},
            {"height": 2.0, "width": 3.0}
        ]
    }
    series = Series(series_data)
    container = SeriesContainer()
    row = ContainerRow()
    for stamp in series.stamps:
        rect = [0.0, 0.0, stamp.width, stamp.height]
        row.stamp_containers.append(StampContainer(stamp=stamp, rect=rect))
    container.rows.append(row)
    container.width = max(stamp.width for stamp in series.stamps)
    container.height = sum(stamp.height for stamp in series.stamps)
    return container

def test_print_to_pdf(series_container, tmp_path):
    output_pdf_path = tmp_path / "output.pdf"
    print_to_pdf(series_container, str(output_pdf_path))
    
    assert os.path.exists(output_pdf_path)
    
    # Open the generated PDF and check its content
    pdf_document = fitz.open(str(output_pdf_path))
    assert pdf_document.page_count == 1
    page = pdf_document[0]
    
    # Check if the red rectangle is drawn
    red_rects = [drawing for drawing in page.get_drawings() if drawing['color'] == (1, 0, 0)]
    assert len(red_rects) > 0
    
    # Check if the blue rectangles are drawn
    blue_rects = [drawing for drawing in page.get_drawings() if drawing['color'] == (0, 0, 1)]
    assert len(blue_rects) == len(series_container.rows[0].stamp_containers)
    
    pdf_document.close()