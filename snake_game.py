import pygame
import random

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

#Класс Еда
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))