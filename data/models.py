from typing import List, Dict, Any

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
            self.name: str = data.get("name", "")
            self.year: int = data.get("year", 0)
            self.stamps: List[Stamp] = [Stamp(stamp) for stamp in data.get("stamps", [])]
        else:
            self.name: str = ""
            self.year: int = 0
            self.stamps: List[Stamp] = []

    def to_dict(self) -> Dict[str, Any]:
        """Returns the series as a dictionary."""
        return {
            "name": self.name,
            "year": self.year,
            "stamps": [stamp.to_dict() for stamp in self.stamps]
        }

    def __repr__(self) -> str:
        return f"Series(name={self.name}, year={self.year}, stamps={len(self.stamps)})"

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
