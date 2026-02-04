import pygame 
import sys
from game_types.index import Snake, Food, Game

def show_menu(screen):
    """Меню с выбором Resume/Exit. Возвращает True если продолжить, False если выход."""
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 48)
    options = ["Resume", "Exit"]
    selected = 0
    running = True
    while running:
        screen.fill((0, 0, 0))
        title = font.render("Меню", True, (255, 255, 255))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, screen.get_height() // 2 - 120))
        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else (255, 255, 255)
            text = small_font.render(opt, True, color)
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2 + i * 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if options[selected] == "Resume":
                        return True
                    elif options[selected] == "Exit":
                        return False
                elif event.key == pygame.K_ESCAPE:
                    return True

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
                    resume = show_menu(screen)
                    if not resume:
                        pygame.quit()
                        sys.exit()
            # Обработка левого стика для смены направления
            if event.type == pygame.JOYAXISMOTION and controller:
                if event.axis == 0:  # Left stick X
                    if event.value > 0.5:
                        game.snake.set_direction((1, 0))  # Right
                    elif event.value < -0.5:
                        game.snake.set_direction((-1, 0))  # Left
                elif event.axis == 1:  # Left stick Y
                    if event.value > 0.5:
                        game.snake.set_direction((0, 1))  # Down
                    elif event.value < -0.5:
                        game.snake.set_direction((0, -1))  # Up
            # Обработка D-Pad (как кнопки)
            if event.type == pygame.JOYBUTTONDOWN and controller:
                if event.button == 11:
                    game.snake.set_direction((0, -1))
                elif event.button == 12:
                    game.snake.set_direction((0, 1))
                elif event.button == 13:
                    game.snake.set_direction((-1, 0))
                elif event.button == 14:
                    game.snake.set_direction((1, 0))
        
        # Обработка триггера R2 для управления движением (ВМУНЕ цикла событий!)
        if controller:
            r2_value = controller.get_axis(5)  # R2 триггер (обычно 5)
            if r2_value > 0.1:  # Снизили порог до 0.1 для чувствительности
                # Регулируем интервал движения от 2 (очень быстро) до 10 (медленно)
                move_interval = int(10 - r2_value * 8)  # Диапазон: 2-10 кадров
                move_interval = max(2, move_interval)  # Минимум 2 кадра
            else:
                move_interval = 10
        
        # Счётчик движения (ВМЕЖЕ цикла событий)
        move_counter += 1
        if move_counter >= move_interval:
            game.snake.move()
            move_counter = 0
        
        # Обновление игры и отрисовка
        game.update()
        draw = getattr(game, "draw", None)
        if draw:
            draw(screen)
        pygame.display.flip()
        
        # Постоянные 60 FPS для плавности отрисовки
        clock.tick(60)

if __name__ == "__main__":
    main()


