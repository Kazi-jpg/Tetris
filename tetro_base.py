"""Provides the fundamental building blocks for a Tetris game implementation,
including the Cell class for tetris blocks and the Tetromino base class
The module supports drawing, moving, and rotating tetris
pieces using the turtle graphics library.

Classes:
    - Cell: Represents a single cell/block in a tetris piece
    - Tetromino: Base class for different types of tetris pieces

Project:
    - tetris_230fall25,
    - Author(s): Amissah
"""

import turtle as tt
from collections.abc import Sequence
from random import randint
from math import sin, cos, pi


class Cell:
    """Represents a single cell in a Tetris grid, defined by four corner points.
        A Cell can be drawn using a turtle pen, rotated 90 degrees clockwise around a given center,
        and translated along the x or y axis. Cells are considered equal if their corner points match,
        regardless of color or order.
        Attributes:
            size (int or float): The size of the cell.
            color (str): The fill color of the cell.
            pen (turtle.Turtle): The turtle pen used for drawing.
            points (list of tuple): The four corner points of the cell.
            state (int): Optional state value for the cell.
        Methods:
            draw(): Draws the cell using the turtle pen.
            rotate(xc, yc): Rotates the cell 90 degrees clockwise around (xc, yc).
            translate_x(factor=1): Moves the cell horizontally by factor * size.
            translate_y(factor=1): Moves the cell vertically by factor * size.
            __eq__(other): Checks if two cells have the same set of points.
            __ne__(other): Checks if two cells do not have the same set of points.
            __str__(): Returns a string representation of the cell.
            __repr__(): Returns a string representation of the cell.
    """

    def __init__(self, size, color, pen, *points, state=0):
        assert len(points) == 4, "Number of points must be 4"
        assert points[0] != points[1] != points[2] != points[3], "There can't be duplicates in cell corners"
        self.points = list(points)
        self.color = color
        self.pen = pen
        self.size = size
        self.state = state

    def draw(self):
        """Turtle visits each point in self.points to draw cell
        >>> c = Cell(1, "red", tt.RawTurtle(tt.getscreen()), (-1, 1), (1, 1), (1, -1), (-1, -1))
        """
        self.pen.pu()
        self.pen.goto(self.points[0])
        self.pen.fillcolor(self.color)
        self.pen.pd()
        self.pen.begin_fill()
        for p in self.points + [self.points[0]]:
            self.pen.goto(p)
        self.pen.end_fill()

    def rotate(self, xc, yc):
        """Rotates each point by 90 degrees clockwise or -pi/2
        rotation formula for point (x, y) around center (xc, yc) is given by
               x' = xc + (x-xc)*cos(-pi/2) - (y-yc)*sin(-pi/2)
               y' = yc + (x-xc)*sin(-pi/2) + (y-yc)*cos(-pi/2)
        :tests:
        >>> c = Cell(1, "red", tt.RawTurtle(tt.getscreen()), (-1, 1), (1, 1), (1, -1), (-1, -1))
        >>> c.rotate(0, 0)
        >>> c.points
        [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        """
        self.points = [( round(xc + (x-xc)*cos(-pi/2) - (y-yc)*sin(-pi/2)),
                         round(yc + (x-xc)*sin(-pi/2) + (y-yc)*cos(-pi/2)) )
                            for x, y in self.points]

    def translate_x(self, factor=1):
        """Move in x plane by factor times cell size
        negative factors shift cell to left, positive to right
        :tests:
        >>> c = Cell(1, "red", tt.RawTurtle(tt.getscreen()), (-1, 1), (1, 1), (1, -1), (-1, -1))
        >>> c.translate_x(1)
        >>> c.points
        [(0, 1), (2, 1), (2, -1), (0, -1)]
        """
        self.points = [(x+factor*self.size, y) for x, y in self.points]

    def translate_y(self, factor=1):
        """Move in x plane by factor times cell size
        negative factors shift cell to left, positive to right
        :tests:
        >>> c = Cell(1, "red", tt.RawTurtle(tt.getscreen()), (-1, 1), (1, 1), (1, -1), (-1, -1))
        >>> c.translate_y(1)
        >>> c.points
        [(-1, 2), (1, 2), (1, 0), (-1, 0)]
        """
        self.points = [(x, y+factor*self.size) for x, y in self.points]

    def get_bounds(self):
        """Returns 4 tuple lowest point (i.e. bottom left corner) xl, yl
        and highest point (i.e. upper left corner) xh, yh of shape"""
        xl, xh = sorted(set(x for x, y in self.points))
        yl, yh = sorted(set(y for x, y in self.points))
        return xl, yl, xh, yh

    def __neg__(self):
        """-Cell() -> returns a new Cell dropped by 1 unit from the original
        i.e. y-size for all y"""
        points = [(x, y-self.size) for x, y in self.points]
        s, c, p = self.size, self.color, self.pen
        return Cell(s, c, p, *points)

    def __rshift__(self, factor:int):
        """Cell() >> 1 -> returns a new Cell shifted right by 1 unit from the original
            i.e. x+size for all x"""
        points = [(x+factor*self.size, y) for x, y in self.points]
        s, c, p = self.size, self.color, self.pen
        return Cell(s, c, p, *points)

    def __lshift__(self, factor:int):
        """Cell() << 1 -> returns a new Cell shifted left by 1 unit from the original
                    i.e. x-size for all x"""
        points = [(x-factor*self.size, y) for x, y in self.points]
        s, c, p = self.size, self.color, self.pen
        return Cell(s, c, p, *points)

    def __mul__(self, point: Sequence[float, float]):
        """Cell() * (0, 0) -> returns a new Cell rotated clockwise 90 about (0, 0)
              from the original"""
        xc, yc = point
        points = [(round(xc + (x-xc) * cos(-pi/2) - (y - yc) * sin(-pi/2)),
                   round(yc + (x-xc) * sin(-pi/2) + (y - yc) * cos(-pi/2)))
                  for x, y in self.points]
        s, c, p = self.size, self.color, self.pen
        return Cell(s, c, p, *points)

    def __eq__(self, other):
        """Two Cells are equivalent/overlapping if all their points are the same
        :tests:
        >>> c1 = Cell(1, "red", tt.RawTurtle(tt.getscreen()), (-1, 1), (1, 1), (1, -1), (-1, -1))
        >>> c2 = Cell(1, "blue", tt.RawTurtle(tt.getscreen()),  (-1, -1), (1, 1), (-1, 1), (1, -1),)
        >>> c1 == c2
        True
        """
        if not isinstance(other, Cell): return NotImplemented
        return set(self.points) == set(other.points)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        """Returns Class name and bounds i.e. bottom left and
        upper left corner of cell"""
        return f"{self.__class__.__name__}{self.get_bounds()}"

    def __repr__(self):
        return str(self)


