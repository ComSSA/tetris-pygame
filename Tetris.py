import random
import pygame
import pygame_menu
import time
import csv


"""
10 x 20 grid
play_height = 2 * play_width

tetriminos:
    0 - S - green
    1 - Z - red
    2 - I - cyan
    3 - O - yellow
    4 - J - blue
    5 - L - orange
    6 - T - purple
"""

pygame.font.init()

# global variables

col = 10  # 10 columns
row = 20  # 20 rows
s_width = 800  # window width
s_height = 750  # window height
play_width = 300  # play window width; 300/10 = 30 width per block
play_height = 600  # play window height; 600/20 = 20 height per block
block_size = 30  # size of block

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

allscoresfile = 'allscores.csv'
filepath = 'highscore.txt'
fontpath = 'arcade.ttf'
fontpath_mario = 'mario.ttf'
logopath = 'ComSSALogo.png'
#Sets a time for the game to end automatically

MAX_TIME = 60
IMAGE_SIZE = (150, 180)
IMAGE_POSITION = ( 300, 100 )
TETRIS_TITLE_POS = ( 50, 30 )

# shapes formats

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

I = [['.....',
      '..0..',
      '..0..',
      '..0..',
      '..0..'],
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

# index represents the shape
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


# class to represent each of the pieces


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]  # choose color from the shape_color list
        self.rotation = 0  # chooses the rotation according to index


# initialise the grid
def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for x in range(col)] for y in range(row)]  # grid represented rgb tuples

    # locked_positions dictionary
    # (x,y):(r,g,b)
    for y in range(row):
        for x in range(col):
            if (x, y) in locked_pos:
                color = locked_pos[
                    (x, y)]  # get the value color (r,g,b) from the locked_positions dictionary using key (x,y)
                grid[y][x] = color  # set grid position to color

    return grid


def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]  # get the desired rotated shape from piece

    '''
    e.g.
       ['.....',
        '.....',
        '..00.',
        '.00..',
        '.....']
    '''
    for i, line in enumerate(shape_format):  # i gives index; line gives string
        row = list(line)  # makes a list of char from string
        for j, column in enumerate(row):  # j gives index of char; column gives char
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)  # offset according to the input given with dot and zero

    return positions


# checks if current position of piece in grid is valid
def valid_space(piece, grid):
    # makes a 2D list of all the possible (x,y)
    accepted_pos = [[(x, y) for x in range(col) if grid[y][x] == (0, 0, 0)] for y in range(row)]
    # removes sub lists and puts (x,y) in one list; easier to search
    accepted_pos = [x for item in accepted_pos for x in item]

    formatted_shape = convert_shape_format(piece)

    for pos in formatted_shape:
        if pos not in accepted_pos:
            if pos[1] >= 0:
                return False
    return True


# check if piece is out of board
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


# chooses a shape randomly from shapes list
def get_shape():
    return Piece(5, 0, random.choice(shapes))


# draws text in the middle
def draw_text_middle(text, size, color, surface):
    #NW added to clear screen between turns
    surface.fill((0, 0, 0))# fill the surface with black
    lines = text.splitlines()
    imp = pygame.image.load(logopath).convert()
    imp = pygame.transform.scale( imp, IMAGE_SIZE)
    font = pygame.font.Font(fontpath, size, bold=False, italic=True)
    tetrislabel = font.render( "ComSSA   Tetris    Competition", 1, color)
    label = font.render(text, 1, color)

    #NW Added to allow to display multiple lines
    for i, line in enumerate(lines):
        surface.blit(font.render(line, 1, color), (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2) + 50*i))

    surface.blit(imp, IMAGE_POSITION)
    surface.blit( tetrislabel, TETRIS_TITLE_POS)


# draws the lines of the grid for the game
def draw_grid(surface):
    r = g = b = 0
    grid_color = (r, g, b)

    for i in range(row):
        # draw grey horizontal lines
        pygame.draw.line(surface, grid_color, (top_left_x, top_left_y + i * block_size),
                         (top_left_x + play_width, top_left_y + i * block_size))
        for j in range(col):
            # draw grey vertical lines
            pygame.draw.line(surface, grid_color, (top_left_x + j * block_size, top_left_y),
                             (top_left_x + j * block_size, top_left_y + play_height))


# clear a row when it is filled
def clear_rows(grid, locked):
    # need to check if row is clear then shift every other row above down one
    increment = 0
    for i in range(len(grid) - 1, -1, -1):      # start checking the grid backwards
        grid_row = grid[i]                      # get the last row
        if (0, 0, 0) not in grid_row:           # if there are no empty spaces (i.e. black blocks)
            increment += 1
            # add positions to remove from locked
            index = i                           # row index will be constant
            for j in range(len(grid_row)):
                try:
                    del locked[(j, i)]          # delete every locked element in the bottom row
                except ValueError:
                    continue

    # shift every row one step down
    # delete filled bottom row
    # add another empty row on the top
    # move down one step
    if increment > 0:
        # sort the locked list according to y value in (x,y) and then reverse
        # reversed because otherwise the ones on the top will overwrite the lower ones
        for key in sorted(list(locked), key=lambda a: a[1])[::-1]:
            x, y = key
            if y < index:                       # if the y value is above the removed index
                new_key = (x, y + increment)    # shift position to down
                locked[new_key] = locked.pop(key)

    return increment


