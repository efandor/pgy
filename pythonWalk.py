import pygame
import random
import sys
import os
from math import sqrt

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40
PLAYER_SIZE = 30
ARTIFACT_SIZE = 20
ENEMY_SIZE = PLAYER_SIZE
ATTACK_RADIUS = 50
MAIN_COLOR = (198, 255, 202)
CONTRAST_COLOR = (51, 113, 41)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (67, 130, 255)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 150, 0)
DARK_RED = (150, 0, 0)
LIGHT_BLUE = (173, 216, 230)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
COLORS_SET = [(45, 252, 101), (151, 252, 43), (215, 247, 9), (248, 141, 41), (253, 0, 0)]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Лабиринт с загадочными артефактами')
font_large = pygame.font.SysFont('Arial', 48)
font_medium = pygame.font.SysFont('Arial', 36)
font_small = pygame.font.SysFont('Arial', 24)

try:
    click_sound = pygame.mixer.Sound(os.path.join('Sources/Audio', 'click.mp3'))
    attack_sound = pygame.mixer.Sound(os.path.join('Sources/Audio', 'attack.mp3'))
    win_sound = pygame.mixer.Sound(os.path.join('Sources/Audio', 'win.ogg'))
    game_over_sound = pygame.mixer.Sound(os.path.join('Sources/Audio', 'gameOver.mp3'))
    theme_music = pygame.mixer.Sound(os.path.join('Sources/Audio', 'theme.mp3'))
    theme_music.set_volume(0.5)
    click_sound.set_volume(0.7)
except:
    print('Ошибка загрузки звуков')
    class DummySound:
        def play(self): pass


    click_sound = attack_sound = win_sound = game_over_sound = theme_music = DummySound()

try:
    enemy_image = pygame.image.load(os.path.join('Sources/Pictures', 'js.jpg'))
    enemy_image = pygame.transform.scale(enemy_image, (ENEMY_SIZE, ENEMY_SIZE))
    player_image = pygame.image.load(os.path.join('Sources/Pictures', 'pt.png'))
    player_image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
    artifact_image = pygame.image.load(os.path.join('Sources/Pictures', 'art.png'))
    artifact_image = pygame.transform.scale(artifact_image, (ARTIFACT_SIZE, ARTIFACT_SIZE))
except:
    print('Ошибка загрузки изображений')
    enemy_image = None
    player_image = None
    artifact_image = None

