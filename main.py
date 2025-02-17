from container.container_handler import get_optimal_series_container, distribute_serial_containers_in_pages
from data.models import Series
from pdfs_handling.pdf_handling import print_album_pages_to_pdf, formato_pdf
from file_operations.json_files_operations import read_json, validate_json_file


# select album
directory_path = "albums\\_album_sample"
#test_data= read_json("five_series_of_stamps_samples", directory_path)
test_data= read_json("Large serie for generating 2 pages", directory_path)

#deserialize config_file
if validate_json_file("config_file", directory_path): config_file_data = read_json("config_file", directory_path)
else:  print("JSON file not valid.")
page_dimensions = formato_pdf[config_file_data["album_page"]["format"]]
max_container_width= page_dimensions["width"]
stamp_padding= config_file_data["serial_stamps"]["stamp_padding"]

#Create series and containers
series= [Series(data) for data in test_data]
containers = [get_optimal_series_container(s, max_container_width, stamp_padding) for s in series]  
 
#Distribute serial containers in sized pages
album_pages= distribute_serial_containers_in_pages(containers, page_dimensions, horiz_alignment= "uniform", vert_alignment= "middle")

#Print the album pages to a PDF
print_album_pages_to_pdf(album_pages, "album_pages.pdf")






