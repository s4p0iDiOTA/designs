from typing import Any, Dict, List

import fitz

from data.common import coordinates_to_points, in_to_points
from data.models import AlbumPages, Stamp, Series
from data.objects.options import AligmentOptions, BorderOptions, Gaps, Margin


class Container:
    def __init__(self, width: float, height: float, relative_coordinates: tuple) -> None:
        self.width: float = width
        self.height: float = height
        self.relative_coordinates: tuple = relative_coordinates

    def to_dict(self) -> Dict[str, Any]:
        """Returns the container as a dictionary."""
        return {
            "width": self.width,
            "height": self.height,
            "relative_coordinates": self.relative_coordinates,
        }

    def __repr__(self) -> str:
        return f"Container(width={self.width}, height={self.height}, relative_coordinates={self.relative_coordinates})"
                
    def get_x(self) -> float:
        """Returns the x coordinate of the container."""
        return self.relative_coordinates[0]
        
    def set_x(self, x: float) -> None:
        """Sets the x coordinate of the container to the given value."""
        self.relative_coordinates = (x, self.relative_coordinates[1])
        
    def displace_x(self, displacement: float) -> None:
        """Displaces the container horizontally by the given displacement."""
        self.set_x(self.relative_coordinates[0] + displacement)
        
    def get_y(self) -> float:
        """Returns the y coordinate of the container."""
        return self.relative_coordinates[1]
    
    def set_y(self, y: float) -> None:
        """Sets the y coordinate of the container to the given value."""
        self.relative_coordinates = (self.relative_coordinates[0], y)
        
    def displace_y(self, displacement: float) -> None:
        """Displaces the container vertically by the given displacement."""
        self.set_y(self.relative_coordinates[1] + displacement)
        
    def get_width(self) -> float:
        """Returns the width of the container."""
        return self.width

    def set_width(self, width: float) -> None:
        """Sets the width of the container to the given value."""
        self.width = width

    def get_height(self) -> float:
        """Returns the height of the container."""
        return self.height

    def set_height(self, height: float) -> None:
        """Sets the height of the container to the given value."""
        self.height = height
        
    def get_absolute_coordinates(self, origin: tuple) -> tuple:
        """Returns the absolute coordinates (x1, y1, x2, y2) of the container based on the given origin."""
        x1 = origin[0] + self.relative_coordinates[0]
        y1 = origin[1] + self.relative_coordinates[1]
        x2 = x1 + self.width
        y2 = y1 + self.height
        return (x1, y1, x2, y2)
    
    def get_absolute_origin(self, origin: tuple) -> tuple:
        """Returns the absolute origin of the container based on the given origin."""
        x = origin[0] + self.relative_coordinates[0]
        y = origin[1] + self.relative_coordinates[1]
        return (x, y)
    
    def render(self, pdf_page: fitz.Page, origin: tuple) -> None:
        """Renders the container on the given pdf page."""
        x1, y1, x2, y2 = coordinates_to_points(self.get_absolute_coordinates(origin))
        pdf_page.draw_rect((x1, y1, x2, y2), color=(0, 0, 0), width=1)


