import pygame
import cell
import numpy as np
import math
from bitarray import bitarray
from bitarray.util import int2ba

PROJECTION_MATRIX = np.array([[1,0,0],[0,1,0],[0,0,0]])
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
DIMENSION = 5             ## DIMENSION DEFINED HERE : 5-10 recommended for gameplay. Anything higher is entertaining to build but not to play ##
IS_EVEN = DIMENSION % 2 == 0
CELL_SIZE = 50

def draw_grid_numbers(cellgrid, points_2d: list) -> None:

    index = 0
    for i in range(cellgrid.dim):
        for j in range(cellgrid.dim):
            for k in range(cellgrid.dim):
                cellDigit = font.render(f"{cellgrid.grid[i][j][k].connect_vector}", False, black, colors[cellgrid.grid[i][j][k].state])
                screen.blit(cellDigit, (points_2d[index][0]*600/cellgrid.dim+WINDOW_WIDTH/2, points_2d[index][1]*600/cellgrid.dim+WINDOW_HEIGHT/2))
                index += 1   

def draw_grid_skeletal(cellgrid, ang_x, ang_y, ang_z, full_grid: bool, player_position) -> None:

    lines = get_2d_skeleton(cellgrid, ang_x, ang_y, ang_z)
    if player_position == (DIMENSION-1, DIMENSION-1, DIMENSION-1):
        for line in lines:
            (point1, point2) = line
            (x1, y1) = point1;
            (x2, y2) = point2;
            pygame.draw.line(screen, green, (x1*600/DIMENSION+WINDOW_WIDTH/2, y1*600/DIMENSION+WINDOW_HEIGHT/2),
                            (x2*600/DIMENSION+WINDOW_WIDTH/2, y2*600/DIMENSION+WINDOW_HEIGHT/2), 2)

        for line in lines:
            (point1, point2) = line
            (x1, y1) = point1;
            pygame.draw.circle(screen, green, (x1*600/DIMENSION+WINDOW_WIDTH/2, y1*600/DIMENSION+WINDOW_HEIGHT/2), 3)
        
        # draw goal point
        (goal_point, point2) = lines[-1]
        (x1, y1) = goal_point
        pygame.draw.circle(screen, yellow, (x1*600/DIMENSION+WINDOW_WIDTH/2, y1*600/DIMENSION+WINDOW_HEIGHT/2), 5)

        # draw current point
        (x1, y1) = get_specific_point_2dcoords(ang_x, ang_y, ang_z, player_position)
        pygame.draw.circle(screen, red, (x1*600/DIMENSION+WINDOW_WIDTH/2, y1*600/DIMENSION+WINDOW_HEIGHT/2), 5)
        return True

    elif full_grid:
        for line in lines:
            (point1, point2) = line
            (x1, y1) = point1;
            (x2, y2) = point2;
            pygame.draw.line(screen, grey, (x1*600/DIMENSION+WINDOW_WIDTH/2, y1*600/DIMENSION+WINDOW_HEIGHT/2),
                            (x2*600/DIMENSION+WINDOW_WIDTH/2, y2*600/DIMENSION+WINDOW_HEIGHT/2), 2)

        for line in lines:
            (point1, point2) = line
            (x1, y1) = point1;
            pygame.draw.circle(screen, white, (x1*600/DIMENSION+WINDOW_WIDTH/2, y1*600/DIMENSION+WINDOW_HEIGHT/2), 3)
        
        # draw goal point
        (goal_point, point2) = lines[-1]
        (x1, y1) = goal_point
        pygame.draw.circle(screen, yellow, (x1*600/DIMENSION+WINDOW_WIDTH/2, y1*600/DIMENSION+WINDOW_HEIGHT/2), 5)

        # draw current point
        (x1, y1) = get_specific_point_2dcoords(ang_x, ang_y, ang_z, player_position)
        pygame.draw.circle(screen, red, (x1*600/DIMENSION+WINDOW_WIDTH/2, y1*600/DIMENSION+WINDOW_HEIGHT/2), 5)


    else:
        for line in lines:
            (point1, point2) = line
            (x1, y1) = point1;
            (x2, y2) = point2;
            pygame.draw.line(screen, blue, (x1*600/DIMENSION+WINDOW_WIDTH/2, y1*600/DIMENSION+WINDOW_HEIGHT/2),
                            (x2*600/DIMENSION+WINDOW_WIDTH/2, y2*600/DIMENSION+WINDOW_HEIGHT/2), 2)

        for line in lines:
            (point1, point2) = line
            (x1, y1) = point1;
            pygame.draw.circle(screen, black, (x1*600/DIMENSION+WINDOW_WIDTH/2, y1*600/DIMENSION+WINDOW_HEIGHT/2), 3)

