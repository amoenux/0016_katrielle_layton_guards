import pygame
import ast
from functools import reduce

def backtrack_pruning(target_size,n, incompatibilities, sightings_sets, path, result, start=0):
    if path:
        valid_solution = len(reduce(set.union, (sightings_sets[i] for i in path)))==target_size
    else:
        valid_solution=False

    if valid_solution:
        result.append(path[:])
        return

    for i in range(start, n):
        # Early pruning: skip i if it's incompatible with any selected number
        if any(i in incompatibilities[p] or p in incompatibilities[i] for p in path):
            continue

        path.append(i)
        backtrack_pruning(target_size,n, incompatibilities, sightings_sets, path, result,i + 1)
        path.pop()

    return result


def solve(target_size,guard_cells, incompatibilities, sightings_sets):
    return backtrack_pruning(target_size,len(guard_cells), incompatibilities, sightings_sets,path=[],result=[])


# To solve the puzzle
def prepare_and_solve(grid):
    rows = len(grid)
    cols = len(grid[0])

    guardcell_to_number = {}
    guards = []
    guard_cells = []
    for row in range(rows):
        for col in range(cols):
            if grid[row][col] == 1:
                guards.append((row, col))
                guard_cells.append(row * cols + col)
                guardcell_to_number[row * cols + col] = len(guards) - 1

    print(guards)
    print(guard_cells)
    print(guardcell_to_number)
    incompatibilities = []
    sightings = []
    for i, guard in enumerate(guards):
        # print(guard)
        inc = set()
        sight = [0 for _ in range(rows * cols)]
        # print("1")
        sight[guard[0] * cols + guard[1]] = 1
        for vert in range(guard[0] - 1, -1, -1):
            # print(vert,vert*cols+guard[1])
            sight[vert * cols + guard[1]] = 1
            if grid[vert][guard[1]] == 1:
                inc.add(guardcell_to_number[vert * cols + guard[1]])
            if grid[vert][guard[1]] == 2:
                break
        # print("2")
        for vert in range(guard[0] + 1, rows):
            # print(vert,vert*cols+guard[1])
            sight[vert * cols + guard[1]] = 1
            if grid[vert][guard[1]] == 1:
                inc.add(guardcell_to_number[vert * cols + guard[1]])
            if grid[vert][guard[1]] == 2:
                break
        # print("3")
        for hor in range(guard[1] - 1, -1, -1):
            # print(hor,guard[0]*cols+hor)
            sight[guard[0] * cols + hor] = 1
            if grid[guard[0]][hor] == 1:
                inc.add(guardcell_to_number[guard[0] * cols + hor])
            if grid[guard[0]][hor] == 2:
                break
        # print("4")
        for hor in range(guard[1] + 1, cols):
            # print(hor,guard[0]*cols+hor)
            sight[guard[0] * cols + hor] = 1
            if grid[guard[0]][hor] == 1:
                inc.add(guardcell_to_number[guard[0] * cols + hor])
            if grid[guard[0]][hor] == 2:
                break
        #Adding all obstacles so they are artificially seen by all guards
        #Because even if obstacles are not seen by any guard the solution is valid
        for row in range(rows):
            for col in range(cols):
                if grid[row][col]==2:
                    sight[row*cols+col]=1
                
        incompatibilities.append(inc)
        sightings.append(sight)

    print(sightings)
    print(incompatibilities)

    sightings_sets = []
    for sight in sightings:
        sight_set = set()
        for i in range(len(sight)):
            if sight[i] == 1:
                sight_set.add(i)
        sightings_sets.append(sight_set)
        print(sight_set)

    target_size=rows*cols

    result = solve(target_size,guard_cells, incompatibilities, sightings_sets)
    # Print the result
    print(f"\nThe solutions are (counting for 0, by row and then by col):")
    for sol in result:
        print(sol)
    return (
        result[0] if result else None
    )  # Return the first valid solution, or None if no solution is found


def read_grids():
    grids = {}
    old_names = []
    with open("LaytonGuardsGrids.txt", "r") as f:
        for line in f.readlines():
            sp = line.split("\t")
            grids[sp[0]] = ast.literal_eval(sp[1])
            old_names.append(sp[0])
    #print(grids)
    return grids, old_names


def write_grids(grids, new_names):
    with open("LaytonGuardsGrids.txt", "a+") as f:
        for name in new_names:
            f.write(name)
            f.write("\t")
            f.write(str(grids[name]))
            f.write("\n")