class Row(Container):
    def __init__(self, alignment_options: AligmentOptions, relative_coordinates: tuple, width: float = 0.0, items: List[Container] = None) -> None:
        self.alignment_options: AligmentOptions = alignment_options
        self.items: List[Container] = items if items is not None else []
        super().__init__(width, self.get_height(), relative_coordinates)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the row as a dictionary."""
        container_dict = super().to_dict()
        container_dict.update({
            "items": self.items,
            "alignment_options": self.alignment_options,
        })
        return container_dict

    def __repr__(self) -> str:
        return f"Row(width={self.width}, height={self.height}, alignment_options={self.alignment_options}, items={self.items})"
    
    def get_height(self):
        if self.items:
            return max(item.height for item in self.items)
        return 0.0
    
    def get_width(self):
        if self.width:
            return self.width
        elif self.items:
            return sum(item.width for item in self.items) + (len(self.items) - 1) * self.alignment_options.gaps.horizontal
        return 0.0
        
    def align(self, alignment_options: AligmentOptions = None, out_spaced = False) -> None:
        """Aligns the row based on the given alignment options."""
        if alignment_options is not None:
            self.alignment_options = alignment_options
            
        self.vertical_align()
        self.horizontal_align()
        
    def vertical_align(self) -> None:
        """Aligns the items vertically based on the given alignment options."""
        if self.alignment_options.vertical == AligmentOptions.Vertical.UNIFORM:
            # Uniform vertical alignment in this case is the same as CENTER
            for item in self.items:
                item.set_y((self.get_height() - item.get_height()) / 2)
        elif self.alignment_options.vertical == AligmentOptions.Vertical.TOP:
            for item in self.items:
                item.set_y(0.0)
        elif self.alignment_options.vertical == AligmentOptions.Vertical.BOTTOM:
            for item in self.items:
                item.set_y(self.get_height() - item.get_height())
        elif self.alignment_options.vertical == AligmentOptions.Vertical.CENTER:
            for item in self.items:
                item.set_y((self.get_height() - item.get_height()) / 2)
    
    def horizontal_align(self) -> None:
        """Aligns the items horizontally based on the given alignment options."""
        if self.alignment_options.horizontal == AligmentOptions.Horizontal.UNIFORM:
            gap=(self.get_width() - sum(item.get_width() for item in self.items)) / (len(self.items) + 1)
            current_x = gap
            for item in self.items:
                item.set_x(current_x)
                current_x += item.get_width() + gap
        elif self.alignment_options.horizontal == AligmentOptions.Horizontal.LEFT:
            current_x = 0.0
            for item in self.items:
                item.set_x(current_x)
                current_x += item.get_width() + self.alignment_options.gaps.horizontal
        elif self.alignment_options.horizontal == AligmentOptions.Horizontal.RIGHT:
            current_x = self.get_width()
            for item in reversed(self.items):
                current_x -= item.get_width()
                item.set_x(current_x)
                current_x -= self.alignment_options.gaps.horizontal
        elif self.alignment_options.horizontal == AligmentOptions.Horizontal.CENTER:
            gaps_width = (len(self.items) - 1) * self.alignment_options.gaps.horizontal
            current_x = (self.width - sum(item.get_width() for item in self.items) - gaps_width) / 2
            for item in self.items:
                item.set_x(current_x)
                current_x += item.get_width() + self.alignment_options.gaps.horizontal

    def render(self, pdf_page: fitz.Page, origin: tuple) -> None:
        new_origin = self.get_absolute_origin(origin)
        
        for item in self.items:
            item.render(pdf_page, new_origin)


class ContainerWithRows(Container):
    def __init__(self, relative_coordinates: tuple, alignment_options: AligmentOptions, width: float = 0.0, height: float = 0.0, rows: List[Row] = None) -> None:
        self.alignment_options: AligmentOptions = alignment_options
        self.rows: List[Row] = rows if rows is not None else []
        self.width: float = width
        self.height: float = height
        super().__init__(self.get_width(), self.get_height(), relative_coordinates)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the page as a dictionary."""
        container_dict = super().to_dict()
        container_dict.update({
            "alignment_options": self.alignment_options,
            "rows": [row.to_dict() for row in self.rows]
        })
        return container_dict
    
    def __repr__(self) -> str:
        return f"ContainerWithRows(width={self.width}, height={self.height}, alignment_options={self.alignment_options}, rows={len(self.rows)})"
        
    def get_height(self) -> float:
        """Returns the height of the container."""
        if self.height:
            return self.height
        if self.rows:
            return sum(row.get_height() for row in self.rows) + (len(self.rows) - 1) * self.alignment_options.gaps.vertical
        return 0.0
    
    def get_width(self) -> float:
        """Returns the width of the container."""
        if self.width:
            return self.width
        elif self.rows:
            return max(row.get_width() for row in self.rows)
        return 0.0
    
    def align(self, alignment_options: AligmentOptions = None) -> None:
        """Aligns the container rows based on the given alignment options."""
        if alignment_options is not None:
            self.alignment_options = alignment_options
            
        self.vertical_align()
        self.horizontal_align()
        
    def vertical_align(self) -> None:
        """Aligns the rows vertically based on the given alignment options."""                
        if self.alignment_options.vertical == AligmentOptions.Vertical.UNIFORM:
            gap = (self.height - sum(row.get_height() for row in self.rows)) / (len(self.rows) + 1)
            current_y = gap
            for row in self.rows:
                row.set_y(current_y)
                current_y += row.get_height() + gap
        elif self.alignment_options.vertical == AligmentOptions.Vertical.TOP:
            current_y = 0.0
            for row in self.rows:
                row.set_y(current_y)
                current_y += row.get_height() + self.alignment_options.gaps.vertical
        elif self.alignment_options.vertical == AligmentOptions.Vertical.BOTTOM:
            current_y = self.height
            for row in reversed(self.rows):
                current_y -= row.get_height()
                row.set_y(current_y)
                current_y -= self.alignment_options.gaps.vertical
        elif self.alignment_options.vertical == AligmentOptions.Vertical.CENTER:
            gaps_height = (len(self.rows) - 1) * self.alignment_options.gaps.vertical
            current_y = (self.height - sum(row.get_height() for row in self.rows) - gaps_height) / 2
            for row in self.rows:
                row.set_y(current_y)
                current_y += row.get_height() + self.alignment_options.gaps.vertical
                
    def horizontal_align(self) -> None:
        """Aligns the rows horizontally based on the given alignment options."""
        if self.alignment_options.horizontal == AligmentOptions.Horizontal.UNIFORM:
            # Uniform horizontal alignment is in this case is the same as CENTER
            for row in self.rows:
                row.set_x((self.width - row.width) / 2)
        elif self.alignment_options.horizontal == AligmentOptions.Horizontal.LEFT:
            for row in self.rows:
                row.set_x(0.0)
        elif self.alignment_options.horizontal == AligmentOptions.Horizontal.RIGHT:
            for row in self.rows:
                row.set_x(self.width - row.width)
        elif self.alignment_options.horizontal == AligmentOptions.Horizontal.CENTER:
            for row in self.rows:
                row.set_x((self.width - row.width) / 2)
    
    def draw_grid(self, pdf_page: fitz.Page, origin: tuple, grid: float = 1, color: list =(0,1,0) ) -> None:
        x1, y1, x2, y2 = coordinates_to_points(self.get_absolute_coordinates(origin))    
        line_separation_points = in_to_points(grid)

        # Draw vertical lines
        current_x = x1
        while current_x <= x2:
            p1= fitz.Point(current_x, y1)
            p2= fitz.Point(current_x, y2)
            pdf_page.draw_line(p1, p2, color=color, stroke_opacity=0.05, width=1)
            current_x += line_separation_points
        # Draw horizontal lines
        current_y = y1
        while current_y <= y2:
            p1= fitz.Point(x1, current_y)
            p2= fitz.Point(x2, current_y)
            pdf_page.draw_line(p1, p2, color=color, stroke_opacity=0.05, width=1)     
            current_y += line_separation_points

    def render(self, pdf_page: fitz.Page, origin: tuple[float, float], grid = False) -> None:
        new_origin = self.get_absolute_origin(origin)
        if grid: 
            self.draw_grid(pdf_page, origin, 0.1, (0,1,0))    
            self.draw_grid(pdf_page, origin, 1, (0,0,1))
        
        for row in self.rows:
            row.render(pdf_page, new_origin)

