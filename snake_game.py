import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
RED = (255, 50, 50)
BLUE = (30, 144, 255)
GRAY = (40, 40, 40)

# Настройки окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка на Raspberry Pi")
clock = pygame.time.Clock()

# Направления
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

#Класс Змейка
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.score = 0
        # Создаем начальное тело змейки
        for i in range(1, self.length):
            self.positions.append((self.positions[0][0] - i, self.positions[0][1]))
        self.alive = True

    def get_head_position(self):
        return self.positions[0]

    def turn(self, new_direction):
        # Запрещен разворот на 180 градусов
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def move(self):
        if not self.alive:
            return False

        head = self.get_head_position()
        x, y = self.direction
        new_x = (head[0] + x) % GRID_WIDTH
        new_y = (head[1] + y) % GRID_HEIGHT
        new_position = (new_x, new_y)

        # Проверка на столкновение с собой
        if new_position in self.positions[1:]:
            self.alive = False
            return False

        self.positions.insert(0, new_position)
        if len(self.positions) > self.length:
            self.positions.pop()

        return True

    def grow(self):
        self.length += 1
        self.score += 10

    def draw(self, surface):
        for i, p in enumerate(self.positions):
            if not self.alive:
                color = RED if i == 0 else RED
            else:
                color = GREEN if i == 0 else BLUE
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

#Класс Еда
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))

    def draw(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE),
                           (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

#Отрисовка игры
def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, GRAY, rect, 1)


def draw_score(surface, score, game_over=False):
    font = pygame.font.SysFont('arial', 25)
    if game_over:
        color = RED
        text = font.render(f'Последний счет: {score}', True, color)
    else:
        color = WHITE
        text = font.render(f'Счет: {score}', True, color)
    surface.blit(text, (5, 5))


def draw_game_over(surface, score):
    font_large = pygame.font.SysFont('arial', 50)
    font_small = pygame.font.SysFont('arial', 30)

    game_over = font_large.render('ИГРА ОКОНЧЕНА', True, RED)
    score_text = font_small.render(f'Ваш счет: {score}', True, WHITE)
    restart_text = font_small.render('Нажмите R для рестарта', True, WHITE)

    surface.blit(game_over, (WIDTH // 2 - game_over.get_width() // 2, HEIGHT // 2 - 60))
    surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 40))


def main():
    snake = Snake()
    food = Food()
    game_over = False
    final_score = 0  #Хранение финального счета

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        snake.reset()
                        food.randomize_position()
                        game_over = False
                        final_score = 0
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        snake.turn(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        snake.turn(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        snake.turn(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        snake.turn(RIGHT)

        if not game_over:
            # Движение змейки
            if not snake.move():
                game_over = True
                final_score = snake.score  # Сохранение счета при проигрыше

            # Проверка на съедание еды
            if snake.get_head_position() == food.position:
                snake.grow()
                food.randomize_position()
                # Проверка, что еда не появилась в теле змейки
                while food.position in snake.positions:
                    food.randomize_position()

        # Отрисовка
        screen.fill(BLACK)
        draw_grid(screen)
        snake.draw(screen)
        if not game_over:  # Показывать еду только если игра не окончена
            food.draw(screen)

        if game_over:
            draw_score(screen, final_score, game_over=True)
            draw_game_over(screen, final_score)
        else:
            draw_score(screen, snake.score)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()