# draws the upcoming piece
def draw_next_shape(piece, surface):
    font = pygame.font.Font(fontpath, 30)
    label = font.render('Next shape', 1, (255, 255, 255))

    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)

    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (start_x + j*block_size, start_y + i*block_size, block_size, block_size), 0)

    surface.blit(label, (start_x, start_y - 30))

    # pygame.display.update()


#NW Changed to takes list of top scores
# draws the content of the window
def draw_window(surface, grid, seconds_remaining, top_scores, score=0):
    surface.fill((0, 0, 0))  # fill the surface with black

    pygame.font.init()  # initialise font
    font = pygame.font.Font(fontpath_mario, 65, bold=True)
    label = font.render('TETRIS', 1, (255, 255, 255))  # initialise 'Tetris' text with white

    surface.blit(label, ((top_left_x + play_width / 2) - (label.get_width() / 2), 30))  # put surface on the center of the window

    # current score
    font = pygame.font.Font(fontpath, 30)
    label = font.render('SCORE   ' + str(score) , 1, (255, 255, 255))

    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)

    surface.blit(label, (start_x, start_y + 200))

    #NW Added a countdown timer 
    clock_x = top_left_x - 200
    clock_y = top_left_y + 200

    clocklabel = font.render( 'TIME   ' + str(round(seconds_remaining)) + '   s', 2, (255, 255, 255))
    surface.blit( clocklabel, (clock_x, clock_y) )
    #End of timer

    #NW Added comssa logo during gameplay
    imp = pygame.image.load(logopath).convert()
    imp = pygame.transform.scale( imp, (150, 180))
    surface.blit( imp, (50, 50) )

    # last score
    
#NW Can change here to include all top three player if needed. 
    last_score = top_scores[0][1]
    label_hi = font.render('TOP  SCORE   ' + str(last_score), 1, (255, 255, 255))
#NW Changed extra unnecessary math
    start_x_hi = top_left_x - 220
    start_y_hi = top_left_y + 400
    surface.blit(label_hi, (start_x_hi, start_y_hi))

#NW Added student ID of top player.
    top_id = top_scores[0][0]
    label_id = font.render('TOP  PLAYER ', 1, (255, 255, 255))
    y_id = start_y_hi - 100
    surface.blit(label_id, (start_x_hi, y_id))
    surface.blit( font.render(str(top_id), 1, (255,255,255) ), (start_x_hi, y_id+30))

    # draw content of the grid
    for i in range(row):
        for j in range(col):
            # pygame.draw.rect()
            # draw a rectangle shape
            # rect(Surface, color, Rect, width=0) -> Rect
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # draw vertical and horizontal grid lines
    draw_grid(surface)

    # draw rectangular border around play area
    border_color = (255, 255, 255)
    pygame.draw.rect(surface, border_color, (top_left_x, top_left_y, play_width, play_height), 4)

    #pygame.display.update()