class Border(Container):
    def __init__(self, border_options: BorderOptions, width: float, height: float, relative_coordinates: tuple) -> None:
        super().__init__(width, height, relative_coordinates)
        self.border_options: BorderOptions = border_options
        
    def to_dict(self) -> Dict[str, Any]:
        """Returns the border as a dictionary."""
        container_dict = super().to_dict()
        container_dict.update({
            "border_options": self.border_options
        })
        return container_dict
    
    def __repr__(self) -> str:
        return f"Border(width={self.width}, height={self.height}, border_options={self.border_options})"
    
    @staticmethod
    def create_empty() -> 'Border':
        """Creates an empty border."""
        return Border(border_options=BorderOptions(), width=0.0, height=0.0, relative_coordinates=(0.0, 0.0))

    @staticmethod
    def create_from_config(config: AlbumPages, parent: 'Page') -> 'Border':
        """Creates a border from the given config."""
        width = parent.width - parent.margin.get_horizontal()
        height = parent.height - parent.margin.get_vertical()
        relative_coordinates = (parent.margin.left, parent.margin.top)
        
        border_options = BorderOptions(
            style=BorderOptions.Style(config.page_borders["style"]),
            color=tuple(config.page_borders["color"]),
            thickness=config.page_borders["thickness"]
        )
        
        border = Border(border_options=border_options, width=width, height=height, relative_coordinates=relative_coordinates)
        
        return border
    
    def render(self, pdf_page: fitz.Page, origin: tuple) -> None:
        """Renders the border on the given pdf page."""
        x1, y1, x2, y2 = coordinates_to_points(self.get_absolute_coordinates(origin))
        if self.border_options.style == BorderOptions.Style.NONE:
            return
        elif self.border_options.style == BorderOptions.Style.ONE_LINE:
            pdf_page.draw_rect((x1, y1, x2, y2), color=self.border_options.color, width=self.border_options.thickness)
        elif self.border_options.style == BorderOptions.Style.TWO_LINES:
            pdf_page.draw_rect((x1, y1, x2, y2), color=self.border_options.color, width=self.border_options.thickness)
            pdf_page.draw_rect((x1 + 2, y1 + 2, x2 - 2, y2 - 2), color=self.border_options.color, width=self.border_options.thickness / 2)


