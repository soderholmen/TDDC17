from lab1.liuvacuum import *
import copy

DEBUG_OPT_DENSEWORLDMAP = False

AGENT_STATE_UNKNOWN = 0
AGENT_STATE_WALL = 1
AGENT_STATE_CLEAR = 2
AGENT_STATE_DIRT = 3
AGENT_STATE_HOME = 4
AGENT_STATE_VISITED = 5

AGENT_DIRECTION_NORTH = 0
AGENT_DIRECTION_EAST = 1
AGENT_DIRECTION_SOUTH = 2
AGENT_DIRECTION_WEST = 3


HAVE_SEQ = 0
NOT_SEQ = 1
FIND_HOME = 2

def direction_to_string(cdr):
    cdr %= 4
    return  "NORTH" if cdr == AGENT_DIRECTION_NORTH else\
            "EAST"  if cdr == AGENT_DIRECTION_EAST else\
            "SOUTH" if cdr == AGENT_DIRECTION_SOUTH else\
            "WEST" #if dir == AGENT_DIRECTION_WEST

"""
Internal state of a vacuum agent
"""
class MyAgentState:

    def __init__(self, width, height):

        # Initialize perceived world state
        self.world = [[AGENT_STATE_UNKNOWN for _ in range(height)] for _ in range(width)]
        self.world[1][1] = AGENT_STATE_HOME

        # Agent internal state
        self.last_action = ACTION_NOP
        self.direction = AGENT_DIRECTION_EAST
        self.pos_x = 1
        self.pos_y = 1
        self.working_state = NOT_SEQ

        # Metadata
        self.world_width = width
        self.world_height = height

    """
    Update perceived agent location
    """
    def update_position(self, bump):
        if not bump and self.last_action == ACTION_FORWARD:
            if self.direction == AGENT_DIRECTION_EAST:
                self.pos_x += 1
            elif self.direction == AGENT_DIRECTION_SOUTH:
                self.pos_y += 1
            elif self.direction == AGENT_DIRECTION_WEST:
                self.pos_x -= 1
            elif self.direction == AGENT_DIRECTION_NORTH:
                self.pos_y -= 1

    """
    Update perceived or inferred information about a part of the world
    """
    def update_world(self, x, y, info):
        self.world[x][y] = info

    """
    Dumps a map of the world as the agent knows it
    """
    def print_world_debug(self):
        for y in range(self.world_height):
            for x in range(self.world_width):
                if self.world[x][y] == AGENT_STATE_UNKNOWN:
                    print("?" if DEBUG_OPT_DENSEWORLDMAP else " ? ", end="")
                elif self.world[x][y] == AGENT_STATE_WALL:
                    print("#" if DEBUG_OPT_DENSEWORLDMAP else " # ", end="")
                elif self.world[x][y] == AGENT_STATE_CLEAR:
                    print("." if DEBUG_OPT_DENSEWORLDMAP else " . ", end="")
                elif self.world[x][y] == AGENT_STATE_DIRT:
                    print("D" if DEBUG_OPT_DENSEWORLDMAP else " D ", end="")
                elif self.world[x][y] == AGENT_STATE_HOME:
                    print("H" if DEBUG_OPT_DENSEWORLDMAP else " H ", end="")

            print() # Newline
        print() # Delimiter post-print

