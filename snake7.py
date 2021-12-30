"""
Module: Snake

Authors: Sarah Haetzel
Department of Computer Science
University of San Diego

Description:
A Python implementation of greedy snake, using Tkinter and implemented
using the model-view-controller design pattern.

Iteration 7:

Final iteration of the greedy snake program. This last iteration implements
the even handler functions in the controller (the Snake class)
that were created as stub functions in iteration 5."""

import random
import tkinter as tk
from tkinter.font import Font
from enum import Enum
import time

class Snake:
    """ This is the controller """
    def __init__(self):
        """ Initializes the snake game """

        self.NUM_ROWS = 30
        self.NUM_COLS = 30
        self.DEFAULT_STEP_TIME_MILLIS = 1000
        self.wraparound_activated = False
        self.food_location = None
        self.point_rate = 0
        self.game_over_showing = False
        self.pause_clicked = False
        self.pause_time = 0
        self.restart_time = 0

        # Create model
        self.model = SnakeModel(self.NUM_ROWS, self.NUM_COLS)

        # Create view
        self.view = SnakeView(self.NUM_ROWS, self.NUM_COLS)

        # Set up step time
        self.step_time_millis = self.DEFAULT_STEP_TIME_MILLIS


        # start
        self.view.set_start_handler(self.start_handler)
        self.is_running = False

        # Pause
        self.view.set_pause_handler(self.pause_handler)

        # Reset
        self.view.set_reset_handler(self.reset_handler)

        # Quit
        self.view.set_quit_handler(self.quit_handler)

        # Wraparound
        self.view.set_wraparound_handler(self.wraparound_handler)

        # Step speed
        self.view.set_step_speed_handler(self.step_speed_handler)

        # Set the arrow key press handler
        self.view.set_arrow_key_handler(self.arrow_key_handler)

        #Initialize the game
        self.view.make_food(self.model.initial_food[0], self.model.initial_food[1])
        self.view.make_snake_head(self.model.initial_snake[0], self.model.initial_snake[1])

        # Start the simulation
        self.view.window.mainloop()

    # Start handler to execute when start button is pressed
    def start_handler(self):
        if not self.is_running:
            if self.game_over_showing == True:
                self.reset()
                self.game_over_showing = False
            if self.pause_clicked == True:
                self.pause_clicked = False
                self.restart_time = time.time()
                self.model.pause_time = self.restart_time - self.pause_time
            elif self.pause_clicked == False:
                self.model.start_time = time.time()
            self.is_running = True
            self.view.schedule_next_step(self.step_time_millis,
                                        self.continue_simulation)
                                
                                
    # Pause handler to execute when pause button is pressed
    def pause_handler(self):
        if self.is_running:
            self.view.cancel_next_step()
            self.is_running = False
            self.pause_clicked = True
            self.pause_time = time.time()

    # Reset handler to execute when reset button is pressed
    def reset_handler(self):
        self.pause_handler()
        self.reset()
        self.is_running = False
        self.start_handler()

    # Quit handler to execute when quit button is pressed
    def quit_handler(self):
        self.view.window.destroy()

    # Wraparound handler to toggle the wraparound instance variable of the model class
    def wraparound_handler(self):
        if self.model.wraparound == False:
            self.model.wraparound = True
        else:
            self.model.wraparound = False

    # Handles changes in speed when the step speed slider is dragged    
    def step_speed_handler(self, value):
        self.step_time_millis = self.DEFAULT_STEP_TIME_MILLIS//int(value)

    # Method to reset the game
    def reset(self):
        self.model.reset()
        self.view.reset()
        self.point_rate = 0.0

    # Method to continue the game
    def continue_simulation(self):
        self.one_step()
        self.view.schedule_next_step(self.step_time_millis,self.continue_simulation)
        if self.is_running == False:
            self.view.cancel_next_step()
        
    # One step method to update the view based on the model
    def one_step(self):
        self.model.one_step()
        self.view.points.set(self.model.point_standing)
        self.view.time.set(self.model.elapsed_time)
        self.view.pointrate.set(self.model.point_rate)

        if self.model.game_over:
            self.game_over()
            
        else:
    
            for row in range(self.NUM_ROWS):
                for col in range(self.NUM_COLS):
                    if self.model.state[row][col] == CellState.EMPTY:
                        self.view.make_empty(row,col)
                    if self.model.state[row][col] == CellState.FOOD:
                        self.view.make_food(row,col)
                    if self.model.state[row][col] == CellState.SNAKE:
                        self.view.make_snake(row,col)
                    if self.model.state[row][col] == CellState.SNAKE_HEAD:
                        self.view.make_snake_head(row,col)
            
    
    # Method to handle arrow key presses on the keyboard
    def arrow_key_handler(self, event):
        if event.keysym == "Up":
            self.model.set_direction("NORTH")
        elif event.keysym == "Down":
            self.model.set_direction("SOUTH")
        elif event.keysym == "Right":
            self.model.set_direction("EAST")
        elif event.keysym == "Left":
            self.model.set_direction("WEST")

    # Method to handle if the game is over
    def game_over(self):
        self.game_over_showing = True
        self.view.show_game_over()
        self.view.cancel_next_step()
        self.is_running = False

    
    