class WorkingArea(ContainerWithRows):
    def __init__(self, width: float, height: float, relative_coordinates: tuple, alignment_options: AligmentOptions, margin: Margin = None, rows: List[Row] = None) -> None:
        super().__init__(relative_coordinates, alignment_options, width=width, height=height, rows=rows)
        self.margin: Margin = margin if margin is not None else Margin()
        self.rows: List[Row] = rows if rows is not None else []

    def to_dict(self) -> Dict[str, Any]:
        """Returns the working area as a dictionary."""
        container_dict = super().to_dict()
        container_dict.update({
            "margin": self.margin,
        })
        return container_dict
    
    def __repr__(self) -> str:
        return f"WorkingArea(width={self.width}, height={self.height}, relative_coordinates={self.relative_coordinates}, margin={self.margin})"
    
    @staticmethod
    def create_empty() -> 'WorkingArea':
        """Creates an empty working area."""
        return WorkingArea(width=0.0, height=0.0, relative_coordinates=(0.0, 0.0), alignment_options=AligmentOptions())
    
    @staticmethod
    def create_from_config(config: AlbumPages, parent: 'Page') -> 'WorkingArea':
        """Creates a working area from the given config."""
        width = parent.width - parent.margin.get_horizontal()
        height = parent.height - parent.margin.get_vertical()
        relative_coordinates = (parent.margin.left, parent.margin.top)
        alignment_options = AligmentOptions(
            gaps=Gaps(
                vertical=config.cont_vert_pad,
                horizontal=config.cont_horiz_pad
            ),
            horizontal=AligmentOptions.Horizontal(config.cont_horiz_algmt),
            vertical=AligmentOptions.Vertical(config.cont_vert_algmt),
        )
        margin = Margin(
            left=config.working_margins["left"],
            right=config.working_margins["right"],
            top=config.working_margins["top"],
            bottom=config.working_margins["bottom"]
        )
        
        working_area = WorkingArea(
            width=width,
            height=height,
            relative_coordinates=relative_coordinates,
            alignment_options=alignment_options,
            margin=margin
        )
        
        return working_area
        
    def get_effective_width(self) -> float:
        """Returns the effective width of the page."""
        return self.width - self.margin.get_horizontal()
    
    def get_effective_height(self) -> float:
        """Returns the effective height of the page."""
        return self.height - self.margin.get_vertical()