"""
Vacuum agent
"""
class MyVacuumAgent(Agent):

    def __init__(self, world_width, world_height, log):
        super().__init__(self.execute)
        self.initial_random_actions = 10
        self.iteration_counter = 800
        self.state = MyAgentState(world_width, world_height)
        self.log = log
        self.seq = []


    def move_to_random_start_position(self, bump):
        action = random()

        self.initial_random_actions -= 1
        self.state.update_position(bump)

        if action < 0.1666666:   # 1/6 chance
            self.state.direction = (self.state.direction + 3) % 4
            self.state.last_action = ACTION_TURN_LEFT
            return ACTION_TURN_LEFT
        elif action < 0.3333333: # 1/6 chance
            self.state.direction = (self.state.direction + 1) % 4
            self.state.last_action = ACTION_TURN_RIGHT
            return ACTION_TURN_RIGHT
        else:                    # 4/6 chance
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD

    def update_direction(self, movement):
        if self.state.direction == AGENT_DIRECTION_NORTH:
            if movement == ACTION_TURN_LEFT:
                self.state.direction = AGENT_DIRECTION_WEST
            elif movement == ACTION_TURN_RIGHT:
                self.state.direction = AGENT_DIRECTION_EAST
        elif self.state.direction == AGENT_DIRECTION_SOUTH:
            if movement == ACTION_TURN_LEFT:
                self.state.direction = AGENT_DIRECTION_EAST
            elif movement == ACTION_TURN_RIGHT:
                self.state.direction = AGENT_DIRECTION_WEST
        elif self.state.direction == AGENT_DIRECTION_WEST:
            if movement == ACTION_TURN_LEFT:
                self.state.direction = AGENT_DIRECTION_SOUTH
            elif movement == ACTION_TURN_RIGHT:
                self.state.direction = AGENT_DIRECTION_NORTH
        elif self.state.direction == AGENT_DIRECTION_EAST:
            if movement == ACTION_TURN_LEFT:
                self.state.direction = AGENT_DIRECTION_NORTH
            elif movement == ACTION_TURN_RIGHT:
                self.state.direction = AGENT_DIRECTION_SOUTH

    def calc_param(self, dir_old, dir_new):
        if dir_new == dir_old:
            return [1, [ACTION_FORWARD]]
        elif abs(dir_old - dir_new) == 2:
            return [3, [ACTION_TURN_RIGHT, ACTION_TURN_RIGHT, ACTION_FORWARD]]
        elif dir_old == 0 or dir_old == 3:
            if dir_new == 1 or dir_new == 0:
                return [2, [ACTION_TURN_RIGHT, ACTION_FORWARD]]
            else:
                return [2, [ACTION_TURN_LEFT, ACTION_FORWARD]]
        else:
            if dir_old < dir_new:
                return [2, [ACTION_TURN_RIGHT, ACTION_FORWARD]]
            else:
                return [2, [ACTION_TURN_LEFT, ACTION_FORWARD]]


    def find_un(self, dir, cord, cost, seq, temp_map):
        if temp_map[cord[0]][cord[1]] > 4 and temp_map[cord[0]][cord[1]] < cost+5:
            return [-1, cord, []]
        temp_map[cord[0]][cord[1]] = cost+5
        if self.state.world[cord[0]][cord[1]] == AGENT_STATE_UNKNOWN:
            return [cost, cord, seq]
        elif self.state.world[cord[0]][cord[1]] == AGENT_STATE_WALL:
            return [-1, cord, []]
        else:

            w = [-1]
            e = [-1]
            s = [-1]
            n = [-1]
            if (cord[0] - 1 > 0 ):
                param = self.calc_param(dir, AGENT_DIRECTION_WEST)
                w = self.find_un(AGENT_DIRECTION_WEST, [cord[0]-1, cord[1]], cost+param[0], seq+param[1], temp_map)

            if (cord[0] + 1 < len(self.state.world)-1 ):
                param = self.calc_param(dir, AGENT_DIRECTION_EAST)
                e = self.find_un(AGENT_DIRECTION_EAST, [cord[0]+1, cord[1]], cost+param[0], seq+param[1], temp_map)

            if (cord[1] - 1 > 0 ):
                param = self.calc_param(dir, AGENT_DIRECTION_NORTH)
                n = self.find_un(AGENT_DIRECTION_NORTH, [cord[0], cord[1]-1], cost+param[0], seq+param[1], temp_map)

            if (cord[1] + 1 < len(self.state.world[0])-1):
                param = self.calc_param(dir, AGENT_DIRECTION_SOUTH)
                s = self.find_un(AGENT_DIRECTION_SOUTH, [cord[0], cord[1]+1], cost+param[0], seq+param[1], temp_map)

            temp_list = [w,e,n,s]
            temp_list.sort(key=lambda x: x[0])
            """
            for i in temp_list:
                if i[0] > 0:
                    return i

            """
            for i in range(0,len(temp_list)):
                if temp_list[i][0] > 0:
                    if i < len(temp_list)-1:
                        if temp_list[i][0] == temp_list[i+1][0] and \
                        (temp_list[i][1][0] + temp_list[i][1][1]) < (temp_list[i+1][1][0] + temp_list[i+1][1][1]):
                            return temp_list[i+1]
                    return temp_list[i]

            return [-1, cord, []]


    def find_home(self, home_cord, dir, cord, cost, seq, temp_map):
        if temp_map[cord[0]][cord[1]] > 4 and temp_map[cord[0]][cord[1]] < cost+5:
            return [-1, cord, []]
        elif self.state.world[cord[0]][cord[1]] == AGENT_STATE_WALL:
            return [-1, cord, []]
        temp_map[cord[0]][cord[1]] = cost+5
        if home_cord == cord:
            return [cost, cord, seq]
        else:
            w = [-1]
            e = [-1]
            s = [-1]
            n = [-1]
            if (cord[0] - 1 > 0):
                param = self.calc_param(dir, AGENT_DIRECTION_WEST)
                w = self.find_home([1,1], AGENT_DIRECTION_WEST, [cord[0]-1, cord[1]], cost+param[0], seq+param[1], temp_map)

            if (cord[0] + 1 < len(self.state.world)-1):
                param = self.calc_param(dir, AGENT_DIRECTION_EAST)
                e = self.find_home([1,1], AGENT_DIRECTION_EAST, [cord[0]+1, cord[1]], cost+param[0], seq+param[1], temp_map)

            if (cord[1] - 1 > 0):
                param = self.calc_param(dir, AGENT_DIRECTION_NORTH)
                n = self.find_home([1,1], AGENT_DIRECTION_NORTH, [cord[0], cord[1]-1], cost+param[0], seq+param[1], temp_map)

            if (cord[1] + 1 < len(self.state.world[0])-1):
                param = self.calc_param(dir, AGENT_DIRECTION_SOUTH)
                s = self.find_home([1,1], AGENT_DIRECTION_SOUTH, [cord[0], cord[1]+1], cost+param[0], seq+param[1], temp_map)

            temp_list = [w,e,n,s]
            temp_list.sort(key=lambda x: x[0])
            for i in temp_list:
                if i[0] > 0:
                    return i

            return [-1, cord, []]


    def execute(self, percept):

        ###########################
        # DO NOT MODIFY THIS CODE #
        ###########################

        bump = percept.attributes["bump"]
        dirt = percept.attributes["dirt"]
        home = percept.attributes["home"]

        # Move agent to a randomly chosen initial position
        if self.initial_random_actions > 0:
            self.log("Moving to random start position ({} steps left)".format(self.initial_random_actions))
            return self.move_to_random_start_position(bump)

        # Finalize randomization by properly updating position (without subsequently changing it)
        elif self.initial_random_actions == 0:
            self.initial_random_actions -= 1
            self.state.update_position(bump)
            self.state.last_action = ACTION_SUCK
            self.log("Processing percepts after position randomization")
            return ACTION_SUCK


        ########################
        # START MODIFYING HERE #
        ########################

        # Max iterations for the agent
        if self.iteration_counter < 1:
            if self.iteration_counter == 0:
                self.iteration_counter -= 1
                self.log("Iteration counter is now 0. Halting!")
                self.log("Performance: {}".format(self.performance))
            return ACTION_NOP

        self.log("Position: ({}, {})\t\tDirection: {}".format(self.state.pos_x, self.state.pos_y,
                                                              direction_to_string(self.state.direction)))

        self.iteration_counter -= 1

        # Track position of agent
        self.state.update_position(bump)

        if bump:
            # Get an xy-offset pair based on where the agent is facing
            offset = [(0, -1), (1, 0), (0, 1), (-1, 0)][self.state.direction]
            self.state.last_bump_dir = self.state.direction
            # Mark the tile at the offset from the agent as a wall (since the agent bumped into it)
            self.state.update_world(self.state.pos_x + offset[0], self.state.pos_y + offset[1], AGENT_STATE_WALL)

        # Update perceived state of current tile
        if dirt:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_DIRT)
        else:
            self.state.update_world(self.state.pos_x, self.state.pos_y, AGENT_STATE_CLEAR)

        # Debug
        self.state.print_world_debug()
