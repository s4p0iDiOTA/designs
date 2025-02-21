import fitz  # PyMuPDF
import os
 
formato_pdf = {                
    "letter":              # 8.5x 11" = 215.9 x 279  mm
        {
            "width": 8.5,
            "height": 11
        },                       
    "legal":                # 8.5x 14" = 215.9 x 355.6 mm 
        {
            "width": 8.5,
            "height": 14
        },                
    "A4":                   # 8.27x 11.69" = 210  x 297 mm 
        {
            "width": 8.27,
            "height": 11.69
        },             
    "A3":                   # 11.9 x 16.4" = 297  x 420   mm 
        {
            "width": 11.69,
            "height": 16.54
        },                
    "tabloid":              # 11 x 17" = 279.4 x 431.8 mm 
        {
            "width": 11,
            "height": 17
        }, 
    "customized":           # for non-standard formats modify here      
        {
            "width": 7,
            "height": 11 
        }                   
}      
        
width, height = formato_pdf["customized"].values()     # seleccionar el formato y ponerlo aqui

def setting_up_page_to_print(current_page, pg_num, config_file, content_options):
    
    paper_sizes = formato_pdf[config_file["paper_options"]["type"]]
    page_margins = config_file["paper_options"]["margins"] 
    page_border = config_file["paper_options"]["borders"]
    border_style= page_border["style"]
    border_thickness= page_border["thickness"]
    border_color= page_border["color"]
    album_title =content_options["country"]

    ## temporal para visualizar los limites del papel (letter: 8.5 x 11 en este ejemplo)
    x00= 0
    y00= 0
    x01= paper_sizes["width"] 
    y01= paper_sizes["height"] 
    rect = fitz.Rect(x00*72, y00*72, x01*72, y01*72)  # inches to points
    current_page.draw_rect(rect, color=(0, 0, 0), width=1)  # negro
    point= fitz.Point((x01-x00)*72, 24)
    current_page.insert_text(point, "Paper_limits", fontsize=12, color=(1,1,1))
    ## ______________________________________________________________

    
    # printing album_page margins:
    x0= page_margins["left"] *72
    y0= page_margins["top"] *72
    x1= (paper_sizes["width"] - page_margins["right"]) *72
    y1= (paper_sizes["height"] - page_margins["bottom"]) *72

    point= fitz.Point(x1-x0, y0)
    current_page.insert_text(point, album_title, fontsize=12, color=(0,0,1)) # title of the page arriba al centro (centrar bien pdte)
 
    point= fitz.Point(( y1 - y0 )*2 /3, y1)
    current_page.insert_text(point, "Page "+str(pg_num), fontsize=12, color=(1,1,1))   # print page number   

    rect = fitz.Rect(x0, y0, x1, y1) 
    current_page.draw_rect(rect, color= (1,1,1), width=1)  # resolver border_color
    if border_style == "single_line":                                       # single fine line
        pass
        if border_style == "double_line":                                   # double fine lines
            rect = fitz.Rect(x0+4, y0+4, x1-4, y1-4) 
            current_page.draw_rect(rect, border_color, width=1)    
        elif border_style == "fine_thick_line":                             # double line: fine outside, thick inside
            rect = fitz.Rect(x0+6, y0+6, x1-6, y1-6), 
            current_page.draw_rect(rect, border_color, width=2)
        elif border_style == "thick_fine_line":                             # double line:  thick outside, fine inside
            rect = fitz.Rect(x0-6, y0-6, x1+6, y1+6) 
            current_page.draw_rect(rect, border_color, width=1)   
           
    """
    # temporal (cuadricular la pagina a 1"):  
    y0= 72
    x0= 72
    y1= page_height
    x1= page_width
    for y in range((y0, y1, 72):
        p1= fitz.point(x0, y)
        p2= fitz.point(x1, y)    
        new_page.draw_line(p1, p2, color=(1, 1, 0), witdh= 1)
    """


def print_album_pages_to_pdf(pages_contents, config_file, content_options):        # trabajar aqui con el config_file los margenes !!
    
    # create a new pdf document for saving the album pages
    pdf_document = fitz.open()
    paper_sizes = formato_pdf[config_file["paper_options"]["type"]]

    for pg_num, working_area in enumerate(pages_contents, start=1):
        working_area_width = int(working_area.width * 72)            # inches to points
        working_area_height = int(working_area.height * 72)          # inches to points

        # create a new page in the pdf document 
        album_pdf_page = pdf_document.new_page(width= paper_sizes["width"], height= paper_sizes["height"])

        # to print container:
        for x, y, container in working_area.containers:   
            x0, y0 = x * 72, y * 72  # inches to points
            x1, y1 = (x + container.width) * 72, (y + container.height) * 72  # inches to points
            container_rect = fitz.Rect(x0, y0, x1, y1)
            #album_pdf_page.draw_rect(container_rect, fill=(.2, .2, .2), fill_opacity= 0.5)  # temporal
            album_pdf_page.draw_rect(container_rect, color=(1,1,1))
            
             # to print stamps inside the container:       
            for row in container.rows:             
                for stamp_container in row.stamp_containers:
                    x00, y00, x01, y01 = [coord * 72 for coord in stamp_container.rect]  
                    stamp_rect = fitz.Rect(x00 + x0, y00 + y0, x01 + x0, y01 + y0)
                    #album_pdf_page.draw_rect(stamp_rect, fill=(0.8, 0.8, 0.8), color=(1, 1, 1), width=1)
                    album_pdf_page.draw_rect(stamp_rect, color=(1, 1, 1), width=1)
        #setting_up_page_to_print(album_pdf_page, pg_num, config_file, content_options)

   #save the pdf in my_designs\country name folder
    output_file_name= content_options["output_options"]["file_name"]  
    output_file_path= content_options["output_options"]["path"] 
    try:
        os.mkdir(output_file_path)
    except FileExistsError: pass
    pdf_document.save(os.path.join(output_file_path, output_file_name))
    pdf_document.close()

     

"""
 * (0, 0, 0): Negro
 * (1, 0, 0): Rojo
 * (0, 1, 0): Verde
 * (0, 0, 1): Azul
 * (1, 1, 0): Amarillo
 * (1, 0, 1): Magenta
 * (0, 1, 1): Cian
 * (1, 1, 1): Blanco

** Además del modelo RGB, PyMuPDF también soporta otros modelos de color, como CMYK y Gray
"""