class Page(Container):
    def __init__(self, width: float, height: float, margin: Margin = None, working_area: WorkingArea = None, border: Border = None) -> None:
        super().__init__(width, height, (0.0, 0.0))
        self.margin: Margin = margin if margin is not None else Margin()
        self.working_area: WorkingArea = working_area if working_area is not None else WorkingArea.create_empty()
        self.border: Border = border if border is not None else Border.create_empty()

        
    def to_dict(self) -> Dict[str, Any]:
        """Returns the page as a dictionary."""
        container_dict = super().to_dict()
        container_dict.update({
            "margin": self.margin
        })
        return container_dict

    def __repr__(self) -> str:
        return f"Page(width={self.width}, height={self.height}, margin={self.margin})"
    
    @staticmethod
    def create_from_config(config: AlbumPages) -> 'Page':
        """Creates a page from the given config."""
        width = config.paper_sizes["width"]
        height = config.paper_sizes["height"]
        margin = Margin(
            left=config.page_margins["left"],
            right=config.page_margins["right"],
            top=config.page_margins["top"],
            bottom=config.page_margins["bottom"]
        )
        
        page = Page(width=width, height=height, margin=margin)
        
        border = Border.create_from_config(config, page)
        working_area = WorkingArea.create_from_config(config, page)
        page.border = border        
        page.working_area = working_area
            
        return page


