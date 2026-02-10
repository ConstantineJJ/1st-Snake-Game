import pygame 
import sys
import json
import os
from game_types.index import Snake, Food, Game

def load_highscores():
    """Загружает таблицу рекордов из файла"""
    highscore_file = os.path.join(os.path.dirname(__file__), 'highscores.json')
    try:
        if os.path.exists(highscore_file):
            with open(highscore_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📖 Загружено {len(data)} рекордов из файла")
                return data
        else:
            print(f"⚠️ Файл рекордов не найден: {highscore_file}")
            return []
    except Exception as e:
        print(f"❌ Ошибка загрузки рекордов: {e}")
        return []

def save_highscores(highscores):
    """Сохраняет таблицу рекордов в файл"""
    highscore_file = os.path.join(os.path.dirname(__file__), 'highscores.json')
    try:
        with open(highscore_file, 'w', encoding='utf-8') as f:
            json.dump(highscores, f, indent=2, ensure_ascii=False)
        print(f"✅ Таблица рекордов сохранена в {highscore_file}")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

def add_highscore(score, level, name="Player"):
    """Добавляет новый рекорд в таблицу"""
    highscores = load_highscores()
    from datetime import datetime
    highscores.append({
        'name': name,
        'score': score,
        'level': level,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    # Сортируем по убыванию очков и оставляем топ-10
    highscores = sorted(highscores, key=lambda x: x['score'], reverse=True)[:10]
    save_highscores(highscores)
    print(f"💾 Рекорд сохранен: {name} - {score} очков (уровень {level})")
    return highscores

def input_player_name(screen, score, level, controller=None):
    """Экран ввода имени игрока для сохранения рекорда"""
    print(f"\n🎮 Открываю экран ввода имени для рекорда {score}...")
    font = pygame.font.Font(None, 64)
    medium_font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)
    
    player_name = ""
    max_name_length = 15
    clock = pygame.time.Clock()
    
    while True:
        screen.fill((20, 20, 40))
        
        # Заголовок
        title = font.render("🎮 НОВЫЙ РЕКОРД! 🎮", True, (255, 215, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 80))
        
        # Информация о рекорде
        score_text = medium_font.render(f"Счет: {score}", True, (255, 255, 255))
        level_text = medium_font.render(f"Уровень: {level}", True, (255, 255, 255))
        screen.blit(score_text, (screen.get_width() // 2 - score_text.get_width() // 2, 200))
        screen.blit(level_text, (screen.get_width() // 2 - level_text.get_width() // 2, 280))
        
        # Ввод имени
        input_label = medium_font.render("Введите ваше имя:", True, (200, 200, 200))
        screen.blit(input_label, (screen.get_width() // 2 - input_label.get_width() // 2, 400))
        
        # Поле ввода
        input_box_width = 500
        input_box_height = 60
        input_box_x = screen.get_width() // 2 - input_box_width // 2
        input_box_y = 500
        pygame.draw.rect(screen, (100, 100, 100), (input_box_x, input_box_y, input_box_width, input_box_height), 2)
        
        # Текст в поле
        name_display = player_name + ("_" if len(player_name) < max_name_length else "")
        name_text = medium_font.render(name_display, True, (255, 255, 255))
        screen.blit(name_text, (input_box_x + 20, input_box_y + 10))
        
        # Подсказка
        hint = small_font.render("Enter для сохранения | Backspace для удаления | ESC для отмены", True, (150, 150, 150))
        screen.blit(hint, (screen.get_width() // 2 - hint.get_width() // 2, screen.get_height() - 100))
        
        pygame.display.flip()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # Сохраняем рекорд
                    if len(player_name) == 0:
                        player_name = "Player"
                    print(f"✅ Сохраняю имя: {player_name}")
                    add_highscore(score, level, player_name)
                    return
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return
                elif len(player_name) < max_name_length:
                    if event.unicode.isalnum() or event.unicode in " -_":
                        player_name += event.unicode
            
            # Геймпад кнопка A для ввода
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # Cross/A - подтвердить
                    if len(player_name) == 0:
                        player_name = "Player"
                    add_highscore(score, level, player_name)
                    return
                elif event.button == 1:  # Circle/B - отмена
                    return

def show_highscores(screen, controller=None):
    """Показывает таблицу рекордов"""
    font = pygame.font.Font(None, 64)
    medium_font = pygame.font.Font(None, 42)
    small_font = pygame.font.Font(None, 32)
    highscores = load_highscores()
    
    running = True
    while running:
        screen.fill((20, 20, 40))
        
        # Заголовок
        title = font.render("🏆 ТАБЛИЦА РЕКОРДОВ 🏆", True, (255, 215, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 80))
        
        # Таблица рекордов
        if highscores:
            y_pos = 200
            for i, record in enumerate(highscores):
                rank_color = (255, 215, 0) if i == 0 else (192, 192, 192) if i == 1 else (205, 127, 50) if i == 2 else (255, 255, 255)
                rank_text = medium_font.render(f"{i+1}.", True, rank_color)
                name_text = medium_font.render(record.get('name', 'Player'), True, rank_color)
                score_text = medium_font.render(f"{record['score']} очков", True, rank_color)
                level_text = small_font.render(f"Ур.{record['level']}", True, (150, 150, 150))
                date_text = small_font.render(f"{record['date']}", True, (120, 120, 120))
                
                screen.blit(rank_text, (300, y_pos))
                screen.blit(name_text, (380, y_pos))
                screen.blit(score_text, (600, y_pos))
                screen.blit(level_text, (850, y_pos))
                screen.blit(date_text, (1000, y_pos))
                y_pos += 65
        else:
            no_records = medium_font.render("Рекордов пока нет", True, (150, 150, 150))
            screen.blit(no_records, (screen.get_width() // 2 - no_records.get_width() // 2, 300))
        
        # Подсказка
        hint = small_font.render("Нажмите ESC или Start для выхода", True, (200, 200, 200))
        screen.blit(hint, (screen.get_width() // 2 - hint.get_width() // 2, screen.get_height() - 100))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 9:  # Start на DualSense
                    return
                if event.button == 1:  # Circle/B - выход
                    return

def show_menu(screen, controller=None):
    """Меню с выбором Resume/Highscores/Exit. Возвращает действие."""
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 48)
    options = ["Resume", "Highscores", "Exit"]
    selected = 0
    running = True
    clock = pygame.time.Clock()
    
    while running:
        screen.fill((0, 0, 0))
        title = font.render("Меню", True, (255, 255, 255))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, screen.get_height() // 2 - 180))
        
        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else (255, 255, 255)
            text = small_font.render(opt, True, color)
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2 - 60 + i * 60))
        
        pygame.display.flip()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Клавиатура
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if options[selected] == "Resume":
                        return "resume"
                    elif options[selected] == "Highscores":
                        show_highscores(screen, controller)
                    elif options[selected] == "Exit":
                        return "exit"
                elif event.key == pygame.K_ESCAPE:
                    return "resume"
            
            # Геймпад D-Pad
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 11:  # D-Pad Up
                    selected = (selected - 1) % len(options)
                elif event.button == 12:  # D-Pad Down
                    selected = (selected + 1) % len(options)
                elif event.button == 0:  # Cross/A - подтвердить
                    if options[selected] == "Resume":
                        return "resume"
                    elif options[selected] == "Highscores":
                        show_highscores(screen, controller)
                    elif options[selected] == "Exit":
                        return "exit"
                elif event.button == 9:  # Start - выход из меню
                    return "resume"
                elif event.button == 1:  # Circle/B - выход из меню
                    return "resume"
            
            # Геймпад Left Stick
            if event.type == pygame.JOYAXISMOTION and controller:
                if event.axis == 1:  # Left stick Y
                    if event.value < -0.5:
                        selected = (selected - 1) % len(options)
                        pygame.time.delay(200)  # Задержка чтобы не листать слишком быстро
                    elif event.value > 0.5:
                        selected = (selected + 1) % len(options)
                        pygame.time.delay(200)

def main():
    pygame.init()
    
    # Инициализация джойстика
    pygame.joystick.init()
    joysticks = pygame.joystick.get_count()
    controller = None
    if joysticks > 0:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        print(f"Контроллер подключен: {controller.get_name()}")
    
    # Full HD окно
    screen_width = 1920
    screen_height = 1080
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Snake Game')

    # Initialize game objects
    game = Game(screen_width, screen_height)
    game.set_controller(controller)
    
    clock = pygame.time.Clock()
    game_running = True
    move_counter = 0  # Счётчик для регулировки скорости движения
    move_interval = 10  # Как часто вызывать move() (в кадрах)
    
    while game_running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Обработка клавиатуры и контроллера
            handle_input = getattr(game, "handle_input", None)
            if handle_input:
                handle_input(event)
            # Обработка нажатия клавиши ESC для открытия меню
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    action = show_menu(screen, controller)
                    if action == "exit":
                        pygame.quit()
                        sys.exit()
            
            # Обработка кнопки Start на DualSense для открытия меню
            if event.type == pygame.JOYBUTTONDOWN and controller:
                print(f"🎮 Нажата кнопка: {event.button}")  # Отладка
                if event.button == 6:  # Кнопка Start (три палочки)
                    print("📋 Открываю меню...")
                    action = show_menu(screen, controller)
                    if action == "exit":
                        pygame.quit()
                        sys.exit()
                # D-Pad и навигация
                elif event.button == 11:  # D-Pad Up
                    direction = (0, -1)
                    if game.reverse_control_timer > 0:
                        direction = (-direction[0], -direction[1])
                    game.snake.set_direction(direction)
                elif event.button == 12:  # D-Pad Down
                    direction = (0, 1)
                    if game.reverse_control_timer > 0:
                        direction = (-direction[0], -direction[1])
                    game.snake.set_direction(direction)
                elif event.button == 13:  # D-Pad Left
                    direction = (-1, 0)
                    if game.reverse_control_timer > 0:
                        direction = (-direction[0], -direction[1])
                    game.snake.set_direction(direction)
                elif event.button == 14:  # D-Pad Right
                    direction = (1, 0)
                    if game.reverse_control_timer > 0:
                        direction = (-direction[0], -direction[1])
                    game.snake.set_direction(direction)
            
            # Обработка левого стика для смены направления
            if event.type == pygame.JOYAXISMOTION and controller:
                if event.axis == 0:  # Left stick X
                    direction = None
                    if event.value > 0.5:
                        direction = (1, 0)  # Right
                    elif event.value < -0.5:
                        direction = (-1, 0)  # Left
                    # Применяем реверс управления от гриба
                    if direction and game.reverse_control_timer > 0:
                        direction = (-direction[0], -direction[1])
                    if direction:
                        game.snake.set_direction(direction)
                elif event.axis == 1:  # Left stick Y
                    direction = None
                    if event.value > 0.5:
                        direction = (0, 1)  # Down
                    elif event.value < -0.5:
                        direction = (0, -1)  # Up
                    # Применяем реверс управления от гриба
                    if direction and game.reverse_control_timer > 0:
                        direction = (-direction[0], -direction[1])
                    if direction:
                        game.snake.set_direction(direction)
        
        # Обработка триггера R2 для управления движением (ВМУНЕ цикла событий!)
        base_move_interval = 10
        if controller:
            r2_value = controller.get_axis(5)  # R2 триггер (обычно 5)
            if r2_value > 0.1:  # Снизили порог до 0.1 для чувствительности
                # Регулируем интервал движения от 2 (очень быстро) до 10 (медленно)
                base_move_interval = int(10 - r2_value * 8)  # Диапазон: 2-10 кадров
                base_move_interval = max(2, base_move_interval)  # Минимум 2 кадра
            else:
                base_move_interval = 10
        
        # Применяем эффекты ускорения/замедления от бонусов и дебафов
        move_interval = base_move_interval
        if game.slowdown_timer < 0:  # Ускорение от яблока
            move_interval = max(2, base_move_interval - 5)  # Ускоряем на 5 кадров
            game.slowdown_timer += 1  # Уменьшаем таймер (движется к 0)
        elif game.slowdown_timer > 0:  # Замедление от паука
            move_interval = min(20, base_move_interval + 5)  # Замедляем на 5 кадров
            game.slowdown_timer -= 1  # Уменьшаем таймер
        
        # Счётчик движения (ВМЕЖЕ цикла событий)
        move_counter += 1
        if move_counter >= move_interval:
            # Не двигаемся, если активна заморозка
            if game.freeze_timer == 0:
                game.snake.move()
            move_counter = 0
        
        # Обновление игры и отрисовка
        game.update()
        draw = getattr(game, "draw", None)
        if draw:
            draw(screen)
        
        pygame.display.flip()
        
        # Если игра закончилась, просим ввести имя и сохранить рекорд
        if game.game_over and not game._score_saved:
            input_player_name(screen, game.score, game.level, controller)
            game._score_saved = True
            # После сохранения рекорда, показываем меню
            action = show_menu(screen, controller)
            if action == "exit":
                pygame.quit()
                sys.exit()
            # Иначе перезагружаем игру
            game_running = False
        
        # Постоянные 60 FPS для плавности отрисовки
        clock.tick(60)

if __name__ == "__main__":
    main()


