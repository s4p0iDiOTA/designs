from enum import Enum
from typing import Any, Dict

      
class Gaps:
    def __init__(self, vertical: float = 0.0, horizontal: float = 0.0) -> None:
        self.vertical: float = vertical
        self.horizontal: float = horizontal

    def to_dict(self) -> Dict[str, Any]:
        """Returns the gaps as a dictionary."""
        return {
            "vertical": self.vertical,
            "horizontal": self.horizontal
        }
        
    def __repr__(self) -> str:
        return f"Gaps(vertical={self.vertical}, horizontal={self.horizontal})"
    
class Margin:
    def __init__(self, top: float = 0.0, bottom: float = 0.0, left: float = 0.0, right: float = 0.0) -> None:
        self.top: float = top
        self.bottom: float = bottom
        self.left: float = left
        self.right: float = right

    def to_dict(self) -> Dict[str, Any]:
        """Returns the margin as a dictionary."""
        return {
            "top": self.top,
            "bottom": self.bottom,
            "left": self.left,
            "right": self.right
        }
        
    def __repr__(self) -> str:
        return f"Margin(top={self.top}, bottom={self.bottom}, left={self.left}, right={self.right})"
    
    def get_vertical(self) -> float:
        """Returns the vertical margin as a float."""
        return self.top + self.bottom
    
    def get_horizontal(self) -> float:
        """Returns the horizontal margin as a float."""
        return self.left + self.right

class AligmentOptions:
    class Horizontal(Enum):
        LEFT = "left"
        CENTER = "center"
        UNIFORM = "uniform"
        RIGHT = "right"

    class Vertical(Enum):
        TOP = "top"
        CENTER = "center"
        UNIFORM = "uniform"
        BOTTOM = "bottom"
    
    def __init__(self, gaps: Gaps = None, horizontal: Horizontal = Horizontal.CENTER, vertical: Vertical = Vertical.UNIFORM) -> None:
        self.gaps: Gaps = gaps if gaps else Gaps()
        self.horizontal: 'AligmentOptions.Horizontal' = horizontal
        self.vertical: 'AligmentOptions.Vertical' = vertical

    def to_dict(self) -> Dict[str, Any]:
        """Returns the alignment options as a dictionary."""
        return {
            "gaps": self.gaps.to_dict(),
            "horizontal": self.horizontal,
            "vertical": self.vertical,
        }
  
class BorderOptions:
    class Style(Enum):
        NONE = ""
        ONE_LINE = "fine_line"
        TWO_LINES = "thick_fine_line"
    
    def __init__(self, style: Style = Style.NONE, color: tuple = (0,0,0), thickness: int = 0, margin: Margin = None) -> None:
        self.style: 'BorderOptions.Style' = style
        self.color: tuple = color
        self.thickness: int = thickness
        self.margin: Margin = margin if margin else Margin()
        
    def to_dict(self) -> Dict[str, Any]:
        """Returns the border options as a dictionary."""
        return {
            "style": self.style.value,
            "color": self.color,
            "thickness": self.thickness,
            "margin": self.margin.to_dict()
        }
    
    def __repr__(self) -> str:
        return f"BorderOptions(style={self.style}, color={self.color}, thickness={self.thickness}, margin={self.margin})"