import fitz  # PyMuPDF
from data.models import SeriesContainer

formato_pdf = {                
    "letter":              # 8.5x 11" = 215.9 x 279  mm
        {
            "width": 8.5,
            "heigth": 11
        },                       
    "legal":                # 8.5x 14" = 215.9 x 355.6 mm 
        {
            "width": 8.5,
            "heigth": 14
        },                
    "A4":                   # 8.27x 11.69" = 210  x 297 mm 
        {
            "width": 8.27,
            "heigth": 11.69
        },             
    "A3":                   # 11.9 x 16.4" = 297  x 420   mm 
        {
            "width": 11.69,
            "heigth": 16.54
        },                
    "tabloid":              # 11 x 17" = 279.4 x 431.8 mm 
        {
            "width": 11,
            "heigth": 17
        }, 
    "customized":           # for non-standard formats modify here      
        {
            "width": 8.5,
            "heigth": 14 
        }                   
}      
        
width, height = formato_pdf["legal"].values()     # seleccionar el formato y ponerlo aqui

def print_to_pdf(container: SeriesContainer, output_pdf_path="output.pdf"):
    # Open new PDF document
    new_pdf_document = fitz.open()
    # Add a page to the document
    new_page = new_pdf_document.new_page(width=width*72, height=height*72)  # in inches
    
    # Define rectangle coordinates (x0, y0, x1, y1)
    container_rect = fitz.Rect(0, 0, container.width*72, container.height*72)

    # Draw the rectangle
    new_page.draw_rect(container_rect, color=(1, 0, 0), width=2)  # Red rectangle with 2pt width
    
    for row in container.rows:
        for stamp_container in row.stamp_containers:        
            # Define rectangle coordinates (x0, y0, x1, y1)
            x0, y0, x1, y1 = [i*72 for i in stamp_container.rect]  # to inches
            stamp_rect = fitz.Rect(x0, y0, x1, y1)

            # Draw the rectangle
            new_page.draw_rect(stamp_rect, color=(0, 0, 1), width=2)  # Blue rectangle with 2pt width
    
    # Save the new PDF
    new_pdf_document.save(output_pdf_path)
    new_pdf_document.close()