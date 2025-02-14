from typing import List
from container.container_handler import get_optimal_series_container
from data.models import Series, SeriesContainer
from file_operations.write_to_file import save_json
from pdfs.pdf_handling import print_stamps_container_to_pdf, print_album_pages_to_pdf

# TODO: Clean this function to separate concerns, extracting all pdf operations away. Assume data is in points.
#  Move container operations to appropiate module.

from data.models import AlbumPage
from pdfs.pdf_handling import formato_pdf

def distribute_serial_containers_in_pages(list_of_containers: List[SeriesContainer], page_size: str, alignment: str = "uniform"):
    page_dimensions = formato_pdf[page_size]
   # work_area_width, work_area_height = page_dimensions
    work_area_width = page_dimensions["width"]
    work_area_height = page_dimensions["height"]

    current_x = 0
    current_y = 0
    max_height_on_row = 0
    album_pages = []
    current_page = AlbumPage(page_size, page_dimensions)

    for container in list_of_containers:
        container_width = container.width
        container_height = container.height

        # Check if the container fits in the current row
        if current_x + container_width > work_area_width:
            # Move to the next row
            current_x = 0
            current_y += max_height_on_row
            max_height_on_row = 0

        # Check if the container fits in the current work area
        if current_y + container_height > work_area_height:
            # Add the current page to the album pages and create a new page
            album_pages.append(current_page)
            current_page = AlbumPage(page_size, page_dimensions)
            current_x = 0
            current_y = 0
            max_height_on_row = 0

        # Add the container to the current page
        current_page.add_container(current_x, current_y, container)
        current_x += container_width
        max_height_on_row = max(max_height_on_row, container_height)

    # Add the last page
    album_pages.append(current_page)

    # Align the containers in each page
    for page in album_pages:
        align_containers_in_page(page, work_area_width, alignment)

    return album_pages

def align_containers_in_page(page: AlbumPage, work_area_width: float, alignment: str):
    rows = []
    current_row = []
    current_x = 0
    current_y = 0
    max_height_on_row = 0

    for x, y, container in page.containers:
        if current_x + container.width > work_area_width:
            rows.append((current_row, max_height_on_row))
            current_row = []
            current_x = 0
            current_y += max_height_on_row
            max_height_on_row = 0

        current_row.append((x, y, container))
        current_x += container.width
        max_height_on_row = max(max_height_on_row, container.height)

    rows.append((current_row, max_height_on_row))

    for row, row_height in rows:
        if alignment == "uniform":
            total_width = sum(container.width for _, _, container in row)
            space = (work_area_width - total_width) / (len(row) + 1)
            current_x = space
            for i, (x, y, container) in enumerate(row):
                new_x = current_x
                new_y = y + (row_height - container.height)
                row[i] = (new_x, new_y, container)
                current_x += container.width + space

    page.containers = [item for row, _ in rows for item in row]


test_data = [ 
    {
        "name": "serie_with_one_stamp", # caso1
        "year": "",
        "stamps": [
            {
                "height": 2,
                "width": 1
            }
        ]
    },
    {
        "name": "serie_that_fits_in_6.5", # caso2
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
        "name": "serie_that_does_not_fit_in_6.5", # caso3
        "year": "",
        "stamps": [
            {
                "height": 0.8,
                "width": 1
            },
            {
                "height": 1.2,
                "width": 1
            },
            {
                "height": 2,
                "width": 2
            },
            {
                "height": 1.5,
                "width": 1
            }
        ]
    },
    {
        "name": "serie_that_should_be_narrow", # caso4
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
        "name": "serie_that_should_be_wide", # caso5
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
        "name": " para llegar a 2 paginas", # caso6 
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
                "width": 1.2
            },
            {
                "height": 1,
                "width": 2
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

series = Series(test_data[0])
container1 = get_optimal_series_container(series=series, max_width=6.5, stamp_padding= 0.25)
series = Series(test_data[1])
container2 = get_optimal_series_container(series=series, max_width=6.5, stamp_padding= 0.25)
series = Series(test_data[2])
container3 = get_optimal_series_container(series=series, max_width=6.5, stamp_padding= 0.25)
series = Series(test_data[3])
container4 = get_optimal_series_container(series=series, max_width=6.5, stamp_padding= 0.25)
series = Series(test_data[4])
container5 = get_optimal_series_container(series=series, max_width=6.5, stamp_padding= 0.25)
series=Series(test_data[5])
container6 = get_optimal_series_container(series=series, max_width=6.5, stamp_padding= 0.25)

#save_json(containers, "containers.json")
#print_stamps_container_to_pdf(container6, "series_container.pdf")

containers= list_of_containers = [container2, container3, container4, container5, container6]   
album_pages= distribute_serial_containers_in_pages(containers, page_size="A4", alignment= "uniform")
print_album_pages_to_pdf(album_pages, "album_pages.pdf")
    





# TODO: Move test data to a file. Create a read_json(file) under file_operations.read_from_file.py and
#  use it to get the test data. Read serialize/deserialize for more info.

