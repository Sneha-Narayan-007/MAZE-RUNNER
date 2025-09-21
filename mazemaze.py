import pygame
import sys
import random
import os


pygame.init()
pygame.mixer.init()
NEON_PINK = (255, 20, 147)
NEON_BLUE = (0, 255, 255)
NEON_GREEN = (57, 255, 20)


screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
clock = pygame.time.Clock()


BASE = os.path.dirname(__file__)
ASSETS = os.path.join(BASE, "assets")


WALL = 0
PATH = 1
PLAYER = 2
EXIT = 3
FAKE_EXIT = 4

DIFFICULTIES = {
    "EASY":   {"size": 15, "density": 0.20},
    "MEDIUM": {"size": 25, "density": 0.30},
    "HARD":   {"size": 35, "density": 0.40},
}


wall_img = pygame.image.load(os.path.join(ASSETS, "45298.jpg"))
runner_img = pygame.image.load(os.path.join(ASSETS, "vecteezy_cartoon-anime-onepiece-with-shopping-bag-ai-generative_34227675.png"))
exit_img = pygame.image.load(os.path.join(ASSETS,  "vecteezy_ancient-stone-archway-gate-with-intricate-carvings-and-metal_59052225.png"))
bg_img = pygame.image.load(os.path.join(ASSETS, "vecteezy_waterfall-game-background_24098100.jpg"))
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load sounds
pygame.mixer.music.load(os.path.join(ASSETS, "game-gaming-minecraft-background-music-377647.mp3"))
step_sound = pygame.mixer.Sound(os.path.join(ASSETS, "wood-step-sample-1-47664.mp3"))
win_sound = pygame.mixer.Sound(os.path.join(ASSETS, "violin-win-5-185128.mp3"))


def generate_maze(size, density):
    maze = [[WALL for _ in range(size)] for _ in range(size)]

    def carve(r, c):
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < size - 1 and 0 < nc < size - 1 and maze[nr][nc] == WALL:
                maze[r + dr // 2][c + dc // 2] = PATH
                maze[nr][nc] = PATH
                carve(nr, nc)

    maze[1][1] = PATH
    carve(1, 1)
    # Place real exit
    exit_r, exit_c = size - 2, size - 2
    maze[exit_r][exit_c] = EXIT

    # Place fake exit randomly on edge (but not same as real)
    edges = [(1, size - 2), (size - 2, 1), (1, 1), (size - 2, size - 3)]
    random.shuffle(edges)
    for fr, fc in edges:
        if maze[fr][fc] == PATH:
            maze[fr][fc] = FAKE_EXIT
            break

    return maze

# Draw maze tiles
def draw_maze(maze, player_pos, tile_size):
    maze_height = len(maze) * tile_size
    maze_width = len(maze[0]) * tile_size
    offset_x = (SCREEN_WIDTH - maze_width) // 2
    offset_y = (SCREEN_HEIGHT - maze_height) // 2

    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            x = c * tile_size + offset_x
            y = r * tile_size + offset_y
            if cell == WALL:
                screen.blit(pygame.transform.scale(wall_img, (tile_size, tile_size)), (x, y))
            elif cell == EXIT:
                screen.blit(pygame.transform.scale(exit_img, (tile_size, tile_size)), (x, y))
            elif (r, c) == player_pos:
                screen.blit(pygame.transform.scale(runner_img, (tile_size, tile_size)), (x, y))
            elif cell == FAKE_EXIT:
                pygame.draw.rect(screen, NEON_BLUE, (x, y, tile_size, tile_size), 3)  # Draw fake exit border



def home_screen():
    pygame.mixer.music.play(-1)
    font = pygame.font.SysFont("comicsansms", 72, bold=True)
    small_font = pygame.font.SysFont("arial", 36)

    while True:
        screen.blit(bg_img, (0, 0))
        title = font.render("MAZE RUNNER", True, NEON_PINK)

        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        y = 250
        for i, level in enumerate(DIFFICULTIES):
            btn = small_font.render(level, True, NEON_GREEN)

            screen.blit(btn, (SCREEN_WIDTH//2 - btn.get_width()//2, y))
            y += 60

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                y = 250
                for level in DIFFICULTIES:
                    rect = pygame.Rect(SCREEN_WIDTH//2 - 100, y, 200, 40)
                    if rect.collidepoint((mx, my)):
                        play_game(level)
                        break
                    y += 60


def play_game(difficulty):
    pygame.mixer.music.stop()
    config = DIFFICULTIES[difficulty]
    size = config["size"]
    maze = generate_maze(size, config["density"])
    player_pos = [1, 1]

    tile_size = min(SCREEN_WIDTH // size, SCREEN_HEIGHT // size)

    while True:
        screen.fill((0, 0, 0))
        draw_maze(maze, tuple(player_pos), tile_size)
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                r, c = player_pos
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_UP and maze[r - 1][c] != WALL:
                    player_pos[0] -= 1
                    step_sound.play()
                if event.key == pygame.K_DOWN and maze[r + 1][c] != WALL:
                    player_pos[0] += 1
                    step_sound.play()
                if event.key == pygame.K_LEFT and maze[r][c - 1] != WALL:
                    player_pos[1] -= 1
                    step_sound.play()
                if event.key == pygame.K_RIGHT and maze[r][c + 1] != WALL:
                    player_pos[1] += 1
                    step_sound.play()

                if maze[player_pos[0]][player_pos[1]] == EXIT:
                    win_sound.play()
                    show_congratulations()
                    return


def show_congratulations():
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont("comicsansms", 64, bold=True)
    text = font.render("🎉 Congratulations! You Escaped!", True, NEON_GREEN)

    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

# Start game
if __name__ == "__main__":
    home_screen()