# update the score txt file with high score
#NW Changed to track top 3 scores in order with student number
def update_score_file(new_score, playerID ):

    scores = get_max_scores()
    scores = update_max_scores( new_score, playerID, scores)

    with open( filepath, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        for line in scores:
            csv_writer.writerow(line)


#Updates the list of 3 scores if new score is higher
def update_max_scores( new_score, playerID, scores):

    i = 2
    while( ( new_score > int(scores[i][1]) ) and ( i >= 0 ) ) :
        i = i - 1

    scores.insert( (i+1), [playerID, new_score])
    #Remove lowest score, only save 3
    scores.pop()

    return scores




#NW Changed to read new file format with top 3 scores
# get the high score from the file
def get_max_scores():
    with open( filepath, "r") as file:
        scores = list( csv.reader(file, delimiter=",") )
    return scores


def main(window, start_time, playerID):
    locked_positions = {}
    create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    # fall_speed = 0.35
    fall_speed = 0.5
    level_time = 0
    score = 0
    top_scores = get_max_scores()
    #Takes just the top score, can be updated to include all three scores
    last_score = int(top_scores[0][1])

    while run:
        # need to constantly make new grid as locked positions always change
        grid = create_grid(locked_positions)

        # helps run the same on every computer
        # add time since last tick() to fall_time
        fall_time += clock.get_rawtime()  # returns in milliseconds
        level_time += clock.get_rawtime()

        clock.tick()  # updates clock

        if level_time/1000 > 5:    # make the difficulty harder every 10 seconds
            level_time = 0
            if fall_speed > 0.15:   # until fall speed is 0.15
                fall_speed -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                # since only checking for down - either reached bottom or hit another piece
                # need to lock the piece position
                # need to generate new piece
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1  # move x position left
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1  # move x position right
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1

                elif event.key == pygame.K_DOWN:
                    # move shape down
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                if event.key == pygame.K_UP:
                    # rotate shape
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

                #NW Added "SPACE" for drop condition
                elif event.key == pygame.K_SPACE:
                    #Moves piece to last valid position
                    while( valid_space(current_piece, grid) ):
                        current_piece.y += 1
                    #Undoes last loop to put piece back in a valid spot. 
                    current_piece.y -= 1
                
        piece_pos = convert_shape_format(current_piece)

        # draw the piece on the grid by giving color in the piece locations
        for i in range(len(piece_pos)):
            x, y = piece_pos[i]
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:  # if the piece is locked
            for pos in piece_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color       # add the key and value in the dictionary
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10    # increment score by 10 for every row cleared
        #NW removed as was doing a file read every score update, too much potential for errors
            #update_score(score, playerID)
            top_scores = update_max_scores( score, playerID, top_scores)

        #SM Use time module instead of pygame.time to work out seconds remaining
        seconds_remaining = MAX_TIME - (time.time() - start_time)

        draw_window(window, grid, seconds_remaining, top_scores, score)
        draw_next_shape(next_piece, window)
        pygame.display.update()

        #NW Added condition if max time reached to also end game
        if ( check_lost(locked_positions) ) or ( seconds_remaining <= 0 ):
            run = False
            update_all_scores( score, playerID )
            update_score_file( score, playerID )
    
    # SM Added quick results menu
    global comssa_theme
    results_menu = pygame_menu.Menu(
        height=s_height,
        title='Settings',
        theme=comssa_theme,
        width=s_width
    )

    #NW Added condition to show whether time expired or lost
    if( seconds_remaining <= 0 ):
        # draw_text_middle("Times   Up\nYour  Score   " + str(score), 40, (255, 255, 255), window)
        results_menu.add.label(
            "Times Up",
            font_size=60,
            font_name='arcade.ttf',
            font_color=(255, 255, 255)
        )
    else:
        # draw_text_middle("You   Crashed\nYour  Score   " + str(score), 40, (255, 255, 255), window)
        results_menu.add.label(
            "You Crashed",
            font_size=60,
            font_name='arcade.ttf',
            font_color=(255, 255, 255)
        )

    results_menu.add.label(
        "Your Score " + str(score),
        font_size=60,
        font_name='arcade.ttf',
        font_color=(255, 255, 255),
    )

    # vertical space
    results_menu.add.vertical_margin(50)

    results_menu.add.button(
        'Return to Main Menu',
        # exit menu
        results_menu.disable,
        align=pygame_menu.locals.ALIGN_CENTER,
        font_size=32
    )

    results_menu.mainloop(win)

    reset()
    #pygame.quit()


def update_all_scores( score, playerID ):
    with open( 'allscores.csv', 'a') as allscoresfile:
        allscoresfile.write(str(playerID) + "," + str(score) + "\n")
    allscoresfile.close()

def main_menu(window, playerID):
    run = True
    start_time = time.time()
    while run:
        draw_text_middle('Press any key to begin', 50, (255, 255, 255), window)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                main(window, start_time, playerID)
            #Added to set main window after a play
                pygame.display.update()

    pygame.quit()
    #sys.exit()

# SM custom theme for menu
comssa_theme = pygame_menu.themes.THEME_DARK.copy()
# background color #4459a5
comssa_theme.background_color = (68, 89, 165)
# no default title
comssa_theme.title = False
# selection colour for input with 30% transparency for color #f5831f 
comssa_theme.cursor_selection_color = (245, 131, 31, 80)
# cursor color #f5831f
comssa_theme.cursor_color = (245, 131, 31)

# SM add reset function to restart the game
def reset():
    # Initialize pygame
    pygame.init()
    
    # SM added settings menu
    menu = pygame_menu.Menu(
        height=s_height,
        title='Settings',
        theme=comssa_theme,
        width=s_width
    )

    playerID = 0

    # ComSSA logo
    logo = pygame_menu.baseimage.BaseImage(
        image_path='ComSSALogo.png',
        drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL
    )
    menu.add.image(logo)

    menu.add.label(
        'ComSSA   Tetris',
        align=pygame_menu.locals.ALIGN_CENTER,
        font_size=50,
        # color of white
        font_color=(255, 255, 255),
        font_name='arcade.ttf'
    )

    menu.add.text_input(
        'Enter your Student/Staff ID: ',
        default='12345678',
        textinput_id='player_id',
        font_size=32,
    )

    menu.add.button(
        'PLAY',
        # exit menu
        menu.disable,
        align=pygame_menu.locals.ALIGN_CENTER,
        font_size=32
    )

    menu.mainloop(win)

    # SM get the player ID from the menu
    playerID = menu.get_input_data()['player_id']

    # SM after this menu, run the actual game
    print("Player ID: " + str(playerID))
    main_menu(win, playerID)

if __name__ == '__main__':
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('ComSSA Tetris')

    reset()
    