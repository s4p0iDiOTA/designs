from containers_handling.container_handler import generate_album_pages 
from data.data_layer import read_json, validate_json_file


# call to the function that orchestrate the album pages creation
#  - Description: This function orchestrates the creation of album pages based on the content_options and the album_page_layout.
#  - Args: content_options that includes: selection criteries of needed series from an input file and the output path.
#  - Returns: album_pages file in the specified output path in content_options


if validate_json_file("content_options"): content_options = read_json("content_options")
else:  print("JSON file not valid.")
if validate_json_file("album_page_layout"): config_file_data = read_json("album_page_layout")
else:  print("JSON file not valid.")

generate_album_pages(content_options, config_file_data)  # uses content_options.json and album_page_layout.json



#_______________________________________________________________________________________________________________

# Add function to orchestrate the album pages creation
#  - Args: content_options, border_options, paper_options, output_options
#  - Returns: None
#  - Get series from the database based on content_options
#  - Get page border based on border_options and paper_options
#  - Create series containers and distribute them in pages
#  - Print the album pages to a PDF with the specified paper_options and output_options

# content_options = {
    #    "country": "Albania",
    #    "year_range": [1951, 1960]
    #}
    
    # border_options = {
    #    "type": "single",
    #    "color": "black",
    #}
    
    # paper_options = {
    #    "type": "letter",
    #    "margins": [
    #       "top": 0.5,
    #       "bottom": 0.5,
    #       "left": 1.5,
    #       "right": 0.5,],
    #}
    
    # output_options = {
    #    "file_name": "1951-1960.pdf",
    #    "path": "my_designs\\albania",
    #}


    


