
# Finds the container for the stamps in the series that has the minimum height within a given width.
# Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates to the container and some metadata.
def get_series_container_min_height(series, max_width, stamp_padding, non_inclusive_max_width=False):
    # This can be converted into an object later.
    series_container = {
        "height": 0,
        "width": 0,
        "stamps": []
    }

    starting_y_pos = stamp_padding
    last_width = stamp_padding
    max_stamp_height = 0
    
    for stamp in series["stamps"]:
        # The effective height and width of the stamp is what the stamp needs plus padding on each direction. 
        
        # Check if by adding this stamp we would go over the max_width. If so, move to the next line.
        curr_row_width = last_width + stamp["width"] + stamp_padding               
        if  (curr_row_width > max_width):
            last_width = stamp_padding
            curr_row_width = last_width
            starting_y_pos += stamp_padding + max_stamp_height           
            max_stamp_height = 0
    
        max_stamp_height = max(stamp["height"], max_stamp_height)
        
        # Check if by adding this stamp we would be at or over the max_width. If so, move to the next line. Only if non_inclusive_max_width was set to True.
        if non_inclusive_max_width and curr_row_width >= max_width:
            last_width = stamp_padding
            curr_row_width = last_width
            starting_y_pos += max_stamp_height + stamp_padding         
            max_stamp_height = 0
        
            # Check if this was happened on the first item. If so, return an empty container.
            if len(series_container["stamps"]) < 1:
                return series_container
            
        # Set the relative coordinates for the stamp within the container and add the stamp to the list.     
        x1 = last_width 
        y1 = starting_y_pos    
        x2 = x1 + stamp["width"]
        y2 = y1 + stamp["height"]  
        rect = [x1,y1,x2,y2]                              

        last_width = x2 + stamp_padding

        series_container["stamps"].append({
            "rect": rect,
            "metadata": stamp
            })
 
        # Check if the width or height of the container should change by adding the stamps. If so, update it.       
        if  x2 > series_container["width"]:
            series_container["width"] = x2 + stamp_padding           
        if  y2 > series_container["height"]:
            series_container["height"] = y2 + stamp_padding
        
    return series_container


# Finds the container for the stamps in the series with the minimum height and minimum width for that height.
# Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates to the container and some metadata.
def get_optimal_series_container(series, max_width, stamp_padding=0.5):

    # Do a first run to find the optimal height and initial width.
    smallest_container = get_series_container_min_height(series=series, max_width=max_width, stamp_padding=stamp_padding, non_inclusive_max_width=False)

    # Keep calling the function with a reduced width until it has to go over the height to accomodate it, or it can't place any stamps.
    while True:
        # Passing non_inclusive_max_width=True makes the function look for a smaller width than the one passed.
        next_container = get_series_container_min_height(series=series, max_width=smallest_container["width"], stamp_padding=stamp_padding, non_inclusive_max_width=True)
        # Check if the function could not place any stamps with the width passed and returned an empty container.
        if next_container["height"] == 0:
            break
        # Check if the returned container has a higher height.
        if next_container["height"] > smallest_container["height"]:
            break
        # If a smaller width was found, save it.
        elif next_container["width"] < smallest_container["width"]:
            smallest_container = next_container

    # Adjust the base of the stamps on the same line
    smallest_container["stamps"]= vertical_alignment(smallest_container)
    # Adjust the position of the stamps in the horizontal direction
    smallest_container["stamps"]= horizontal_alignment(smallest_container,"uniform") 

    return smallest_container


def horizontal_alignment(series_container, alignment="uniform"):
    # "uniform": distribuye uniformemente modificando los gaps. (by default)
    # "justify": variante de "uniform" pero mantiene los gaps izq y derechos respecto del margen.
    # "center" : todos los sellos al centro manteniendo los gaps.
    #  "left"  : alineacion a la izq. manteniendo los gaps. 
    #  "rigth" : alineacion derecha manteniendo los gaps.
 
    stamp_width =0
    stapms_width = 0
    last_row = False     
    last_cnt = 0

    for current_cnt, stamp  in enumerate(series_container["stamps"]):  

        x0, y0, x1, y1 = stamp["rect"] 
        stamp_width= (x1- x0)  
        stapms_width += stamp_width  

        # comprueba si la fila esta completa y prepara el proximo if.
        if len(series_container["stamps"]) == (current_cnt +1):       # un solo sello o ultima fila. Evita IndexError en el sgte elif !
            last_row = True
        elif (current_cnt < len(series_container["stamps"])-1):       # mas de una fila
            next_stamp= series_container["stamps"][current_cnt+1]     # para poder trabajar con el sgte sello                                                
              
        if last_row or (y1 != next_stamp["rect"][3]):  # no alterar el orden del If !!! para evitar posible IndexError.
            
            match alignment:
                case "uniform":                  
                    new_gap = (series_container["width"]- stapms_width) / ((current_cnt+1)-last_cnt+1) # un gap entre sellos + 2 a cada lado
                    last_x_coord = 0
                         
                    for current_stamp in series_container["stamps"][last_cnt: current_cnt+1]:                        
                        x_0, y_0, x_1, y_1 = current_stamp["rect"]      
                        width = x_1 - x_0
                        x_0 = last_x_coord + new_gap   
                        x_1 = x_0 + width                             
                        rect = [x_0, y_0, x_1, y_1]
                        current_stamp["rect"]= rect                       
                        last_x_coord = x_1                         
                        
                case "justify":
                    pp =0
                case "center":
                    pp=0
                case "rigth":                
                    pp=0
 
            last_cnt = current_cnt +1   # comienzo de la sgte fila
            stapms_width = 0
                      
    return series_container["stamps"]


def vertical_alignment(series_container):    # adjusting the Y position of the stapms on the rows 
                               
    row =[] 
    series_by_row ={}
    max_stamp_height = 0 

    for stamp_in_container in series_container["stamps"]:
        row_key = str(stamp_in_container["rect"][1])            
        series_by_row.setdefault(row_key,[]).append(stamp_in_container)     # series organized with stamps by row

    for elem in series_by_row:                
        row= series_by_row[elem]                      
        for rect in row:                                                # max height of the stamp in the current row.                           
            max_stamp_height = max(max_stamp_height, rect["rect"][3])       
        for rect in  row:                                               # adjusting the values of y1 and y3  
            diff = max_stamp_height - rect["rect"][3]
            if (rect["rect"][3] < max_stamp_height):          
                rect["rect"][1] += diff                                 # y1 (initial pos of the spamp)
                rect["rect"][3] += diff                                 # y3 (height)        
        max_stamp_height= 0

    series_container["stamps"].clear()
    for series_fila in series_by_row.values():
        series_container["stamps"].extend(series_fila)     
   
    return series_container["stamps"]

