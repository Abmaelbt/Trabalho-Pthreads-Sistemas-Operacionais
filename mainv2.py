import pygame
import threading
import random
import time

# Configurações do Jogo
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Parâmetros de dificuldade
difficulty = {
    1: {'k': 40, 'speed': 1, 'm': 10},
    2: {'k': 30, 'speed': 2, 'm': 15},
    3: {'k': 20, 'speed': 3, 'm': 20}
}
difficulty_level = 3  # Pode ser 1, 2 ou 3

# Configuração Inicial
rocket_capacity = difficulty[difficulty_level]['k']
alien_speed = difficulty[difficulty_level]['speed']
alien_count = difficulty[difficulty_level]['m']
rockets_left = rocket_capacity

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Inicializa o Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jogo de Defesa Aérea")
clock = pygame.time.Clock()

# Classe para representar a bateria antiaérea
class Battery:
    def __init__(self):
        self.position = 'vertical'
        self.rockets = rocket_capacity
        self.lock = threading.Lock()

    def fire(self):
        with self.lock:
            if self.rockets > 0:
                self.rockets -= 1
                return True
            return False

    def reload(self):
        with self.lock:
            self.rockets = rocket_capacity

battery = Battery()

# Classe para representar as naves alienígenas
class Alien(threading.Thread):
    def __init__(self, x, speed):
        threading.Thread.__init__(self)
        self.x = x
        self.y = 0
        self.speed = speed
        self.hit = False

    def run(self):
        global running, aliens_reached_ground, aliens_hit
        while self.y < SCREEN_HEIGHT and not self.hit:
            self.y += self.speed
            time.sleep(0.1)
        if self.y >= SCREEN_HEIGHT and not self.hit:
            with aliens_lock:
                aliens_reached_ground += 1
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

# Variáveis de estado do jogo
aliens = []
aliens_lock = threading.Lock()
aliens_reached_ground = 0
aliens_hit = 0
running = True
rockets = []

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

def game_loop():
    global running, rockets_left
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if battery.fire():
                        # Dispara um foguete
                        rocket = Rocket(SCREEN_WIDTH // 2, SCREEN_HEIGHT, battery.position)
                        rockets.append(rocket)
                if event.key == pygame.K_r:
                    battery.reload()
                if event.key == pygame.K_LEFT:
                    battery.position = 'left'
                if event.key == pygame.K_RIGHT:
                    battery.position = 'right'
                if event.key == pygame.K_UP:
                    battery.position = 'vertical'
                if event.key == pygame.K_a:
                    battery.position = 'diagonal_left'
                if event.key == pygame.K_d:
                    battery.position = 'diagonal_right'

        screen.fill(WHITE)

        # Desenha a bateria
        if battery.position == 'vertical':
            pygame.draw.line(screen, RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT), (SCREEN_WIDTH//2, SCREEN_HEIGHT - 50), 5)
        elif battery.position == 'left':
            pygame.draw.line(screen, RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT), (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT), 5)
        elif battery.position == 'right':
            pygame.draw.line(screen, RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT), (SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT), 5)
        elif battery.position == 'diagonal_left':
            pygame.draw.line(screen, RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT), (SCREEN_WIDTH//2 - 35, SCREEN_HEIGHT - 35), 5)
        elif battery.position == 'diagonal_right':
            pygame.draw.line(screen, RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT), (SCREEN_WIDTH//2 + 35, SCREEN_HEIGHT - 35), 5)

        # Move e desenha os foguetes
        for rocket in rockets[:]:
            rocket.move()
            if rocket.y < 0 or rocket.x < 0 or rocket.x > SCREEN_WIDTH:
                rockets.remove(rocket)
            else:
                pygame.draw.rect(screen, RED, (rocket.x, rocket.y, 5, 10))

        # Desenha os aliens e verifica colisões
        for alien in aliens:
            if not alien.hit:
                for rocket in rockets[:]:
                    if check_collision(rocket, alien):
                        alien.hit = True
                        rockets.remove(rocket)
                        break
                if not alien.hit:
                    pygame.draw.circle(screen, GREEN, (alien.x, alien.y), 10)

        # Desenha a contagem de foguetes
        font = pygame.font.Font(None, 36)
        text = font.render(f'Rockets: {battery.rockets}', True, RED)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

        # Verifica condições de vitória/derrota
        if aliens_hit >= alien_count // 2:
            print("Vitória!")
            running = False
        if aliens_reached_ground >= alien_count // 2:
            print("Derrota!")
            running = False

# Cria a thread para criar as naves
alien_thread = threading.Thread(target=create_aliens)
alien_thread.start()

# Inicia o loop do jogo
game_loop()

# Aguarda a finalização das threads
for alien in aliens:
    alien.join()

pygame.quit()
