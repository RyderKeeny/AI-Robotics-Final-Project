import pygame
import sys
import numpy as np
import random

pygame.init()

# Initialize the screen and grid settings
SCREEN_SIZE = 500  # Window size
GRID_SIZE = 10  # Number of rows and columns in the playable grid
SWAMP_BORDER = 2  # Additional rows/columns around the grid for the swamp
TOTAL_SIZE = GRID_SIZE + 2 * SWAMP_BORDER  # Total grid size including the swamp
CELL_SIZE = SCREEN_SIZE // TOTAL_SIZE  # Cell size adjusted for swamp inclusion

# Grid colors
WHITE = (255, 255, 255)
BLUE = (30, 100, 250)
GREEN = (10, 100, 32)
ORANGE = (255, 90, 0)

# Initialize game objects
gator_start_pos = [SWAMP_BORDER + GRID_SIZE // 2, SWAMP_BORDER + GRID_SIZE // 2]  # Gator starts in the middle
gator_pos = gator_start_pos.copy()
traps = []  # No initial traps

# Load and scale images
try:
    gator_image = pygame.image.load("Pixel_Gator.png")
    trap_image = pygame.image.load("Trap.png")
    gator_image = pygame.transform.scale(gator_image, (CELL_SIZE, CELL_SIZE))
    trap_image = pygame.transform.scale(trap_image, (CELL_SIZE, CELL_SIZE))
except pygame.error:
    # If images are not found, use colored rectangles
    gator_image = None
    trap_image = None

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Trap the Gator")

# Define possible actions
actions = ["up", "down", "left", "right"]


def draw_grid():
    """
    Draw the grid and place objects like the gator and traps.
    """
    screen.fill(GREEN)  # Swamp background
    for row in range(TOTAL_SIZE):
        for col in range(TOTAL_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if (SWAMP_BORDER <= row < SWAMP_BORDER + GRID_SIZE and
                    SWAMP_BORDER <= col < SWAMP_BORDER + GRID_SIZE):
                pygame.draw.rect(screen, BLUE, rect)  # Playable grid cells
            else:
                pygame.draw.rect(screen, GREEN, rect)  # Swamp cells
            pygame.draw.rect(screen, WHITE, rect, 1)  # Grid lines

            # Place objects on the grid
            if [row, col] == gator_pos:
                if gator_image:
                    screen.blit(gator_image, rect)
                else:
                    pygame.draw.rect(screen, ORANGE, rect)  # Gator as a colored square
            elif [row, col] in traps:
                if trap_image:
                    screen.blit(trap_image, rect)
                else:
                    pygame.draw.rect(screen, (255, 0, 0), rect)  # Trap as a red square


def place_trap(mouse_pos):
    """
    Place a trap at the grid position corresponding to the mouse click.
    """
    x, y = mouse_pos
    row, col = y // CELL_SIZE, x // CELL_SIZE
    new_trap = [row, col]

    # Place trap only in valid cells
    if (new_trap not in traps and new_trap != gator_pos and
            is_playable_cell(new_trap)):
        traps.append(new_trap)


def is_playable_cell(position):
    """
    Check if the position is within the playable grid (not swamp).
    """
    row, col = position
    return (SWAMP_BORDER <= row < SWAMP_BORDER + GRID_SIZE and
            SWAMP_BORDER <= col < SWAMP_BORDER + GRID_SIZE)


def is_gator_trapped(gator_pos, traps):
    """
    Check if the gator is completely trapped (no valid moves).
    """
    for action in actions:
        new_pos = get_new_position(gator_pos, action)
        if is_valid_position(new_pos, traps):
            return False
    return True


def animate_gator_exit():
    """
    Animate the gator running off the screen before showing the "You Lose!" screen.
    """
    global gator_pos
    dx, dy = 0, 0

    # Determine the direction in which the gator left the grid
    if gator_pos[0] < SWAMP_BORDER:
        dx, dy = -1, 0
    elif gator_pos[0] >= SWAMP_BORDER + GRID_SIZE:
        dx, dy = 1, 0
    elif gator_pos[1] < SWAMP_BORDER:
        dx, dy = 0, -1
    elif gator_pos[1] >= SWAMP_BORDER + GRID_SIZE:
        dx, dy = 0, 1

    # Animate the gator moving step by step off the screen
    for _ in range(SWAMP_BORDER + 2):
        gator_pos = [gator_pos[0] + dx, gator_pos[1] + dy]
        draw_grid()
        rect = pygame.Rect(gator_pos[1] * CELL_SIZE, gator_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if gator_image:
            screen.blit(gator_image, rect)
        else:
            pygame.draw.rect(screen, ORANGE, rect)
        pygame.display.flip()
        pygame.time.delay(300)


def end_screen(message):
    """
    Display the end screen with a message and a replay button.
    """
    font = pygame.font.Font(None, 50)
    button_font = pygame.font.Font(None, 40)

    text = font.render(message, True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 3))
    button = pygame.Rect(SCREEN_SIZE // 2 - 75, SCREEN_SIZE // 2, 150, 50)
    button_text = button_font.render("Play Again", True, WHITE)
    button_text_rect = button_text.get_rect(center=button.center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and button.collidepoint(event.pos):
                main()  # Restart the game

        screen.fill(BLUE)
        screen.blit(text, text_rect)
        pygame.draw.rect(screen, ORANGE, button)
        screen.blit(button_text, button_text_rect)
        pygame.display.flip()


def get_new_position(position, action):
    """
    Get the new position based on the current position and the action.
    """
    row, col = position
    if action == "up":
        return [row - 1, col]
    elif action == "down":
        return [row + 1, col]
    elif action == "left":
        return [row, col - 1]
    elif action == "right":
        return [row, col + 1]
    return position


def is_valid_position(position, traps):
    """
    Check if the new position is valid (inside the playable grid and not a trap).
    """
    row, col = position
    return (SWAMP_BORDER <= row < SWAMP_BORDER + GRID_SIZE and
            SWAMP_BORDER <= col < SWAMP_BORDER + GRID_SIZE and
            position not in traps)


def is_in_swamp(position):
    """
    Check if the position is in the swamp area (outside the playable grid).
    """
    row, col = position
    return not (SWAMP_BORDER <= row < SWAMP_BORDER + GRID_SIZE and
                SWAMP_BORDER <= col < SWAMP_BORDER + GRID_SIZE)


def satisfies_ltl(move, gator_pos, traps):
    """
    Use LTL logic to check if the gator's next move satisfies safety and reachability.
    """
    new_pos = get_new_position(gator_pos, move)
    # Safety: Avoid traps
    if new_pos in traps:
        return False
    # Reachability: Eventually reach the swamp
    if is_in_swamp(new_pos):
        return True
    return True


def get_best_move(gator_pos, traps, policy):
    """
    Decide the best move for the gator based on the optimal policy and LTL constraints.
    """
    action = policy.get(tuple(gator_pos))
    if action is None:
        return gator_pos

    if satisfies_ltl(action, gator_pos, traps):
        new_pos = get_new_position(gator_pos, action)
        return new_pos
    else:
        for alt_action in actions:
            if satisfies_ltl(alt_action, gator_pos, traps):
                alt_new_pos = get_new_position(gator_pos, alt_action)
                if is_valid_position(alt_new_pos, traps) or is_in_swamp(alt_new_pos):
                    return alt_new_pos
        return gator_pos


def value_iteration(traps, gamma=0.9, theta=1e-4):
    """
    Perform Value Iteration to compute the value function and policy.
    Uses stochastic transitions:
    - 80% chance to move in the chosen direction
    - 20% chance spread equally among other directions
    """
    states = [(row, col) for row in range(TOTAL_SIZE) for col in range(TOTAL_SIZE)]
    value_function = {state: 0.0 for state in states}
    policy = {state: None for state in states}

    # Initialize terminal and trap states
    for state in states:
        if is_in_swamp(state):
            value_function[state] = 0.0
        elif list(state) in traps:
            value_function[state] = -float('inf')

    action_prob_main = 0.8
    action_prob_side = (1.0 - action_prob_main) / (len(actions) - 1)

    while True:
        delta = 0
        for state in states:
            if is_in_swamp(state) or list(state) in traps:
                continue

            max_value = -float('inf')
            best_action = None

            for action in actions:
                expected_value = 0.0
                for candidate_action in actions:
                    prob = action_prob_side
                    if candidate_action == action:
                        prob = action_prob_main
                    new_pos = get_new_position(list(state), candidate_action)

                    if is_in_swamp(new_pos):
                        reward = 100
                        next_val = 0.0
                    elif list(new_pos) in traps:
                        reward = -10
                        next_val = value_function[state]
                    elif is_valid_position(new_pos, traps):
                        reward = -1
                        next_val = value_function[tuple(new_pos)]
                    else:
                        reward = -10
                        next_val = value_function[state]

                    expected_value += prob * (reward + gamma * next_val)

                if expected_value > max_value:
                    max_value = expected_value
                    best_action = action

            delta = max(delta, abs(max_value - value_function[state]))
            value_function[state] = max_value
            policy[state] = best_action

        if delta < theta:
            break

    return value_function, policy


def compute_policy():
    """
    Compute the optimal policy based on current traps.
    """
    value_func, optimal_policy = value_iteration(traps)
    return optimal_policy


def move_gator(policy):
    """
    Move the gator using the optimal policy and LTL constraints.
    With 80% probability follow best_move, else random action from the others.
    Print whether the chosen action was optimal or random.
    """
    global gator_pos
    best_move = policy.get(tuple(gator_pos))
    if best_move is None:
        print("No optimal action found. Gator stays in place.")
        return

    if not satisfies_ltl(best_move, gator_pos, traps):
        possible_moves = [a for a in actions if satisfies_ltl(a, gator_pos, traps)]
        if not possible_moves:
            print("No LTL-compliant actions available. Gator stays in place.")
            return
        best_move = random.choice(possible_moves)

    # 80% optimal, 20% random
    if random.random() < 0.8:
        chosen_action = best_move
        taken_action_type = "optimal"
    else:
        others = [a for a in actions if a != best_move]
        chosen_action = random.choice(others)
        taken_action_type = "random"

    new_pos = get_new_position(gator_pos, chosen_action)
    if is_valid_position(new_pos, traps) or is_in_swamp(new_pos):
        gator_pos = new_pos
        print(f"Gator took action: {chosen_action} ({taken_action_type})")
    else:
        print(f"Chosen action {chosen_action} ({taken_action_type}) was invalid. Gator stays in place.")


def get_full_path(policy):
    """
    Compute the full path the gator will take from its current position to escape.
    Deterministic tracing of the policy (not considering stochasticity).
    """
    path = []
    current_state = tuple(gator_pos)
    visited = set()
    max_steps = TOTAL_SIZE * TOTAL_SIZE

    for _ in range(max_steps):
        if is_in_swamp(current_state):
            path.append(current_state)
            break
        if current_state in visited:
            path.append(current_state)
            break
        visited.add(current_state)
        action = policy.get(current_state)
        if action is None:
            path.append(current_state)
            break
        next_state = tuple(get_new_position(list(current_state), action))
        path.append(current_state)
        current_state = next_state

    return path


def print_full_path(policy):
    """
    Print the entire optimal path for the gator based on the current policy.
    """
    path = get_full_path(policy)
    if not path:
        print("No path found for the gator.")
        return
    path_description = " -> ".join([str(state) for state in path])
    print(f"Optimal path for the gator: {path_description}")


def print_full_path_with_moves(policy):
    """
    Print the entire optimal path for the gator with move directions.
    """
    path = get_full_path(policy)
    if not path:
        print("No path found for the gator.")
        return

    path_description = ""
    for i in range(len(path) - 1):
        current = path[i]
        next_ = path[i + 1]
        move = get_move_direction(current, next_)
        path_description += f"{current} -> {next_} "
    path_description += f"{path[-1]}"
    print(f"Path for the gator:\n{path_description}")


def get_move_direction(current, next_):
    """
    Determine the direction of movement from current state to next state.
    """
    row_diff = next_[0] - current[0]
    col_diff = next_[1] - current[1]

    if row_diff == -1 and col_diff == 0:
        return "up"
    elif row_diff == 1 and col_diff == 0:
        return "down"
    elif row_diff == 0 and col_diff == -1:
        return "left"
    elif row_diff == 0 and col_diff == 1:
        return "right"
    return "unknown"


def main():
    global gator_pos, traps
    gator_pos = gator_start_pos.copy()  # Reset gator position
    traps = []  # Reset traps
    policy = compute_policy()

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Mouse click to place traps
            if event.type == pygame.MOUSEBUTTONDOWN:
                place_trap(event.pos)
                policy = compute_policy()  # Recompute policy after placing a trap
                move_gator(policy)  # Move the gator after the player places a trap
                print_full_path_with_moves(policy)  # Print the entire optimal path

        draw_grid()

        # Check if the Gator escapes to the swamp
        if is_in_swamp(gator_pos):
            animate_gator_exit()
            end_screen("You Lose!")
            return

        # Check if the Gator is trapped
        if is_gator_trapped(gator_pos, traps):
            end_screen("You Win!")
            return

        pygame.display.flip()
        clock.tick(5)


if __name__ == "__main__":
    main()
