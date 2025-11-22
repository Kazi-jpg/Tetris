import turtle as tt
from random import choice
from itertools import cycle
from typing import Optional

from tetrominoes import I, J, L, S, Z, O, T
from tetro_base import Tetromino, Cell

SHAPE_CLASSES = cycle((O, I, J, L, S, Z, T))


class World(Tetromino):
    """Represents the tetris world
    defined by a grid of 20x10 (visible) cells
    Components:
        - tetro: the currently active Tetromino
        - stack:  the stack of past Tetromino blocks
    Tetro moves:
        - down -> key Down: Drops active tetro by 1 cell
        - Left -> key Left: Shifts active tetro right by 1 cell
        - right -> key Right: Shifts active tetro left by 1 cell
        - rotate -> key Up: Rotates active tetro 90 clockwise
        - hard_drop -> key space: Drops active tetro till stop at stack or bottom

    A new tetro is spawned in cell 22 (i.e. out of visible grid)
    An active tetro is dropped by one cell each play cycle until
    it's at the bottom of the world or
    its bottom row of cells collides with the stack.
    An active tetro is absorbed by the Stack at this point and a new tetro
    is spawned.
    The game is over once the stack hits the world ceiling i.e.
    highest row in stack is 19"""
    def __init__(self, size=1, screen=None):
        super().__init__(size, screen)
        self.screen = self.pen.getscreen()
        self.stack = self.tetro = None
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_active = True
        self.paused = False
        self.message_pen = None
        self.init_screen()

    def init_screen(self, **settings):
        s = self.size
        xl, yl, xu, yu = -5, 0, 15, 20
        self.screen.setworldcoordinates(xl*s, yl*s, xu*s, yu*s)
        self.screen.bgcolor("white")
        # Reset world grid drawing state
        self.pen.clear()
        self.cells.clear()
        self.start = None
        self.draw(0, s, "#253525")
        if self.stack is None:
            self.stack = Stack(self)
        else:
            self.stack.reset()
        self.spawn()
        self.display_score()

    def draw(self, x, y, color=""):
        """Draws the world, a 20x10 grid"""
        for row in range(20):
            for col in range(10):
                super().draw(x, y, color)
                x += self.size
            x, y = 0, y+self.size
        self.screen.update()

    def spawn(self):
        """create a new/active tetro"""
        self.tetro = next(SHAPE_CLASSES)(self.size, self.screen)
        x, y = 4*self.size, 22*self.size
        self.tetro.draw(x, y)
        self.screen.update()

    def get_tetro(self):
        """Returns the current active tetromino"""
        return self.tetro

    def move(self, instr="down"):
        """If game over (check state of stack) invoke game_over
        Otherwise check if move is acceptable (i.e. invoke ok_move on stack)
         and invoke move on tetro if move is ok."""
        if not self.game_active or self.paused:
            return
            
        if self.stack.game_over:
            return self.game_over()

        t = self.tetro
        option = dict(down=t.down, right=t.right, left=t.left, rotate=t.rotate)
        if self.stack.ok_move(t, instr):
            option.get(instr)()

    def hard_drop(self):
        """While ok, drop current tetro by a cell until it hits bottom or stack"""
        if not self.game_active or self.stack.game_over or self.paused:
            return
            
        # Keep dropping until we can't anymore
        while self.stack.ok_move(self.tetro, "down"):
            self.tetro.down()
        
        # One more move to trigger absorption
        self.move("down")

    def play(self):
        """Main game loop - automatically drops tetromino every cycle"""
        if not self.game_active or self.stack.game_over or self.paused:
            return
            
        self.move("down")
        
        # Calculate delay based on level (gets faster as level increases)
        delay = max(100, 500 - (self.level - 1) * 50)
        self.screen.ontimer(self.play, delay)

    def game_over(self):
        """Simplest game over graphic I could think of
        randomly reset cell colors to yellow or green and redraw"""
        if not self.game_active:
            return
        self.game_active = False
        colors = ("green", "yellow")

        # Recolor background grid
        for c in self.cells:
            c.color = choice(colors)
        self.redraw()

        # Clear stacked blocks so the background pattern shows through
        if self.stack:
            self.stack.pen.clear()

        # Clear active tetromino drawing if it is still visible
        if self.tetro:
            self.tetro.pen.clear()
        
        # Display game over message
        if self.message_pen is None:
            self.message_pen = tt.RawTurtle(self.screen)
            self.message_pen.hideturtle()
            self.message_pen.pu()
        pen = self.message_pen
        pen.clear()

        # Draw a white panel behind the text for readability
        panel_left = 2 * self.size
        panel_top = 12 * self.size
        panel_width = 6 * self.size
        panel_height = 6 * self.size
        pen.goto(panel_left, panel_top)
        pen.setheading(0)
        pen.color("black")
        pen.fillcolor("white")
        pen.pd()
        pen.begin_fill()
        for _ in range(2):
            pen.fd(panel_width)
            pen.right(90)
            pen.fd(panel_height)
            pen.right(90)
        pen.end_fill()
        pen.pu()

        # Centered messages
        pen.goto(5*self.size, 10.5*self.size)
        pen.color("red")
        pen.write("GAME OVER", align="center", font=("Arial", 24, "bold"))
        pen.goto(5*self.size, 9*self.size)
        pen.write(f"Score: {self.score}", align="center", font=("Arial", 16, "normal"))
        pen.goto(5*self.size, 7.5*self.size)
        pen.color("black")
        pen.write("Press R to restart", align="center", font=("Arial", 14, "normal"))
        self.screen.update()

    def reset_game(self):
        """Reset world state after game over"""
        if self.tetro:
            self.tetro.pen.clear()
        self.tetro = None
        if self.stack:
            self.stack.reset()
        if hasattr(self, "score_pen"):
            self.score_pen.clear()
        if self.message_pen:
            self.message_pen.clear()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_active = True
        self.paused = False
        self.init_screen()
        # Restart automatic drop loop
        self.screen.ontimer(self.play, 500)

    def toggle_pause(self):
        """Toggle paused state and manage pause overlay"""
        if not self.game_active:
            return
        # keep existing toggle behaviour available
        self.paused = not self.paused
        if self.paused:
            if self.message_pen is None:
                self.message_pen = tt.RawTurtle(self.screen)
                self.message_pen.hideturtle()
                self.message_pen.pu()
            pen = self.message_pen
            pen.clear()
            pen.goto(5*self.size, 10*self.size)
            pen.color("blue")
            pen.write("PAUSED", align="center", font=("Arial", 28, "bold"))
            pen.goto(5*self.size, 8*self.size)
            pen.color("black")
            pen.write("Click Play button to resume", align="center", font=("Arial", 16, "normal"))
        else:
            # Resume gameplay loop
            if self.message_pen:
                self.message_pen.clear()
            self.screen.ontimer(self.play, max(100, 500 - (self.level - 1) * 50))
        self.screen.update()

    def pause_game(self):
        """Explicitly pause the game and show overlay."""
        if not self.game_active:
            return
        if self.message_pen is None:
            self.message_pen = tt.RawTurtle(self.screen)
            self.message_pen.hideturtle()
            self.message_pen.pu()
        self.paused = True
        pen = self.message_pen
        pen.clear()
        pen.goto(5*self.size, 10*self.size)
        pen.color("blue")
        pen.write("PAUSED", align="center", font=("Arial", 28, "bold"))
        pen.goto(5*self.size, 8*self.size)
        pen.color("black")
        pen.write("Click Play button to resume", align="center", font=("Arial", 16, "normal"))
        self.screen.update()

    def resume_game(self):
        """Explicitly resume the game and remove overlay."""
        if not self.game_active:
            return
        if not self.paused:
            return
        self.paused = False
        if self.message_pen:
            self.message_pen.clear()
        # Resume gameplay loop
        self.screen.ontimer(self.play, max(100, 500 - (self.level - 1) * 50))
        self.screen.update()
    def update_score(self, lines):
        """Update score based on number of lines cleared
        Scoring: 1 line=100, 2 lines=300, 3 lines=500, 4 lines=800"""
        if lines == 0:
            return
            
        score_map = {1: 100, 2: 300, 3: 500, 4: 800}
        points = score_map.get(lines, 0) * self.level
        self.score += points
        self.lines_cleared += lines
        
        # Level up every 10 lines
        self.level = (self.lines_cleared // 10) + 1
        
        self.display_score()

    def display_score(self):
        """Display current score, lines, and level"""
        # Clear previous score display
        if hasattr(self, 'score_pen'):
            self.score_pen.clear()
        else:
            self.score_pen = tt.RawTurtle(self.screen)
            self.score_pen.hideturtle()
            self.score_pen.pu()
        
        self.score_pen.goto(11*self.size, 18*self.size)
        self.score_pen.color("black")
        self.score_pen.write(f"Score: {self.score}", font=("Arial", 12, "bold"))
        self.score_pen.goto(11*self.size, 16*self.size)
        self.score_pen.write(f"Lines: {self.lines_cleared}", font=("Arial", 12, "normal"))
        self.score_pen.goto(11*self.size, 14*self.size)
        self.score_pen.write(f"Level: {self.level}", font=("Arial", 12, "normal"))
        # Buttons on the right side now control Pause/Play
        self.score_pen.goto(11*self.size, 12*self.size)
        self.score_pen.write("Use buttons to Pause / Play", font=("Arial", 11, "normal"))


class Stack(Tetromino):
    def __init__(self, world: World):
        super().__init__(world.size, world.screen)
        self.state_matrix = None
        self.world = world
        self.game_over = False
        self.init_state_matrix()

    def reset(self):
        """Clear stack state for a new game"""
        self.pen.clear()
        self.cells.clear()
        self.init_state_matrix()
        self.game_over = False

    def init_state_matrix(self):
        """Initializes stack state i.e.  20x10 table with 0's """
        self.state_matrix = [[0 for _ in range(10)] for _ in range(20)]

    def _rebuild_state_matrix(self):
        """Recompute the occupancy grid from current cells"""
        self.init_state_matrix()
        overflow = False
        max_row = -1
        max_top = float("-inf")
        for cell in self.cells:
            xl, yl, xh, yh = cell.get_bounds()
            row = int(yl // self.size)
            col = int(xl // self.size)
            max_row = max(max_row, row)
            max_top = max(max_top, yh)
            if row >= 20 or col < 0 or col >= 10:
                overflow = True
                continue
            if 0 <= row < 20 and 0 <= col < 10:
                self.state_matrix[row][col] = 1
        if overflow or max_row >= 19 or max_top >= 20 * self.size:
            self.game_over = True

    def _validate_cells(self, cells, *, absorb=False, tetro: Optional[Tetromino] = None, enforce_bottom=False) -> bool:
        """Check whether proposed cells are in bounds and collision-free"""
        for cell in cells:
            xl, yl, xh, yh = cell.get_bounds()
            if xl < 0 or xh > 10 * self.size:
                return False
            if enforce_bottom and yl < 0:
                if absorb and tetro:
                    self.absorb(tetro=tetro)
                return False
            row = int(yl // self.size)
            col = int(xl // self.size)
            if 0 <= row < 20 and 0 <= col < 10 and self.state_matrix[row][col]:
                if absorb and tetro:
                    self.absorb(tetro=tetro)
                return False
        return True

    def ok_move(self, tetro: Tetromino, move="down") -> bool:
        """Given a Tetromino and intended move returns a boolean
        indicating whether move is OK.
        NB:
            - Cannot move outside world boundaries
            - Cannot overlap with the stack
            - Once the base of a tetromino touches the stack is absorbed
        Hint (checking overlap with stack):
            Use check_overlap, and dunder methods
            that return cells for proposed move from tetro
              Ex. for a right move check_overlap(*[c >> 1 for c in tetro.cells])
            without drawing or affecting the state of the world"""
        if move == "down":
            next_cells = [-c for c in tetro.cells]
            return self._validate_cells(next_cells, absorb=True, tetro=tetro, enforce_bottom=True)

        if move == "right":
            next_cells = [c >> 1 for c in tetro.cells]
            return self._validate_cells(next_cells)

        if move == "left":
            next_cells = [c << 1 for c in tetro.cells]
            return self._validate_cells(next_cells)

        if move == "rotate":
            rotated_cells = [c * tetro.rot_center for c in tetro.cells]
            return self._validate_cells(rotated_cells, enforce_bottom=True)

        return False

    def absorb(self, *cells, tetro: Tetromino = None):
        """Absorb tetromino into the stack and spawn new one"""
        if tetro:
            # Clone tetromino cells so stack owns its drawing state
            new_cells = [
                Cell(self.size, cell.color, self.pen, *cell.points)
                for cell in tetro.cells
            ]
            tetro.pen.clear()
            tetro.cells.clear()

            self.cells.extend(new_cells)
            self._rebuild_state_matrix()
            self.redraw()

            # Check for completed lines and rearrange
            self.rearrange()

            # Check for game over condition or spawn next tetromino
            self.request_tetro()

    def request_tetro(self):
        """Invokes spawn on world after a tetro is absorbed
        Sets game_over property to True if height is greater than 19"""
        if self.game_over:
            self.world.game_over()
            return

        # Check if any cells occupy the top visible row
        for col in range(10):
            if self.state_matrix[19][col] == 1:
                self.game_over = True
                self.world.game_over()
                return

        # Spawn new tetromino
        self.world.spawn()

    def rearrange(self):
        """Rearrange stack after absorbing a tetro
            - Find row index of full lines i.e. all cells no zeros
            - Clear out full lines
            - Drop lines above each deleted line (starting from the top)
        """
        lines_to_clear = [row for row in range(20) if all(self.state_matrix[row])]
        if not lines_to_clear:
            return

        lines_to_clear.sort()
        cleared_set = set(lines_to_clear)
        updated_cells = []
        for cell in self.cells:
            xl, yl, xh, yh = cell.get_bounds()
            row = int(yl // self.size)
            if row in cleared_set:
                continue
            drop = sum(1 for cleared in lines_to_clear if cleared < row)
            if drop:
                cell.translate_y(-drop)
            updated_cells.append(cell)

        self.cells = updated_cells
        self._rebuild_state_matrix()
        self.world.update_score(len(lines_to_clear))
        self.redraw()


if __name__ == '__main__':
    tt.ht()
    tt.tracer(10000)
    w = World()

    scr = tt.getscreen()
    
    # Key bindings
    scr.onkey(lambda: w.move("down"), "Down")
    scr.onkey(lambda: w.move("right"), "Right")
    scr.onkey(lambda: w.move("left"), "Left")
    scr.onkey(lambda: w.move("rotate"), "Up")
    scr.onkey(lambda: w.hard_drop(), "space")
    scr.onkey(lambda: w.reset_game(), "r")
    scr.onkey(lambda: w.reset_game(), "R")

    # Draw Pause and Play buttons on the right side and bind clicks
    def make_button(label, x, y, color, handler, buttons_list):
        btn = tt.RawTurtle(scr)
        btn.hideturtle()
        btn.pu()
        btn.goto(x, y)
        btn.setheading(0)
        btn.color("black")
        btn.fillcolor(color)
        btn.pd()
        btn.begin_fill()
        width = 2 * w.size
        height = 1 * w.size
        for _ in range(2):
            btn.fd(width)
            btn.right(90)
            btn.fd(height)
            btn.right(90)
        btn.end_fill()
        btn.pu()
        # center label
        btn.goto(x + width/2, y - height/2)
        btn.color("white" if color != "white" else "black")
        btn.write(label, align="center", font=("Arial", 10, "bold"))
        # Register button bounds and handler in shared list
        buttons_list.append({"x": x, "y": y, "w": width, "h": height, "handler": handler})
        return btn

    # Button positions (right-side panel)
    bx = 11 * w.size
    by_play = 9 * w.size
    by_pause = 6.5 * w.size
    buttons = []
    play_btn = make_button("PLAY", bx, by_play, "green", lambda: w.resume_game(), buttons)
    pause_btn = make_button("PAUSE", bx, by_pause, "red", lambda: w.pause_game(), buttons)

    # Single onclick handler that checks all registered button bounds
    def _on_click(xc, yc):
        for b in buttons:
            bx = b["x"]
            by = b["y"]
            wdt = b["w"]
            hgt = b["h"]
            if bx <= xc <= bx + wdt and by - hgt <= yc <= by:
                try:
                    b["handler"]()
                except Exception:
                    pass
                break

    scr.onclick(_on_click)
    
    # Start game loop
    scr.ontimer(w.play, 500)
    
    tt.listen()
    tt.done()