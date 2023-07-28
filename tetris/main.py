import pygame
from random import choice
from os import path, system

pygame.font.init()
pygame.mixer.init()

current_dir = path.dirname(path.abspath(__file__))
sound_path = path.join(current_dir, 'assets', 'fall_piece.wav') # sound effect location
icon_path = path.join(current_dir, 'assets', 'tetris_icon.png') # icon location
#background_path = path.join(current_dir, 'assets', 'ENTER NAME HERE') #(if you want to put it) --> use .mp3 or .wav audio formats

s_width = 800
s_height = 700
play_width = 300  # where 300 // 10 = 30 width per piece
play_height = 600  # where 600 // 20 = 20 height per piece
points = 0

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# Pieces
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]
 
Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]
 
I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]
 
O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]
 
J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]
 
L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]
 
T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]
 
shapes = [S, Z, I, O, J, L, T] # all pieces in a single list
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]# color of each piece

class Piece(object):
    rows = 20
    columns = 10
    
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # 0-3 or 3-0

def create_grid(locked_positions={}):
    grid = [[(0,0,0) for x in range(10)] for x in range(20)]
 
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid

def convert_shape_format(shape) -> list:
    # Don't change this function
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
 
    return positions

def valid_space(shape, grid) -> bool:
    # Don't change this function
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True

def check_lost(positions) -> bool:
    # Don't change this function
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False

def get_shape() -> Piece:
    global shapes, shape_colors

    return Piece(5, 0, choice(shapes))

def draw_text_middle(text, size, color, surface) -> None: # prints text in the center (game over | press any key)
    font = pygame.font.SysFont('consolas', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))

def draw_grid(surface, row, col) -> None:
    sx = top_left_x
    sy = top_left_y

    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*30), (sx + play_width, sy + i * 30))  # horizontal
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * 30, sy), (sx + j * 30, sy + play_height))  # vertical

def clear_rows(grid, locked) -> None:
    """ 
    Basically, it first checks the rows to be removed, then deletes them from the grid 
    """
    global points
    inc = 0
    aux = 0

    # need to see if line is clean for shift every two lines down
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            # add positions to remove
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                    aux += 10
                except:
                    continue
    if aux>100:
        points += aux # points add

    if inc > 0:
        # removing rows
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

def draw_next_shape(shape, surface) -> None:
    font = pygame.font.SysFont('consolas', 27)
    label = font.render('Next piece', 25, (255,255,255)) # Setting the font configs for display

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*30, sy + i*30, 30, 30), 0)

    surface.blit(label, (sx + 10, sy- 30))

def draw_points(points,surface) -> None:
    font = pygame.font.SysFont('consolas', 27)
    label = font.render('Points', 25, (255,255,255))
    label_points = font.render(f'{points}', 23, (255,0,0))
    surface.blit(label,(top_left_x-175, (top_left_y+play_height/2)-120))
    surface.blit(label_points, (top_left_x - (140+len(str(points)) + (len(str(points))**2)), (top_left_y + play_height/2) - 65))

def draw_window(surface) -> None:
    surface.fill((0,0,0))
    font = pygame.font.SysFont('consolas', 40)
    label = font.render('TETRIS', 1, (255,255,255))
 
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))
 
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j* 30, top_left_y + i * 30, 30, 30), 0)
 
    # inserting the grid and border
    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 1, 1), (top_left_x, top_left_y, play_width, play_height), 2)

def main():
    global grid
    global points

    #   Loading sound effect 'Fall' -> K_SPACE
    space_fall_sound = False
    try:
        space_fall = pygame.mixer.Sound(sound_path)
        space_fall_sound = True
    except (Exception, pygame.error, FileNotFoundError) as error:
        print(f"ERROR: {error}")
        print("Sound effect '\033[1mfall\033[m' not found...")

    locked_positions = {}  # (x,y):(255,0,0) -> {piece position : respective color}
    grid = create_grid(locked_positions)
    
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock() # using Pygame built-in `time` to avoid bugs
    fall_time = 0
 
    while run:
        fall_speed = 0.25
 
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick(120) # FPS (Frames per second)

        # Peça caindo
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1

            # If the piece touch the "ground"
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT: # if the player closes the game
                run = False
                print("\033[1;31mThank you for playing my game!\033[m")
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN: # if the event is a key pressed
                if event.key == pygame.K_c or event.key == pygame.K_RSHIFT: # change piece
                    current_piece = next_piece
                    next_piece = get_shape()
                    draw_window(win)
                    pygame.display.update()

                if event.key == pygame.K_a or event.key == pygame.K_LEFT: # turn piece left
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT: # turn piece right
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1

                elif event.key == pygame.K_w or event.key == pygame.K_UP: # clockwise rotation
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

                elif event.key == pygame.K_q or event.key == pygame.K_RCTRL: # counterclockwise rotation
                    aux = current_piece.rotation
                    if current_piece.rotation > 0:
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)
                        if not valid_space(current_piece, grid):
                            current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    else:
                        current_piece.rotation = -1 % len(current_piece.shape)
                        if not valid_space(current_piece, grid):
                            current_piece.rotation = aux + 1 % len(current_piece.shape)

                if event.key == pygame.K_s or event.key == pygame.K_DOWN: # move piece down
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                if event.key == pygame.K_SPACE: # "force drop" piece
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    if space_fall_sound:
                        space_fall.play() # sound effect triggered
 
        shape_pos = convert_shape_format(current_piece)

        # add piece to grid to draw
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # If the piece falls to the ground
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            clear_rows(grid, locked_positions)

        draw_window(win)
        draw_points(points,win)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Check if the player won (50k+ points | 500 lines deleted)
        if points >= 50000:
            run = False
        elif check_lost(locked_positions): # check game over
            run = False
            
    if int(points)<50000:
        draw_text_middle("GAME OVER!", 55, (255,255,255), win)
    else:
        draw_text_middle("YOU BEAT TETRIS!", 55, (0,255,0), win)

    pygame.display.update()
    points = 0
    pygame.time.delay(2500)

def main_menu():
    #   Loading background music
    """
    try:
        pygame.mixer.music.load(background_path)
        pygame.mixer.music.set_volume(0.3)  # *volume* -> if you want to change, set 0.0 ~ 1.0
    except (FileNotFoundError, pygame.error, Exception):
        print("\033[1mBackground music not found...\033[m")
    """
    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle('PRESS ANY KEY', 40, (255, 255, 255), win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main() # loading game

    pygame.quit()

system("cls")
print(f"""
---------------------------------------
Python Tetris by @LukaMotta ~ in GitHub
https://github.com/LukaMotta
---------------------------------------
Pygame version: v{pygame.__version__}\n
""")

win = pygame.display.set_mode((s_width, s_height))

# loading icon window
try:
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
except (Exception, FileNotFoundError) as error:
    print(f"ERROR: {error}")

pygame.display.set_caption('Python Tetris by LukaMotta')
main_menu()  # start game