class Tetromino:
    """A simple Tetromino with 1 cell
    Initialize by passing size of cell and a TurtleScreen object for drawing
    :tests:
    >>> t = Tetromino()
    >>> t.size, t.state
    (20, 0)
    """
    rot_offsets = ((0, 0, 0, 0), ) * 4

    def __init__(self, size=20, screen=None):
        self.__size = size
        self.start = None
        self.rot_center = (0, 0)
        self.rot_bounds = None
        self.color = "white"
        self.cells = []
        self.state = 0
        self.pen = tt.RawTurtle(screen or tt.getscreen(), visible=False)

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, value):
        self.__size = value

    def draw(self, x, y, color=""):
        """Method for initial drawing of a basic Tetromino Cell requires a drawing starting
        points i.e. self.start given by x, y and an optional fill color
        a starting point and an optional color
        :Tests:
        >>> t = Tetromino()
        >>> t.start
        >>> t.color
        'white'
        >>> t.draw(0, 0, "red")
        >>> t.start
        (0, 0)
        >>> t.color
        'red'
        >>> t.cells
        [Cell(0, -20, 20, 0)]
        """
        self.start = self.start or (x, y)
        self.color = color or self.color
        self.pen.pu()
        self.pen.goto(x, y)
        self.pen.fillcolor(self.color)
        self.pen.pd()
        self.pen.begin_fill()
        points = []
        for _ in range(4):
            self.pen.fd(self.size)
            self.pen.right(90)
            x, y = [round(p) for p in self.pen.pos()]
            points.append((x,y))
        self.cells.append(Cell(self.size, color, self.pen, *points))
        self.pen.end_fill()

    def draw_bounds(self):
        """Helper method visualize shapes rotational bounds
        Comes in handy for debugging weird behavior typically when
        rot_center is not updated in sync with other moves"""
        if self.rot_bounds:
            xl, yl, xh, yh = self.rot_bounds
            points = [(xl, yl), (xl, yh), (xh, yh), (xh, yl)]
            self.pen.pu()
            self.pen.goto(points[0])
            self.pen.pd()
            for p in points + [points[0]]:
                self.pen.goto(p)
            self.update_screen()

    def redraw(self):
        """Called after a tetromino undergoes transformation
        ex. rotation, translation where cell points are changed"""
        self.pen.clear()
        self.update_bounds()
        for cell in self.cells:
            cell.draw()
        self.update_screen()

    def right(self, factor:int=1):
        """Move right by given number of steps"""
        if self.cells:
            x, y = self.start
            self.start = x + factor * self.size, y
            self.update_bounds()
            for cell in self.cells:
                cell.translate_x(factor)
            self.redraw()

    def left(self, factor:int=1):
        """Move left by given number of steps"""
        self.right(-factor)

    def up(self, factor:int=1):
        """Ascend/Climb by a step of 1"""
        x, y = self.start
        self.start = x, y + factor*self.size
        for cell in self.cells:
            cell.translate_y(factor)
        self.redraw()

    def down(self, factor:int=1):
        """Descend/Drop by step of 1"""
        self.up(-factor)

    def rotate(self):
        """Rotate clockwise by 90 around shapes' rotation center
        invokes change_state after rotation
        Ref: https://tetris.wiki/Super_Rotation_System"""
        for c in self.cells:
            c.rotate(*self.rot_center)
        self.redraw()
        self.change_state()

    def check_overlap(self, *cells: Cell, other:"Tetromino"=None):
        """TODO CX:
        Checks given cells or cells of a given Tetromino for overlap
        Useful with moves to avoid moving into occupied cells"""
        cells = other.cells if other else cells
        for other_cell in cells:
            for my_cell in self.cells:
                if other_cell == my_cell:
                    return True
        return False

    def change_state(self):
        """TODO CX:
        Increments current state by 1 upto (not including) 4.
        States must cycle through 0, 1, 2, 3 on subsequent calls
        """
        self.state = (self.state + 1) % 4

    def get_actual_bounds(self, state: int=None):
        """ TODO CX:
        Returns shape bounding box. This is calculated from
        rotational bounds (if known) and the shapes orientation/state
        We store offsets from rotational bounds on shapes where this applies
        """
        if self.rot_bounds:
            offsets = self.rot_offsets[state or self.state]
            bounds = self.rot_bounds
            return [l+o*self.size for l, o in zip(bounds, offsets)]

    def update_bounds(self):
        """TODO CX
        Updates rotation bounds (i.e. self.rot_bounds) wrt Tetromino's top left corner
        (i.e. self.start) and sets the shapes rotation center (i.e. self.rot_center).
        Must be invoked with every move/redraw of a Tetromino
        Ref: https://tetris.wiki/Super_Rotation_System
        """
        self.rot_center = (0, 0)

    def clear(self):
        """Helper to clear pen drawings on screen"""
        self.pen.clear()

    def update_screen(self):
        """Helper method to update pen drawings on screen"""
        self.pen.getscreen().update()


def draw(x, y):
    r, g, b = [randint(0, 255) for _ in range(3)]
    colr = f"#{r:02x}{g:02x}{b:02x}"
    tetro.draw(x, y, colr)


def move_tetro(key):
    global tetro
    key = "rotate" if key == "space" else key
    getattr(tetro, key.lower())()
    tetro.draw_bounds()


if __name__ == '__main__':
    # import doctest
    # doctest.testmod()
    tt.tracer(100)
    tt.ht()

    tetro = Tetromino()   # initialize tetro

    screen = tt.getscreen()
    screen.onclick(draw)
    for move in "Left Right Up Down space".split():
        screen.onkey(lambda k=move: move_tetro(k), move)
    screen.listen()

    tt.mainloop()




