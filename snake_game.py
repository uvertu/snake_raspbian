import pygame
import random
import sys
import socket
import threading
import json

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
pygame.display.set_caption("Змейка - Сервер")
clock = pygame.time.Clock()

# Направления
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Сетевые настройки
HOST = '0.0.0.0'
PORT = 5555
connected_clients = []
server_socket = None
game_state_lock = threading.Lock()

# Глобальное состояние игры
game_state = {
    'status': 'WAITING',  # WAITING, PLAYING, PAUSED, GAME_OVER
    'score': 0,
    'snake_length': 0,
    'snake_alive': False,
    'food_position': (0, 0),
    'android_command': None
}


# Класс Змейка
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.score = 0
        for i in range(1, self.length):
            self.positions.append((self.positions[0][0] - i, self.positions[0][1]))
        self.alive = True

    def get_head_position(self):
        return self.positions[0]

    def turn(self, new_direction):
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


# Класс Еда
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))


# Серверная логика
def start_server():
    global server_socket, game_state

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Сервер запущен на {HOST}:{PORT}")
        print("Ожидание подключения Android-приложения...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Подключено Android-устройство: {addr}")
            connected_clients.append(client_socket)

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket,),
                daemon=True
            )
            client_thread.start()

    except Exception as e:
        print(f"Ошибка сервера: {e}")
    finally:
        if server_socket:
            server_socket.close()


def handle_client(client_socket):
    global game_state

    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8').strip()
            if not data:
                break

            with game_state_lock:
                if data in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                    if game_state['status'] == 'PLAYING':
                        game_state['android_command'] = data
                elif data == 'NEW_GAME':
                    game_state['status'] = 'PLAYING'
                    game_state['android_command'] = 'NEW_GAME'
                elif data == 'PAUSE':
                    if game_state['status'] == 'PLAYING':
                        game_state['status'] = 'PAUSED'
                    elif game_state['status'] == 'PAUSED':
                        game_state['status'] = 'PLAYING'
                elif data == 'END_GAME':
                    game_state['status'] = 'WAITING'
                    game_state['android_command'] = 'END_GAME'

            # Отправляем подтверждение
            client_socket.send("OK".encode('utf-8'))

    except ConnectionResetError:
        print("Соединение с Android разорвано")
    except Exception as e:
        print(f"Ошибка обработки клиента: {e}")
    finally:
        if client_socket in connected_clients:
            connected_clients.remove(client_socket)
        client_socket.close()


def broadcast_game_state(snake, food):
    global game_state, connected_clients

    if not connected_clients:
        return

    # Обновляем состояние игры
    with game_state_lock:
        game_state['score'] = snake.score
        game_state['snake_length'] = snake.length
        game_state['snake_alive'] = snake.alive
        game_state['food_position'] = food.position

        if not snake.alive and game_state['status'] == 'PLAYING':
            game_state['status'] = 'GAME_OVER'

        state_json = json.dumps(game_state)

    # Отправляем всем подключенным клиентам
    for client in connected_clients[:]:
        try:
            client.send((state_json + '\n').encode('utf-8'))
        except:
            if client in connected_clients:
                connected_clients.remove(client)


def process_android_command(snake):
    global game_state

    with game_state_lock:
        command = game_state.get('android_command')
        game_state['android_command'] = None

    if command == 'NEW_GAME':
        snake.reset()
        return 'RESET_FOOD'
    elif command == 'END_GAME':
        snake.reset()
        return 'END_GAME'
    elif command in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
        direction_map = {
            'UP': UP, 'DOWN': DOWN,
            'LEFT': LEFT, 'RIGHT': RIGHT
        }
        snake.turn(direction_map[command])

    return None


# Отрисовка
def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, GRAY, rect, 1)


def draw_snake(surface, snake):
    for i, p in enumerate(snake.positions):
        if not snake.alive:
            color = RED
        else:
            color = GREEN if i == 0 else BLUE
        rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE),
                           (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)


