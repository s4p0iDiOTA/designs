from data.models import Series, SeriesContainer, ContainerRow, StampContainer, AlbumPage
from data.data_layer import get_series 
from pdfs_handling.pdf_handling import print_album_pages_to_pdf, formato_pdf
import os

# Finds the container for the stamps in the series that has the minimum height within a given width.
# Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates to the container and some metadata.
def get_series_container_min_height(series: Series, max_width: float, stamp_padding: float, non_inclusive_max_width: bool = False) -> SeriesContainer:
    series_container = SeriesContainer()
    current_row = ContainerRow()

    row_y1 = 0
    
    for stamp in series.stamps:
        horizontal_padding = stamp_padding if current_row.stamp_containers else 0
        row_width_with_stamp = current_row.width + horizontal_padding + stamp.width
        
        goes_over_max_width = row_width_with_stamp > max_width
        goes_over_max_width_non_inclusive = non_inclusive_max_width and row_width_with_stamp >= max_width
        
        # Check if by adding this stamp we would go over the max_width. If so, move to the next row.
        if goes_over_max_width or goes_over_max_width_non_inclusive:
            # This condition needs additional review to take in consideration the case when 
            # a stamp other than the first is wider than the max_width.
            # Check if this happened on the first item. If so, return an empty container.
            if not current_row.stamp_containers and not series_container.rows:
                return SeriesContainer()
            
            row_y1 += stamp_padding + current_row.height
            series_container.rows.append(current_row)
            current_row = ContainerRow()

        # Set the relative coordinates for the stamp container and add it to the row.        
        horizontal_padding = stamp_padding if current_row.stamp_containers else 0
        x1 = current_row.width + horizontal_padding
        y1 = row_y1
        x2 = x1 + stamp.width
        y2 = y1 + stamp.height
        coordinates = [x1, y1, x2, y2]
        current_row.stamp_containers.append(StampContainer(stamp=stamp, rect=coordinates))

        # Update the width and height of the current row.
        current_row.width = x2
        current_row.height = max(stamp.height, current_row.height)
 
        # Check if the width or height of the series container needs to be updated.
        series_container.width = max(current_row.width, series_container.width)
        series_container.height = max(y2, series_container.height)

    if current_row.stamp_containers:
        series_container.rows.append(current_row)
        
    return series_container


# Finds the container for the stamps in the series with the minimum height and minimum width for that height.
# Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates
#  to the container and some metadata.
def get_optimal_series_container(series, max_width, stamp_padding=0.5):
    
    # Do a first run to find the optimal height and initial width.
    smallest_container = get_series_container_min_height(series=series, max_width=max_width, stamp_padding=stamp_padding, non_inclusive_max_width=False)

    # Keep calling the function with a reduced width until it has to go over the height to accommodate it, or it can't place any stamps.
    while True:
        # Passing non_inclusive_max_width=True makes the function look for a smaller width than the one passed.
        next_container = get_series_container_min_height(series=series, max_width=smallest_container.width, stamp_padding=stamp_padding, non_inclusive_max_width=True)
        # Check if the function could not place any stamps with the width passed and returned an empty container.
        if not next_container.rows:
            break
        # Check if the returned container has a higher height.
        if next_container.height > smallest_container.height:
            break
        # If a smaller width was found, save it.
        elif next_container.width < smallest_container.width:
            smallest_container = next_container

    return smallest_container

# the smallest containers needs to be aligned
def align_stamps_in_containers(containers, alignment):
    for container in containers:
        # Adjust the position of the stamps in the horizontal direction
        horiz_stamps_alignment(container, alignment)    
        # Adjust the base of the stamps on the same line
        vert_stamps_alignment(container)
 
# Adjust X position of the stamps on the rows
def horiz_stamps_alignment(series_container: SeriesContainer, alignment) -> SeriesContainer: # pdte otros alignments !!
    series_container_center = series_container.width / 2
    for row in series_container.rows:
        stamps_width = sum(stamp_container.width for stamp_container in row.stamp_containers)
        
        # If there is only one stamp in the row, center it.
        if len(row.stamp_containers) == 1:
            row.stamp_containers[0].rect[0] = series_container_center - (stamps_width / 2)
            row.stamp_containers[0].rect[2] = row.stamp_containers[0].rect[0] + row.stamp_containers[0].width
            continue
        elif alignment == "uniform":
            pass
        elif alignment == "justify":
            new_gap = (series_container.width - stamps_width) / (len(row.stamp_containers) - 1)
            last_x_coord = 0
            for stamp_container in row.stamp_containers:
                stamp_container.rect[0] = last_x_coord
                stamp_container.rect[2] = stamp_container.rect[0] + stamp_container.width
                last_x_coord = stamp_container.rect[2] + new_gap
        elif alignment == "center":
                pass
        elif alignment == "right":
                pass
    return series_container

# Adjust  Y position of the stamps on the rows
def vert_stamps_alignment(series_container: SeriesContainer) -> SeriesContainer: 
    for row in series_container.rows:
        for stamp_container in row.stamp_containers:
            diff = row.height - stamp_container.height
            stamp_container.rect[1] += diff  # y1 (initial pos of the stamp)
            stamp_container.rect[3] += diff  # y3 (height)
    return series_container


# TODO: Add minimum space between series containers, both horizontal and vertical.