#########################################################################################################################################################33


        if dirt:
            self.state.last_action = ACTION_SUCK
            return ACTION_SUCK
        elif bump:
            self.state.working_state = NOT_SEQ

        if self.state.working_state == NOT_SEQ:
            self.seq = self.find_un(self.state.direction, [self.state.pos_x, self.state.pos_y], 0, [], copy.deepcopy(self.state.world))
            if len(self.seq[2]) == 0:
                if home:
                    self.iteration_counter = 0
                    self.state.last_action = ACTION_NOP
                    return ACTION_NOP
                else:
                    self.state.working_state = FIND_HOME
                    self.seq = self.find_home([1,1], self.state.direction, [self.state.pos_x, self.state.pos_y], 0, [], copy.deepcopy(self.state.world))
            else:
                self.state.working_state = HAVE_SEQ


        if self.state.working_state == HAVE_SEQ or self.state.working_state == FIND_HOME:
            new_action = self.seq[2][0]
            self.seq[2].pop(0)
            if len(self.seq[2]) == 0:
                self.state.working_state = NOT_SEQ
            self.update_direction(new_action)
            self.state.last_action = new_action
            return new_action


"""
        if dirt:
            self.state.last_action = ACTION_SUCK
            return ACTION_SUCK
        if self.state.working_state == FIND_START_POS_S:
            if bump:
                self.state.working_state = FIND_START_POS_E
                self.state.last_action = ACTION_TURN_LEFT
                self.update_direction(ACTION_TURN_LEFT)
                return ACTION_TURN_LEFT
            else:
                if self.state.direction != AGENT_DIRECTION_SOUTH:
                    self.state.last_action = ACTION_TURN_RIGHT
                    self.update_direction(ACTION_TURN_RIGHT)
                    return ACTION_TURN_RIGHT
                else:
                    self.state.last_action = ACTION_FORWARD
                    return ACTION_FORWARD
        elif self.state.working_state == FIND_START_POS_E:
            if bump:
                self.state.working_state = CLEANING_S
                self.state.last_action = ACTION_TURN_LEFT
                self.update_direction(ACTION_TURN_LEFT)
                return ACTION_TURN_LEFT
            else:
                self.state.last_action = ACTION_FORWARD
                return ACTION_FORWARD
        elif self.state.working_state == CLEANING_S:

            if bump:
                if self.state.direction == AGENT_DIRECTION_NORTH:
                    self.state.working_state = CLEANING_T1
                    self.state.last_action = ACTION_TURN_LEFT
                    self.update_direction(ACTION_TURN_LEFT)
                    return ACTION_TURN_LEFT

                elif self.state.direction == AGENT_DIRECTION_SOUTH:
                    self.state.working_state = CLEANING_T1
                    self.state.last_action = ACTION_TURN_RIGHT
                    self.update_direction(ACTION_TURN_RIGHT)
                    return ACTION_TURN_RIGHT

            else:
                self.state.last_action = ACTION_FORWARD
                return ACTION_FORWARD

        elif self.state.working_state == CLEANING_T1:

            self.state.working_state = CLEANING_T2
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD
        elif self.state.working_state == CLEANING_T2:
            if bump:
                self.log("Find Home")
                self.state.working_state = FIND_HOME
                self.update_direction(ACTION_TURN_RIGHT)
                self.state.last_action = ACTION_TURN_RIGHT
                return ACTION_TURN_RIGHT
            else:

                self.state.working_state = CLEANING_S

                if self.state.last_bump_dir == AGENT_DIRECTION_SOUTH:
                    self.state.last_action = ACTION_TURN_RIGHT
                    self.update_direction(ACTION_TURN_RIGHT)
                    return ACTION_TURN_RIGHT
                else:
                    self.state.last_action = ACTION_TURN_LEFT
                    self.update_direction(ACTION_TURN_LEFT)
                    return ACTION_TURN_LEFT
        elif self.state.working_state == FIND_HOME:
            if bump:
                self.log("Home")
                self.state.last_action = ACTION_NOP
                self.iteration_counter = 1
                return ACTION_NOP
            else:
                self.state.last_action = ACTION_FORWARD
                return ACTION_FORWARD
"""
