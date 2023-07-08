from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui import QPen, QColor

import constants


class GridScene(QGraphicsScene):
    """
    A custom QGraphicsScene class that represents a scene with a grid.

    Inherits from QGraphicsScene.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gridPen = QPen(QColor(50, 50, 50))

    def drawBackground(self, painter, rect):
        """
        Override of the drawBackground method in QGraphicsScene to draw grid lines in the background.

        Parameters:
            painter (QPainter): The painter object used for drawing.
            rect (QRectF): The rectangle defining the area to be redrawn.

        Returns:
            None

        """
        super().drawBackground(painter, rect)

        # Calculate the left, top, right, and bottom coordinates of the visible area
        left = int(rect.left()) - (int(rect.left()) % constants.GRID_SIZE)
        top = int(rect.top()) - (int(rect.top()) % constants.GRID_SIZE)
        right = int(rect.right())
        bottom = int(rect.bottom())

        # Generate vertical grid lines
        lines = []
        for x in range(left, right, constants.GRID_SIZE):
            lines.append(((x, top), (x, bottom)))

        # Generate horizontal grid lines
        for y in range(top, bottom, constants.GRID_SIZE):
            lines.append(((left, y), (right, y)))

        # Set the pen for drawing the grid lines
        painter.setPen(self.gridPen)

        # Draw the grid lines
        for line in lines:
            start_point = line[0]
            end_point = line[1]
            painter.drawLine(*start_point, *end_point)
