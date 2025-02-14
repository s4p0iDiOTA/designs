import fitz  # PyMuPDF
 
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
            "width": 8.5,
            "height": 14 
        }                   
}      
        
width, height = formato_pdf["customized"].values()     # seleccionar el formato y ponerlo aqui


def print_album_pages_to_pdf(album_pages, output_pdf_path: str):
    new_pdf_document = fitz.open()

    for album_page in album_pages:
        page_width = int(album_page.width * 72)  # inches to points
        page_height = int(album_page.height * 72) # inches to points
        new_page = new_pdf_document.new_page(width=page_width, height=page_height)
    
        for x, y, container in album_page.containers:   # to print containers
            x0, y0 = x * 72, y * 72  # inches to points
            x1, y1 = (x + container.width) * 72, (y + container.height) * 72  # inches to points
            container_rect = fitz.Rect(x0, y0, x1, y1)
            new_page.draw_rect(container_rect, color=(0, 0, 1), width=2)  # Blue 
            
            for row in container.rows:              # to print stamps inside the container
                for stamp_container in row.stamp_containers:
                    x00, y00, x01, y01 = [coord * 72 for coord in stamp_container.rect]  
                    stamp_rect = fitz.Rect(x00 + x0, y00 + y0, x01 + x0, y01 + y0)
                    new_page.draw_rect(stamp_rect, color=(1, 0, 0), width=1)  # Red 

    new_pdf_document.save(output_pdf_path)
    new_pdf_document.close()


def print_stamps_container_to_pdf(series_container, output_pdf_path):
    new_pdf_document = fitz.open()

    page_width = series_container.width * 72   
    page_height = series_container.height * 72   
    new_page = new_pdf_document.new_page(width=page_width, height=page_height)

    for row in series_container.rows:
        for stamp_container in row.stamp_containers:
            x0, y0, x1, y1 = [coord * 72 for coord in stamp_container.rect]  
            container_rect = fitz.Rect(x0, y0, x1, y1)
            new_page.draw_rect(container_rect, color=(1, 1, 1), width=2)  # Black 

    new_pdf_document.save(output_pdf_path)
    new_pdf_document.close()


def print_to_pdf(rows, work_area_width, work_area_height, output_pdf_path="output.pdf"):
    # Open new PDF document
    new_pdf_document = fitz.open()
    # Add a page to the document
    rect = new_pdf_document.new_page(width=width*72, height=height*72)  # inches to points
    
    # Draw limits of the working area
    containers_rect = fitz.Rect(0, 0, work_area_width*72, work_area_height*72)
    rect.draw_rect(containers_rect, color=(1, 0, 0), width=2)  # Red rectangle with 2pt width
    
    for row in rows:        
        # Define rectangle coordinates (x0, y0, x1, y1)
        x0, y0, x1, y1 = [i*72 for i in row]             # inches to points
        container_rect = fitz.Rect(x0, y0, x1, y1)

        # Draw the rectangle
        rect.draw_rect(container_rect, color=(0, 0, 1), width=2)  # Red rectangle with 2pt width

    # temporal (cuadricular la pagina a 1"):
    """
    for y in range((int(containers.rect.y0), int(containers.rect.y1)), 72):
        p1= fitz.point(containers.rect.x0, y)
        p2= fitz.point(containers.rect.x1, y)    
        new_page.draw_line(p1, p2, color=(0, 0, 0), witdh= 1)
    """
    # Save the new PDF
    new_pdf_document.save(output_pdf_path)
    new_pdf_document.close()