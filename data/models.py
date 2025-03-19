from typing import List, Dict, Any
from data.common import formato_pdf

class Stamp:
    def __init__(self, data: Dict[str, Any] = None) -> None:
        if data:
            self.height: float = data.get("height", 0.0)
            self.width: float = data.get("width", 0.0)
        else:
            self.height: float = 0.0
            self.width: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Returns the stamp as a dictionary."""
        return {
            "height": self.height,
            "width": self.width
        }

    def __repr__(self) -> str:
        return f"Stamp(height={self.height}, width={self.width})"


class Series:
    def __init__(self, data: Dict[str, Any] = None) -> None:
        if data:
            self.country: str = data.get("country", "")
            self.name: str = data.get("name", "")
            self.year: int = data.get("year", 0)
            self.stamps: List[Stamp] = [Stamp(stamp) for stamp in data.get("stamps", [])]
        else:
            self.country: str = ""
            self.name: str = ""
            self.year: int = 0
            self.stamps: List[Stamp] = []

    def to_dict(self) -> Dict[str, Any]:
        """Returns the series as a dictionary."""
        return {
            "country": self.country, 
            "name": self.name,            
            "year": self.year,
            "stamps": [stamp.to_dict() for stamp in self.stamps]
        }

    def __repr__(self) -> str:
        return f"Series(country = {self.country}, name={self.name}, year={self.year}, stamps={len(self.stamps)})"


class AlbumPages:
    default_config_file=[]
    def __init__(self, config_file: str = None):
        if config_file:
            AlbumPages.default_config_file= config_file
        config_file= AlbumPages.default_config_file
        
        self.paper_sizes = formato_pdf[config_file["page_options"]["paper_type"]]
        # the page_area, is all the area inside the paper limited by the borders.
        # the working_area is the page_area minus the margins between the paper borders and the same working area.
        self.page_margins = config_file["page_options"]["page_margins"]
        self.page_borders= config_file["page_options"]["page_borders"]
        self.page_width = self.paper_sizes["width"] - self.page_margins["left"] - self.page_margins["right"]
        self.page_height = self.paper_sizes["height"] - self.page_margins["top"] - self.page_margins["bottom"]
        self.page_numbers = config_file["page_options"]["page_numbers"]

        self.working_margins = config_file["work_area"]["margins"]
        self.working_area_width = self.page_width - self.working_margins["left"] - self.working_margins["right"]
        self.working_area_height = self.page_height - self.working_margins["top"] - self.working_margins["bottom"]
        self.working_area = ({"width": self.working_area_width, "height": self.working_area_height}) 
        self.max_container_width = self.working_area_width        
        self.cont_horiz_pad= config_file["work_area"]["container_settings"]["horizontal_paddings"] 
        self.cont_vert_pad= config_file["work_area"]["container_settings"]["vertical_paddings"]
        self.cont_horiz_algmt= config_file["work_area"]["container_settings"]["horizontal_alignment"]
        self.cont_vert_algmt= config_file["work_area"]["container_settings"]["vertical_alignment"]

        self.stamp_padding = config_file["stamps_settings"]["stamp_padding"]
        self.stamps_horiz_alignment = config_file["stamps_settings"]["horizontal_alignment"]
        self.stamps_vert_alignment = config_file["stamps_settings"]["vertical_alignment"]

    
