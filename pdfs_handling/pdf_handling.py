import fitz  # PyMuPDF
from data.common import formato_pdf
from data.models import AlbumPages
import os

width, height = formato_pdf["customized"].values()  # define in album_page_layout. By default "customized"


# create a pdf document. Locates serial containers in the pdf pages.
def put_containers_boxes_in_pdf_pages(containers_box):
    # open a new pdf document for storing the stamp containers.
    pdf_document = fitz.open()
           
    # create a pdf_page object with the album_pages paper size. It is not added automatically to the document.
    album_page = AlbumPages(None) 
    #pdf_page=fitz.Page
    pdf_page = pdf_document.new_page(width=album_page.paper_sizes["width"] * 72, height=album_page.paper_sizes["height"] * 72)
  
    x_0 = x_1 = y_0 = y_1 = 0  # tmp.... resolver ajuste de coordenadas para ubicar el working page
    last_y_pos = 0

    for serials_containers in containers_box:
        # locate boxes in pages. In one page might be located one or more boxes
        for _index, serial_container in enumerate(serials_containers):      ???????????????????? cambiar 

            # to save position of containers in pages
            for j,(x, y, serial_container) in enumerate(serial_containers):
                x0, y0 = (x_0 + x) * 72, (y_0 + y) * 72
                x1, y1 = (x_1 + x + serial_container.width) * 72, (y_1 + y + serial_container.height) * 72
                container_rect = fitz.Rect(x0, y0, x1, y1)
                pdf_page.draw_rect(container_rect, fill=(.8, .8, .8), fill_opacity=0.1)  # limites del contenedor. temporal!!!!
                
                # to put stamps inside the containers:
                for row in serial_container.rows:
                    for stamp_container in row.stamp_containers:
                        x00, y00, x01, y01 = [coord * 72 for coord in stamp_container.rect]
                        stamp_rect = fitz.Rect(x00 + x0, y00 + y0, x01 + x0, y01 + y0)
                        pdf_page.draw_rect(stamp_rect, fill=(0, 0, .8), fill_opacity=0.1, color=(1, 0, 0), stroke_opacity=0.2, width=1)
                        # working_area.draw_rect(stamp_rect, color=(0, 0, 0), width=1)

                # at the end of the page, save it to the pdf_document and create another page if there is another box.
                if _index != len(serials_containers)-1 and not (y >= last_y_pos) : # (para excl last_pos=0)
                    #pdf_document.insert_page(-1, pdf_page)
                    pdf_page = pdf_document.new_page(width=album_page.paper_sizes["width"] * 72, height=album_page.paper_sizes["height"] * 72)          
                    _index += 1           
                last_y_pos = y  
    
    return pdf_document
 
def conform_album_pages(pdf_document, content_options):

 ##   pdf_file = fitz.open(pdf_document_path)
    num_pgs = pdf_document.page_count
   ## pdf_page = pdf_document[0]  # open the first page

    album_pages = AlbumPages(None)

    # album_page limits:
    coor= album_pages.get_page_borders()
    x0, y0, x1, y1 = [ i*72 for i in coor.values()]

    border_style= album_pages.page_borders["style"]
    border_color= album_pages.page_borders["color"]

    for pg, pdf_page in enumerate(pdf_document):

       # drawing page borders
        rect = fitz.Rect(x0, y0, x1, y1)
        pdf_page.draw_rect(rect, color=(0, 0, 0), width=1)  # resolver problema de border_color !!
        if border_style == "single_line":                        # single fine line
            pass
        if border_style == "double_line":                        # double fine lines
            rect = fitz.Rect(x0 + 4, y0 + 4, x1 - 4, y1 - 4)
            pdf_page.draw_rect(rect, border_color, width=1)
        if border_style == "fine_thick_line":                    # double line: fine outside, thick inside
            rect = fitz.Rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3),
            pdf_page.draw_rect(rect, border_color, width=2)
        if border_style == "thick_fine_line":                    # double line:  thick outside, fine inside
            rect = fitz.Rect(x0 - 3, y0 - 3, x1 + 3, y1 + 3)
            pdf_page.draw_rect(rect, (0, 0, 0), width=2)
 
        # put the country as the title of the page (tmp) in the top of the page...to be defined the location, color, etc in settings.
        album_title = content_options["country"] 
        #pdf_page.insert_textbox(fitz.Rect(x0 , y0, x1, y0 + 20), album_title, fontsize=12, color=(0,0,1), align=1) # title of the page arriba al centro (centrar bien pdte) 
        x_pos= (x1- len(album_title))/2
        point= fitz.Point(x_pos,y0+18)
        pdf_page.insert_text(point, album_title, fontsize=12, color=(0,0,1))
        # write the page number
        ## pdf_page.insert_textbox(fitz.Rect(x1 - 50, y1 - 20, x1, y1), f"__Pag._ {pg}", fontsize=8, color=(0,0,0), align=2) 

        #______ cuadricular TMP !__________________________________________
        sizes= album_pages.paper_sizes
        x1 = int(sizes["width"] * 72)
        y1 = int(sizes["height"] * 72)
        x = 0
        y = 0
        for x in range(0, x1, 72):
            p1 = fitz.Point(x, 0)
            p2 = fitz.Point(x, y1)
            pdf_page.draw_line(p1, p2, color=(.2, .2, .2), stroke_opacity=0.1, width=1)
        for y in range(0, y1, 72):
            p1 = fitz.Point(0, y)
            p2 = fitz.Point(x1, y)
            pdf_page.draw_line(p1, p2, color=(.2, .2, .2), stroke_opacity=0.1, width=1)
        # _________________________________________________________

   # Save the pdf_document to a file
    output_file_name = content_options["output_options"]["file_name"]
    output_file_path = content_options["output_options"]["path"]
    try:
        os.makedirs(output_file_path, exist_ok=True)
    except FileExistsError:
        pass
    pdf_document_path = os.path.join(output_file_path, output_file_name)
    pdf_document.save(pdf_document_path)
    pdf_document.close()






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