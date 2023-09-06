from bitarray import bitarray
from bitarray.util import int2ba
import random

#          /\ <->
NORTH = (0,-1,0)
EAST = (0,0,1)
SOUTH = (0,1,0)
WEST = (0,0,-1) 
UP = (-1,0,0)
DOWN = (1,0,0)
#               0      1    2    3     4     5
DIRECTIONS = [NORTH, EAST, UP, SOUTH, WEST, DOWN]

BRANCH_PROB = 5
TURN_PROB = 10

class Cell:

    def __init__(self) -> None:
        # State: 0 = disconnected, 1 = seed, 2 = invite, 3 = connected
        self.state = 0

        # Vector that points the parent cell
        self.connect_vector = -1

        # Vector that points to the invited cell
        self.invite_vector = -1

        # bitarray detecting all elible adjacent cells
        self.neighbors = bitarray('000000')

    def __str__(self) -> str:
        return f"({self.state}, {self.connect_vector}, {self.invite_vector}, {self.neighbors})"
    
class CellGrid:

    def __init__(self, dim) -> None:
        # Create an array of cells initialized to the value given in the grid
        self.dim = dim
        self.grid = [[[Cell() for i in range(self.dim)] for j in range(self.dim)] for k in range(self.dim)]

        # Choose a cell to the be starting seed
        self.grid[0][0][0].state = 1

        # state that the current state has a seed in it
        self.seed_present = True
        
    def __str__(self) -> str:
        s = ""
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                for k in range(len(self.grid[i][j])):
                    s += f"{self.grid[i][j].state}"
                s += "\n"
            s += "\n\n"
        return s

    # update_grid will go through an entire interation on the grid
    def update_grid(self) -> bool:

        # determine whether there will be a seed at the end of the iteration
        seen_seed = False
        all_connected = True

        # iterate through each Cell in the grid
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                for k in range(len(self.grid[i][j])):
                    cell = self.grid[i][j][k]

                    # determine the state of the cell, and then do an action depending on what the cell is
                    match cell.state:
                        case 0:
                            # look for an invitation from inviting cell
                            # check the four squares around this one to see if they have the right vector DIRECTION IS AN INDEX
                            for direction in range(6):
                                # we've seen a disconnected cell, so it must be that not all cells are connected
                                all_connected = False

                                # for each direction, find the neighboring cell coordinate in that direction
                                (i_change, j_change, k_change) = DIRECTIONS[direction]
                                i_n = i_change + i
                                j_n = j_change + j
                                k_n = k_change + k

                                # if the value isn't in the grid, check the next direction
                                if not self.in_grid(i_n,j_n,k_n):
                                    continue
                                
                                # otherwise, create a reference to that neighboring cell
                                cell_n = self.grid[i_n][j_n][k_n]

                                # if the neighboring cell is not sending an invitation to this cell
                                if not self.is_inviting(cell_n, direction):
                                    continue

                                # at this point, we've confirmed that the cell in the current direction is an inviting cell
                                cell.connect_vector = direction
                                cell.state = 1
                                seen_seed = True
                                break

                        case 1:
                            # scan the neighboring cells and create a map of which ones are disconnected and eligible
                            cell = self.determine_neighbors(i, j, k, cell)

                            # now that the bitarray is determined, we can choose a random valid neighbor and begin the operation
                            # check that the seed has valid branch neighbors
                            if cell.neighbors.count(1) == 0:
                                # let the seed die
                                cell.state = 3
                            else:
                                # pick a random valid candidate and assign that direction to the invite vector
                                cell.invite_vector = self.valid_candidate_direction(cell)
                                cell.state = 2
                                all_connected = False
                                
                        case 2:
                            # invite cell either becomes connected, or it becomes a seed as well
                            if random.randint(1,100) <= BRANCH_PROB:
                                cell.state = 1
                                seen_seed = True
                                all_connected = False
                            else:
                                cell.state = 3

                        case 3:
                            # if there not a live seed in the grid, we have to check more
                            if not self.seed_present:

                                # check that there is a disconnected cell in the neighborhood
                                cell = self.determine_neighbors(i, j, k, cell)
                                if cell.neighbors.count(1) > 0:

                                    # since there is a valid cell, then conditionally become a seed
                                    if random.randint(1,100) <= BRANCH_PROB:
                                        cell.state = 1
                                        seen_seed = True
                                        all_connected = False

                        case _:
                            print("This is not supposed to happen!")

                    # any clean up after the operation is done?

        # After the loops have run, we update whether there's a seed in the grid
        self.seed_present = seen_seed

        # Then, return whether the entire grid is connected or not
        return all_connected

    # in_grid determines whether, given a coordinate, if that coordinate is valid in the grid.
    def in_grid(self, zpos, ypos, xpos) -> bool:
        if zpos < 0 or zpos >= self.dim or ypos < 0 or ypos >= self.dim or xpos < 0 or xpos >= self.dim :
            return False
        return True
    
    # is_inviting determines whether the neighboring cell is an inviting cell pointing to the current cell
    def is_inviting(self, cell_n: Cell, direction) -> bool:
        if cell_n.state != 2:
            return False
        
        # invert the neighbor's invite vector. If it matches the current cell's pointing direction, there's a match
        negative_vector = (cell_n.invite_vector + 3) % 6
        if negative_vector == direction:
            return True
        
        return False

    # returns the number 0-3 representing a direction of a vector
    def valid_candidate_direction(self, cell: Cell) -> int:
        # determine an initial direction for the candidate neighbor
        # if we go with a random 
        if random.randint(1,100) <= TURN_PROB and cell.connect_vector >= 0:
            direction = (cell.connect_vector + 3) % 6   # go straight
        else:
            direction = random.randint(0,5)             # go random direction

        # continue generating new directions if the current one isn't valid
        while cell.neighbors & int2ba(2**direction, 6) == bitarray('000000'):
            direction = random.randint(0,5)

        return direction

    # determine neighbors returns a modified Cell object that has its neighborhood updated
    def determine_neighbors(self, i, j, k, cell: Cell) -> Cell:

        # initialize the neighbors bitarray
        cell.neighbors = bitarray('000000')

        for direction in range(6):
            # for each direction, find the neighboring cell coordinate in that direction
            (i_change, j_change, k_change) = DIRECTIONS[direction]
            i_n = i_change + i
            j_n = j_change + j
            k_n = k_change + k

            # if the value isn't in the grid, check the next direction
            if not self.in_grid(i_n,j_n,k_n):
                continue

            # otherwise, create a reference to that neighboring cell
            cell_n = self.grid[i_n][j_n][k_n]

            # if the neighboring cell is disconnected, we add it to the bitarray
            if cell_n.state == 0:
                b =  int2ba(2**direction, 6)
                cell.neighbors = cell.neighbors | b

        return cell


        
