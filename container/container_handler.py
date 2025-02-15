from data.models import Series, SeriesContainer, ContainerRow, StampContainer, AlbumPage
from pdfs.pdf_handling import formato_pdf

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
# Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates to the container and some metadata.
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

    # Adjust the base of the stamps on the same line
    smallest_container = vertical_alignment(smallest_container)
    # Adjust the position of the stamps in the horizontal direction
    smallest_container = horizontal_alignment(smallest_container, "justify")

    return smallest_container


# Adjusting the X position of the stamps on the rows
def horizontal_alignment(series_container: SeriesContainer, alignment: str="justify") -> SeriesContainer:
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


# Adjusting the Y position of the stamps on the rows
def vertical_alignment(series_container: SeriesContainer) -> SeriesContainer:
    for row in series_container.rows:
        for stamp_container in row.stamp_containers:
            diff = row.height - stamp_container.height
            stamp_container.rect[1] += diff  # y1 (initial pos of the stamp)
            stamp_container.rect[3] += diff  # y3 (height)
    return series_container


# Distribute the series containers in pages
def distribute_serial_containers_in_pages(list_of_containers: list[SeriesContainer], page_size: str, alignment: str = "uniform"):
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

# Align the containers in each page
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