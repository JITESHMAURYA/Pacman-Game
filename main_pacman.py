import pygame
import sys
import random
import math
import heapq
from collections import deque

pygame.init()

BLACK = (0, 0, 0)
BLUE = (0, 0, 110)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

CELL_SIZE = 30
GRID_WIDTH = 19
GRID_HEIGHT = 21
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + 50

PLAYING = 0
GAME_OVER = 1
MODE_SELECT = 2
YOU_WON = 3
game_state = MODE_SELECT


is_ai_mode = True  

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man AI/Manual")

font = pygame.font.Font(None, 36) 

grid = [
    [1]*19,
    [1,0,0,0,1,0,0,0,1,1,1,0,0,0,1,0,0,0,1],
    [1,0,1,0,1,0,1,0,1,1,1,0,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,1,1,0,1,1,1,0,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,1],
    [1,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,1,1,1],
    [1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1]*19
]

totalScore = 0
for i in range (0,21):
    for j in range (0,19):
        if grid[i][j]==0:
            totalScore += 10

pacman = {'x': 1, 'y': 1, 'mouth_open': False}
ghosts = [
    {'x': 9, 'y': 8, 'color': RED},
    {'x': 7, 'y': 9, 'color': PINK},
    {'x': 11, 'y': 9, 'color': CYAN},
    {'x': 9, 'y': 10, 'color': ORANGE},
]

score = 0

clock = pygame.time.Clock()
#timing variables
last_pacman_move_time = 0
last_ghost_move_time = 0
last_mouth_anim_time = 0
#movement delays
pacman_move_delay = 200
ghost_move_delay = 400
mouth_anim_delay = 300
manual_move_delay = 150
last_manual_move_time = 0

directions = [(1,0), (0,1), (-1,0), (0,-1)] 

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])



def astar(start, goals):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    ghost_positions = [(ghost['x'], ghost['y']) for ghost in ghosts]

    while frontier:
        _p, current = heapq.heappop(frontier)
        if current in goals:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in directions:
            next = (current[0] + dx, current[1] + dy)
            if 0 <= next[0] < GRID_WIDTH and 0 <= next[1] < GRID_HEIGHT and grid[next[1]][next[0]] != 1:
                danger_penalty = sum(5 for gx, gy in ghost_positions if abs(next[0]-gx)+abs(next[1]-gy) <= 2)
                new_cost = cost_so_far[current] + 1 + danger_penalty
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    nearest_goal = min(goals, key=lambda g: heuristic(next, g))
                    priority = new_cost + heuristic(next, nearest_goal)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current
    return []




def bfs(start, goal):
    queue = deque([start])
    came_from = {}
    visited = {start}
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and grid[ny][nx] != 1:
                next_pos = (nx, ny)
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append(next_pos)
                    came_from[next_pos] = current
    if goal not in came_from:
        return []
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def find_all_dots():
    return [(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if grid[y][x] == 0]

def move_pacman():
    global score

    if grid[pacman['y']][pacman['x']] == 0:
        grid[pacman['y']][pacman['x']] = 2
        score += 10

    all_dots = find_all_dots()
    if not all_dots:
        return

    def is_near_ghost(x, y, distance=3):
        return any(abs(x - ghost['x']) + abs(y - ghost['y']) <= distance for ghost in ghosts)

    def select_best_dot(dots):
        best_dot = None
        best_score = float('-inf')
        for dot in dots:
            ghost_penalty = sum(10 for ghost in ghosts if abs(dot[0] - ghost['x']) + abs(dot[1] - ghost['y']) <= 3)
            dot_score = 1 / (abs(dot[0] - pacman['x']) + abs(dot[1] - pacman['y']) + 1) - ghost_penalty
            if dot_score > best_score:
                best_score = dot_score
                best_dot = dot
        return best_dot

    best_dot = select_best_dot(all_dots)
    if not best_dot:
        return

    path = astar((pacman['x'], pacman['y']), [best_dot])
    if not path:
        return

    next_x, next_y = path[0]  # Only take 1 step
    pacman['x'], pacman['y'] = next_x, next_y
    if grid[next_y][next_x] == 0:
        grid[next_y][next_x] = 2
        score += 10

def move_ghost(ghost):
    path = bfs((ghost['x'], ghost['y']), (pacman['x'], pacman['y']))
    if path:
        next_x, next_y = path[0]
        if all(g['x'] != next_x or g['y'] != next_y for g in ghosts): 
            ghost['x'], ghost['y'] = next_x, next_y

def draw_pacman():
    x = pacman['x'] * CELL_SIZE + CELL_SIZE // 2
    y = pacman['y'] * CELL_SIZE + CELL_SIZE // 2 + 50
    radius = CELL_SIZE // 2 - 2

    if pacman['mouth_open']:
        # pie with a wedge removed (mouth open)
        mouth_angle = math.pi / 4  # 45 degrees
        start_angle = mouth_angle
        end_angle = 2 * math.pi - mouth_angle
        pygame.draw.arc(screen, YELLOW, (x - radius, y - radius, radius * 2, radius * 2), start_angle, end_angle, radius)
        # filled pie shape
        points = [(x, y)]
        for angle in [a / 100.0 * (end_angle - start_angle) + start_angle for a in range(101)]:
            points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))
        pygame.draw.polygon(screen, YELLOW, points)
    else:
        pygame.draw.circle(screen, YELLOW, (x, y), radius)

