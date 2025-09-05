import pygame
import random
import math
import os

# Ініціалізація Pygame
pygame.init()

# Налаштування екрану
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Морська Битва")

# Кольори
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Шлях до папки з файлами гри
game_folder = os.path.dirname(__file__)

# Завантаження зображень
try:
    player_image = pygame.image.load(os.path.join(game_folder, 'player.png')).convert_alpha()
    enemy_image = pygame.image.load(os.path.join(game_folder, 'enemy.png')).convert_alpha()
except pygame.error as e:
    print("Не вдалося завантажити зображення. Переконайтеся, що файли player.png та enemy.png знаходяться в папці гри.")
    raise SystemExit(e)

# Зменшення розміру зображень для кращої сумісності
player_image = pygame.transform.scale(player_image, (50, 50))
enemy_image = pygame.transform.scale(enemy_image, (40, 40))

# Шрифти
font = pygame.font.Font(None, 36)

# Клас для гравця (корабля)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = 0
        self.speed_y = 0
        self.angle = 0 # Кут повороту
        self.original_image = self.image.copy() # Зберігаємо оригінал для обертання

    def update(self):
        self.speed_x = 0
        self.speed_y = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.speed_x = -5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.speed_x = 5
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed_y = -5
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed_y = 5
        
        # Оновлення позиції
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Обмеження руху гравця в межах екрану
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0
            
        # Обертання
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        self.angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

# Клас для ворогів
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_pos):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        
        # Випадкова точка появи ворога за межами екрану
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            self.rect.x = random.randrange(SCREEN_WIDTH)
            self.rect.y = random.randrange(-100, -40)
        elif side == "bottom":
            self.rect.x = random.randrange(SCREEN_WIDTH)
            self.rect.y = random.randrange(SCREEN_HEIGHT + 40, SCREEN_HEIGHT + 100)
        elif side == "left":
            self.rect.x = random.randrange(-100, -40)
            self.rect.y = random.randrange(SCREEN_HEIGHT)
        elif side == "right":
            self.rect.x = random.randrange(SCREEN_WIDTH + 40, SCREEN_WIDTH + 100)
            self.rect.y = random.randrange(SCREEN_HEIGHT)
        
        self.speed = random.randrange(1, 4)

    def update(self, player_pos):
        # Рух ворога до гравця
        dx = player_pos.x - self.rect.x
        dy = player_pos.y - self.rect.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist != 0:
            self.rect.x += self.speed * (dx / dist)
            self.rect.y += self.speed * (dy / dist)

# Клас для снарядів (ядер)
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Визначення швидкості та напрямку снаряда
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx**2 + dy**2)
        self.speed = 10
        if dist != 0:
            self.speed_x = self.speed * (dx / dist)
            self.speed_y = self.speed * (dy / dist)
        else:
            self.speed_x = 0
            self.speed_y = -self.speed

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Видалення снаряда, якщо він вилетів за межі екрану
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

# Групи спрайтів
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Створення гравця
player = Player()
all_sprites.add(player)

# Змінні гри
score = 0
running = True
clock = pygame.time.Clock()

# Змінні для спавну ворогів
spawn_timer = 0
spawn_rate = 180 # Кожні 3 секунди (60 FPS * 3)
max_enemies = 3 # Максимальна кількість ворогів на екрані

while running:
    # Обробка подій
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 1 - ліва кнопка миші
                mouse_pos = pygame.mouse.get_pos()
                bullet = Bullet(player.rect.centerx, player.rect.centery, mouse_pos[0], mouse_pos[1])
                all_sprites.add(bullet)
                bullets.add(bullet)

    # Логіка спавну ворогів
    spawn_timer += 1
    if spawn_timer >= spawn_rate and len(enemies) < max_enemies:
        enemy = Enemy(player.rect)
        all_sprites.add(enemy)
        enemies.add(enemy)
        spawn_timer = 0 # Скидаємо таймер
        spawn_rate = random.randrange(120, 240) # Випадковий інтервал 2-4 секунди

    # Оновлення спрайтів
    player.update()
    enemies.update(player.rect)
    bullets.update()
    
    # Перевірка зіткнень
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10
        
    # Перевірка зіткнень гравця з ворогами
    player_hits = pygame.sprite.spritecollide(player, enemies, False)
    if player_hits:
        print("Гра закінчена! Ваш рахунок:", score)
        running = False

    # Рендеринг (малювання)
    screen.fill(BLUE)
    all_sprites.draw(screen)

    # Виведення рахунку
    score_text = font.render(f"Очки: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Оновлення екрану
    pygame.display.flip()

    # Обмеження FPS
    clock.tick(60)

pygame.quit()