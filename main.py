from typing import List
from container.container_handler import get_optimal_series_container
from data.models import Series, SeriesContainer
from file_operations.write_to_file import save_json
from pdfs.pdf_handling import print_to_pdf


# TODO: Clean this function to separate concerns, extracting all pdf operations away. Assume data is in points. Move container operations to appropiate module.
import fitz  # PyMuPDF
from pdfs.pdf_handling import formato_pdf
def distribute_containers(containers: List[SeriesContainer], alignment="uniform", pageformat="A4", output_pdf_path="album_pages.pdf"):
    
    # Get the dimensions of the specified page format
    page_width = formato_pdf[pageformat]["width"] * 72    # inches to points
    page_height = formato_pdf[pageformat]["heigth"] * 72  # inches to points

    # Create the PDF document
    pdf_document = fitz.open()

    current_x = 0
    current_y = page_height
    max_height_on_page = 0

    for container in containers:
        container_width = container.width * 72    
        container_height = container.height * 72  

        # Check if the container fits in the current row. 
        if current_x + container_width > page_width:  
            #move to the next row.       
            current_x = 0
            current_y -= max_height_on_page
            max_height_on_page = 0

        # Check if the container fits in the current page
        if current_y - container_height < 0:
            # Add a new page
            pdf_document.new_page(width=page_width, height=page_height)
            current_x = 0
            current_y = page_height
            max_height_on_page = 0

        # Ensure there is at least one page in the document
        if len(pdf_document) == 0:
            pdf_document.new_page(width=page_width, height=page_height)

        # Draw the container on the PDF
        page = pdf_document[-1]  # Get the last page
        container_rect = fitz.Rect(current_x, current_y - container_height, current_x + container_width, current_y)
        page.draw_rect(container_rect, color=(1, 0, 0), width=2)  # Red 

        # Draw the stamps inside the container
        for row in container.rows:
            for stamp_container in row.stamp_containers:
                x0, y0, x1, y1 = [i * 72 for i in stamp_container.rect]  # to inches
                stamp_rect = fitz.Rect(current_x + x0, current_y - y1, current_x + x1, current_y - y0)
                page.draw_rect(stamp_rect, color=(0, 0, 1), width=2)  # blue

        current_x += container_width
        max_height_on_page = max(max_height_on_page, container_height)

    # Save the PDF
    pdf_document.save(output_pdf_path)
    pdf_document.close()

# TODO: Move test data to a file. Create a read_json(file) under file_operations.read_from_file.py and use it to get the test data. Read serialize/deserialize for more info.

# Sample data to run scenarios and validate the functions.
test_data = [ 
    {
        "name": "serie_with_one_stamp",
        "year": "",
        "stamps": [
            {
                "height": 2,
                "width": 1
            }
        ]
    },
    {
        "name": "serie_that_fits_in_6.5",
        "year": "",
        "stamps": [
            {
                "height": 2,
                "width": 1
            },
            {
                "height": 2,
                "width": 1
            },
            {
                "height": 1.5,
                "width": 1.5
            }
        ]
    },
    {
        "name": "serie_that_does_not_fit_in_6.5",
        "year": "",
        "stamps": [
            {
                "height": 2,
                "width": 1
            },
            {
                "height": 2,
                "width": 1
            },
            {
                "height": 2,
                "width": 2
            },
            {
                "height": 2,
                "width": 1
            }
        ]
    },
    {
        "name": "serie_that_should_be_narrow",
        "year": "",
        "stamps": [
            {
                "height": 1,
                "width": 1.5
            },
            {
                "height": 2,
                "width": 1
            },
            {
                "height": 1,
                "width": 1.5
            },
            {
                "height": 2,
                "width": 1
            }
        ]
    },
    {
        "name": "serie_that_should_be_wide",
        "year": "",
        "stamps": [
            {
                "height": 2,
                "width": 1
            },
            {
                "height": 1,
                "width": 1.5
            },
            {
                "height": 2,
                "width": 1
            },
            {
                "height": 1,
                "width": 2
            }
        ]
    },
    {
        "name": " otro para test ajuste vertical -- case6 ",
        "year": "",
        "stamps": [
            {
                "height": 1.2,
                "width": 1.2
            },
            {
                "height": 1.6,
                "width": 0.8
            },
            {
                "height": 1.3,
                "width": 1.2
            },
            {
                "height": 1.8,
                "width": 1.4
            },
            {
                "height": 1,
                "width": 1.4
            },
            {
                "height": 1.4,
                "width": 1.2,
            },
            {
                "height": 1,
                "width": 2
            }
        ]
    }
]



# When this file is executed, run some scenarios to check the functionality. This can be transformed into tests in the future.

#print("Base case, 1 stamp. Expected: height and width equal to stamp's height and width plus padding. (arbitrary decision)")
container1 = get_optimal_series_container(series=Series(test_data[0]), max_width=6.5)
#save_json(json_object=container1, file_name="container1")
print_to_pdf(container1, "case1.pdf")

#print("Stamps fit in one line. Expected: height will be the tallest stamp's height, width is the sum of all (plus padding)")
container2 = get_optimal_series_container(series=Series(test_data[1]), max_width=6.5)
#save_container("container2", container)
print_to_pdf(container2, "case2.pdf")

#print("Stamps don't fit in one line. Expected: height will be the tallest stamp's height in each row, width is the longest row (plus padding). Optimized")
container3 = get_optimal_series_container(series=Series(test_data[2]), max_width=6.5)
#save_container("container3", container)
print_to_pdf(container3, "case3.pdf")

#print("Stamps go evenly in 2 lines. Expected: height will be the tallest stamp's height in each row, width is the longest row (plus padding). Optimized")
container4 = get_optimal_series_container(series=Series(test_data[3]), max_width=6.5)
#save_container("container4", container)
print_to_pdf(container4, "case4.pdf")

#print("Stamps same stamps as before but different order. Expected: wider than the previous, but less height. Changing rows to reduce width causes more height.")
container5 = get_optimal_series_container(series=Series(test_data[4]), max_width=6.5)
#save_container("container5", container)
print_to_pdf(container5, "case5.pdf")

container6 = get_optimal_series_container(series=Series(test_data[5]), max_width=6.5)
#save_container("container6", container)
print_to_pdf(container6, "case6.pdf")


containers = [container1, container2, container3,container4, container5, container6]
distribute_containers(containers, alignment="uniform",  pageformat="A4", output_pdf_path="album_pages.pdf")