import os
from data.data_layer import validate_json_file, read_json, get_series
from data.models import AlbumPages
from data.objects.containers import Page, Row, SeriesContainer
from data.objects.options import AligmentOptions, Gaps
from pdfs_handling.pdf_handling import create_pdf_from_pages

def distribute_containers(series__containers: list[SeriesContainer], config: AlbumPages) -> list[Page]:
    # Distributes as many series_containers as the working area can fit. 
    # The containers are distributed as much as they can fit fisrt horizontally then vertically.
    # Adds the start coordinates of each container relative to the start coordinates of
    # the working area. When the containers fills up the area corresponding to a work area,
    # their start coordinates are adjusted to the start of the working area. 

    pages = []
    page = Page.create_from_config(config)
    
    row_alignment_options = AligmentOptions(
        gaps=page.working_area.alignment_options.gaps,
        horizontal=AligmentOptions.Horizontal.UNIFORM,
        vertical=AligmentOptions.Vertical.BOTTOM)
    
    row = Row(alignment_options=row_alignment_options, 
        relative_coordinates=(page.working_area.margin.left, page.working_area.margin.top),
        width=page.working_area.get_effective_width())
    
    x_in_row = 0.0
    y_in_working_area = 0.0

    for series_container in series__containers:
        # if the series_container doesn't fit horizontally, move to a new row:
        if x_in_row + series_container.width > row.width:
            row.vertical_align()      # vertical align the row with more than one container
            page.working_area.rows.append(row)
            x_in_row = 0.0                                       
            y_in_working_area += row.get_height() + page.working_area.alignment_options.gaps.vertical
            row = Row(alignment_options=row_alignment_options, 
                relative_coordinates=(page.working_area.margin.left, y_in_working_area),
                width=page.working_area.get_effective_width())

        # if the container doesn't fit vertically, change to a new page
        if y_in_working_area + series_container.height  > page.working_area.get_effective_height():
            #page.working_area.rows.append(row)    #pq aqui dejaria un row vacio al final de la pagina
            pages.append(page)           
            x_in_row = page.working_area.margin.left                                         
            y_in_working_area = page.working_area.margin.top
            row = Row(alignment_options=row_alignment_options, 
                relative_coordinates=(page.working_area.margin.left, page.working_area.margin.top),
                width=page.working_area.get_effective_width())
            page = Page.create_from_config(config)

        series_container.set_x(x_in_row)
        row.items.append(series_container)
        x_in_row += series_container.width + page.working_area.alignment_options.gaps.horizontal     
    if row.items:  
        page.working_area.rows.append(row)
    if page.working_area.rows:
        pages.append(page)

    # Aligment of rows with series_containers (columns) inside the pages
    for page in pages:
        for row in page.working_area.rows:
            row.horizontal_align()
        page.working_area.vertical_align()

    return pages

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
    config = AlbumPages(config_file)
    
    # Get stamp series from data source based on the provided content options.  
    series_list = get_series(content_options)
        
    # Distribute stamp series in rows inside the containers of optimized dimensions within the work area.
    page = Page.create_from_config(config)    
    max_width = page.working_area.get_effective_width()
    gaps = Gaps(vertical=config.cont_vert_pad, horizontal=config.cont_horiz_pad)
    algmnt_opts = AligmentOptions(gaps=gaps, horizontal=config.cont_horiz_algmt, vertical=config.cont_vert_algmt)
    series__containers = [SeriesContainer.create(series=series, max_width=max_width, alignment_options=algmnt_opts) for series in series_list]
 
    #Distribute containers in working_areas of sized pages, returning containers organized
    # across the width and height of the area. 
    pages = distribute_containers(series__containers, config)
    
    #Print the album pages to a PDF
    #document = put_containers_in_pdf_pages(series__containers)  
    #conform_album_pages(document, content_options) 
    pdf = create_pdf_from_pages(pages)
    output_file_name = content_options["output_options"]["file_name"]
    output_file_path = content_options["output_options"]["path"]
    try:
        os.makedirs(output_file_path, exist_ok=True)
    except FileExistsError:
        pass
    pdf_document_path = os.path.join(output_file_path, output_file_name)
    pdf.save(pdf_document_path)
    pdf.close()

