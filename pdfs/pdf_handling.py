import fitz  # PyMuPDF

def print_to_pdf(container, output_pdf_path="output.pdf"):
    # Open new PDF document
    new_pdf_document = fitz.open()
    # Add a page to the document
    new_page = new_pdf_document.new_page(width=612, height=1008)  # 8.5x14 inches = 612x1008 points
    
    # Define rectangle coordinates (x0, y0, x1, y1)
    container_rect = fitz.Rect(0, 0, container["width"]*72, container["height"]*72)

    # Draw the rectangle
    new_page.draw_rect(container_rect, color=(1, 0, 0), width=2)  # Red rectangle with 2pt width
    
    for stamp in container["stamps"]:        
        # Define rectangle coordinates (x0, y0, x1, y1)
        x0, y0, x1, y1 = stamp["rect"]        
        stamp_rect = fitz.Rect(x0*72, y0*72, x1*72, y1*72)

        # Draw the rectangle
        new_page.draw_rect(stamp_rect, color=(0, 0, 1), width=2)  # Red rectangle with 2pt width
    
    # Save the new PDF
    new_pdf_document.save(output_pdf_path)
    new_pdf_document.close()