class SeriesContainer(ContainerWithRows):
    def __init__(self, series: Series, alignment_options: AligmentOptions, relative_coordinates: tuple = (0.0, 0.0), rows: List[Row] = None) -> None:
        self.rows: List[Row] = rows if rows is not None else []
        self.alignment_options: AligmentOptions = alignment_options
        self.series: Series = series
        super().__init__(relative_coordinates, alignment_options, rows=rows, height=self.get_height(), width=self.get_width())

    def to_dict(self) -> Dict[str, Any]:
        """Returns the series container as a dictionary."""
        container_dict = super().to_dict()
        container_dict.update({"series": self.series})
        return container_dict

    def __repr__(self) -> str:
        return f"SeriesContainer(width={self.width}, height={self.height}, relative_coordinates={self.relative_coordinates}, series={self.series})"
        
    def get_height(self) -> float:
        """Returns the height of the container."""
        if self.rows:
            return sum(row.get_height() for row in self.rows) + (len(self.rows) - 1) * self.alignment_options.gaps.vertical
        return 0.0
    
    def get_width(self) -> float:
        """Returns the width of the container."""
        if self.rows:
            return max(row.get_width() for row in self.rows)
        return 0.0

    def render(self, pdf_page, origin):     # dibujar borde de la serie ____TEMPORAL_
        x1, y1, x2, y2 = coordinates_to_points(self.get_absolute_coordinates(origin))
        pdf_page.draw_rect((x1, y1, x2, y2), color=(0,1,0), width=1)     
        return super().render(pdf_page, origin)

    # Finds the container for the stamps in the series that has the minimum height within a given width.
    # Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates to the container and some metadata.
    @staticmethod
    def _generate_container_with_minimum_height(series: Series, max_width: float, alignment_options: AligmentOptions, inclusive_max_width: bool = True) -> 'SeriesContainer':
        rows: List[Container] = []
        row_alignment_options = AligmentOptions(
            gaps=alignment_options.gaps,
            horizontal=AligmentOptions.Horizontal.UNIFORM,
            vertical=AligmentOptions.Vertical.BOTTOM
        )
        current_row = Row(alignment_options=row_alignment_options, relative_coordinates=(0.0, 0.0))
        
        current_x = 0.0
        current_y = 0.0
        _row_width = 0.0
        
        for stamp in series.stamps:
            width_with_stamp = current_x + stamp.width
            goes_over_max_width = width_with_stamp > max_width if inclusive_max_width else width_with_stamp >= max_width
            
            # Check if by adding this stamp we would go over the max_width. If so, move to the next row.
            if goes_over_max_width:
                # This condition needs additional review to take in consideration the case when 
                # a stamp other than the first is wider than the max_width.
                # Check if this happened on the first item. If so, return an empty container.
                if not current_row.items and not rows:
                    return SeriesContainer(series=series, alignment_options=alignment_options)
                
                ##_row_width = current_row.get_width()    # para el alineamiento horiz de la siguiente fila
                ##current_row.horizontal_align(out_spaced=False)                   
                rows.append(current_row)
                current_x = 0.0
                current_y += current_row.get_height() + alignment_options.gaps.vertical
                current_row = Row(alignment_options=row_alignment_options, relative_coordinates=(0.0, current_y))
            
            stamp_container = StampContainer(width=stamp.width, height=stamp.height, relative_coordinates=(current_x, 0.0), stamp=stamp)
            current_row.items.append(stamp_container)
            
            current_x += stamp.width + alignment_options.gaps.horizontal
            
        if current_row.items:               
            rows.append(current_row)

            
        return SeriesContainer(series=series, alignment_options=alignment_options, rows=rows)


    # Finds the container for the stamps in the series with the minimum height and minimum width for that height.
    # Returns a container with a height, width and a list of Stamps. Each Stamp has a rect with relative coordinates
    # to the container and some metadata.
    @staticmethod
    def create(series: Series, max_width: float, alignment_options: AligmentOptions) -> 'SeriesContainer':        
        # Do a first run to find the optimal height and initial width.
        smallest_container = SeriesContainer._generate_container_with_minimum_height(series, max_width, alignment_options, True)

        # Keep calling the function with a reduced width until it has to go over the height to accommodate it, or it can't place any stamps.
        while True:
            # Passing non_inclusive_max_width=True makes the function look for a smaller width than the one passed.
            next_container = SeriesContainer._generate_container_with_minimum_height(series, smallest_container.get_width(), alignment_options, False)
            # Check if the function could not place any stamps with the width passed and returned an empty container.
            if not next_container.rows:
                break
            # Check if the returned container has a higher height.
            if next_container.get_height() > smallest_container.get_height():
                break
            # If a smaller width was found, save it.
            elif next_container.get_width() < smallest_container.get_width():
                smallest_container = next_container

        # stamp containers alignment inside the rows
        for row in smallest_container.rows:
            row.vertical_align()
            row.width= max(row.get_width() for row in smallest_container.rows)           
            row.horizontal_align()


        #smallest_container.align()

        return smallest_container


class StampContainer(Container):
    def __init__(self, width: float = 0.0, height: float = 0.0, relative_coordinates: tuple = (0.0, 0.0), stamp: Stamp = None) -> None:
        super().__init__(width, height, relative_coordinates)
        self.stamp: Stamp = stamp if stamp is not None else Stamp(0, "")

    def to_dict(self) -> Dict[str, Any]:
        """Returns the stamp container as a dictionary."""
        container_dict = super().to_dict()
        container_dict.update({"stamp": self.stamp.to_dict()})
        return container_dict

    def __repr__(self) -> str:
        return f"StampContainer(width={self.width}, height={self.height}, relative_coordinates={self.relative_coordinates}, stamp={self.stamp})"