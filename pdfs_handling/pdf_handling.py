import fitz  # PyMuPDF
import os
 
formato_pdf = {                
    "letter":               # 8.5x 11" = 215.9 x 279  mm
        {   "width": 8.5,
            "height": 11    },                       
    "legal":                # 8.5x 14" = 215.9 x 355.6 mm 
        {   "width": 8.5,
            "height": 14    },                
    "A4":                   # 8.27x 11.69" = 210 x 297 mm 
        {   "width": 8.27,
            "height": 11.69 },             
    "A3":                   # 11.9 x 16.4" = 297 x 420 mm 
        {   "width": 11.69,
            "height": 16.54 },                
    "tabloid":              # 11 x 17" = 279.4 x 431.8 mm 
        {    "width": 11,
            "height": 17    }, 
    "customized":           # for non-standard formats modify here      
        {    "width": 7,
            "height": 11    }                   
}      
        
width, height = formato_pdf["customized"].values()     # define in album_page_layout. By default "customized"

def setting_up_page_to_print(current_page, config_file, content_options):
    
    paper_sizes = formato_pdf[config_file["page_options"]["paper_type"]]
    page_margins = config_file["page_options"]["paper_margins"] 
    page_border = config_file["page_options"]["paper_borders"]
    border_style= page_border["style"]
    border_thickness= page_border["thickness"]
    border_color= page_border["color"]
    album_title =content_options["country"]        # tmp

    ##__________________________  paper info___tmp_______________________________________________
    x= paper_sizes["width"] 
    y= paper_sizes["height"]
    point= fitz.Point(x*72/3, 24)
    current_page.insert_text(point, "Paper format: "+str(x)+" x "+str(y), fontsize=8, color=(0,0,0))
    ## ______________________________________________________________

    
    # album_page margins:
    x0= page_margins["left"] *72
    y0= page_margins["top"] *72
    x1= (paper_sizes["width"] - page_margins["right"]) *72
    y1= (paper_sizes["height"] - page_margins["bottom"]) *72
    
    """
    point= fitz.Point((x1-x0)/2, (y0)/2)                                          # ver si definir esa posicion en page layout
    current_page.insert_text(point, album_title, fontsize=12, color=(0,0,1)) # title of the page arriba al centro (centrar bien pdte)
    point= fitz.Point(( y1 - y0 )*2 /3, y1)
    current_page.insert_text(point, "Page "+str(pg_num +1), fontsize=12, color=(1,1,1))   # print page number   
    """
    
    rect = fitz.Rect(x0, y0, x1, y1) 
    current_page.draw_rect(rect, color=(0,0,0), width=1)  # resolver border_color
    if border_style == "single_line":                                       # single fine line
        pass
    if border_style == "double_line":                                   # double fine lines
        rect = fitz.Rect(x0+4, y0+4, x1-4, y1-4) 
        current_page.draw_rect(rect, border_color, width=1)    
    if border_style == "fine_thick_line":                             # double line: fine outside, thick inside
        rect = fitz.Rect(x0+3, y0+3, x1-3, y1-3), 
        current_page.draw_rect(rect, border_color, width=2)
    if border_style == "thick_fine_line":                             # double line:  thick outside, fine inside
        rect = fitz.Rect(x0-3, y0-3, x1+3, y1+3) 
        current_page.draw_rect(rect, (0,0,0), width=2)   

   ####______ cuadricular paper TMP__________________________________________
    paper_sizes = formato_pdf[config_file["page_options"]["paper_type"]]  
    x1=int(paper_sizes["width"]*72)
    y1=int(paper_sizes["height"]*72)
    x=0
    y=0
    for x in range(0, x1, 72):
        p1= fitz.Point(x, 0) 
        p2= fitz.Point(x, y1)
        current_page.draw_line(p1, p2, color=(.2,.2,.2), stroke_opacity=0.1, width= 1)
    for y in range(0, y1, 72):
        p1= fitz.Point(0, y)          
        p2= fitz.Point(x1, y)    
        current_page.draw_line(p1, p2, color=(.2,.2,.2), stroke_opacity=0.1, width= 1)
    #_________________________________________________________



# create a pdf document. Locates serial containers in the pdf pages.
def print_album_pages_to_pdf(container_box, config_file, content_options):        
    
    # open a new pdf document for saving the album pages. 
    pdf_document = fitz.open()    
    paper_sizes = formato_pdf[config_file["page_options"]["paper_type"]]   # size of the paper for storing the album page 
                                                                      # the size of the album_pages will be equal to paper_sizes
 
    # locate the containers in the working area of pages. it is the area defined by the paper borders                                                                    
    for containers in container_box:

        # create a page in the pdf_document with the paper size
        album_pdf_page = pdf_document.new_page(width= paper_sizes["width"] *72, height= paper_sizes["height"] *72) 
        """
        # limits of working area:
        page_margin= config_file["page_options"]["paper_margins"]
        x_0=page_margin["left"]
        x_1=page_margin["right"]
        y_0=page_margin["top"]
        y_1=page_margin["bottom"]

        # define initial coordinates of boxes taking into account the inside margins of working areas:
        w_area= config_file["page_options"]["work_area_margins"]
        x_0 += w_area["left"]
        x_1 += w_area["right"]
        y_0 += w_area["top"]
        y_1 += w_area["bottom"]
        """
        x_0= x_1= y_0= y_1=0


        # locate containers inside the working area:
        for x, y, container in containers.containers:   
            x0, y0 = (x_0+ x) * 72, (y_0+ y) * 72  
            x1, y1 = (x_1+ x + container.width) * 72, (y_1+ y + container.height) * 72
            container_rect = fitz.Rect(x0, y0, x1, y1)
            album_pdf_page.draw_rect(container_rect, fill=(.8, .8, .8), fill_opacity= 0.1)  # limites del contenedor. temporal!!!!
            
             # to print stamps inside the container:       
            for row in container.rows:             
                for stamp_container in row.stamp_containers:
                    x00, y00, x01, y01 = [coord * 72 for coord in stamp_container.rect]  
                    stamp_rect = fitz.Rect(x00+x0, y00+y0, x01+x0, y01+y0)
                    album_pdf_page.draw_rect(stamp_rect, fill=(0, 0, .8),fill_opacity= 0.1, color=(1,0,0), stroke_opacity=0.2, width=1)
                    #working_area.draw_rect(stamp_rect, color=(0, 0, 0), width=1)
        
        setting_up_page_to_print(album_pdf_page, config_file, content_options)


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

 Además del modelo RGB, PyMuPDF también soporta otros modelos de color, como CMYK y Gray
"""