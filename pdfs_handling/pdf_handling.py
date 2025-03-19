import fitz  # PyMuPDF
import os

from data.common import in_to_points
from data.models import AlbumPages
from data.objects.containers import Page


def create_pdf_from_pages(pages: list[Page]) -> fitz.Document:
    pdf_document = fitz.open()
    
    for page in pages:
        pdf_page = pdf_document.new_page(width=in_to_points(page.width), height=in_to_points(page.height)) 
        page.border.render(pdf_page=pdf_page, origin=(0.0, 0.0))
        page.working_area.render(pdf_page=pdf_page, origin=(0.0, 0.0), grid=True) 
           
    return pdf_document
        
def album_pages_design(pdf_document, config) -> None:  #___ TMP  
   
    doc= fitz.open(pdf_document)

    
    # Add Page number
    for _page_num in range(doc.page_count):
        page = doc[_page_num]
        x1, y1, x2, y2 = page.rect
        num_pgs = doc.page_count
        pg_text= f"_ Pg: {_page_num+1} / {num_pgs} _"
        x_pos= (x2-x1-len(pg_text))/2                     # pos. al medio de la pagina
        point= fitz.Point(x_pos,y1-18)
        page.insert_text(point, pg_text, fontsize=8, color=(0,0,1))    

    return doc


""" # Add Series name
        series_name = content_options["output_options"]["file_name"]
        x_pos= (x1- len(series_name))/2
        point= fitz.Point(x_pos,y1-30)
        page.insert_text(point, series_name, fontsize=10, color=(0,0,1))
        """

"""  
______________________________________________________________________________


        * (1, 1, 0): Amarillo
        * (1, 0, 1): Magenta
        * (0, 1, 1): Cian


    Además del modelo RGB, PyMuPDF soporta otros modelos de color: como CMYK y Gray.

"""