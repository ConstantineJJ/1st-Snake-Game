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
                    body_dir = (segment[0] - prev_x, segment[1] - prev_y)
                    
                    # Горизонтальное или вертикальное
                    if body_dir[0] != 0:  # Движется по X (горизонтально)
                        texture = self.body_horizontal
                    else:  # Движется по Y (вертикально)
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
        self.lifetime = 300
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
    """Дебафф - паук (замедление -1 очко)"""
    def __init__(self, grid_size=20, width=48, height=27):
        self.base_grid_size = grid_size
        self.grid_size = grid_size * 2
        self.width = width
        self.height = height
        self.active = True
        self.lifetime = 300
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
        self.score = 0
        self.game_over = False
        self.controller = None
        self.speed_boost = False
        self.slowdown_timer = 0
        self.font = pygame.font.Font(None, 36)

    def set_controller(self, controller):
        self.controller = controller

    def update(self):
        if self.game_over:
            return
        
        # Обновляем таймеры бонусов
        self.bonus.update(self.snake)
        self.debuff.update(self.snake)
        
        # Обёртывание через края
        head_x, head_y = self.snake.body[0]
        grid_width = self.width // self.grid_size
        grid_height = self.height // self.grid_size
        
        head_x = head_x % grid_width
        head_y = head_y % grid_height
        self.snake.body[0] = (head_x, head_y)

        # Проверка столкновения с собой
        if self.snake.body[0] in self.snake.body[1:]:
            self.game_over = True
            return

        # Проверка столкновения с обычной едой
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            points_earned = self.food.points
            self.score += points_earned
            self.food.spawn(self.snake)
            if self.controller:
                self.controller.rumble(0.7, 0.7, 200)

        # Проверка столкновения с бонусом (яблоко)
        if self.bonus.active and self.snake.body[0] == self.bonus.position:
            self.snake.grow()
            self.score += 3
            self.slowdown_timer = -150
            self.bonus.spawn(self.snake)
            if self.controller:
                self.controller.rumble(1.0, 0.5, 300)

        # Проверка столкновения с дебаффом (паук)
        if self.debuff.active and self.snake.body[0] == self.debuff.position:
            self.snake.grow()
            self.score = max(0, self.score - 1)
            self.slowdown_timer = 150
            self.debuff.spawn(self.snake)
            if self.controller:
                self.controller.rumble(0.3, 0.8, 200)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.snake.set_direction((0, -1))
            elif event.key == pygame.K_DOWN:
                self.snake.set_direction((0, 1))
            elif event.key == pygame.K_LEFT:
                self.snake.set_direction((-1, 0))
            elif event.key == pygame.K_RIGHT:
                self.snake.set_direction((1, 0))
            elif event.key == pygame.K_r:
                self.reset()
        
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                self.reset()
        
        if event.type == pygame.JOYAXISMOTION and event.axis == 4:
            self.speed_boost = event.value > 0.5

    def draw(self, screen):
        self.background.draw(screen)
        self.snake.draw(screen)
        self.food.draw(screen)
        self.bonus.draw(screen)
        self.debuff.draw(screen)
        
        # Отображение счёта
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # Отображение статуса ускорения/замедления
        if self.slowdown_timer < 0:  # ОТРИЦАТЕЛЬНОЕ = УСКОРЕНИЕ
            boost_text = self.font.render('⚡ BOOST! (Apple)', True, (255, 255, 0))
            screen.blit(boost_text, (10, 50))
        
        if self.slowdown_timer > 0:  # ПОЛОЖИТЕЛЬНОЕ = ЗАМЕДЛЕНИЕ
            slow_text = self.font.render('🕷️ SLOWDOWN! (Spider)', True, (255, 100, 100))
            screen.blit(slow_text, (10, 90))
        
        # Отображение Game Over
        if self.game_over:
            game_over_text = self.font.render('GAME OVER!', True, (255, 0, 0))
            restart_text = self.font.render('Press R to Restart', True, (255, 255, 255))
            screen.blit(game_over_text, (self.width // 2 - 100, self.height // 2 - 50))
            screen.blit(restart_text, (self.width // 2 - 130, self.height // 2))

    def reset(self):
        self.snake = Snake(self.base_grid_size)
        self.food = Food(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.bonus = Bonus(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.debuff = Debuff(self.base_grid_size, self.width // self.grid_size, self.height // self.grid_size)
        self.background = Background(self.width, self.height, self.grid_size)
        self.score = 0
        self.game_over = False
        self.slowdown_timer = 0

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