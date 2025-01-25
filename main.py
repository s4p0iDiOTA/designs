test_data = [
    {
        "name": "serie_with_one_stamp",
        "year": "",
        "stamps": [
            {
                "height": 2,
                "width": 1
            }
        ]
    },
    {
        "name": "serie_that_fits_in_6.5",
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
                "width": 2
            }
        ]
    },
    {
        "name": "serie_that_does_not_fit_in_6.5",
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
                "width": 2
            },
            {
                "height": 1.5,
                "width": 2
            }
        ]
    }
]


# Finds the container for the stamps in the series that has the minimum height and width. Prioritizes finding the minimum height first.
# Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates to the container and some metadata.
def get_series_container(series, max_width, stamp_padding=0.4):
    series_container = {
        "height": 0,
        "width": 0,
        "stamps": []
    }
    
    starting_height = 0
    last_width = 0
    
    for stamp in series["stamps"]:
        # The effective height and width of the stamp is what the stamp needs plus padding on each direction. 
        height = stamp["height"] + 2 * stamp_padding
        width = stamp["width"] + 2 * stamp_padding
        
        # Check if by adding this stamp we would go over the max_width. If so, move to the next line.
        if last_width + width > max_width:
            last_width = 0
            starting_height = series_container["height"]
            
        # Set the relative coordinates for the stamp within the container and add the stamp to the list.
        x1 = last_width
        y1 = starting_height
        x2 = x1 + width
        y2 = y1 + height
        rect = [x1,y1,x2,y2]
        
        series_container["stamps"].append({
            "rect": rect,
            "metadata": stamp
            })
        
        # Set the last_width to the last x coordinate on this line.
        last_width = x2
        
        # Check if the width or height of the container should change by adding this stamp. If so, update it.
        if x2 > series_container["width"]:
            series_container["width"] = x2
        if y2 > series_container["height"]:
            series_container["height"] = y2
        
    return series_container

print(get_series_container(test_data[2], 6.5))