def draw_food(surface, food):
    rect = pygame.Rect((food.position[0] * GRID_SIZE,
                        food.position[1] * GRID_SIZE),
                       (GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(surface, RED, rect)
    pygame.draw.rect(surface, BLACK, rect, 1)


def draw_ui(surface, game_state):
    font = pygame.font.SysFont('arial', 25)

    # Счет
    score_text = font.render(f'Счет: {game_state["score"]}', True, WHITE)
    surface.blit(score_text, (5, 5))

    # Статус игры
    status_colors = {
        'WAITING': (200, 200, 200),
        'PLAYING': GREEN,
        'PAUSED': (255, 165, 0),
        'GAME_OVER': RED
    }

    status_texts = {
        'WAITING': 'Ожидание игры...',
        'PLAYING': 'Игра идет',
        'PAUSED': 'ПАУЗА',
        'GAME_OVER': 'ИГРА ОКОНЧЕНА'
    }

    status = game_state['status']
    status_color = status_colors.get(status, WHITE)
    status_text = font.render(status_texts[status], True, status_color)
    surface.blit(status_text, (WIDTH - status_text.get_width() - 10, 5))

    # Экран завершения игры
    if status == 'GAME_OVER':
        font_large = pygame.font.SysFont('arial', 50)
        font_small = pygame.font.SysFont('arial', 30)

        game_over = font_large.render('ИГРА ОКОНЧЕНА', True, RED)
        score_text = font_small.render(f'Ваш счет: {game_state["score"]}', True, WHITE)

        surface.blit(game_over, (WIDTH // 2 - game_over.get_width() // 2, HEIGHT // 2 - 60))
        surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))


def get_local_ip():
    """Получить локальный IP-адрес для подключения"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# В начале main() добавьте:
def main():
    local_ip = get_local_ip()
    print("=" * 50)
    print(f"Сервер змейки запущен")
    print(f"Локальный IP: {local_ip}")
    print(f"Порт: {PORT}")
    print("=" * 50)
    print("Для подключения с Android введите этот IP в приложении")
    print("=" * 50)

    global game_state

    # Запускаем сервер
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Инициализация игры
    snake = Snake()
    food = Food()
    food.randomize_position()

    print("Игра инициализирована. Ожидание команды 'NEW_GAME' от Android...")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Локальное управление для тестирования
                if event.key == pygame.K_UP:
                    snake.turn(UP)
                elif event.key == pygame.K_DOWN:
                    snake.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.turn(RIGHT)
                elif event.key == pygame.K_p:
                    if game_state['status'] == 'PLAYING':
                        game_state['status'] = 'PAUSED'
                    elif game_state['status'] == 'PAUSED':
                        game_state['status'] = 'PLAYING'
                elif event.key == pygame.K_n:
                    game_state['status'] = 'PLAYING'
                    snake.reset()
                    food.randomize_position()

        # Обработка команд от Android
        command_result = process_android_command(snake)
        if command_result == 'RESET_FOOD':
            food.randomize_position()
            while food.position in snake.positions:
                food.randomize_position()
        elif command_result == 'END_GAME':
            food.randomize_position()

        # Игровая логика (только если игра активна)
        if game_state['status'] == 'PLAYING' and snake.alive:
            if not snake.move():
                game_state['status'] = 'GAME_OVER'

            if snake.get_head_position() == food.position:
                snake.grow()
                food.randomize_position()
                while food.position in snake.positions:
                    food.randomize_position()

        # Отправка состояния на Android
        broadcast_game_state(snake, food)

        # Отрисовка
        screen.fill(BLACK)
        draw_grid(screen)

        if game_state['status'] != 'WAITING':
            draw_snake(screen, snake)
            draw_food(screen, food)

        draw_ui(screen, game_state)

        pygame.display.update()
        clock.tick(FPS)

    # Завершение
    if server_socket:
        server_socket.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()