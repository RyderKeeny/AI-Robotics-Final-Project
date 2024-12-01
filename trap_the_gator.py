import pygame
import sys

pygame.init()

# initialize the screen and grid settings
SCREEN_SIZE = 500  # window size
GRID_SIZE = 10  # number of rows and columns in the playable grid
SWAMP_BORDER = 2  # additional rows/columns around the grid for the swamp
TOTAL_SIZE = GRID_SIZE + 2 * SWAMP_BORDER  # total grid size including the swamp
CELL_SIZE = SCREEN_SIZE // TOTAL_SIZE  # cell size adjusted for swamp inclusion

# grid colors
WHITE = (255, 255, 255)
BLUE = (30, 100, 250)
GREEN = (10, 100, 32)
ORANGE = (255, 90, 0)

# initialize game objects
gator_pos = [SWAMP_BORDER + GRID_SIZE // 2, SWAMP_BORDER + GRID_SIZE // 2]  # gator starts in the middle of the grid
traps = []  # no initial traps

gator_image = pygame.image.load("Pixel_Gator.png")
trap_image = pygame.image.load("Trap.png")
gator_image = pygame.transform.scale(gator_image, (CELL_SIZE, CELL_SIZE))
trap_image = pygame.transform.scale(trap_image, (CELL_SIZE, CELL_SIZE))

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Trap the Gator")


def draw_grid():
    """
    Draw the grid and place objects like the gator and traps.
    Args:
        None
    Returns:
        None
    """
    screen.fill(GREEN)  # Swamp background

    # grid
    for row in range(SWAMP_BORDER, SWAMP_BORDER + GRID_SIZE):
        for col in range(SWAMP_BORDER, SWAMP_BORDER + GRID_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLUE, rect)  # grid cells
            pygame.draw.rect(screen, WHITE, rect, 1)  # grid lines

            # put objects on the grid
            if [row, col] == gator_pos:
                screen.blit(gator_image, rect)  # Gator
            elif [row, col] in traps:
                screen.blit(trap_image, rect)  # Trap


# THIS WILL BE REPLACED BY MDP & LTL LOGIC
def move_gator():
    """
    Move the gator with a preference for moving off the grid (toward the swamp).
    Args:
        None
    Returns:
        None
    """
    global gator_pos
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

    # prioritize moves that lead outside the grid
    for dx, dy in directions:
        new_pos = [gator_pos[0] + dx, gator_pos[1] + dy]
        # check if the move leads to the swamp (outside the grid)
        if not (SWAMP_BORDER <= new_pos[0] < SWAMP_BORDER + GRID_SIZE and
                SWAMP_BORDER <= new_pos[1] < SWAMP_BORDER + GRID_SIZE):
            gator_pos = new_pos  # move off the grid
            return

    # if no move leads off the grid, try valid moves within the grid
    for dx, dy in directions:
        new_pos = [gator_pos[0] + dx, gator_pos[1] + dy]
        if (SWAMP_BORDER <= new_pos[0] < SWAMP_BORDER + GRID_SIZE and
                SWAMP_BORDER <= new_pos[1] < SWAMP_BORDER + GRID_SIZE and
                new_pos not in traps):
            gator_pos = new_pos
            return


def place_trap(mouse_pos):
    """
    Place a trap at the grid position corresponding to the mouse click.
    Args:
        mouse_pos (tuple): (x, y) coordinates of the mouse click.
    Returns:
        None
    """
    # convert mouse position to grid coordinates
    x, y = mouse_pos
    row, col = y // CELL_SIZE, x // CELL_SIZE
    new_trap = [row, col]

    # place trap only in valid cells
    if new_trap not in traps and new_trap != gator_pos:
        traps.append(new_trap)


def is_gator_trapped(gator_pos, traps):
    """
    Check if the gator is completely trapped (no valid moves).
    Args:
        gator_pos (list): Current position of the gator.
        traps (list): List of trap positions.
    Returns:
        bool: True if the gator is trapped, False otherwise.
    """
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        new_pos = [gator_pos[0] + dx, gator_pos[1] + dy]
        # check if the move is within the playable grid and not a trap
        if (SWAMP_BORDER <= new_pos[0] < SWAMP_BORDER + GRID_SIZE and
                SWAMP_BORDER <= new_pos[1] < SWAMP_BORDER + GRID_SIZE and
                new_pos not in traps):
            return False  # found a valid move
    return True  # no valid moves exist

def animate_gator_exit():
    """
    Animate the gator running off the screen before the "You Lose!" screen is shown.
    Args:
        None
    Returns:
        None
    """
    global gator_pos
    dx, dy = 0, 0

    # determine the direction in which the gator left the grid
    if gator_pos[0] < SWAMP_BORDER:
        dx, dy = -1, 0  # move up
    elif gator_pos[0] >= SWAMP_BORDER + GRID_SIZE:
        dx, dy = 1, 0  # move down
    elif gator_pos[1] < SWAMP_BORDER:
        dx, dy = 0, -1  # move left
    elif gator_pos[1] >= SWAMP_BORDER + GRID_SIZE:
        dx, dy = 0, 1  # move right

    # animate the gator moving step by step off the screen
    for _ in range(SWAMP_BORDER + 2):
        gator_pos = [gator_pos[0] + dx, gator_pos[1] + dy]
        draw_grid()
        rect = pygame.Rect(
            gator_pos[1] * CELL_SIZE,
            gator_pos[0] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )
        screen.blit(gator_image, rect)  
        pygame.display.flip()
        pygame.time.delay(300)



def end_screen(message):
    """
    Display the end screen with a message and a replay button.
    Args:
        message (str): The message to display ("You Win!" or "You Lose!").
    Returns:
        None
    """
    font = pygame.font.Font(None, 50)
    button_font = pygame.font.Font(None, 40)

    # message and restart button
    text = font.render(message, True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 3))
    button = pygame.Rect(SCREEN_SIZE // 2 - 75, SCREEN_SIZE // 2, 150, 50)
    button_text = button_font.render("Play Again", True, WHITE)
    button_text_rect = button_text.get_rect(center=button.center)

    while True:
        screen.fill(BLUE)
        screen.blit(text, text_rect)
        pygame.draw.rect(screen, ORANGE, button)
        screen.blit(button_text, button_text_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and button.collidepoint(event.pos):
                main()  # restart the game

### MDP Logic Placeholder ###
# replace this section with MDP logic
# - define the states, actions, and transition probabilities for the gator's movement
# - make a function to calculate the optimal move for the gator based on the MDP policy
#
# I think like this (I used the same function format from our hws):
# def get_optimal_move_mdp(gator_pos, traps):
#     """
#     Use MDP logic to determine the optimal move for the gator
#     Args:
#         gator_pos (list): Current position of the gator
#         traps (list): List of trap positions
#     Returns:
#         str: Optimal move ("up", "down", "left", "right")
#     """
#     # add MDP logic here (defining states and solving for the optimal policy)
#     return "up"  <- replace with actual optimal move based on MDP


### LTL Logic & Adversarial Strategy Placeholder ###
# replace this section with LTL logic for adversarial strategy
# - define safety objectives: "Always avoid traps"
# - define reachability objectives: "Eventually reach the swamp"
# - use these statements to help the gator's decision-making (MDP)
#
# I think like this (I used the same function format from our hws):
# def satisfies_ltl(mdp_move, gator_pos, traps):
#     """
#     Use LTL logic to check if the gator's next move based on MDP satisfies safety and reachability objectives
#     Args:
#         mdp_move (str): Move suggested by MDP logic
#         gator_pos (list): Current position of the gator
#         traps (list): List of trap positions
#     Returns:
#         bool: True if the move satisfies LTL objectives, False otherwise
#     """
#     # add LTL-based logic here to determine the safest and most goal-oriented move
#     return True  <- replace with actual LTL logic to validate the MDP move


### combined MDP and LTL Logic ###
# take the outputs of MDP and LTL logic to determine the gator's best move
# 
# 1. **MDP Logic**: 
#    - determines the optimal move for the gator based on defined states, actions, and transition probabilities
#    - focuses on minimizing penalties (avoiding traps) & maximizing rewards (escaping to the swamp).
# 
# 2. **LTL Logic**:
#    - validates whether the MDP's suggested move satisfies safety and reachability objectives
#    - safety objective: the gator should "always avoid traps"
#    - reachability objective: the gator should "eventually reach the swamp"
# 
# 3. **Fallback**:
#    - if the MDP's suggested move violates LTL objectives, the function explores alternative moves that align with LTL constraints
#    - if no valid moves exist, the gator remains in its current position (indicating it is trapped), game over
# 
# - this combined function ensures that the gator’s behavior is both probabilistically optimized (MDP) and logically constrained (LTL)
# - the output is the best possible move for the gator that adheres to both probabilistic and logical objectives
#
# how I think it could be implemented:
# def get_best_move(gator_pos, traps):
#     """
#     Combines MDP and LTL logic to decide the best move for the gator
#     Args:
#         gator_pos (list): Current position of the gator
#         traps (list): List of trap positions
#     Returns:
#         list: The best move for the gator as [row, col]
#     """
#     # Step 1: use MDP logic to calculate the optimal move (get_optimal_move_mdp function)
#     # Step 2: check if the MDP move is good with LTL objectives (satisfies_ltl function)
#     # Step 3: fallback to alternative moves if the MDP move fails LTL validation
#     # Step 4: return the best move (or current position if no valid moves exist)
#     return [gator_pos[0], gator_pos[1]]  <- replace with actual best move based on MDP and LTL logic



def main():
    global gator_pos, traps
    gator_pos = [SWAMP_BORDER + GRID_SIZE // 2, SWAMP_BORDER + GRID_SIZE // 2]  # reset gator position
    traps = []  # reset traps

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # mouse click to place traps
            if event.type == pygame.MOUSEBUTTONDOWN:
                place_trap(event.pos)
                move_gator()  # move the gator after the player places a trap

        # clear screen
        screen.fill(GREEN)  # Swamp

        # draw the grid and objects
        draw_grid()

        # check for Robot win (Gator escapes to the swamp)
        if not (SWAMP_BORDER <= gator_pos[0] < SWAMP_BORDER + GRID_SIZE and
                SWAMP_BORDER <= gator_pos[1] < SWAMP_BORDER + GRID_SIZE):
            animate_gator_exit()
            end_screen("You Lose!")
            return

        # check for Robot loss (Gator is trapped)
        if is_gator_trapped(gator_pos, traps):
            end_screen("You Win!")
            return

        # update display
        pygame.display.flip()
        clock.tick(10)


if __name__ == "__main__":
    main()
