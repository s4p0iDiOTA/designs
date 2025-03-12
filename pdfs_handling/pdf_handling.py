import fitz  # PyMuPDF
import os

from data.common import in_to_points
from data.models import AlbumPages
from data.objects.containers import Page, Grid


def create_pdf_from_pages(pages: list[Page]) -> fitz.Document:
    pdf_document = fitz.open()
    
    for page in pages:
        pdf_page = pdf_document.new_page(width=in_to_points(page.width), height=in_to_points(page.height)) 
        page.border.render(pdf_page=pdf_page, origin=(0.0, 0.0))
        page.working_area.render(pdf_page=pdf_page, origin=(0.0, 0.0))

        grid = Grid(width=8.5, height=11, relative_coordinates=(0, 0))
        grid.render(pdf_page, origin=(0, 0))  
           
    return pdf_document
        





    """

        # Add Page number
        num_pgs = pdf_document.page_count
        pg_text= f"_ Pg: {pg+1} / {num_pgs} _"
        x_pos= (x1- len(pg_text))/2             # pos. al medio de la pagina
        point= fitz.Point(x_pos,y1-18)
        pdf_page.insert_text(point, pg_text, fontsize=8, color=(0,0,1))    
______________________________________________________________________________


        * (1, 1, 0): Amarillo
        * (1, 0, 1): Magenta
        * (0, 1, 1): Cian


    Además del modelo RGB, PyMuPDF soporta otros modelos de color: como CMYK y Gray.

    """