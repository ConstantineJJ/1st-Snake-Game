import random
import pygame
import os
import sys

# Получаем абсолютный путь к папке проекта
def get_project_root():
    """Возвращает корневую папку проекта"""
    if getattr(sys, 'frozen', False):
        # Если запущен как exe
        return os.path.dirname(sys.executable)
    else:
        # Если запущен как скрипт - поднимаемся на 2 уровня вверх от index.py
        current_file = os.path.abspath(__file__)  # .../game_types/index.py
        src_dir = os.path.dirname(os.path.dirname(current_file))  # .../src
        project_root = os.path.dirname(src_dir)  # .../snake-game
        return project_root

PROJECT_ROOT = get_project_root()
ASSETS_PATH = os.path.join(PROJECT_ROOT, 'assets')

print(f"🔍 Корневая папка проекта: {PROJECT_ROOT}")
print(f"🔍 Путь к assets: {ASSETS_PATH}")

class Snake:
    def __init__(self, grid_size=20):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.body = [(10, 10), (9, 10), (8, 10)]  # Начинаем с 3 сегментов
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        
        # Загрузка отдельных текстур
        try:
            # Загружаем голову
            head_img = pygame.image.load(os.path.join(ASSETS_PATH, 'snake_head.png'))
            self.head_right = pygame.transform.scale(head_img, (self.grid_size, self.grid_size))
            self.head_left = pygame.transform.flip(self.head_right, True, False)
            self.head_up = pygame.transform.rotate(self.head_right, 90)
            self.head_down = pygame.transform.rotate(self.head_right, -90)
            
            # Загружаем тело (горизонтальное)
            body_img = pygame.image.load(os.path.join(ASSETS_PATH, 'snake_body.png'))
            body_scaled = pygame.transform.scale(body_img, (self.grid_size, self.grid_size))
            self.body_horizontal = body_scaled
            self.body_vertical = pygame.transform.rotate(body_scaled, 90)
            
            # Загружаем диагональное тело (для поворотов)
            try:
                diagonal_img = pygame.image.load(os.path.join(ASSETS_PATH, 'snake_body_diagonal.png'))
                self.body_diagonal = pygame.transform.scale(diagonal_img, (self.grid_size, self.grid_size))
                print("✅ Диагональная текстура змейки загружена!")
            except:
                print("⚠️ Диагональная текстура не найдена, будет использоваться вращение")
                self.body_diagonal = None
            
            # Загружаем хвост
            tail_img = pygame.image.load(os.path.join(ASSETS_PATH, 'snake_tail.png'))
            tail_scaled = pygame.transform.scale(tail_img, (self.grid_size, self.grid_size))
            self.tail_right = tail_scaled
            self.tail_left = pygame.transform.flip(tail_scaled, True, False)
            self.tail_up = pygame.transform.rotate(tail_scaled, 90)
            self.tail_down = pygame.transform.rotate(tail_scaled, -90)
            
            print("✅ Текстуры змейки загружены!")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки текстур змейки: {e}")
            print(f"Путь к assets: {ASSETS_PATH}")
            self.head_right = None
            self.body_horizontal = None
            self.body_diagonal = None
            self.tail_right = None

    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.next_direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        self.body.pop()
        self.direction = self.next_direction

    def grow(self):
        self.body.append(self.body[-1])

    def set_direction(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.next_direction = direction

    def create_turn_texture(self, incoming_dir, outgoing_dir):
        """Создает текстуру поворота из диагональной текстуры"""
        if not self.body_diagonal:
            # Fallback - если диагональная текстура не загружена, используем горизонтальную
            return self.body_horizontal if self.body_horizontal else None
        
        import math
        
        # Определяем направление поворота (векторное произведение)
        # Положительное = поворот налево (внутренний угол)
        # Отрицательное = поворот направо (внешний угол)
        cross_product = incoming_dir[0] * outgoing_dir[1] - incoming_dir[1] * outgoing_dir[0]
        is_right_turn = cross_product < 0  # Внешний угол
        
        # Вычисляем угол входящего направления
        incoming_angle = math.atan2(incoming_dir[1], incoming_dir[0]) * 180 / math.pi
        # Вычисляем угол выходящего направления
        outgoing_angle = math.atan2(outgoing_dir[1], outgoing_dir[0]) * 180 / math.pi
        
        # Вычисляем разницу между углами
        diff = outgoing_angle - incoming_angle
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        
        # Рассчитываем угол поворота диагонали
        diagonal_angle = incoming_angle + diff / 2
        
        # Берем базовую диагональную текстуру
        texture = self.body_diagonal
        
        # Если это внешний угол (поворот направо), поворачиваем на 180 градусов
        if is_right_turn:
            texture = pygame.transform.rotate(texture, 180)
        
        # Поворачиваем диагональную текстуру на нужный угол
        rotated = pygame.transform.rotate(texture, -diagonal_angle)
        
        # Масштабируем обратно до нормального размера (диагональ немного больше)
        center = rotated.get_rect().center
        # Вырезаем квадрат из повернутой текстуры
        result = pygame.Surface((self.grid_size, self.grid_size), pygame.SRCALPHA)
        result.fill((0, 0, 0, 0))
        
        # Копируем центральную часть повернутой текстуры
        rotated_rect = rotated.get_rect()
        src_rect = pygame.Rect(
            rotated_rect.centerx - self.grid_size // 2,
            rotated_rect.centery - self.grid_size // 2,
            self.grid_size,
            self.grid_size
        )
        # Обрезаем, если выходит за границы
        src_rect.clamp_ip(rotated_rect)
        
        if src_rect.width > 0 and src_rect.height > 0:
            dest_x = max(0, self.grid_size // 2 - src_rect.centerx)
            dest_y = max(0, self.grid_size // 2 - src_rect.centery)
            result.blit(rotated, (dest_x, dest_y), src_rect)
        
        return result

    def draw(self, screen):
        for i, segment in enumerate(self.body):
            x, y = segment
            
            # ГОЛОВА
            if i == 0 and self.head_right:
                if self.direction == (1, 0):
                    texture = self.head_right
                elif self.direction == (-1, 0):
                    texture = self.head_left
                elif self.direction == (0, -1):
                    texture = self.head_up
                else:
                    texture = self.head_down
                screen.blit(texture, (x * self.grid_size, y * self.grid_size))
            
            # ХВОСТ
            elif i == len(self.body) - 1 and self.tail_right:
                # Определяем направление хвоста (от предпоследнего сегмента)
                if len(self.body) > 1:
                    prev_x, prev_y = self.body[i - 1]
                    tail_dir = (segment[0] - prev_x, segment[1] - prev_y)
                    
                    if tail_dir == (1, 0):
                        texture = self.tail_right
                    elif tail_dir == (-1, 0):
                        texture = self.tail_left
                    elif tail_dir == (0, -1):
                        texture = self.tail_up
                    else:
                        texture = self.tail_down
                else:
                    texture = self.tail_right
                screen.blit(texture, (x * self.grid_size, y * self.grid_size))
            
            # ТЕЛО
            elif self.body_horizontal:
                # Определяем направление тела
                if i > 0:
                    prev_x, prev_y = self.body[i - 1]
                    # Направление входящего потока
                    incoming_dir = (segment[0] - prev_x, segment[1] - prev_y)
                    
                    # Проверяем следующий сегмент для обнаружения поворота
                    if i < len(self.body) - 1:
                        next_x, next_y = self.body[i + 1]
                        # Направление исходящего потока
                        outgoing_dir = (next_x - segment[0], next_y - segment[1])
                        
                        # Если направления разные - это поворот
                        if incoming_dir != outgoing_dir:
                            texture = self.create_turn_texture(incoming_dir, outgoing_dir)
                        else:
                            # Прямой участок
                            if incoming_dir[0] != 0:
                                texture = self.body_horizontal
                            else:
                                texture = self.body_vertical
                    else:
                        # Последний сегмент перед хвостом
                        if incoming_dir[0] != 0:
                            texture = self.body_horizontal
                        else:
                            texture = self.body_vertical
                else:
                    texture = self.body_horizontal
                    
                screen.blit(texture, (x * self.grid_size, y * self.grid_size))
            else:
                # Fallback
                rect = pygame.Rect(x * self.grid_size, y * self.grid_size, self.grid_size, self.grid_size)
                pygame.draw.rect(screen, (0, 255, 0), rect)

class Food:
    def __init__(self, grid_size=20, width=48, height=27):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.width = width
        self.height = height
        self.points = 1
        self.position = self.spawn()
        
        # Загрузка текстуры еды
        try:
            food_img = pygame.image.load(os.path.join(ASSETS_PATH, 'food.png'))
            self.texture = pygame.transform.scale(food_img, (self.grid_size, self.grid_size))
            print("✅ Текстура еды загружена!")
        except Exception as e:
            print(f"❌ Ошибка загрузки еды: {e}")
            self.texture = None

    def spawn(self, snake=None):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            # Не спавниться на теле змейки
            if snake and (x, y) in snake.body:
                continue
            self.position = (x, y)
            self.points = random.randint(1, 5)
            return self.position

    def draw(self, screen):
        x, y = self.position
        if self.texture:
            screen.blit(self.texture, (x * self.grid_size, y * self.grid_size))
        else:
            # Fallback красный квадрат
            rect = pygame.Rect(x * self.grid_size, y * self.grid_size, self.grid_size, self.grid_size)
            pygame.draw.rect(screen, (255, 0, 0), rect)

class Bonus:
    """Бонус - яблоко (ускорение +3 очка)"""
    def __init__(self, grid_size=20, width=48, height=27):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.width = width
        self.height = height
        self.active = True
        self.lifetime = 1000
        self.timer = 0
        self.position = self.spawn()
        
        # Загрузка текстуры
        try:
            bonus_img = pygame.image.load(os.path.join(ASSETS_PATH, 'bonus_apple.png'))
            self.texture = pygame.transform.scale(bonus_img, (self.grid_size, self.grid_size))
            print("✅ Текстура бонуса загружена!")
        except Exception as e:
            print(f"❌ Ошибка загрузки бонуса: {e}")
            self.texture = None

    def spawn(self, snake=None):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            # Не спавниться на теле змейки
            if snake and (x, y) in snake.body:
                continue
            self.position = (x, y)
            self.timer = self.lifetime
            return self.position

    def update(self, snake=None):
        """Уменьшает таймер и переспавнивает при истечении"""
        if self.timer > 0:
            self.timer -= 1
        if self.timer == 0:
            self.spawn(snake)

    def draw(self, screen):
        x, y = self.position
        if self.texture:
            screen.blit(self.texture, (x * self.grid_size, y * self.grid_size))

class Debuff:
    """Дебафф - паук (замедление -3 очко)"""
    def __init__(self, grid_size=20, width=48, height=27):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.width = width
        self.height = height
        self.active = True
        self.lifetime = 800
        self.timer = 0
        self.position = self.spawn()
        
        # Загрузка текстуры
        try:
            debuff_img = pygame.image.load(os.path.join(ASSETS_PATH, 'debuff_spider.png'))
            self.texture = pygame.transform.scale(debuff_img, (self.grid_size, self.grid_size))
            print("✅ Текстура дебаффа загружена!")
        except Exception as e:
            print(f"❌ Ошибка загрузки дебаффа: {e}")
            self.texture = None

    def spawn(self, snake=None):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            # Не спавниться на теле змейки
            if snake and (x, y) in snake.body:
                continue
            self.position = (x, y)
            self.timer = self.lifetime
            return self.position

    def update(self, snake=None):
        """Уменьшает таймер и переспавнивает при истечении"""
        if self.timer > 0:
            self.timer -= 1
        if self.timer == 0:
            self.spawn(snake)

    def draw(self, screen):
        x, y = self.position
        if self.texture:
            screen.blit(self.texture, (x * self.grid_size, y * self.grid_size))

class Strawberry:
    """Клубника - дает +5 очков и укорачивает змею на 1 сегмент"""
    def __init__(self, grid_size=20, width=48, height=27):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.width = width
        self.height = height
        self.active = True
        self.lifetime = 800
        self.timer = 0
        self.position = self.spawn()
        
        # Загрузка текстуры
        try:
            strawberry_img = pygame.image.load(os.path.join(ASSETS_PATH, 'strawberry.png'))
            self.texture = pygame.transform.scale(strawberry_img, (self.grid_size, self.grid_size))
            print("✅ Текстура клубники загружена!")
        except Exception as e:
            print(f"❌ Ошибка загрузки клубники: {e}")
            self.texture = None

    def spawn(self, snake=None):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if snake and (x, y) in snake.body:
                continue
            self.position = (x, y)
            self.timer = self.lifetime
            return self.position

    def update(self, snake=None):
        if self.timer > 0:
            self.timer -= 1
        if self.timer == 0:
            self.spawn(snake)

    def draw(self, screen):
        x, y = self.position
        if self.texture:
            screen.blit(self.texture, (x * self.grid_size, y * self.grid_size))

class Diamond:
    """Алмаз - редкий бонус, дает +10 очков"""
    def __init__(self, grid_size=20, width=48, height=27):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.width = width
        self.height = height
        self.active = True
        self.lifetime = 600
        self.timer = 0
        self.position = self.spawn()
        
        # Загрузка текстуры
        try:
            diamond_img = pygame.image.load(os.path.join(ASSETS_PATH, 'diamond.png'))
            self.texture = pygame.transform.scale(diamond_img, (self.grid_size, self.grid_size))
            print("✅ Текстура алмаза загружена!")
        except Exception as e:
            print(f"❌ Ошибка загрузки алмаза: {e}")
            self.texture = None

    def spawn(self, snake=None):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if snake and (x, y) in snake.body:
                continue
            self.position = (x, y)
            self.timer = self.lifetime
            return self.position

    def update(self, snake=None):
        if self.timer > 0:
            self.timer -= 1
        if self.timer == 0:
            self.spawn(snake)

    def draw(self, screen):
        x, y = self.position
        if self.texture:
            screen.blit(self.texture, (x * self.grid_size, y * self.grid_size))

class Star:
    """Звезда - неуязвимость (можно проходить сквозь себя) на 5 секунд"""
    def __init__(self, grid_size=20, width=48, height=27):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.width = width
        self.height = height
        self.active = True
        self.lifetime = 1000
        self.timer = 0
        self.position = self.spawn()
        
        # Загрузка текстуры
        try:
            star_img = pygame.image.load(os.path.join(ASSETS_PATH, 'star.png'))
            self.texture = pygame.transform.scale(star_img, (self.grid_size, self.grid_size))
            print("✅ Текстура звезды загружена!")
        except Exception as e:
            print(f"❌ Ошибка загрузки звезды: {e}")
            self.texture = None

    def spawn(self, snake=None):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if snake and (x, y) in snake.body:
                continue
            self.position = (x, y)
            self.timer = self.lifetime
            return self.position

    def update(self, snake=None):
        if self.timer > 0:
            self.timer -= 1
        if self.timer == 0:
            self.spawn(snake)

    def draw(self, screen):
        x, y = self.position
        if self.texture:
            screen.blit(self.texture, (x * self.grid_size, y * self.grid_size))

class Mushroom:
    """Гриб - реверс управления на 3 секунды"""
    def __init__(self, grid_size=20, width=48, height=27):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.width = width
        self.height = height
        self.active = True
        self.lifetime = 700
        self.timer = 0
        self.position = self.spawn()
        
        # Загрузка текстуры
        try:
            mushroom_img = pygame.image.load(os.path.join(ASSETS_PATH, 'mushroom.png'))
            self.texture = pygame.transform.scale(mushroom_img, (self.grid_size, self.grid_size))
            print("✅ Текстура гриба загружена!")
        except Exception as e:
            print(f"❌ Ошибка загрузки гриба: {e}")
            self.texture = None

    def spawn(self, snake=None):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if snake and (x, y) in snake.body:
                continue
            self.position = (x, y)
            self.timer = self.lifetime
            return self.position

    def update(self, snake=None):
        if self.timer > 0:
            self.timer -= 1
        if self.timer == 0:
            self.spawn(snake)

    def draw(self, screen):
        x, y = self.position
        if self.texture:
            screen.blit(self.texture, (x * self.grid_size, y * self.grid_size))

class Ice:
    """Лёд - замораживает змею на 0.5 секунды"""
    def __init__(self, grid_size=20, width=48, height=27):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.width = width
        self.height = height
        self.active = True
        self.lifetime = 600
        self.timer = 0
        self.position = self.spawn()
        
        # Загрузка текстуры
        try:
            ice_img = pygame.image.load(os.path.join(ASSETS_PATH, 'ice.png'))
            self.texture = pygame.transform.scale(ice_img, (self.grid_size, self.grid_size))
            print("✅ Текстура льда загружена!")
        except Exception as e:
            print(f"❌ Ошибка загрузки льда: {e}")
            self.texture = None

    def spawn(self, snake=None):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if snake and (x, y) in snake.body:
                continue
            self.position = (x, y)
            self.timer = self.lifetime
            return self.position

    def update(self, snake=None):
        if self.timer > 0:
            self.timer -= 1
        if self.timer == 0:
            self.spawn(snake)

    def draw(self, screen):
        x, y = self.position
        if self.texture:
            screen.blit(self.texture, (x * self.grid_size, y * self.grid_size))

class Obstacle:
    """Препятствие (камень 2х2) - при столкновении Game Over"""
    def __init__(self, grid_size=20, width=48, height=27, count=5):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.width = width
        self.height = height
        self.count = count
        self.positions = []  # Позиции левого верхнего угла камня 2х2
        
        # Загрузка текстуры (камень будет 2х2 клетки)
        try:
            obstacle_img = pygame.image.load(os.path.join(ASSETS_PATH, 'obstacle.png'))
            self.texture = pygame.transform.scale(obstacle_img, (self.grid_size * 2, self.grid_size * 2))
            print("✅ Текстура камня загружена!")
        except Exception as e:
            print(f"❌ Ошибка загрузки камня: {e}")
            self.texture = None

    def generate_obstacles(self, snake=None):
        """Генерирует случайные препятствия 2х2"""
        self.positions = []
        # Получаем y-координату горизонтальной линии змеи (все сегменты на одной y при старте)
        snake_y = snake.body[0][1] if snake else None
        
        for _ in range(self.count):
            attempts = 0
            while attempts < 100:  # Защита от бесконечного цикла
                x = random.randint(2, self.width - 4)  # -4 чтобы камень 2х2 влез
                y = random.randint(2, self.height - 4)
                
                # Проверяем все 4 клетки камня 2х2
                occupied_cells = [
                    (x, y), (x+1, y),
                    (x, y+1), (x+1, y+1)
                ]
                
                # Исключаем горизонтальную линию, где спавнится змея (включая соседние строки для безопасности)
                if snake_y is not None:
                    # Исключаем 3 строки: саму строку змеи и по одной сверху и снизу
                    excluded_y_values = {snake_y - 1, snake_y, snake_y + 1, snake_y + 2}
                    if any(y == excluded_y for excluded_y in excluded_y_values):
                        attempts += 1
                        continue
                
                # Проверяем что нет пересечений с другими камнями
                overlap = False
                for other_pos in self.positions:
                    other_cells = [
                        (other_pos[0], other_pos[1]), (other_pos[0]+1, other_pos[1]),
                        (other_pos[0], other_pos[1]+1), (other_pos[0]+1, other_pos[1]+1)
                    ]
                    if any(cell in other_cells for cell in occupied_cells):
                        overlap = True
                        break
                
                # Проверяем что не на змее
                if not overlap:
                    if not snake or not any(cell in snake.body for cell in occupied_cells):
                        self.positions.append((x, y))
                        break
                attempts += 1
    
    def check_collision(self, pos):
        """Проверяет столкновение с любой клеткой камня 2х2"""
        for obstacle_pos in self.positions:
            occupied_cells = [
                (obstacle_pos[0], obstacle_pos[1]), (obstacle_pos[0]+1, obstacle_pos[1]),
                (obstacle_pos[0], obstacle_pos[1]+1), (obstacle_pos[0]+1, obstacle_pos[1]+1)
            ]
            if pos in occupied_cells:
                return True
        return False

    def draw(self, screen):
        if self.texture:
            for pos in self.positions:
                x, y = pos
                screen.blit(self.texture, (x * self.grid_size, y * self.grid_size))

class Game:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.base_grid_size = 20
        self.grid_size = 40
        self.background = Background(width, height, self.grid_size)
        self.snake = Snake(self.base_grid_size)
        self.food = Food(self.base_grid_size, width // self.grid_size, height // self.grid_size)
        self.bonus = Bonus(self.base_grid_size, width // self.grid_size, height // self.grid_size)
        self.debuff = Debuff(self.base_grid_size, width // self.grid_size, height // self.grid_size)
        
        # Новые бонусы
        self.strawberry = Strawberry(self.base_grid_size, width // self.grid_size, height // self.grid_size)
        self.diamond = Diamond(self.base_grid_size, width // self.grid_size, height // self.grid_size)
        self.star = Star(self.base_grid_size, width // self.grid_size, height // self.grid_size)
        self.mushroom = Mushroom(self.base_grid_size, width // self.grid_size, height // self.grid_size)
        self.ice = Ice(self.base_grid_size, width // self.grid_size, height // self.grid_size)
        
        # Препятствия
        self.obstacles = Obstacle(self.base_grid_size, width // self.grid_size, height // self.grid_size, count=5)
        self.obstacles.generate_obstacles(self.snake)  # Генерируем с учетом змеи
        
        self.score = 0
        self.game_over = False
        self.controller = None
        self.speed_boost = False
        self.slowdown_timer = 0
        
        # Новые механики
        self.invincible_timer = 0  # Неуязвимость от звезды
        self.reverse_control_timer = 0  # Реверс управления от гриба
        self.freeze_timer = 0  # Заморозка от льда
        self.combo_counter = 0  # Счетчик комбо
        self.last_pickup_was_bonus = False  # Для отслеживания комбо
        self.level = 1  # Текущий уровень
        self._score_saved = False  # Флаг для сохранения рекорда
        self.wall_surfaces = None
        self.wall_hud_gap_width = 360
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def set_controller(self, controller):
        self.controller = controller

    def update(self):
        if self.game_over:
            return
        
        # Обновляем таймеры бонусов
        self.bonus.update(self.snake)
        self.debuff.update(self.snake)
        self.strawberry.update(self.snake)
        self.diamond.update(self.snake)
        self.star.update(self.snake)
        self.mushroom.update(self.snake)
        self.ice.update(self.snake)
        
        # Обновляем таймеры эффектов
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.reverse_control_timer > 0:
            self.reverse_control_timer -= 1
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
        
        # Обёртывание через края (до 5 уровня) или стены по периметру (после 5 уровня)
        head_x, head_y = self.snake.body[0]
        grid_width = self.width // self.grid_size
        grid_height = self.height // self.grid_size
        
        if self.level > 5:
            if head_x < 0 or head_x >= grid_width or head_y < 0 or head_y >= grid_height:
                self.game_over = True
                if self.controller:
                    self.controller.rumble(1.0, 1.0, 500)
                return
        else:
            head_x = head_x % grid_width
            head_y = head_y % grid_height
            self.snake.body[0] = (head_x, head_y)

        # Проверка столкновения с собой (если нет неуязвимости)
        if self.invincible_timer == 0:
            if self.snake.body[0] in self.snake.body[1:]:
                self.game_over = True
                return
        
        # Проверка столкновения с препятствиями 2х2 (если нет неуязвимости)
        if self.invincible_timer == 0:
            if self.obstacles.check_collision(self.snake.body[0]):
                self.game_over = True
                if self.controller:
                    self.controller.rumble(1.0, 1.0, 500)
                return

        # Проверка столкновения с обычной едой
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            points_earned = self.food.points
            self.score += points_earned
            self.food.spawn(self.snake)
            self.last_pickup_was_bonus = False
            self.combo_counter = 0
            if self.controller:
                self.controller.rumble(0.7, 0.7, 200)
            self.check_level_up()

        # Проверка столкновения с бонусом (яблоко)
        if self.bonus.active and self.snake.body[0] == self.bonus.position:
            self.snake.grow()
            points = 3 * (1 + self.combo_counter) if self.last_pickup_was_bonus else 3
            self.score += points
            self.slowdown_timer = -150
            self.bonus.spawn(self.snake)
            if self.last_pickup_was_bonus:
                self.combo_counter += 1
            else:
                self.combo_counter = 1
            self.last_pickup_was_bonus = True
            if self.controller:
                self.controller.rumble(1.0, 0.5, 300)
            self.check_level_up()

        # Проверка столкновения с дебаффом (паук)
        if self.debuff.active and self.snake.body[0] == self.debuff.position:
            self.snake.grow()
            self.score = max(0, self.score - 1)
            self.slowdown_timer = 150
            self.debuff.spawn(self.snake)
            self.last_pickup_was_bonus = False
            self.combo_counter = 0
            if self.controller:
                self.controller.rumble(0.3, 0.8, 200)
        
        # Проверка столкновения с клубникой
        if self.strawberry.active and self.snake.body[0] == self.strawberry.position:
            points = 5 * (1 + self.combo_counter) if self.last_pickup_was_bonus else 5
            self.score += points
            # Укорачиваем змею на 1 сегмент (если больше 3 сегментов)
            if len(self.snake.body) > 3:
                self.snake.body.pop()
            self.strawberry.spawn(self.snake)
            if self.last_pickup_was_bonus:
                self.combo_counter += 1
            else:
                self.combo_counter = 1
            self.last_pickup_was_bonus = True
            if self.controller:
                self.controller.rumble(0.8, 0.6, 250)
            self.check_level_up()
        
        # Проверка столкновения с алмазом
        if self.diamond.active and self.snake.body[0] == self.diamond.position:
            self.snake.grow()
            points = 10 * (1 + self.combo_counter) if self.last_pickup_was_bonus else 10
            self.score += points
            self.diamond.spawn(self.snake)
            if self.last_pickup_was_bonus:
                self.combo_counter += 1
            else:
                self.combo_counter = 1
            self.last_pickup_was_bonus = True
            if self.controller:
                self.controller.rumble(1.0, 1.0, 400)
            self.check_level_up()
        
        # Проверка столкновения со звездой
        if self.star.active and self.snake.body[0] == self.star.position:
            self.snake.grow()
            self.score += 2
            self.invincible_timer = 300  # 5 секунд при 60 FPS
            self.star.spawn(self.snake)
            if self.last_pickup_was_bonus:
                self.combo_counter += 1
            else:
                self.combo_counter = 1
            self.last_pickup_was_bonus = True
            if self.controller:
                self.controller.rumble(0.5, 0.5, 200)
            self.check_level_up()
        
        # Проверка столкновения с грибом
        if self.mushroom.active and self.snake.body[0] == self.mushroom.position:
            self.snake.grow()
            self.score += 1
            self.reverse_control_timer = 180  # 3 секунды при 60 FPS
            self.mushroom.spawn(self.snake)
            self.last_pickup_was_bonus = False
            self.combo_counter = 0
            if self.controller:
                self.controller.rumble(0.6, 0.4, 250)
            self.check_level_up()
        
        # Проверка столкновения со льдом
        if self.ice.active and self.snake.body[0] == self.ice.position:
            self.snake.grow()
            self.score += 1
            self.freeze_timer = 600  # 10 секунд при 60 FPS
            self.ice.spawn(self.snake)
            self.last_pickup_was_bonus = False
            self.combo_counter = 0
            if self.controller:
                self.controller.rumble(0.4, 0.8, 150)
            self.check_level_up()
    
    def check_level_up(self):
        """Проверка повышения уровня каждые 250 очков"""
        new_level = (self.score // 250) + 1
        if new_level > self.level:
            self.level = new_level
            # Добавляем новые препятствия каждый уровень
            self.obstacles.count = min(5 + self.level, 15)
            self.obstacles.generate_obstacles(self.snake)
            if self.controller:
                self.controller.rumble(1.0, 1.0, 600)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # Направления (с учетом реверса управления)
            directions = {
                pygame.K_UP: (0, -1),
                pygame.K_DOWN: (0, 1),
                pygame.K_LEFT: (-1, 0),
                pygame.K_RIGHT: (1, 0)
            }
            
            if event.key in directions:
                direction = directions[event.key]
                # Если активен реверс управления, инвертируем направление
                if self.reverse_control_timer > 0:
                    direction = (-direction[0], -direction[1])
                self.snake.set_direction(direction)
            elif event.key == pygame.K_r:
                self.reset()
        
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 4:
                self.reset()
        
        if event.type == pygame.JOYAXISMOTION and event.axis == 4:
            self.speed_boost = event.value > 0.5

    def draw(self, screen):
        self.background.draw(screen)
        
        # Рисуем стены по периметру после 5 уровня
        if self.level > 5:
            if self.wall_surfaces is None:
                self.wall_surfaces = self._build_wall_surfaces()
            wall_h, wall_v = self.wall_surfaces
            wall_thickness = self.grid_size
            # Верхняя стена с зазором под UI
            if self.wall_hud_gap_width < self.width:
                screen.blit(wall_h, (self.wall_hud_gap_width, 0), area=pygame.Rect(self.wall_hud_gap_width, 0, self.width - self.wall_hud_gap_width, wall_thickness))
            # Нижняя стена
            screen.blit(wall_h, (0, self.height - wall_thickness))
            # Левая и правая стены
            screen.blit(wall_v, (0, 0))
            screen.blit(wall_v, (self.width - wall_thickness, 0))
        
        # Рисуем препятствия
        self.obstacles.draw(screen)
        
        # Рисуем змею (с эффектом неуязвимости)
        if self.invincible_timer > 0 and self.invincible_timer % 10 < 5:
            # Мерцание при неуязвимости
            pass
        else:
            self.snake.draw(screen)
        
        # Рисуем все бонусы
        self.food.draw(screen)
        self.bonus.draw(screen)
        self.debuff.draw(screen)
        self.strawberry.draw(screen)
        self.diamond.draw(screen)
        self.star.draw(screen)
        self.mushroom.draw(screen)
        self.ice.draw(screen)
        
        # Отображение счёта и уровня
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        level_text = self.small_font.render(f'Level: {self.level}', True, (200, 200, 200))
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 45))
        
        # Отображение комбо
        if self.combo_counter > 0:
            combo_text = self.font.render(f'COMBO x{self.combo_counter + 1}!', True, (255, 200, 0))
            screen.blit(combo_text, (10, 75))
        
        # Отображение статусов
        y_offset = 115
        
        if self.slowdown_timer < 0:  # УСКОРЕНИЕ
            boost_text = self.small_font.render('⚡ BOOST! (Apple)', True, (255, 255, 0))
            screen.blit(boost_text, (10, y_offset))
            y_offset += 30
        
        if self.slowdown_timer > 0:  # ЗАМЕДЛЕНИЕ
            slow_text = self.small_font.render('🕷️ SLOWDOWN! (Spider)', True, (255, 100, 100))
            screen.blit(slow_text, (10, y_offset))
            y_offset += 30
        
        if self.invincible_timer > 0:
            inv_text = self.small_font.render(f'⭐ INVINCIBLE! ({self.invincible_timer // 60}s)', True, (255, 255, 100))
            screen.blit(inv_text, (10, y_offset))
            y_offset += 30
        
        if self.reverse_control_timer > 0:
            rev_text = self.small_font.render(f'🍄 REVERSED! ({self.reverse_control_timer // 60}s)', True, (200, 100, 200))
            screen.blit(rev_text, (10, y_offset))
            y_offset += 30
        
        if self.freeze_timer > 0:
            freeze_text = self.small_font.render('🧊 FROZEN!', True, (150, 200, 255))
            screen.blit(freeze_text, (10, y_offset))
            y_offset += 30
        # Отображение Game Over
        if self.game_over:
            # Полупрозрачный чёрный фон
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render('GAME OVER!', True, (255, 0, 0))
            score_display = self.font.render(f'Final Score: {self.score}', True, (255, 255, 255))
            level_display = self.font.render(f'Level Reached: {self.level}', True, (255, 255, 255))
            restart_text = self.small_font.render('Press R to Restart', True, (200, 200, 200))
            
            screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, self.height // 2 - 80))
            screen.blit(score_display, (self.width // 2 - score_display.get_width() // 2, self.height // 2 - 20))
            screen.blit(level_display, (self.width // 2 - level_display.get_width() // 2, self.height // 2 + 20))
            screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2 + 60))

    def _build_wall_surfaces(self):
        wall_thickness = self.grid_size
        base_color = (105, 105, 120)
        alt_color = (130, 130, 150)
        crack_color = (70, 70, 85)
        stone_color = (90, 90, 105)
        tile = max(8, self.grid_size // 2)

        wall_h = pygame.Surface((self.width, wall_thickness))
        wall_v = pygame.Surface((wall_thickness, self.height))

        wall_h.fill(base_color)
        wall_v.fill(base_color)

        # Шахматный паттерн
        for y in range(0, wall_thickness, tile):
            for x in range(0, self.width, tile):
                if ((x // tile) + (y // tile)) % 2 == 0:
                    pygame.draw.rect(wall_h, alt_color, (x, y, tile, tile))
        for y in range(0, self.height, tile):
            for x in range(0, wall_thickness, tile):
                if ((x // tile) + (y // tile)) % 2 == 0:
                    pygame.draw.rect(wall_v, alt_color, (x, y, tile, tile))

        rng = random.Random(17)
        # Камни
        for _ in range(40):
            x = rng.randint(0, self.width - 1)
            y = rng.randint(0, wall_thickness - 1)
            r = rng.randint(2, 4)
            pygame.draw.circle(wall_h, stone_color, (x, y), r)
        for _ in range(40):
            x = rng.randint(0, wall_thickness - 1)
            y = rng.randint(0, self.height - 1)
            r = rng.randint(2, 4)
            pygame.draw.circle(wall_v, stone_color, (x, y), r)

        # Трещины
        for _ in range(12):
            x1 = rng.randint(0, self.width - 1)
            x2 = min(self.width - 1, x1 + rng.randint(30, 120))
            y = rng.randint(2, wall_thickness - 3)
            pygame.draw.line(wall_h, crack_color, (x1, y), (x2, y), 1)
        for _ in range(12):
            y1 = rng.randint(0, self.height - 1)
            y2 = min(self.height - 1, y1 + rng.randint(30, 120))
            x = rng.randint(2, wall_thickness - 3)
            pygame.draw.line(wall_v, crack_color, (x, y1), (x, y2), 1)

        return wall_h, wall_v

    def reset(self):
        self.snake = Snake(self.base_grid_size)
        self.food = Food(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.bonus = Bonus(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.debuff = Debuff(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.strawberry = Strawberry(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.diamond = Diamond(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.star = Star(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.mushroom = Mushroom(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.ice = Ice(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.obstacles = Obstacle(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size, count=5)
        self.obstacles.generate_obstacles(self.snake)  # Генерируем с учетом змеи
        self.background = Background(self.width, self.height, self.grid_size)
        self.score = 0
        self.game_over = False
        self.slowdown_timer = 0
        self.invincible_timer = 0
        self.reverse_control_timer = 0
        self.freeze_timer = 0
        self.combo_counter = 0
        self.last_pickup_was_bonus = False
        self.level = 1
        self._score_saved = False

class Background:
    """Генерирует фон в виде вспаханного поля"""
    def __init__(self, width=1920, height=1080, grid_size=40):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.surface = pygame.Surface((width, height))
        self.generate_field()

    def generate_field(self):
        """Генерирует текстуру вспаханного поля"""
        # Цвета земли
        dark_brown = (101, 67, 33)
        light_brown = (139, 90, 43)
        
        # Заполняем фон
        self.surface.fill(dark_brown)
        
        # Рисуем борозды (полосы вспахивания)
        for y in range(0, self.height, self.grid_size * 2):
            pygame.draw.line(self.surface, light_brown, (0, y), (self.width, y), 3)
        
        # Добавляем точки грязи для эффекта
        for _ in range(200):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            color = (random.randint(80, 120), random.randint(50, 80), random.randint(20, 40))
            pygame.draw.circle(self.surface, color, (x, y), size)
        
        # Добавляем травку на краях
        for x in range(0, self.width, 20):
            grass_color = (34, 139, 34)
            pygame.draw.polygon(self.surface, grass_color, [
                (x, self.height - 10),
                (x + 15, self.height - 20),
                (x + 10, self.height - 5)
            ])

    def draw(self, screen):
        """Отрисовывает фон"""
        screen.blit(self.surface, (0, 0))