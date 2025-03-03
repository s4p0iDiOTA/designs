from data.data_layer import validate_json_file, read_json, get_series
from data.models import Series, SeriesContainer, ContainerRow, StampContainer, WorkSpace, AlbumPages
from pdfs_handling.pdf_handling import put_containers_in_pdf_pages, conform_album_pages


# Finds the container for the stamps in the series that has the minimum height within a given width.
# Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates to the container and some metadata.
def get_series_container_min_height(series: Series, max_width: float, stamp_padding, non_inclusive_max_width: bool = False) -> SeriesContainer:
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
        series_container.height = max(y2, series_container.height)   #+ stamp_padding       ####

    if current_row.stamp_containers:
        series_container.rows.append(current_row)
        
    return series_container


# Finds the container for the stamps in the series with the minimum height and minimum width for that height.
# Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates
#  to the container and some metadata.
def get_optimal_series_container(series, max_width, stamp_padding):
    
    # Do a first run to find the optimal height and initial width.
    smallest_container = get_series_container_min_height(series=series, max_width=max_width, stamp_padding=stamp_padding,  non_inclusive_max_width=False)

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

# Adjust  Y position of the stamps on the rows.
def vert_stamps_alignment(series_container: SeriesContainer) -> SeriesContainer: 
    for row in series_container.rows:
        for stamp_container in row.stamp_containers:
            diff = row.height - stamp_container.height
            stamp_container.rect[1] += diff  # y1 (initial pos of the stamp)
            stamp_container.rect[3] += diff  # y3 (height)
    return series_container
 
def distribute_containers(series__containers: list[SeriesContainer]) -> list[WorkSpace]:
    # Distributes as many series_containers as the working area can fit. 

    album_page= AlbumPages(None)
    box= WorkSpace(None)

    # working space limits
    coor=WorkSpace.get_working_limits(None)
    x0,y0,x1,y1 = coor.values()

    current_x = x0              # working_area left side
    current_y = y0              # working_area top
    max_height_on_row = 0
    horiz_pad = album_page.cont_horiz_pad
    vert_pad = album_page.cont_vert_pad

    for series_containers in series__containers:

        # if the next container don´t fits horizontally in the work_area:
        if current_x + series_containers.width + horiz_pad * 2 > x1:  # move down
            current_x = x0                                          
            current_y += max_height_on_row + vert_pad       
            max_height_on_row = 0

        # if the container don´t fits down, change to a new work_area
        if current_y + series_containers.height > y1:  
            current_x = x0
            current_y = y0
            max_height_on_row = 0

        current_x += horiz_pad if current_x == x0 else horiz_pad 
        series_containers.ini_coord= [current_x, current_y]
        current_x += series_containers.width
        max_height_on_row = max(max_height_on_row, series_containers.height)

    # Align the series_containers in the work area:

#  horiz_alignment(series__containers)
#  vert_alignment(series_containers_list)

    return series__containers

def horiz_alignment(series__containers: list[SeriesContainer]):

    # Group containers by their y-coordinate (ini_coord[1])
    rows = {}
    last_y_coord= 0
    ord = 0
    for container in series__containers:
        y_coord = container.ini_coord[1]
        if (ord,y_coord) not in rows: #and not (y_coord >= last_y_coord): # ??? todavia.. no puedo dejar la misma llave
            ord += 1
            rows[(ord, y_coord)] = []        
        rows[(ord, y_coord)].append(container)

    page = AlbumPages(None)
    horiz_pad = page.cont_horiz_pad
    alignment = page.cont_horiz_algmt

    for y_coord, row in rows.items():
        total_width = sum(container.width for container in row)
        available_width = page.page_width - 2 * horiz_pad

        if alignment == "uniform":               #containers are spaced uniformly 
            space = (available_width - total_width) / (len(row) + 1)
            current_x = horiz_pad + space
            for container in row:
                container.ini_coord[0] = current_x
                current_x += container.width + space
        elif alignment == "justify":      #containers are spaced to fill the available width, with equal space between them.
            if len(row) > 1:
                space = (available_width - total_width) / (len(row) - 1)
                current_x = horiz_pad
                for container in row:
                    container.ini_coord[0] = current_x
                    current_x += container.width + space
            else:
                container.ini_coord[0] = (available_width - total_width) / 2 + horiz_pad
        elif alignment == "center":          # containers are centered within the available width.
            current_x = (available_width - total_width) / 2 + horiz_pad
            for container in row:
                container.ini_coord[0] = current_x
                current_x += container.width
        elif alignment == "right":          #containers are aligned to the right within the available width.
            current_x = available_width - total_width + horiz_pad
            for container in row:
                container.ini_coord[0] = current_x
                current_x += container.width
        elif alignment == "left":           #containers are aligned to the left within the available width.
            current_x = horiz_pad
            for container in row:
                container.ini_coord[0] = current_x
                current_x += container.width

    return series__containers


def vert_alignment(series_containers_list: list[SeriesContainer]): # alignment can be: "top", "middle", or "bottom". 
    rows = []
    current_row = []
    current_y = 0
    max_height_on_row = 0
    page= AlbumPages(None)

    for x, y, container in box.containers:
        if current_y + container.height > box.height:
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
            if page.cont_vert_algmt == "top":                                
                new_y = y
            elif page.cont_vert_algmt == "middle":
                new_y = y + (row_height - container.height) / 2
            elif page.cont_vert_algmt == "bottom":
                new_y = y + (row_height - container.height)
            else:
                raise ValueError("Invalid alignment type. Choose from 'top', 'middle', or 'bottom'.")
            row[i] = (x, new_y, container)

    box.containers = [item for row, _ in rows for item in row]


# This function orchestrates the creation of album pages based on the content_options and the album_page_layout.
# Args: - content_options, includes: selection criteries of needed series from an input file and the output path.
#       
# Returns: album_pages file in the specified output path in content_options

# The funtion does the following:
#  - Get series from the database based on content_options
#  - Get page border based on border_options and paper_options
#  - Create series containers and distribute them in pages
#  - Print the album pages to a PDF with the specified paper_options and output_options

def generate_album_pages():  

    if validate_json_file("content_options"): 
        content_options = read_json("content_options")
    else:  print("JSON file not valid.")
    if validate_json_file("album_page_layout"): 
        config_file = read_json("album_page_layout")
    else:  print("JSON file not valid.")

    # Create an AlbumPages object
    album_pages = AlbumPages(config_file)
    
    # Get stamp series from data source based on the provided content options.  
    series= get_series(content_options)       
    
    # Distribute stamp series in rows inside the containers of optimized dimensions within the work area.
    max_width= album_pages.max_container_width
    stamp_padding= album_pages.stamp_padding
    series__containers = [get_optimal_series_container(serie, max_width, stamp_padding) for serie in series]

    # Align the stamps inside the series_containers.The stamp coordinates are set to the same vert. level by rows.
    # and aligned horizontally. 
    alignment = album_pages.stamps_horiz_alignment
    align_stamps_in_containers(series__containers, alignment)
    
    #Distribute containers in working_areas of sized pages, returning containers organized
    # across the width and height of the area. 
    distribute_containers(series__containers)
    
    #Print the album pages to a PDF
    document= put_containers_in_pdf_pages(series__containers)  
    conform_album_pages(document, content_options) 


