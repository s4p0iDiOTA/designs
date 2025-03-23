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
   
    # Page number
    if config.page_opt_page_num_show:
        for _page_num in range(pdf_document.page_count):
            page = pdf_document[_page_num]
            x1, y1, x2, y2 = page.rect
            num_pgs = pdf_document.page_count
            text= f"  Page: {_page_num + 1} of  {num_pgs} "
            if config.page_opt_page_num_pg_num_pos == "bottom_center":
                x_pos= (x2-len(text)*4)/2
            elif config.page_opt_page_num_pg_num_pos == "bottom_right":
                x_pos= (x2 - 1.5* len(text)*4)                   
            fontname= config.page_opt_page_num_font
            fontsize= config.page_opt_page_num_font_size
            color= config.page_opt_page_num_color
            y_pos= y2 - config.page_opt_page_margins_bottom *72   
            rect=fitz.Rect(x_pos, y_pos-fontsize, x_pos+len(text)*4, y_pos+16)
            page.draw_rect(rect, color=(1,1,1), fill=(1,1,1))             
            page.insert_text((x_pos,y_pos), text, fontname= fontname, fontsize= fontsize, color= color)    

    return 

