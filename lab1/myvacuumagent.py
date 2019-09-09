from lab1.liuvacuum import *

DEBUG_OPT_DENSEWORLDMAP = False

AGENT_STATE_UNKNOWN = 0
AGENT_STATE_WALL = 1
AGENT_STATE_CLEAR = 2
AGENT_STATE_DIRT = 3
AGENT_STATE_HOME = 4

AGENT_DIRECTION_NORTH = 0
AGENT_DIRECTION_EAST = 1
AGENT_DIRECTION_SOUTH = 2
AGENT_DIRECTION_WEST = 3

FIND_START_POS_S = 0
FIND_START_POS_E = 1
CLEANING_S = 2
CLEANING_T1 = 3
CLEANING_T2 = 4
FIND_HOME = 5

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
        self.working_state = FIND_START_POS_S
        self.last_bump_dir = AGENT_DIRECTION_NORTH

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
        self.iteration_counter = 300
        self.state = MyAgentState(world_width, world_height)
        self.log = log


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
        elif self.state.working_state == CLEANING:
            if dirt:
                self.state.last_action = ACTION_SUCK
                return ACTION_SUCK
            elif bump:
                if self.state.direction == AGENT_DIRECTION_WEST:
                    self.state.last_action = ACTION_TURN_RIGHT
                    self.update_direction(ACTION_TURN_RIGHT)
                    return ACTION_TURN_RIGHT
                elif self.state.direction == AGENT_DIRECTION_EAST:
                    self.state.last_action = ACTION_TURN_LEFT
                    self.update_direction(ACTION_TURN_LEFT)
                    return ACTION_TURN_LEFT
                else:
                    self.state.working_state = FIND_HOME
            elif self.state.direction == AGENT_DIRECTION_NORTH:
                if self.state.last_action == ACTION_TURN_RIGHT or self.state.last_action == ACTION_TURN_LEFT:
                    self.state.last_action = ACTION_FORWARD
                    self.update_direction(ACTION_FORWARD)
                    return ACTION_FORWARD
                else:
                    if self.state.last_bump_dir == AGENT_DIRECTION_WEST:
                        self.state.last_action = ACTION_TURN_RIGHT
                        self.update_direction(ACTION_TURN_RIGHT)
                        return ACTION_TURN_RIGHT
                    else:
                        self.state.last_action = ACTION_TURN_LEFT
                        self.update_direction(ACTION_TURN_LEFT)
                        return ACTION_TURN_LEFT

            else:
                self.state.last_action = ACTION_FORWARD
                return ACTION_FORWARD

                """


        """
        # Decide action
        if dirt:
            self.log("DIRT -> choosing SUCK action!")
            self.state.last_action = ACTION_SUCK
            return ACTION_SUCK
        elif bump:
            self.state.last_action = ACTION_NOP
            return ACTION_NOP
        else:
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD
        """
