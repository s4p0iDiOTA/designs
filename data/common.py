formato_pdf = {                
    "letter":               # 8.5x 11" = 215.9 x 279  mm
        {   "width": 8.5,
            "height": 11    },                       
    "legal":                # 8.5x 14" = 215.9 x 355.6 mm 
        {   "width": 8.5,
            "height": 14    },                
    "A4":                   # 8.27x 11.69" = 210 x 297 mm 
        {   "width": 8.27,
            "height": 11.69 },             
    "A3":                   # 11.9 x 16.4" = 297 x 420 mm 
        {   "width": 11.69,
            "height": 16.54 },                
    "tabloid":              # 11 x 17" = 279.4 x 431.8 mm 
        {    "width": 11,
            "height": 17    }, 
    "customized":           # for non-standard formats modify here      
        {    "width": 7,
            "height": 11    }                   
}      
        
width, height = formato_pdf["customized"].values()     # define in album_page_layout. By default "customized"