def distribute_serial_containers_in_pages(list_of_containers: list[SeriesContainer], working_area: str, container_settings) -> list[AlbumPage]:
    
    horiz_alignment= container_settings["horizontal_alignment"] 
    vert_alignment= container_settings["vertical_alignment"] 
    vert_padding= container_settings["vertical_paddings"] 
    
    current_x = 0
    current_y = vert_padding
    max_height_on_row = 0
    album_pages = []

    current_page = AlbumPage(working_area)

    for container in list_of_containers:
        container_width = container.width
        container_height = container.height

        # if the container don´t fits in the current row: 
        if current_x + container_width > working_area["width"]:   # move to the next row:
            current_x = 0                                          
            current_y += max_height_on_row + vert_padding        
            max_height_on_row = 0

        # if the container don´t fits in the current page:
        if current_y + container_height > working_area["height"]: # add the current page to the album pages and create a new page.      
            album_pages.append(current_page)
            current_page = AlbumPage(working_area)
            current_x = 0
            current_y = vert_padding
            max_height_on_row = 0

        # Add the container to the current page
        current_page.add_container(current_x, current_y, container)
        current_x += container_width
        max_height_on_row = max(max_height_on_row, container_height)

    # Add the last page
    album_pages.append(current_page)

    # Align the containers in each page
    for page in album_pages:
        horiz_align_containers_in_page(page, working_area["width"], horiz_alignment)

    # Align the containers vertically within the page.
    for page in album_pages:
        vert_align_containers_in_page(page, vert_alignment)

    return album_pages

# Align the containers horizontally in each page
def horiz_align_containers_in_page(page: AlbumPage, working_area_width, alignment: str): # alignment can be: "uniform",..pdte
     
    rows = []
    current_row = []
    current_x = 0
    current_y = 0
    max_height_on_row = 0

    for x, y, container in page.containers:
        if current_x + container.width > working_area_width:
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
            space = (working_area_width - total_width) / (len(row) + 1)
            current_x = space
            for i, (x, y, container) in enumerate(row):
                new_x = current_x
                new_y = y + (row_height - container.height)
                row[i] = (new_x, new_y, container)
                current_x += container.width + space

    page.containers = [item for row, _ in rows for item in row]


# Align the containers vertically within the page.
def vert_align_containers_in_page(page: AlbumPage, alignment): # alignment can be: "top", "middle", or "bottom". 
    rows = []
    current_row = []
    current_y = 0
    max_height_on_row = 0

    for x, y, container in page.containers:
        if current_y + container.height > page.height:
            rows.append((current_row, max_height_on_row))
            current_row = []
            current_y += max_height_on_row
            max_height_on_row = 0

        current_row.append((x, y, container))
        current_y += container.height
        max_height_on_row = max(max_height_on_row, container.height)

    rows.append((current_row, max_height_on_row))

    for row, row_height in rows:
        for i, (x, y, container) in enumerate(row):
            if alignment == "top":                                
                new_y = y
            elif alignment == "middle":
                new_y = y + (row_height - container.height) / 2
            elif alignment == "bottom":
                new_y = y + (row_height - container.height)
            else:
                raise ValueError("Invalid alignment type. Choose from 'top', 'middle', or 'bottom'.")
            row[i] = (x, new_y, container)

    page.containers = [item for row, _ in rows for item in row]

# Generate the border based on border_options and paper_options.          
def get_page_border(page_size: str) -> dict:
    page_dimensions = formato_pdf[page_size]
    return {
        "x1": 0,
        "y1": 0,
        "x2": page_dimensions["width"],
        "y2": page_dimensions["height"]
    }


# This function orchestrates the creation of album pages based on the content_options and the album_page_layout.
# Args: - content_options, includes: selection criteries of needed series from an input file and the output path.
#       - config_file, contains the values of album_page_layout.json file. 
#                      Includes paper and border options, container settings, serial_stamps and output_options.
# Returns: album_pages file in the specified output path in content_options

# The funtion does the following:
#  - Get series from the database based on content_options
#  - Get page border based on border_options and paper_options
#  - Create series containers and distribute them in pages
#  - Print the album pages to a PDF with the specified paper_options and output_options

def generate_album_pages(content_options, config_file):  
    
    # from album_page_layout file:

    paper_sizes = formato_pdf[config_file["paper_options"]["type"]]
    margin_settings= config_file["paper_options"]["margins"]      
    page_width= paper_sizes["width"] - margin_settings["left"] - margin_settings["right"]
    page_height= paper_sizes["height"] - margin_settings["top"] -margin_settings["bottom"]
    working_area_width= page_width - margin_settings["left"] - margin_settings["right"]
    working_area_height= page_height - margin_settings["top"] - margin_settings["bottom"]

    working_area= {"width": working_area_width, "height": working_area_height}
    max_container_width= working_area_width

    container_settings= config_file["container_settings"]

    stamp_padding= config_file["serial_stamps"]["stamp_padding"]
    stapms_horiz_aligment= config_file["serial_stamps"]["horizontal_alignment"]
    
    #Create series and containers 
    series= get_series(content_options, os.getcwd())   # ver luego donde ubicar content_options.json y album_page_layout.json      
  
    # create containers list and aligne stamps inside the containers
    containers = [get_optimal_series_container(s, max_container_width, stamp_padding) for s in series] 
    align_stamps_in_containers(containers, stapms_horiz_aligment)
    
    #Distribute serial containers in working_areas of sized pages
    pages_contents= distribute_serial_containers_in_pages(containers, working_area, container_settings)
    
    #Print the album pages to a PDF
    print_album_pages_to_pdf(pages_contents, config_file, content_options)




# TODO: Add function for vertical alignment of the containers in the page.    

