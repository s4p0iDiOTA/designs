from file_operations.json_files_operations import save_json, validate_json_file

# select or modify the test_data to create the file

saving_directory_path = "data_samples_for_testing"

#source_data:

test_data = [ 
    {
        "name": "serie_with_one_stamp", # caso1
        "year": "",
        "stamps": [
            {
                "height": 2,
                "width": 1
            }
        ]
    },
    {
        "name": "serie_that_fits_in_6.5", # caso2
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
        "name": "serie_that_does_not_fit_in_6.5", # caso3
        "year": "",
        "stamps": [
            {
                "height": 0.8,
                "width": 1
            },
            {
                "height": 1.2,
                "width": 1
            },
            {
                "height": 2,
                "width": 2
            },
            {
                "height": 1.5,
                "width": 1
            }
        ]
    },
    {
        "name": "serie_that_should_be_narrow", # caso4
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
        "name": "serie_that_should_be_wide", # caso5
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
                "width": 2
            }
        ]
    },
    {
        "name": " para llegar a 2 paginas", # caso6 
        "year": "",
        "stamps": [
            {
                "height": 1.2,
                "width": 1.2
            },
            {
                "height": 1.6,
                "width": 0.8
            },
            {
                "height": 1.3,
                "width": 1.2
            },
            {
                "height": 1.8,
                "width": 1.4
            },
            {
                "height": 1,
                "width": 1.4
            },
            {
                "height": 1.4,
                "width": 1.2
            },
            {
                "height": 1,
                "width": 2
            },
            {
                "height": 1.8,
                "width": 1.4
            },
            {
                "height": 1,
                "width": 1.4
            },
            {
                "height": 1.4,
                "width": 1.2
            },
            {
                "height": 1,
                "width": 2
            }
        ]
    }
]

# write the file name that will be created in the saving_directory_path
file_name= "five_series_of_stamps_samples"

selected_data= [data for data in test_data]

#Save selected series data to JSON file
save_json(selected_data, file_name, saving_directory_path)