class SnakeView:

    def __init__(self, num_rows, num_cols):
        """ Initialize view of the game """
        self.CELL_SIZE = 20
        self.CONTROL_FRAME_HEIGHT = 100
        self.SCORE_FRAME_WIDTH = 200
        self.gameover_showing = False

        # Size of grid
        self.num_rows = num_rows
        self.num_cols = num_cols

        # Create window
        self.window = tk.Tk()
        self.window.title("Greedy Snake")
        
        # Create frame for grid of cells
        self.grid_frame = tk.Frame(self.window, height = num_rows * self.CELL_SIZE,
                        width = num_cols * self.CELL_SIZE, )
        self.grid_frame.grid(row = 1, column = 1)
        self.cells = self.create_cells()

        # Create frame for controls
        self.control_frame = tk.Frame(self.window, width = num_cols * self.CELL_SIZE,
                        height = self.CONTROL_FRAME_HEIGHT)
        self.control_frame.grid(row = 2, column = 1)
        self.control_frame.grid_propagate(False)

        # Add buttons to the control frame
        (self.start_button, self.pause_button,
        self.step_slider, self.reset_button,
        self.quit_button, self.wraparound_option) = self.add_buttons()




        # Create frame for score
        self.score_frame = tk.Frame(self.window, width = self.SCORE_FRAME_WIDTH,
                        height = num_rows * self.CELL_SIZE, borderwidth = 1,
                            relief = "solid")
        self.score_frame.grid(row = 1, column = 2)
        self.score_frame.grid_propagate(False)

        # Initialize a label which will display the word "score"
        self.score_text = tk.Label(self.score_frame, text = "Score", padx = 75, pady = 20)
        self.score_text.grid(row = 1, column = 1)

        # Create frame for points
        self.point_frame = tk.Frame(self.score_frame, borderwidth = 1, relief = "solid")
        self.point_frame.grid(row = 2, column = 1)

        # Initialize a label which will display the word "points"
        self.point_label = tk.Label(self.point_frame, text = "Points: ")
        self.point_label.grid(row = 1, column = 1)

        # Initialize a label which will display the user's points
        self.points = tk.StringVar()
        self.points.set(0)
        self.points_display = tk.Label(self.point_frame, textvariable = self.points)
        self.points_display.grid(row = 1, column = 2)
    
        # Create a frame for the time display
        self.time_frame = tk.Frame(self.score_frame, borderwidth = 1, relief = "solid")
        self.time_frame.grid(row = 3, column = 1)

        # Create a label which will display the word "time"
        self.time_label = tk.Label(self.time_frame, text = "Time: ")
        self.time_label.grid(row = 1, column = 1)

        # Initialize a label which will keep track of the elapsed time
        self.time = tk.StringVar()
        self.time.set(0.00)
        self.time_display = tk.Label(self.time_frame, textvariable = self.time)
        self.time_display.grid(row = 1, column = 2)
        
        # Create a frame for the point scoring rate
        self.point_rate_frame = tk.Frame(self.score_frame, borderwidth = 1, relief = "solid")
        self.point_rate_frame.grid(row = 4, column = 1)

         # Create a label which will display the word "points per second"
        self.point_rate_label = tk.Label(self.point_rate_frame, text = "Points per sec: ")
        self.point_rate_label.grid(row =1, column = 1)

        # Create a label which will display the point scoring rate
        self.pointrate = tk.StringVar()
        self.pointrate.set(0.0)
        self.point_rate_display = tk.Label(self.point_rate_frame, textvariable = self.pointrate)
        self.point_rate_display.grid(row = 1, column = 2)

        # Adjust the layout of widgets in the score frame
        self.score_frame.grid_rowconfigure(0, weight = 2)
        self.score_frame.grid_rowconfigure(1, weight = 2)
        self.score_frame.grid_rowconfigure(2, weight = 2)
        self.score_frame.grid_rowconfigure(3, weight = 2)
        self.score_frame.grid_rowconfigure(4, weight = 2)
        self.score_frame.grid_rowconfigure(5, weight = 2)
        self.score_frame.grid_rowconfigure(6, weight = 50)

    # Method to show the words "Game Over" if the game is over
    def show_game_over(self):
        self.gameover_text = tk.Label(self.score_frame,text = "Game over", font = ("Times New Roman", 20))
        self.gameover_text.grid(row = 5, column = 1)
        self.gameover_showing = True
    
    # Method to add cell widgets to the grid 
    def create_cells(self):
        cells = []
        for rows in range(self.num_rows):
            row = []
            for cols in range(self.num_cols):
                frame = tk.Frame(self.grid_frame, width = self.CELL_SIZE,
                            height = self.CELL_SIZE, borderwidth = 1,
                            relief = "solid")
                frame.grid(row = rows, column = cols)
                row.append(frame)
            cells.append(row)
        return cells

    # Method to add buttons to the control frame and configure their layout
    def add_buttons(self):
        
        # Start button which will start the game
        start_button = tk.Button(self.control_frame, text = "Start")
        start_button.grid(row = 1, column = 1)

        # Pause button which will pause the game
        pause_button = tk.Button(self.control_frame, text = "Pause")
        pause_button.grid(row = 1, column = 2)

        # Slider to change the speed of the game
        step_slider = tk.Scale(self.control_frame, from_ =1, to =10,
                 label = "Step Speed", showvalue = 0, orient = tk.HORIZONTAL)
        step_slider.grid(row = 1, column = 3)

        # Reset button which will reset the game
        reset_button = tk.Button(self.control_frame, text = "Reset")
        reset_button.grid(row = 1, column = 4)

        # Quit button which will quit the game
        quit_button = tk.Button(self.control_frame, text = "Quit")
        quit_button.grid(row = 1, column = 5)

        # Wraparound option will eliminate boundaries as a game ending obstruction
        wraparound_option = tk.Checkbutton(self.control_frame, text = "Wraparound")
        wraparound_option.grid(row = 1, column = 6)

        # Organize layout of the controls in the control frame
        self.control_frame.grid_rowconfigure(1, weight = 1)
        self.control_frame.grid_columnconfigure(0, weight = 1)
        self.control_frame.grid_columnconfigure(1, weight = 1)
        self.control_frame.grid_columnconfigure(2, weight = 1)
        self.control_frame.grid_columnconfigure(3, weight = 1)
        self.control_frame.grid_columnconfigure(4, weight = 1)
        self.control_frame.grid_columnconfigure(5, weight = 1)
        self.control_frame.grid_columnconfigure(6, weight = 1)

        return (start_button,pause_button,step_slider,reset_button,quit_button,
                wraparound_option)
    

    # Method to make the game board empty
    def empty_game_board(self, row, col):
        self.cells[row][col]['bg'] = 'white'
        self.cells[row][col].state = CellState.EMPTY

    # Method to connect the arrow key events to the handler
    def set_arrow_key_handler(self, handler):
        self.window.bind('<Up>', handler)
        self.window.bind('<Down>', handler)
        self.window.bind('<Left>', handler)
        self.window.bind('<Right>', handler)
        
    # Method to connect the start button to the start handler
    def set_start_handler(self, handler):
        self.start_button.configure(command = handler)

    # Method to connect the pause button to the pause handler
    def set_pause_handler(self, handler):
        self.pause_button.configure(command = handler)

    # Method to connect the step speed slider to its handler
    def set_step_speed_handler(self,handler):
        self.step_slider.configure(command = handler)

    # Method to connect the reset button to the reset handler
    def set_reset_handler(self, handler):
        self.reset_button.configure(command = handler)

    # Method to connect quit button to the quit handler
    def set_quit_handler(self, handler):
        self.quit_button.configure(command = handler)

    # Method to connect wraparound check box to its handler
    def set_wraparound_handler(self, handler):
        self.wraparound_option.configure(command = handler)
    
    # Method to make empty cells white
    def make_empty(self, row, column):
        self.cells[row][column]['bg'] = 'white'
    
    # Method to make food cells red
    def make_food(self, row, column):
        self.cells[row][column]['bg'] = 'red'
    
    # Method to make snake head cells black
    def make_snake_head(self, row, column):
        self.cells[row][column]['bg'] = 'black'
    
    # Method to make snake cells blue
    def make_snake(self, row, column):
        self.cells[row][column]['bg'] = "blue"

    # Method to reset the game board and game state
    def reset(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.empty_game_board(r,c)
        self.gameover_text.grid_forget()
        self.time.set(0.0)
        self.pointrate.set(0.0)
        self.points.set(0.0)
    
    # Method to schedule timed next step
    def schedule_next_step(self,step_time_millis, step_handler):
        self.start_timer_object = self.window.after(step_time_millis, step_handler)

    # Method to cancel the timed next step
    def cancel_next_step(self):
        self.window.after_cancel(self.start_timer_object)

class SnakeModel:
    def __init__(self, num_rows, num_cols):
        """ initialize the model of the game """
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.direction = None
        self.point_standing = 0.0
        self.snake_cells = []
        self.food = None
        self.snake_head = None
        self.start_time = time.time()
        self.pause_time = 0.0
        self.elapsed_time = 0
        self.time_standing = 0
        self.wraparound = False
        self.game_over = False

        # Initialize the state of the game
        self.state = [[CellState.EMPTY for c in range(0, self.num_cols)]
                        for r in range(0, self.num_rows)]

        # Initialize the game with food and a snake head
        self.initial_food = self.make_food()
        self.food = self.initial_food
        self.state[self.food[0]][self.food[1]] = CellState.FOOD
        self.initial_snake = self.place_snake_head()
        self.snake_head = self.initial_snake

    # Method to randomly place food in a empty cell
    def make_food(self):
        row = self.num_rows
        col = self.num_cols
        row_index = random.randint(0,row -1)
        col_index = random.randint(0,col -1)

        # Check to make sure the cell is empty
        while self.state[row_index][col_index] != CellState.EMPTY:
            row_index = random.randint(0,row -1)
            col_index = random.randint(0,col -1)

        self.state[row_index][col_index] = CellState.FOOD

        self.food = (row_index,col_index)
        return (row_index,col_index)     

    # Method to randomly place the snake head in a empty cell
    def place_snake_head(self):
        row = self.num_rows
        col = self.num_cols
        row_index = random.randint(0,row -1)
        col_index = random.randint(0,col -1)

        # Check to makle sure the cell is empty
        while self.state[row_index][col_index] != CellState.EMPTY:
            row_index = random.randint(0,row -1)
            col_index = random.randint(0,col -1)

        self.state[row_index][col_index] = CellState.SNAKE_HEAD
        self.snake_cells.append((row_index,col_index))

        self.initialize_direction(row_index, col_index)
        self.snake_head = (row_index, col_index)
        return((row_index,col_index))

    # Method to compute initial direction of the snake head    
    def initialize_direction(self, row_index, col_index):
        row_cutoff = (self.num_rows/2) -1
        col_cutoff = (self.num_cols/2) - 1
        if row_index >= row_cutoff and col_index >= col_cutoff:
            if row_index >= col_index:
                self.direction = Direction.NORTH
            elif col_index > row_index:
                self.direction = Direction.WEST
        
        elif row_index >= row_cutoff and col_index < col_cutoff:
            if self.num_cols - col_index >= row_index:
                self.direction = Direction.EAST
            elif self.num_cols - col_index < row_index:
                self.direction = Direction.NORTH
        
        elif col_index >= col_cutoff and row_index < row_cutoff:
            if self.num_rows - row_index >= col_index:
                self.direction = Direction.SOUTH
            elif self.num_rows - row_index < col_index:
                self.direction = Direction.WEST
        
        elif row_index < row_cutoff and col_index < col_cutoff:
            if row_index <= col_index:
                self.direction = Direction.SOUTH
            elif row_index > col_index:
                self.direction = Direction.EAST

    # Method that grows the snake and increases the score each time food is eaten 
    def grow_snake(self):
        self.point_standing += 1
        end_of_snake = self.snake_cells[-1]

        if len(self.snake_cells) > 1:
            piece_before_end = self.snake_cells[-2]

            if end_of_snake[0]-piece_before_end[0] == 1:
                new_snake_part = (end_of_snake[0] + 1, end_of_snake[1])
                
            elif end_of_snake[0] - piece_before_end[0] == -1:
                new_snake_part = (end_of_snake[0] - 1, end_of_snake[1])

            elif end_of_snake[1] - piece_before_end[1] == 1:
                new_snake_part = (end_of_snake[0], end_of_snake[1] + 1)

            elif end_of_snake[1] - piece_before_end[1] == -1:
                new_snake_part = (end_of_snake[0], end_of_snake[1] -1)
            
            self.snake_cells.append(new_snake_part)
            self.state[new_snake_part[0]][new_snake_part[1]] = CellState.SNAKE
        
        elif (len(self.snake_cells)) == 1:
            if self.direction == Direction.NORTH:
                new_snake_part = (end_of_snake[0] + 1, end_of_snake[1])
            elif self.direction == Direction.SOUTH:
                new_snake_part = (end_of_snake[0] -1, end_of_snake[1])
            elif self.direction == Direction.EAST:
                new_snake_part = (end_of_snake[0], end_of_snake[1] -1)
            elif self.direction == Direction.WEST:
                new_snake_part = (end_of_snake[0], end_of_snake[1] + 1)

            self.snake_cells.append(new_snake_part)
            self.state[new_snake_part[0]][new_snake_part[1]] = CellState.SNAKE
    
    
    # Method to advance the model one step
    def one_step(self):

        self.update_variables()
        
        current_state = self.state

        next_state = [[CellState.EMPTY for c in range(0, self.num_cols + 1)]
                        for r in range(0, self.num_rows + 1)]
        
        for r in range(0, self.num_rows):
                for c in range(0, self.num_cols):
                    if self.state[r][c] == CellState.FOOD:
                        next_state[r][c] = CellState.FOOD
        
        original_snake = self.snake_cells

        if len(self.snake_cells) >= 1:
            self.update_head()
            next_state[self.snake_head[0]][self.snake_head[1]] = CellState.SNAKE_HEAD


        original_snake.insert(0, self.snake_head)

        if len(self.snake_cells) >= 2:
            original_snake = original_snake[:-1]
            self.snake_cells = original_snake
            for i in range(1,len(self.snake_cells)):
                cell = self.snake_cells[i]
                row = cell[0]
                col = cell[1]
                next_state[row][col] = CellState.SNAKE

        
        self.test_snake_location() 
        head = self.snake_cells[0]
        row = head[0]
        col = head[1]
        next_state[row][col] = CellState.SNAKE_HEAD

        if head[0] == self.food[0] and head[1] == self.food[1]:
            self.grow_snake()
            self.food = self.make_food()
            next_state[self.food[0]][self.food[1]] = CellState.FOOD

        #If the game is over, the model is not advanced
        if self.game_over:
            self.state = current_state
        else:
            self.state = next_state   

    # Method to update the instance variables of the list snake model class
    def update_variables(self):
        self.time_standing = time.time() - self.start_time
        self.elapsed_time += self.time_standing
        self.elapsed_time -= self.pause_time
        self.pause_time = 0
        self.elapsed_time = float('{:0.2f}'.format(self.elapsed_time))
        self.start_time = time.time()
        self.point_rate = self.point_standing/self.elapsed_time
        self.point_rate = float('{:0.2f}'.format(self.point_rate))                

    # Method to test the location of the snake head
    def test_snake_location(self):
        self.game_over = False
        head = self.snake_cells[0]
        row = head[0]
        col = head[1]
        
        # If the snake hits itself the game is over
        if self.snake_cells.count(head) > 1:
            self.game_over = True

        # If the snake hits a boundary and wraparound is not activated the game is over
        elif self.is_boundary(head[0], head[1]) and self.wraparound == False:
            self.game_over = True

        # If the snake reaches a boundary and wraparound is activated the snake head is moved to the opposite side
        elif self.is_boundary(head[0], head[1]) and self.wraparound:
            if row  == self.num_rows:
                row = 0
            elif row == -1:
                row = self.num_rows -1
            elif col == self.num_cols:
                col = 0
            elif col == -1:
                col = self.num_cols -1
            
 
        self.snake_cells.remove(self.snake_cells[0])
        self.snake_head = (row, col)
        self.snake_cells.insert(0,self.snake_head)

    # Method to check if a cell is a boundary = returns True if yes
    def is_boundary(self, row, col):
        is_boundary = False
        if row == self.num_rows  or col == self.num_cols or row == -1 or col== -1:
            is_boundary = True
        return is_boundary

    # Method to update the snake head based on the direction in which it is travelling
    def update_head(self):
        head = self.snake_cells[0]

        if self.direction == Direction.NORTH:
            head = (head[0]-1, head[1])
            
        elif self.direction == Direction.SOUTH:
            head = (head[0]+1, head[1])
            
        elif self.direction == Direction.WEST:
            head = (head[0], head[1] -1)
            
        elif self.direction == Direction.EAST:
            head = (head[0], head[1] +1)
            
        self.snake_head = head

    # Method to set the direction
    def set_direction(self, direction):
        if direction == "NORTH":
            self.direction = Direction.NORTH
        elif direction == "SOUTH":
            self.direction = Direction.SOUTH
        elif direction == "WEST":
            self.direction = Direction.WEST
        elif direction == "EAST":
            self.direction = Direction.EAST
    
    # Method to make the cell at the given row and column empty 
    def make_empty(self, row, col):
        self.state[row][col] = CellState.EMPTY
    
    # Method to reset the model
    def reset(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                self.make_empty(r,c)
        self.snake_cells.clear()
        self.place_snake_head()
        self.make_food()
        self.elapsed_time = 0.0
        self.point_standing = 0


    
class CellState(Enum):
    EMPTY = 0
    FOOD = 1
    SNAKE = 2
    SNAKE_HEAD = 3

class Direction(Enum):
    NORTH = 1
    EAST = 2
    WEST = 3
    SOUTH = 4
       

if __name__ == "__main__":
   snake_game = Snake()
