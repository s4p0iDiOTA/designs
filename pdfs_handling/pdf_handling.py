import fitz  # PyMuPDF
from data.models import SeriesContainer, AlbumPages
import os

# create a pdf document. Locates serial containers in the pdf pages.
def put_containers_in_pdf_pages(series__containers: list[SeriesContainer]):
    # open a new pdf document for storing the stamp containers.
    pdf_document = fitz.open()
           
    # create a pdf_page object with the album_pages paper size. It is not added automatically to the document.
    album_page = AlbumPages(None)
    pg_width= album_page.paper_sizes["width"] * 72
    pg_height= album_page.paper_sizes["height"] * 72
    pdf_page = pdf_document.new_page(width= pg_width, height= pg_height)
  
    x_0 = x_1 = y_0 = y_1 = 0  # tmp.... resolver ajuste de coordenadas para ubicar el working page ?
    last_y_pos = 0
    
    # locate series containers in pages. 
    for series_container in series__containers:

        # Series_container coordinates respect to the begining of the page
        x1 =series_container.ini_coord[0] *72
        y1 = series_container.ini_coord[1] *72
        x2 = x1 + series_container.width *72
        y2 = y1 + series_container.height *72

        # check if the new container should be located in a new page (the 1st one is excluded by the condition).
        if  not (y1 >= last_y_pos):
            pdf_page = pdf_document.new_page(width= pg_width, height= pg_height)            

        # ____ margenes de los contenedores (TMP) ________
        container_rect = fitz.Rect(x1, y1, x2, y2)
        pdf_page.draw_rect(container_rect, fill=(.8, .8, .8), fill_opacity=0.1)
        # ________________________________________________

        # Putting stamps inside the containers:
        for row in series_container.rows:
            for stamp_container in row.stamp_containers:
                x01, y01, x02, y02 = [coord * 72 for coord in stamp_container.rect]
                stamp_rect = fitz.Rect(x1+x01, y1+y01 , x1+x02, y1+y02)
                pdf_page.draw_rect(stamp_rect, fill=(0, 0, .8), fill_opacity=0.1, color=(1, 0, 0), stroke_opacity=0.2, width=1)
                # working_area.draw_rect(stamp_rect, color=(0, 0, 0), width=1)
        
        last_y_pos = y1  

    return pdf_document


 
def conform_album_pages(pdf_document, content_options):

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
 
        # Title... put the country as the title of the page (TMP) in the top of the page...to be defined the location, color, etc in settings.
        album_title = content_options["country"] 
        x_pos= (x1- len(album_title))/2
        point= fitz.Point(x_pos,y0+18)
        pdf_page.insert_text(point, album_title, fontsize=12, color=(0,0,1))

        # Page number
        num_pgs = pdf_document.page_count
        pg_text= f"__Pag._ {pg} / {num_pgs}"
        x_pos= (x1- len(pg_text))/2                             # pos. al medio ..
        point= fitz.Point(x_pos,y1-18)
        pdf_page.insert_text(point, pg_text, fontsize=8, color=(0,0,1))    

        #____________TMP__________________cuadricular paper_____________________________
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
        #______________________________________________________________________________

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