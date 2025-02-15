from container.container_handler import get_optimal_series_container, distribute_serial_containers_in_pages
from data.models import Series, SeriesContainer
from pdfs.pdf_handling import print_album_pages_to_pdf
from file_operations.json_files_operations import read_json, validate_json_file
import os


#read json file

directory_path = "data_samples_for_testing"
file_name = "five_series_of_stamps_samples"
file_path = os.path.join(directory_path, file_name + ".json")
if validate_json_file(file_path): 
    test_data = read_json(file_name, directory_path)
else:  
    print("The JSON file is not valid.")

#Create series and containers
series= [Series(data) for data in test_data]
containers = [get_optimal_series_container(series=s, max_width=6.5, stamp_padding=0.25) for s in series]   

#Distribute serial containers in sized pages
album_pages= distribute_serial_containers_in_pages(containers, page_size="A4", alignment= "uniform")

#Print the album pages to a PDF
print_album_pages_to_pdf(album_pages, "album_pages.pdf")




# TODO: Read serialize/deserialize for more info.  ????????????????