quiz_questions = {
    'Какая функция находит длину строки?': ['len', 'input', 'print', 'length'],
    'Какой оператор нужен для возведения в степень?': ['**', '^', '*', '//'],
    'Как создать пустой список в Python?': ['[]', 'list()', '{}', '()'],
    'Какой метод добавляет элемент в конец списка?': ['append()', 'add()', 'insert()', 'push()'],
    'Как проверить тип переменной в Python?': ['type()', 'typeof()', 'checktype()', 'var_type()'],
    'Какой символ используется для комментариев?': ['#', '//', '--', '/*'],
    'Оператор целочисленного деления?': ['//', '/', '%', '|'],
    'Какой тип данных является неизменяемым?': ['tuple', 'list', 'dict', 'set'],
    'Какой метод разбивает строку по разделителю?': ['split()', 'divide()', 'break()', 'slice()'],
    'Какой оператор проверяет идентичность объектов?': ['is', '==', '=', '==='],
    'Как объявить словарь в Python?': ['{}', 'dict()', '[]', '()'],
    'Метод удаляющий элемент из списка по значению?': ['remove()', 'delete()', 'pop()', 'clear()'],
    'Тип данных для хранения пар ключ-значение?': ['dict', 'list', 'tuple', 'set'],
    'Какой оператор используется для логического И?': ['and', '&', '&&', '|']
}


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, CONTRAST_COLOR, self.rect, 2, border_radius=10)

        text_surf = font_small.render(self.text, True, CONTRAST_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click_sound.play()
            return self.rect.collidepoint(pos)
        return False


class Enemy:
    def __init__(self, x, y, maze, level):
        self.x = x
        self.y = y
        self.maze = maze
        self.level = level
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.move_counter = 0
        self.path_length = random.randint(1, 3)
        self.is_alive = True
        self.speed_counter = 0
        self.speed = self.calculate_speed()

    def calculate_speed(self):
        speed_levels = {
            1: 25,
            2: 20,
            3: 15,
            4: 10,
            5: 5
        }
        return speed_levels.get(self.level, 15)

    def move(self):
        if not self.is_alive:
            return

        self.speed_counter += 1
        if self.speed_counter < self.speed:
            return

        self.speed_counter = 0

        new_x = self.x + self.direction[0]
        new_y = self.y + self.direction[1]

        if (self.move_counter >= self.path_length or
                new_x < 0 or new_x >= self.maze.width or
                new_y < 0 or new_y >= self.maze.height or
                self.maze.grid[new_y][new_x] == 1):

            possible_directions = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = self.x + dx, self.y + dy
                if (0 <= nx < self.maze.width and
                        0 <= ny < self.maze.height and
                        self.maze.grid[ny][nx] == 0):
                    possible_directions.append((dx, dy))

            if possible_directions:
                self.direction = random.choice(possible_directions)
                self.path_length = random.randint(1, 3)
                self.move_counter = 0
            else:
                return

        new_x = self.x + self.direction[0]
        new_y = self.y + self.direction[1]

        if (0 <= new_x < self.maze.width and
                0 <= new_y < self.maze.height and
                self.maze.grid[new_y][new_x] == 0):
            self.x = new_x
            self.y = new_y
            self.move_counter += 1

    def draw(self):
        if self.is_alive:
            if enemy_image:
                screen.blit(enemy_image,
                            (self.x * CELL_SIZE + (CELL_SIZE - ENEMY_SIZE) // 2,
                             self.y * CELL_SIZE + (CELL_SIZE - ENEMY_SIZE) // 2))
            else:
                pygame.draw.rect(screen, PURPLE,
                                 (self.x * CELL_SIZE + (CELL_SIZE - ENEMY_SIZE) // 2,
                                  self.y * CELL_SIZE + (CELL_SIZE - ENEMY_SIZE) // 2,
                                  ENEMY_SIZE, ENEMY_SIZE))

    def check_collision(self, player_x, player_y):
        if not self.is_alive:
            return False
        return self.x == player_x and self.y == player_y


class Player:
    def __init__(self, maze):
        self.maze = maze
        self.x = 0
        self.y = 0
        self.artifacts_collected = 0
        self.find_valid_start()
        self.attack_cooldown = 0

    def find_valid_start(self):
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.grid[y][x] == 0:
                    valid_position = True
                    for enemy in self.maze.enemies:
                        if enemy.x == x and enemy.y == y:
                            valid_position = False
                            break
                    if valid_position:
                        self.x = x
                        self.y = y
                        return

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        if 0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height:
            if self.maze.grid[new_y][new_x] == 0:
                self.x = new_x
                self.y = new_y

    def attack(self):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = 20
            attack_sound.play()
            for enemy in self.maze.enemies:
                if enemy.is_alive:
                    distance = sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
                    if distance <= ATTACK_RADIUS / CELL_SIZE:
                        enemy.is_alive = False
            return True
        return False

    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self):
        if player_image:
            screen.blit(player_image,
                        (self.x * CELL_SIZE + (CELL_SIZE - PLAYER_SIZE) // 2,
                         self.y * CELL_SIZE + (CELL_SIZE - PLAYER_SIZE) // 2))
        else:
            pygame.draw.rect(screen, RED,
                             (self.x * CELL_SIZE + (CELL_SIZE - PLAYER_SIZE) // 2,
                              self.y * CELL_SIZE + (CELL_SIZE - PLAYER_SIZE) // 2,
                              PLAYER_SIZE, PLAYER_SIZE))

        if self.attack_cooldown > 15:
            attack_surface = pygame.Surface((ATTACK_RADIUS * 2, ATTACK_RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(attack_surface, (255, 255, 0, 100), (ATTACK_RADIUS, ATTACK_RADIUS), ATTACK_RADIUS)
            screen.blit(attack_surface, (self.x * CELL_SIZE + CELL_SIZE // 2 - ATTACK_RADIUS,
                                         self.y * CELL_SIZE + CELL_SIZE // 2 - ATTACK_RADIUS))


class Maze:
    def __init__(self, width, height, level=1):
        self.width = width // CELL_SIZE
        self.height = height // CELL_SIZE
        self.level = level
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self.generate_maze(0, 0)
        self.place_artifacts()
        self.enemies = []
        self.place_enemies(level)

    def generate_maze(self, x, y):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)

        self.grid[y][x] = 0

        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] == 1:
                self.grid[y + dy][x + dx] = 0
                self.generate_maze(nx, ny)

    def place_artifacts(self):
        self.artifacts = []
        while len(self.artifacts) < 3:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y][x] == 0 and (x, y) not in self.artifacts:
                self.artifacts.append((x, y))

    def place_enemies(self, count):
        for _ in range(count):
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if self.grid[y][x] == 0:
                    valid_position = True
                    for artifact in self.artifacts:
                        if (x, y) == artifact:
                            valid_position = False
                            break
                    if valid_position:
                        self.enemies.append(Enemy(x, y, self, self.level))
                        break

    def draw(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    pygame.draw.rect(screen, CONTRAST_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                else:
                    pygame.draw.rect(screen, MAIN_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        for artifact in self.artifacts:
            x, y = artifact
            if artifact_image:
                screen.blit(artifact_image,
                            (x * CELL_SIZE + (CELL_SIZE - ARTIFACT_SIZE) // 2,
                             y * CELL_SIZE + (CELL_SIZE - ARTIFACT_SIZE) // 2))
            else:
                pygame.draw.circle(screen, GREEN,
                               (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2),
                               ARTIFACT_SIZE // 2)

        for enemy in self.enemies:
            enemy.draw()


def draw_level_select():
    screen.fill(MAIN_COLOR)
    title = font_large.render('Выберите уровень сложности', True, CONTRAST_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    buttons = []
    for i in range(5):
        btn = Button(WIDTH // 2 - 100, 200 + i * 70, 200, 50, f'Уровень {i + 1}',
                     COLORS_SET[i],
                     YELLOW)
        buttons.append(btn)

    return buttons


def new_game(level):
    maze = Maze(WIDTH, HEIGHT, level)
    player = Player(maze)
    available_questions = list(quiz_questions.items())
    random.shuffle(available_questions)
    return maze, player, available_questions


def draw_game_over_screen(message):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    if 'победили' in message.lower():
        congrats_text = font_large.render('Поздравляем!', True, MAIN_COLOR)
        win_sound.play()
    else:
        congrats_text = font_large.render('Игра окончена', True, MAIN_COLOR)
        game_over_sound.play()

    screen.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2, 150))

    sub_text = font_medium.render(message, True, MAIN_COLOR)
    screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, 220))

    restart_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 50, 'Начать заново', GREEN, DARK_GREEN)
    exit_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 120, 300, 50, 'Выход из игры', RED, DARK_RED)

    return overlay, restart_button, exit_button


def draw_quiz_screen(question, answers):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    question_text = font_medium.render(question, True, MAIN_COLOR)
    screen.blit(question_text, (WIDTH // 2 - question_text.get_width() // 2, 150))

    buttons = []
    for i, answer in enumerate(answers):
        btn = Button(WIDTH // 2 - 150, 200 + i * 70, 300, 50, answer, LIGHT_BLUE, YELLOW)
        buttons.append(btn)

    return overlay, buttons


def main():
    clock = pygame.time.Clock()
    theme_music.play(-1)
    level_selected = None
    level_buttons = draw_level_select()

    while level_selected is None:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for i, button in enumerate(level_buttons):
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, event):
                    level_selected = i + 1

        screen.fill(MAIN_COLOR)
        title = font_large.render('Выберите уровень сложности', True, CONTRAST_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        for button in level_buttons:
            button.draw(screen)

        hint = font_small.render('Чем выше уровень, тем больше врагов и выше их скорость', True, CONTRAST_COLOR)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()
        clock.tick(60)

    maze, player, available_questions = new_game(level_selected)
    game_over = False
    quiz_active = False
    current_question = ''
    current_answers = []
    correct_answer = ''
    quiz_buttons = []
    game_over_message = ''

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_over:
                overlay, restart_button, exit_button = draw_game_over_screen(game_over_message)

                restart_button.check_hover(mouse_pos)
                exit_button.check_hover(mouse_pos)

                if restart_button.is_clicked(mouse_pos, event):
                    level_selected = None
                    while level_selected is None:
                        mouse_pos = pygame.mouse.get_pos()

                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                running = False
                                level_selected = 1

                            for i, button in enumerate(level_buttons):
                                button.check_hover(mouse_pos)
                                if button.is_clicked(mouse_pos, ev):
                                    level_selected = i + 1

                        screen.fill(MAIN_COLOR)
                        title = font_large.render('Выберите уровень сложности', True, CONTRAST_COLOR)
                        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

                        for button in level_buttons:
                            button.draw(screen)

                        hint = font_small.render('Чем выше уровень, тем больше врагов и выше их скорость', True, CONTRAST_COLOR)
                        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

                        pygame.display.flip()
                        clock.tick(60)

                    if running:
                        maze, player, available_questions = new_game(level_selected)
                        game_over = False
                        quiz_active = False
                elif exit_button.is_clicked(mouse_pos, event):
                    running = False
            elif quiz_active:
                for i, button in enumerate(quiz_buttons):
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, event):
                        if button.text == correct_answer:
                            player.artifacts_collected += 1
                            if player.artifacts_collected >= 3:
                                game_over = True
                                game_over_message = 'Вы победили!'
                        else:
                            game_over = True
                            game_over_message = 'Неправильный ответ!'
                        quiz_active = False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        player.move(0, -1)
                    elif event.key == pygame.K_DOWN:
                        player.move(0, 1)
                    elif event.key == pygame.K_LEFT:
                        player.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        player.move(1, 0)
                    elif event.key == pygame.K_SPACE:
                        player.attack()

                for enemy in maze.enemies:
                    if enemy.check_collision(player.x, player.y):
                        game_over = True
                        game_over_message = 'JavaScript победил!'
                        break

                for artifact in maze.artifacts[:]:
                    if (player.x, player.y) == artifact:
                        maze.artifacts.remove(artifact)
                        quiz_active = True

                        if available_questions:
                            question, answers = available_questions.pop()
                            correct_answer = answers[0]
                            current_answers = answers.copy()
                            random.shuffle(current_answers)
                            current_question = question

        player.update()
        for enemy in maze.enemies:
            enemy.move()

        screen.fill(MAIN_COLOR)
        maze.draw()
        player.draw()

        text = font_small.render(f'Артефакты: {player.artifacts_collected}/3', True, BLUE)
        screen.blit(text, (10, 10))

        level_text = font_small.render(f'Уровень: {level_selected}', True, BLUE)
        screen.blit(level_text, (WIDTH - level_text.get_width() - 10, HEIGHT - 30))

        attack_hint = font_small.render('Пробел - атака', True, BLUE)
        screen.blit(attack_hint, (WIDTH - attack_hint.get_width() - 10, 10))

        if game_over:
            overlay, restart_button, exit_button = draw_game_over_screen(game_over_message)
            restart_button.draw(screen)
            exit_button.draw(screen)
        elif quiz_active:
            overlay, quiz_buttons = draw_quiz_screen(current_question, current_answers)
            for button in quiz_buttons:
                button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()