# returns a list of numpy 1x3 arrays for drawing the 3D number grid
def generate_points_list(dim) -> list:
    points = []
    if dim%2 == 0: # if the dimension is even, don't floor the coordinate value
        for x in range(dim):
            for y in range(dim):
                for z in range(dim):
                    points.append(np.array([[x-((dim-1)/2)],[y-((dim-1)/2)],[z-((dim-1)/2)]]))
    else: # if the dimension is odd, floor the coordinate value
        for x in range(dim):
            for y in range(dim):
                for z in range(dim):
                    points.append(np.array([[x-(dim//2)],[y-(dim//2)],[z-(dim//2)]]))
    return points

def get_2d_points(points, ang_x, ang_y, ang_z) -> list:

    # first, define the rotation matrices depending on the angles provided
    rotation_x = np.array([[1, 0, 0],[0, math.cos(ang_x), -math.sin(ang_x)],[0, math.sin(ang_x), math.cos(ang_x)]])
    rotation_y = np.array([[math.cos(ang_y), 0, math.sin(ang_y)],[0, 1, 0],[-math.sin(ang_y), 0, math.cos(ang_y)]])
    rotation_z = np.array([[math.cos(ang_z), -math.sin(ang_z), 0],[math.sin(ang_z), math.cos(ang_z), 0],[0, 0, 1]])

    # define the new points list that will be returned
    points_2d = []

    # now, for every point in points, find the 2D point associated with it
    for point in points:
        new_point = PROJECTION_MATRIX @ rotation_z @ rotation_y @ rotation_x @ point
        points_2d.append((new_point[0][0], new_point[1][0]))

    return points_2d

def generate_raw_line_list(cellgrid: cell.CellGrid) -> list:

    raw_line_list = []

    for i in range(DIMENSION):
        for j in range(DIMENSION):
            for k in range(DIMENSION):

                point1 = (i,j,k)        # create the initial point location
                direction = cellgrid.grid[i][j][k].connect_vector

                if direction == -1:
                    continue
                else:
                    point2 = tuple(map(lambda a, b: a+b, point1, cell.DIRECTIONS[direction]))

                line = (point1, point2)
                raw_line_list.append(line);

    return raw_line_list

def get_2d_skeleton(cellgrid: cell.CellGrid, ang_x, ang_y, ang_z) -> list:

    raw_list = generate_raw_line_list(cellgrid)
    line_list = []
    rotated_line_list = []

    rotation_x = np.array([[1, 0, 0],[0, math.cos(ang_x), -math.sin(ang_x)],[0, math.sin(ang_x), math.cos(ang_x)]])
    rotation_y = np.array([[math.cos(ang_y), 0, math.sin(ang_y)],[0, 1, 0],[-math.sin(ang_y), 0, math.cos(ang_y)]])
    rotation_z = np.array([[math.cos(ang_z), -math.sin(ang_z), 0],[math.sin(ang_z), math.cos(ang_z), 0],[0, 0, 1]])

    # convert the points from cellgrid indexes to drawable coordinates scaled with a radius around 0,0

    if IS_EVEN:
        for line in raw_list:
            (point1, point2) = line
            (x1,y1,z1) = point1
            (x2,y2,z2) = point2
            new_point1 = np.array([[x1-((DIMENSION-1)/2)],[y1-((DIMENSION-1)/2)],[z1-((DIMENSION-1)/2)]])
            new_point2 = np.array([[x2-((DIMENSION-1)/2)],[y2-((DIMENSION-1)/2)],[z2-((DIMENSION-1)/2)]])
            new_line = (new_point1, new_point2)
            line_list.append(new_line)
    else:
        for line in raw_list:
            (point1, point2) = line
            (x1,y1,z1) = point1
            (x2,y2,z2) = point2
            new_point1 = np.array([[x1-(DIMENSION//2)],[y1-(DIMENSION//2)],[z1-(DIMENSION//2)]])
            new_point2 = np.array([[x2-(DIMENSION//2)],[y2-(DIMENSION//2)],[z2-(DIMENSION//2)]])
            new_line = (new_point1, new_point2)
            line_list.append(new_line)

    # convert the points from scaled coordinates to rotated and projected
    for line in line_list:
        (point1, point2) = line
        new_point1 = PROJECTION_MATRIX @ rotation_z @ rotation_y @ rotation_x @ point1
        new_point2 = PROJECTION_MATRIX @ rotation_z @ rotation_y @ rotation_x @ point2
        new_line = ((new_point1[0][0], new_point1[1][0]),(new_point2[0][0], new_point2[1][0]))
        rotated_line_list.append(new_line)

    return rotated_line_list

def get_specific_point_2dcoords(ang_x, ang_y, ang_z, player_position: list) -> list:
    
    # define rotation matrices
    rotation_x = np.array([[1, 0, 0],[0, math.cos(ang_x), -math.sin(ang_x)],[0, math.sin(ang_x), math.cos(ang_x)]])
    rotation_y = np.array([[math.cos(ang_y), 0, math.sin(ang_y)],[0, 1, 0],[-math.sin(ang_y), 0, math.cos(ang_y)]])
    rotation_z = np.array([[math.cos(ang_z), -math.sin(ang_z), 0],[math.sin(ang_z), math.cos(ang_z), 0],[0, 0, 1]])

    # convert point to scaled radius
    (x,y,z) = player_position
    if IS_EVEN:
        new_point = np.array([[x-((DIMENSION-1)/2)],[y-((DIMENSION-1)/2)],[z-((DIMENSION-1)/2)]])
    else:
        new_point = np.array([[x-(DIMENSION//2)],[y-(DIMENSION//2)],[z-(DIMENSION//2)]])
        
    # rotate and project the point
    rotated_point = PROJECTION_MATRIX @ rotation_z @ rotation_y @ rotation_x @ new_point
    new_player_position = (rotated_point[0][0],rotated_point[1][0])

    return new_player_position

def move_player(cellgrid, player_position: list, direction: list, legal_moves: list) -> list:
    new_position = tuple(map(lambda a, b: a+b, player_position, direction))
    for index in new_position:
        if index < 0 or index >= DIMENSION:
            return player_position
    if is_legal_move(player_position, new_position, legal_moves):
        return new_position
    return player_position
    
def is_legal_move(player_position: list, new_position: list, legal_moves: list) -> bool:
    # for all legal moves at this space
    (x,y,z) = player_position
    for points in legal_moves[x][y][z]:
        if points == new_position:
            return True
    return False

def generate_legal_moves(cellgrid: cell.CellGrid) -> list:
    moves_list = [[[[] for i in range(DIMENSION)] for j in range(DIMENSION)] for k in range(DIMENSION)]
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            for k in range(DIMENSION):
                if i == 0 and j == 0 and k == 0:
                    continue

                current_position = (i,j,k)
                current_cell = cellgrid.grid[i][j][k]
                
                new_position = tuple(map(lambda a, b: a+b, current_position, cell.DIRECTIONS[current_cell.connect_vector]))
                
                # add the (x,y,z) of the connect vector position to this (i,j,k) list in moves list
                moves_list[i][j][k].append(new_position)

                # add the current position to the (x,y,z) list in moves list
                (x,y,z) = new_position
                moves_list[x][y][z].append(current_position)
    
    return moves_list


#####################################################################################################################


### pygame setup ###
pygame.init()

screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))  # creates a Surface
clock = pygame.time.Clock()                                     # Creates a clock to track FPS
running = True                                                  # When the game is running
dt = 0                                                          # delta time since last frame
cellgrid = cell.CellGrid(DIMENSION)
font = pygame.font.SysFont('arial', 20, True, False)
clicking = False
dragging = False
points = generate_points_list(cellgrid.dim)
theta_x = 0
theta_y = 0
theta_z = 0
plotting_points = get_2d_points(points, theta_x, theta_y, theta_z)
game1 = True                                                    # Enter game 1 upon start
game2 = False
grid_finished = False
player_pos = (0,0,0)                                            # player index in the cellgrid grid
legal_moves = [[[[]]]]
maze_complete = False

### colors ###
white = (255, 255, 255)
yellow = (255, 255, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
orange = (255, 150, 0)
black = (0, 0, 0)
red = (255, 0 ,0)
grey = (128, 128, 128)
colors = (white, green, blue, orange)

### initial screen fill ###
screen.fill("white")
draw_grid_numbers(cellgrid, plotting_points)
pygame.display.flip()
 
#######################################################################################################################

### GAME LOOP ###

while running:
    if game1:
        # get the relative movement of the mouse
        (movement_x, movement_y) = pygame.mouse.get_rel()

        # get a list of 2D plottable points from the list 
        plotting_points = get_2d_points(points, theta_x, theta_y, theta_z)

        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicking = True
            if event.type == pygame.MOUSEBUTTONUP:
                clicking = False
        
        # edit the angle of the cube based on the mouse movements
        if clicking:
            theta_x += movement_y * -0.1 * dt
            theta_y += movement_x * 0.1 * dt

        # draw one iteration
        screen.fill("white")
        draw_grid_numbers(cellgrid, plotting_points)

        # key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_SPACE]:
            if cellgrid.update_grid():
                grid_finished = True
        if keys[pygame.K_PAGEUP]:
            if grid_finished:   
                game1 = False           # continue onto game 3
                game2 = False
                pygame.event.clear()    # empty the event queue
                legal_moves = generate_legal_moves(cellgrid)
            else:
                game1 = False           # continue onto game 2
                game2 = True
                pygame.event.clear()    # empty the event queue
                pygame.time.wait(50)
        if keys[pygame.K_RIGHT]:
            theta_y += dt
        if keys[pygame.K_LEFT]:
            theta_y -= dt
        if keys[pygame.K_UP]:
            theta_x += dt
        if keys[pygame.K_DOWN]:
            theta_x -= dt
        
        # print all the changes to the Surface onto the screen
        pygame.display.flip()
        dt = clock.tick(60) / 1000

    # end of game 1
    elif game2:

        # get the relative movement of the mouse
        (movement_x, movement_y) = pygame.mouse.get_rel()

        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicking = True
            if event.type == pygame.MOUSEBUTTONUP:
                clicking = False
        
        # edit the angle of the cube based on the mouse movements
        if clicking:
            theta_x += movement_y * -0.1 * dt
            theta_y += movement_x * 0.1 * dt

        # draw one iteration
        screen.fill("white")
        draw_grid_skeletal(cellgrid, theta_x, theta_y, theta_z, grid_finished, player_pos)

        # key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_PAGEDOWN]:
            game1 = True
            pygame.event.clear()    # empty the event queue
            pygame.time.wait(50)
        if keys[pygame.K_SPACE]:
            if cellgrid.update_grid():
                grid_finished = True
                game2 = False
                pygame.event.clear()    # empty the event queue
                legal_moves = generate_legal_moves(cellgrid)
        if keys[pygame.K_RIGHT]:
            theta_y += dt
        if keys[pygame.K_LEFT]:
            theta_y -= dt
        if keys[pygame.K_UP]:
            theta_x += dt
        if keys[pygame.K_DOWN]:
            theta_x -= dt
        
        # print all the changes to the Surface onto the screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    # end of gameloop 2
    else:
        # get the relative movement of the mouse
        (movement_x, movement_y) = pygame.mouse.get_rel()

        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicking = True
            if event.type == pygame.MOUSEBUTTONUP:
                clicking = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w and not maze_complete:
                player_pos = move_player(cellgrid, player_pos, cell.NORTH, legal_moves)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s and not maze_complete:
                player_pos = move_player(cellgrid, player_pos, cell.SOUTH, legal_moves)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a and not maze_complete:
                player_pos = move_player(cellgrid, player_pos, cell.WEST, legal_moves)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d and not maze_complete:
                player_pos = move_player(cellgrid, player_pos, cell.EAST, legal_moves)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q and not maze_complete:
                player_pos = move_player(cellgrid, player_pos, cell.UP, legal_moves)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e and not maze_complete:
                player_pos = move_player(cellgrid, player_pos, cell.DOWN, legal_moves)
        
        # edit the angle of the cube based on the mouse movements
        if clicking:
            theta_x += movement_y * -0.1 * dt
            theta_y += movement_x * 0.1 * dt

        # draw one iteration
        screen.fill("black")
        if draw_grid_skeletal(cellgrid, theta_x, theta_y, theta_z, grid_finished, player_pos):
            maze_complete = True

        # key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_PAGEDOWN]:
            game1 = True
            pygame.event.clear()    # empty the event queue
            pygame.time.wait(50)
        if keys[pygame.K_RIGHT]:
            theta_y += dt
        if keys[pygame.K_LEFT]:
            theta_y -= dt
        if keys[pygame.K_UP]:
            theta_x += dt
        if keys[pygame.K_DOWN]:
            theta_x -= dt

        # print all the changes to the Surface onto the screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000



# end of running

pygame.quit()
