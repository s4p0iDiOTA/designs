from pdfs.pdf_handling import print_to_pdf

# Finds the container for the stamps in the series that has the minimum height within a given width.
# Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates to the container and some metadata.
def get_series_container_min_height(series, max_width, stamp_padding, non_inclusive_max_width=False):
    # This can be converted into an object later.
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
            starting_height = series_container["height"] - stamp_padding
        
        # Check if by adding this stamp we would be at or over the max_width. If so, move to the next line. Only if non_inclusive_max_width was set to True.
        if non_inclusive_max_width and last_width + width >= max_width:
            last_width = 0
            starting_height = series_container["height"] - stamp_padding
            # Check if this was happened on the first item. If so, return an empty container.
            if len(series_container["stamps"]) < 1:
                return series_container
            
        # Set the relative coordinates for the stamp within the container and add the stamp to the list.
        x1 = last_width + stamp_padding
        y1 = starting_height + stamp_padding
        x2 = x1 + width - 2 * stamp_padding
        y2 = y1 + height - 2 * stamp_padding
        rect = [x1,y1,x2,y2]
        
        series_container["stamps"].append({
            "rect": rect,
            "metadata": stamp
            })
                
        # Set the last_width to the last x coordinate on this line.
        last_width = x2
        
        # Check if the width or height of the container should change by adding this stamp. If so, update it.
        if x2 > series_container["width"]:
            series_container["width"] = x2 + stamp_padding
        if y2 > series_container["height"]:
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
    
    return smallest_container

# Sample data to run scenarios and validate the functions.
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
                "width": 1.5
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
                "height": 2,
                "width": 2
            },
            {
                "height": 2,
                "width": 1
            }
        ]
    },
    {
        "name": "serie_that_should_be_narrow",
        "year": "",
        "stamps": [
            {
                "height": 1,
                "width": 1.5
            },
            {
                "height": 2,
                "width": 1
            },
            {
                "height": 1,
                "width": 1.5
            },
            {
                "height": 2,
                "width": 1
            }
        ]
    },
    {
        "name": "serie_that_should_be_wide",
        "year": "",
        "stamps": [
            {
                "height": 2,
                "width": 1
            },
            {
                "height": 1,
                "width": 1.5
            },
            {
                "height": 2,
                "width": 1
            },
            {
                "height": 1,
                "width": 1.5
            }
        ]
    }
]

# When this file is executed, run some scenarios to check the functionality. This can be transformed into tests in the future.
print("Base case, 1 stamp. Expected: height and width equal to stamp's height and width plus padding. (arbitrary decision)")
container = get_optimal_series_container(series=test_data[0], max_width=6.5)
print_to_pdf(container, "case1.pdf")
print("Stamps fit in one line. Expected: height will be the tallest stamp's height, width is the sum of all (plus padding)")
container = get_optimal_series_container(series=test_data[1], max_width=6.5)
print_to_pdf(container, "case2.pdf")
print("Stamps don't fit in one line. Expected: height will be the tallest stamp's height in each row, width is the longest row (plus padding). Optimized")
container = get_optimal_series_container(series=test_data[2], max_width=6.5)
print_to_pdf(container, "case3.pdf")
print("Stamps go evenly in 2 lines. Expected: height will be the tallest stamp's height in each row, width is the longest row (plus padding). Optimized")
container = get_optimal_series_container(series=test_data[3], max_width=6.5)
print_to_pdf(container, "case4.pdf")
print("Stamps same stamps as before but different order. Expected: wider than the previous, but less height. Changing rows to reduce width causes more height.")
container = get_optimal_series_container(series=test_data[4], max_width=6.5)
print_to_pdf(container, "case5.pdf")