def draw_ghost(ghost, idx):
    x = ghost['x'] * CELL_SIZE + CELL_SIZE//2
    y = ghost['y'] * CELL_SIZE + CELL_SIZE//2 + 50
    offset = (idx%2)*4 - 2  # To avoid collision
    pygame.draw.circle(screen, ghost['color'], (x+offset, y-offset), CELL_SIZE//2-4)

def draw_game_over():
    screen.fill(BLACK)
    texts = [
        (pygame.font.Font(None, 64).render("GAME OVER", True, RED), SCREEN_HEIGHT//3),
        (pygame.font.Font(None, 48).render(f"Score: {score}", True, WHITE), SCREEN_HEIGHT//2),
        (pygame.font.Font(None, 36).render("Press SPACE to Restart", True, YELLOW), 2*SCREEN_HEIGHT//3)
    ]
    for text, y_pos in texts:
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))

def draw_mode_select():
    screen.fill(BLACK)
    title = pygame.font.Font(None, 64).render("Pac-Man", True, YELLOW)
    ai_text = pygame.font.Font(None, 48).render("Press A for AI Mode", True, CYAN)
    manual_text = pygame.font.Font(None, 48).render("Press M for Manual Mode", True, ORANGE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//4))
    screen.blit(ai_text, (SCREEN_WIDTH//2 - ai_text.get_width()//2, SCREEN_HEIGHT//2))
    screen.blit(manual_text, (SCREEN_WIDTH//2 - manual_text.get_width()//2, SCREEN_HEIGHT//2 + 60))

def draw_you_won():
    screen.fill(BLACK)
    texts = [
        (pygame.font.Font(None, 64).render("YOU WON!", True, YELLOW), SCREEN_HEIGHT//3),
        (pygame.font.Font(None, 48).render(f"Score: {score}", True, WHITE), SCREEN_HEIGHT//2),
        (pygame.font.Font(None, 36).render("Press SPACE to Restart", True, CYAN), 2*SCREEN_HEIGHT//3)
    ]
    for text, y_pos in texts:
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))

def reset_game():
    global pacman, ghosts, score, game_state, grid
    pacman = {'x': 1, 'y': 1, 'mouth_open': False}
    
    if is_ai_mode:
        ghosts = [
            {'x': 9, 'y': 8, 'color': RED},
            {'x': 11, 'y': 9, 'color': CYAN},
            # {'x': 10, 'y': 10, 'color': PINK},
        ]
    else:
        ghosts = [
            {'x': 9, 'y': 8, 'color': RED},
            {'x': 7, 'y': 9, 'color': PINK},
            {'x': 11, 'y': 9, 'color': CYAN},
            {'x': 9, 'y': 10, 'color': ORANGE},
        ]
    
    score = 0
    game_state = PLAYING
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == 2:
                grid[y][x] = 0 




running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state in (GAME_OVER, YOU_WON) and event.key == pygame.K_SPACE:
                game_state = MODE_SELECT
            elif game_state == MODE_SELECT:
                if event.key == pygame.K_a:
                    is_ai_mode = True
                    reset_game()
                elif event.key == pygame.K_m:
                    is_ai_mode = False
                    reset_game()

    if game_state == PLAYING:
        if is_ai_mode and current_time - last_pacman_move_time > pacman_move_delay:
            move_pacman()
            last_pacman_move_time = current_time

        if not is_ai_mode:
            if current_time - last_manual_move_time > manual_move_delay:
                keys = pygame.key.get_pressed()
                for dx, dy, key in [(1, 0, pygame.K_RIGHT), (-1, 0, pygame.K_LEFT), (0, -1, pygame.K_UP), (0, 1, pygame.K_DOWN)]:
                    if keys[key]:
                        nx, ny = pacman['x'] + dx, pacman['y'] + dy
                        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and grid[ny][nx] != 1:
                            pacman['x'], pacman['y'] = nx, ny
                            break
                last_manual_move_time = current_time

        if grid[pacman['y']][pacman['x']] == 0:
            grid[pacman['y']][pacman['x']] = 2
            score += 10

        if current_time - last_ghost_move_time > ghost_move_delay:
            for ghost in ghosts:
                move_ghost(ghost)
            last_ghost_move_time = current_time

        if current_time - last_mouth_anim_time > mouth_anim_delay:
            pacman['mouth_open'] = not pacman['mouth_open']
            last_mouth_anim_time = current_time

        screen.fill(BLACK)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x] == 1:
                    pygame.draw.rect(screen, BLUE, (x*CELL_SIZE, y*CELL_SIZE+50, CELL_SIZE, CELL_SIZE))
                elif grid[y][x] == 0:
                    pygame.draw.circle(screen, YELLOW, (x*CELL_SIZE+CELL_SIZE//2, y*CELL_SIZE+CELL_SIZE//2+50), 3)

        draw_pacman()
        for idx, ghost in enumerate(ghosts):
            draw_ghost(ghost, idx)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        for ghost in ghosts:
            if (pacman['x'] == ghost['x'] and pacman['y'] == ghost['y']):
                game_state = GAME_OVER
        if (score == totalScore):
            game_state = YOU_WON    

    elif game_state == MODE_SELECT:
        draw_mode_select()
    elif game_state == GAME_OVER:
        draw_game_over()
    elif game_state == YOU_WON:
        draw_you_won()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
