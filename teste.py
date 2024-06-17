import pygame
import threading
import random
import time

# Classe para representar a bateria antiaérea
class Battery:
    def __init__(self):
        self.position = 'vertical'
        self.rockets = rocket_capacity
        self.lock = threading.Lock()
        self.reloading = False

    def fire(self):
        with self.lock:
            if self.rockets > 0:
                self.rockets -= 1
                return True
            return False

    def reload(self):
        self.reloading = True
        with self.lock:
            ReloadBattery().start()


class ReloadBattery(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        time.sleep(RELOAD_TIME_SECONDS)
        battery.rockets = rocket_capacity
        battery.reloading = False


# Classe para representar as naves alienígenas
class Alien(threading.Thread):
    def __init__(self, x, speed):
        threading.Thread.__init__(self)
        self.x = x
        self.y = 0
        self.speed = speed
        self.hit = False

    def run(self):
        global running, aliens_reached_ground, aliens_hit, aliens_remaining
        while self.y < SCREEN_HEIGHT + 10 and not self.hit:
            self.y += self.speed
            time.sleep(0.1)
        if self.y >= SCREEN_HEIGHT + 10 and not self.hit:
            with aliens_lock:
                aliens_reached_ground += 1
                aliens_remaining -= 1  # Decrementa o contador quando uma nave atinge o solo
        if self.hit:
            with aliens_lock:
                aliens_hit += 1


# Classe para representar os foguetes
class Rocket:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.speed = 5
        self.direction = direction

    def move(self):
        if self.direction == 'vertical':
            self.y -= self.speed
        elif self.direction == 'left':
            self.x -= self.speed
        elif self.direction == 'right':
            self.x += self.speed
        elif self.direction == 'diagonal_left':
            self.x -= self.speed
            self.y -= self.speed
        elif self.direction == 'diagonal_right':
            self.x += self.speed
            self.y -= self.speed


def create_aliens():
    for _ in range(alien_count):
        x = random.randint(0, SCREEN_WIDTH)
        alien = Alien(x, alien_speed)
        aliens.append(alien)
        alien.start()
        time.sleep(1)


def check_collision(rocket, alien):
    # Verifica se o foguete colide com a nave
    return (alien.x - 10 < rocket.x < alien.x + 10) and (alien.y - 10 < rocket.y < alien.y + 10)


def draw_battery():
    if battery.position == 'vertical':
        pygame.draw.line(screen, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT),
                         (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50),
                         5)
    elif battery.position == 'left':
        pygame.draw.line(
            screen,
            RED,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 5),
            (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 5),
            5)
    elif battery.position == 'right':
        pygame.draw.line(screen, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 5),
                         (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT - 5),
                         5)
    elif battery.position == 'diagonal_left':
        pygame.draw.line(screen, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT),
                         (SCREEN_WIDTH // 2 - 35, SCREEN_HEIGHT - 35), 5)
    elif battery.position == 'diagonal_right':
        pygame.draw.line(screen, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT),
                         (SCREEN_WIDTH // 2 + 35, SCREEN_HEIGHT - 35), 5)


def check_game_has_finished():
    global running
    won_lost_font = pygame.font.Font(None, 60)
    if aliens_hit >= alien_count // 2:
        won_message = won_lost_font.render("YOU WON!", True, YELLOW)
        won_rect = won_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(won_message, won_rect)
        pygame.display.flip()
        pygame.time.wait(4000)
        running = False
    elif aliens_remaining <= 0:
        lost_message = won_lost_font.render("YOU LOST!", True, RED)
        lost_rect = lost_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(lost_message, lost_rect)
        pygame.display.flip()
        pygame.time.wait(4000)
        running = False


def create_rocket():
    if battery.position in ['left', 'right']:
        return Rocket(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 7, battery.position)
    if battery.position in ['diagonal_left', 'diagonal_right']:
        return Rocket(SCREEN_WIDTH // 2, SCREEN_HEIGHT, battery.position)

    return Rocket(SCREEN_WIDTH // 2 - 2, SCREEN_HEIGHT - 20, battery.position)


def draw_remaining_aliens():
    font = pygame.font.Font(None, 36)
    remaining_text = font.render(f'Remaining Aliens: {aliens_remaining}', True, RED)
    screen.blit(remaining_text, (SCREEN_WIDTH - 250, 10))


def game_loop():
    global running
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if battery.fire():
                        rocket = create_rocket()
                        rockets.append(rocket)
                if event.key == pygame.K_r and not battery.reloading:
                    battery.reload()
                if event.key == pygame.K_a:
                    battery.position = 'left'
                if event.key == pygame.K_d:
                    battery.position = 'right'
                if event.key == pygame.K_w:
                    battery.position = 'vertical'
                if event.key == pygame.K_q:
                    battery.position = 'diagonal_left'
                if event.key == pygame.K_e:
                    battery.position = 'diagonal_right'

        screen.fill(BLACK)

        draw_battery()
        draw_remaining_aliens()

        for rocket in rockets[:]:
            rocket.move()
            if rocket.y < 0 or rocket.x < 0 or rocket.x > SCREEN_WIDTH:
                rockets.remove(rocket)
            else:
                if rocket.direction in ['right', 'left']:
                    pygame.draw.rect(screen, RED, (rocket.x, rocket.y, 10, 5))
                elif rocket.direction == 'diagonal_left':
                    pygame.draw.line(screen, RED, (rocket.x, rocket.y),
                                     (rocket.x - 6, rocket.y - 6), 7)
                elif rocket.direction == 'diagonal_right':
                    pygame.draw.line(screen, RED, (rocket.x, rocket.y),
                                     (rocket.x + 6, rocket.y - 6), 7)
                else:
                    pygame.draw.rect(screen, RED, (rocket.x, rocket.y, 5, 10))

        for alien in aliens:
            if not alien.hit:
                for rocket in rockets[:]:
                    if check_collision(rocket, alien):
                        alien.hit = True
                        rockets.remove(rocket)
                        break
                if not alien.hit:
                    pygame.draw.circle(screen, GREEN, (alien.x, alien.y), 10)

        font = pygame.font.Font(None, 36)
        text = font.render(f'Rockets: {battery.rockets}', True, RED)
        screen.blit(text, (10, 10))

        if battery.reloading:
            reloading_text = font.render('Reloading', True, RED)
            screen.blit(reloading_text, (SCREEN_WIDTH - 150, 10))

        pygame.display.flip()
        clock.tick(FPS)

        check_game_has_finished()


def show_menu():
    menu_running = True
    selected_difficulty = 1
    font = pygame.font.Font(None, 74)

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_difficulty = 1
                    menu_running = False
                if event.key == pygame.K_2:
                    selected_difficulty = 2
                    menu_running = False
                if event.key == pygame.K_3:
                    selected_difficulty = 3
                    menu_running = False

        screen.fill(BLACK)

        text = font.render("GAME DIFFICULTY", True, WHITE)
        screen.blit(text, (100, 100))
        text = font.render("1. EASY", True, GREEN)
        screen.blit(text, (100, 200))
        text = font.render("2. MEDIUM", True, YELLOW)
        screen.blit(text, (100, 300))
        text = font.render("3. HARD", True, RED)
        screen.blit(text, (100, 400))

        pygame.display.flip()
        clock.tick(FPS)

    return selected_difficulty


def setup_difficulty(level):
    global rocket_capacity, alien_speed, alien_count, aliens_remaining
    rocket_capacity = difficulty[level]['rockets_amount']
    alien_speed = difficulty[level]['alien_speed']
    alien_count = difficulty[level]['aliens_amount']
    aliens_remaining = alien_count


# Configurações do Jogo
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Parâmetros de dificuldade
difficulty = {
    1: {'rockets_amount': 40, 'alien_speed': 2, 'aliens_amount': 10},
    2: {'rockets_amount': 30, 'alien_speed': 3, 'aliens_amount': 15},
    3: {'rockets_amount': 20, 'alien_speed': 4, 'aliens_amount': 20}
}

# Configuração Inicial
rocket_capacity = 40
alien_speed = 1
alien_count = 10
RELOAD_TIME_SECONDS = 3

# Cores
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# Inicializa o Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jogo de Defesa Aérea")
clock = pygame.time.Clock()

difficulty_level = show_menu()
setup_difficulty(difficulty_level)

battery = Battery()

# Variáveis de estado do jogo
aliens = []
aliens_lock = threading.Lock()
aliens_reached_ground = 0
aliens_hit = 0
aliens_remaining = alien_count
running = True
rockets = []

# Cria a thread para criar as naves
alien_thread = threading.Thread(target=create_aliens)
alien_thread.start()

# Inicia o loop do jogo
game_loop()

pygame.quit()