def create_new_grid(rows, cols):
    # Initialize Pygame
    pygame.init()

    # Set up the display
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Layton daily puzzle 1")

    # Define colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    # Set up clock for FPS
    clock = pygame.time.Clock()

    # Initialize game state

    side = 60

    horizontal_lines = [
        ((50, a), (50 + (cols * side), a)) for a in range(50, 51 + rows * side, side)
    ]
    vertical_lines = [
        ((a, 50), (a, 50 + (rows * side))) for a in range(50, 51 + cols * side, side)
    ]
    circle_x, circle_y = 750, 550
    circle_radius = 50
    game_over = False

    grid = [[0 for _ in range(cols)] for j in range(rows)]

    # 0 for empty, 1 for guards, 2 for obstacles
    element = 1

    # Draw the grid
    screen.fill(BLACK)
    for line in vertical_lines:
        pygame.draw.line(screen, WHITE, line[0], line[1])
    for line in horizontal_lines:
        pygame.draw.line(screen, WHITE, line[0], line[1])

    # And the circle
    pygame.draw.circle(screen, WHITE, (circle_x, circle_y), circle_radius)

    # And the text
    pygame.font.init()
    my_font = pygame.font.SysFont("Comic Sans MS", 30)
    text_surface = my_font.render("Create", False, BLACK)
    screen.blit(text_surface, (710, 525))

    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (
                    50 <= mouse_x <= 50 + cols * side
                    and 50 <= mouse_y <= 50 + rows * side
                ):
                    sq_x = mouse_x // side - 1
                    sq_y = mouse_y // side - 1

                    print((sq_y, sq_x), element)

                    grid[sq_y][sq_x] = element

                    if element == 0:
                        pygame.draw.circle(
                            screen,
                            BLACK,
                            (sq_x * side + 50 + side / 2, sq_y * side + 50 + side / 2),
                            side / 3,
                        )
                    if element == 1:
                        pygame.draw.circle(
                            screen,
                            RED,
                            (sq_x * side + 50 + side / 2, sq_y * side + 50 + side / 2),
                            side / 3,
                        )
                    if element == 2:
                        pygame.draw.circle(
                            screen,
                            BLUE,
                            (sq_x * side + 50 + side / 2, sq_y * side + 50 + side / 2),
                            side / 3,
                        )

                # Check if the mouse click is inside the circle
                elif (mouse_x - circle_x) ** 2 + (
                    mouse_y - circle_y
                ) ** 2 <= circle_radius**2:
                    print("Created puzzle")
                    print(grid)
                    # sol=solve(grid)
                    # for guard in sol:
                    #    pygame.draw.circle(screen,YELLOW,(guard[0]*side+50+side/2,guard[1]*side+50+side/2),side/3)
                    pygame.quit()
                    return grid

            if event.type == pygame.KEYDOWN:
                if pygame.K_0 == event.key:
                    element = 0
                elif pygame.K_1 == event.key:
                    element = 1
                elif pygame.K_2 == event.key:
                    element = 2
                print(f"Pressed {event.key-pygame.K_0}")

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS


def print_help():
    print()
    print("To create a new puzzle grid input: new <rows> <cols> [name]")
    print("To solve a created puzzle input: solve <name/number>")


def logic():
    grids, old_names = read_grids()
    old_names_set = set(old_names)
    all_names_set = old_names_set

    next_valid_name = 1
    while True:
        if str(next_valid_name) in old_names_set:
            next_valid_name += 1
        else:
            break

    new_names = []

    print_help()
    while inp := input("> "):
        sp = inp.split()
        match sp[0]:
            case "new":  # syntax: new 3 4 [name]

                # Validate input parameters
                if len(sp) < 3:
                    print('Input should be of the form "new 3 4 [name]"')
                    continue
                try:
                    rows = int(sp[1])
                except:
                    ValueError(f"Rows {sp[1]} invalid")
                try:
                    cols = int(sp[2])
                except:
                    ValueError(f"Cols {sp[2]} invalid")

                # Either take a name or assign automatically
                if len(sp) > 3:
                    name = sp[3]
                    if name in all_names_set:
                        print(f"Name taken, assigning {next_valid_name} instead")
                        name = str(next_valid_name)
                else:
                    name = str(next_valid_name)

                # Find next valid (integer) name
                while True:
                    if str(next_valid_name) in all_names_set:
                        next_valid_name += 1
                    else:
                        break

                # Now call pygame to create new grid
                print(f"Creating {rows} {cols} {name}")
                new_grid = create_new_grid(rows, cols)
                if new_grid:
                    grids[name] = new_grid
                    new_names.append(name)
                    all_names_set = old_names_set | set(new_names)

            case "solve":
                if len(sp) > 0:
                    if sp[1] not in all_names_set:
                        print(f"Name {sp[1]} not found")
                    else:
                        prepare_and_solve(grids[sp[1]])
            case default:
                continue

    write_grids(grids, new_names)


# Start the game
# game()
# solve([[1, 0, 0, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 1]])
# solve([[1,0,0,0],[0,1,0,0],[0,0,0,1]])
logic()
