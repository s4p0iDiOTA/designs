import fitz  # PyMuPDF
import os

from data.common import in_to_points
from data.models import AlbumPages
from data.objects.containers import Page, SeriesContainer


def create_pdf_from_pages(pages: list[Page]) -> fitz.Document:
    pdf_document = fitz.open()
    
    for page in pages:
        pdf_page = pdf_document.new_page(width=in_to_points(page.width), height=in_to_points(page.height))
        
        page.border.render(pdf_page=pdf_page, origin=(0.0, 0.0))
        page.working_area.render(pdf_page=pdf_page, origin=(0.0, 0.0))
        
    return pdf_document
        

 
def conform_album_pages(pdf_document, content_options):

    album_pages = AlbumPages(None)

    # album_page limits:
    coor= album_pages.get_page_borders()
    x0, y0, x1, y1 = [ i*72 for i in coor.values()]

    border_style= album_pages.page_borders["style"]
    border_color= album_pages.page_borders["color"]

    for pg, pdf_page in enumerate(pdf_document):

        # Title... put the country as the title of the page (TMP) in the top of the page...to be defined the location, color, etc in settings.
        album_title = content_options["country"] 
        x_pos= (x1- len(album_title))/2
        point= fitz.Point(x_pos,y0+18)
        pdf_page.insert_text(point, album_title, fontsize=12, color=(0,0,1))

        # Page number
        num_pgs = pdf_document.page_count
        pg_text= f"_ Pg: {pg+1} / {num_pgs} _"
        x_pos= (x1- len(pg_text))/2                             # pos. al medio ..
        point= fitz.Point(x_pos,y1-18)
        pdf_page.insert_text(point, pg_text, fontsize=8, color=(0,0,1))    


        #____________TMP__________________cuadricular paper_____________________________
        sizes= album_pages.paper_sizes
        _x1_ = int(sizes["width"] * 72)
        _y1_ = int(sizes["height"] * 72)
        _x0_ = 0
        _y0_ = 0
        for _x0_ in range(0, _x1_, 72):
            p1 = fitz.Point(_x0_, 0)
            p2 = fitz.Point(_x0_, _y1_)
            pdf_page.draw_line(p1, p2, color=(.2, .2, .2), stroke_opacity=0.1, width=1)
        for _y0_ in range(0, _y1_, 72):
            p1 = fitz.Point(0, _y0_)
            p2 = fitz.Point(_x1_, _y0_)
            pdf_page.draw_line(p1, p2, color=(.2, .2, .2), stroke_opacity=0.1, width=1)
        #______________________________________________________________________________

        #____________TMP__________________cuadricular working_area_____________________________
        coor= album_pages.get_working_coordinates()
        _x0_, _y0_, _x1_, _y1_ = coor.values()
        _x0_ = int(_x0_*72)
        _y0_ = int(_y0_*72)
        _x1_ = int(_x1_*72)
        _y1_ = int(_y1_*72)
        rect= (_x0_,_y0_,_x1_,_y1_)
        pdf_page.draw_rect(rect, fill=(0, 0, .8), fill_opacity=0, color=(0, 1, 0), stroke_opacity=0.2, width=1)
        for _x0_ in range(_x0_, _x1_, 72): #vert
            p1 = fitz.Point(_x0_, _y0_)
            p2 = fitz.Point(_x0_, _y1_)
            pdf_page.draw_line(p1, p2, color=(0, 1, 0), stroke_opacity=0.2, width=1)
        _x0_, _y0_, _x1_, _y1_ = coor.values()
        _x0_ = int(_x0_*72)
        _y0_ = int(_y0_*72)
        _x1_ = int(_x1_*72)
        _y1_ = int(_y1_*72)
        for _y0_ in range(_y0_, _y1_, 72): # horiz
            p1 = fitz.Point(_x0_,_y0_)
            p2 = fitz.Point(_x1_,_y0_)
            pdf_page.draw_line(p1, p2, color=(0, 1, 0), stroke_opacity=0.2, width=1)
        #______________________________________________________________________________

    return



    """_______________________________________________________________________________

        * (0, 0, 0): Negro
        * (1, 0, 0): Rojo
        * (0, 1, 0): Verde
        * (0, 0, 1): Azul
        * (1, 1, 0): Amarillo
        * (1, 0, 1): Magenta
        * (0, 1, 1): Cian
        * (1, 1, 1): Blanco

    Además del modelo RGB, PyMuPDF también soporta otros modelos de color, como CMYK y Gray.. rev!
    """