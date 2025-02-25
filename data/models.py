from typing import List, Dict, Any
from pdfs_handling.pdf_handling import formato_pdf
import json

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

class StampContainer:
    def __init__(self, stamp: Stamp = None, rect: List[float] = None) -> None:
        self.stamp: Stamp = stamp if stamp else Stamp()
        self.rect: List[float] = rect if rect else [0.0, 0.0, 0.0, 0.0]
        self.height: float = self.stamp.height
        self.width: float = self.stamp.width

    def to_dict(self) -> Dict[str, Any]:
        """Returns the container as a dictionary."""
        return {
            "stamp": self.stamp.to_dict(),
            "rect": self.rect,
            "height": self.height,
            "width": self.width
        }

    def __repr__(self) -> str:
        return f"StampContainer(stamp={self.stamp}, rect={self.rect}, height={self.height}, width={self.width})"

class ContainerRow:
    def __init__(self) -> None:
        self.height: float = 0.0
        self.width: float = 0.0
        self.stamp_containers: List[StampContainer] = []

    def to_dict(self) -> Dict[str, Any]:
        """Returns the row as a dictionary."""
        return {
            "height": self.height,
            "width": self.width,
            "stamp_containers": [stamp_container.to_dict() for stamp_container in self.stamp_containers]
        }

    def __repr__(self) -> str:
        return f"ContainerRow(height={self.height}, width={self.width}, stamp_containers={len(self.stamp_containers)})"

class SeriesContainer:
    def __init__(self) -> None:
        self.height: float = 0.0
        self.width: float = 0.0
        self.rows: List[ContainerRow] = []

    def to_dict(self) -> Dict[str, Any]:
        """Returns the container as a dictionary."""
        return {
            "height": self.height,
            "width": self.width,
            "rows": [row.to_dict() for row in self.rows]
        }

    def __repr__(self) -> str:
        return f"SeriesContainer(height={self.height}, width={self.width}, rows={len(self.rows)})"


class WorkSpace:
    def __init__(self, work_area: str):
        self.width = work_area.get("width", 0.0)
        self.height = work_area.get("height", 0.0)
        self.containers = []  # List [x, y, SeriesContainer]

    def add_container(self, x: float, y: float, container):
        self.containers.append((x, y, container))

    def get_working_limits(self) -> dict:
        return {
            "x1": AlbumPages.paper_margins["left"] + AlbumPages.working_margins["left"],
            "y1": AlbumPages.paper_margins["top"] + AlbumPages.working_margins["top"],
            "x2": AlbumPages.get_page_borders["x2"] - AlbumPages.working_margins["right"],
            "y2": AlbumPages.get_page_borders["y2"]- AlbumPages.working_margins["bottom"]
        }


class AlbumPages:
    def __init__(self, config_file: str):

        # the page_area, is all the area inside the paper limited by the borders.
        # the working_area is the page_area minus the margins between the paper borders and the same working area.

        self.paper_sizes = formato_pdf[config_file["page_options"]["paper_type"]]
        self.paper_margins = config_file["page_options"]["paper_margins"]

        self.page_width = self.paper_sizes["width"] - self.paper_margins["left"] - self.paper_margins["right"]
        self.page_height = self.paper_sizes["height"] - self.paper_margins["top"] - self.paper_margins["bottom"]

        self.working_margins = config_file["page_options"]["work_area_margins"]
        self.working_area_width = self.page_width - self.working_margins["left"] - self.working_margins["right"]
        self.working_area_height = self.page_height - self.working_margins["top"] - self.working_margins["bottom"]
        self.working_area = WorkSpace({"width": self.working_area_width, "height": self.working_area_height})

        self.cont_horiz_pad= config_file["container_settings"]["horizontal_paddings"] 
        self.cont_vert_pad= config_file["container_settings"]["vertical_paddings"]
        self.cont_horiz_algmt= config_file["container_settings"]["horizontal_alignment"]
        self.cont_vert_algmt= config_file["container_settings"]["vertical_alignment"]

        self.max_container_width = self.working_area.width

        self.stamp_padding = config_file["serial_stamps"]["stamp_padding"]
        self.stamps_horiz_alignment = config_file["serial_stamps"]["horizontal_alignment"]

     #   self.container_boxes:List[container_boxes] = []  # List [x, y, Container_box]

     # Get the border based on border_options and paper_options.         
    def get_page_borders(self) -> dict:
        return {
            "x1": self.paper_margins["left"],
            "y1": self.paper_margins["top"],
            "x2": self.paper_sizes["width"] - self.paper_margins["right"],
            "y2": self.paper_sizes["height"] - self.paper_margins["bottom"]
        }