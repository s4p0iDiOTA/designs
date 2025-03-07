from containers_handling.container_handler import generate_album_pages 


# steps:
# 1- Open content_options.json file and introduce there the data for the series you filter. Also the input
#  and the output path files.
# 2- If it is necesary, open album_page_layout.json file to change some page layouts.
# 3- Call generate_album_pages()    
#  ......and that´s all folks !!!!!!!!!!!! como en los muñes que tu no conociste.


#   This function calls the function that orchestrate the album pages creation through the 
#   implementation of AlbumPages class.
#  - Description: This function orchestrates the creation of album pages based on the content_options with  
#                 the selection criteries of needed series from an input file. Also the output path. 
#  - Returns: album_pages.pdf file  with the name of the series as specified in content_options

generate_album_pages()



"""

-Series__containers es una lista de SeriesContainer. 
-Los StampsContainer con Stamps de una misma serie se ubican en un mismo series_container: SeriesContainer.
-Un series_container puede alojar una serie en una o mas filas. 
-Cuando mas de un series_container de solo una fila caben horizontalmente, se pueden ubicar en un mismo nivel.


Por ver:
-Si un contenedor no cabe en una pagina ?



"""



