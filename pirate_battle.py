import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Піратська Битва")

# Colors
BLUE = (64, 164, 223)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Game settings
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPAWN_DELAY = 180  # frames
MAX_ENEMIES = 5

# Load images and effects
def load_image(path, scale=1.0, angle=0):
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale != 1.0:
            new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
            img = pygame.transform.scale(img, new_size)
        if angle != 0:
            img = pygame.transform.rotate(img, angle)
        return img
    except Exception as e:
        print(f"Error loading {path}: {e}")
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(surf, (random.randint(0, 255), 0, 0), (0, 0, 50, 50))
        return surf

# Load explosion animation
def load_explosion_animation():
    explosion_anim = []
    for i in range(1, 4):
        try:
            filename = f'PNG/Default size/Effects/explosion{i}.png'
            img = load_image(filename, 0.5)
            explosion_anim.append(img)
        except:
            continue
    return explosion_anim

# Load fire animation
def load_fire_animation():
    fire_anim = []
    for i in range(1, 3):
        try:
            filename = f'PNG/Default size/Effects/fire{i}.png'
            img = load_image(filename, 0.3)
            fire_anim.append(img)
        except:
            continue
    return fire_anim

# Список доступних кораблів для ворогів
ENEMY_SHIPS = [
    'ship (1).png', 'ship (2).png', 'ship (3).png',
    'ship (4).png', 'ship (5).png', 'ship (6).png',
    'ship (7).png', 'ship (8).png', 'ship (9).png',
    'dinghyLarge1.png', 'dinghyLarge2.png', 'dinghyLarge3.png'
]

# Клас гравця
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = load_image('PNG/Default size/Ships/ship (1).png', 0.7)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.angle = 0
        self.speed = 5
        self.health = 100
        self.shoot_cooldown = 0
        self.last_shot = 0
        self.shot_delay = 300  # Затрижка між пострілами (мс)

    def update(self):
        # Handle rotation
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle += 3
        if keys[pygame.K_RIGHT]:
            self.angle -= 3
        
        # Update image rotation
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Handle movement
        if keys[pygame.K_UP]:
            self.rect.x += math.sin(math.radians(self.angle)) * self.speed
            self.rect.y -= math.cos(math.radians(self.angle)) * self.speed
        if keys[pygame.K_DOWN]:
            self.rect.x -= math.sin(math.radians(self.angle)) * (self.speed/2)
            self.rect.y += math.cos(math.radians(self.angle)) * (self.speed/2)
        
        # Screen wrapping
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = SCREEN_HEIGHT
        elif self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0

# Explosion effect
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.image = explosion_anim[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # ms

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        # Завантажуємо та масштабуємо зображення ядра
        try:
            self.image = pygame.image.load('PNG/Default size/Ship parts/cannonBall.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (20, 20))
        except:
            # Якщо не вдалося завантажити зображення, створюємо просте коло
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 0, 0), (10, 10), 10)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = 15  # Збільшуємо швидкість кулі
        self.lifetime = 90  # Час життя в кадрах
        
        # Додаємо ефект вогню
        self.fire = FireEffect(self.rect.center, 1)
        all_sprites.add(self.fire)

    def update(self):
        # Рухаємо кулю у напрямку кута
        self.rect.x += math.sin(math.radians(self.angle)) * self.speed
        self.rect.y -= math.cos(math.radians(self.angle)) * self.speed
        
        # Оновлюємо позицію ефекту вогню
        if hasattr(self, 'fire') and self.fire:
            self.fire.rect.center = self.rect.center
        
        # Перевіряємо час життя кулі
        self.lifetime -= 1
        if self.lifetime <= 0:
            # Створюємо невеликий вибух при зникненні кулі
            expl = Explosion(self.rect.center, 'small')
            all_sprites.add(expl)
            self.kill()

# Клас ворога
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Випадково обираємо тип корабля для ворога
        ship_type = random.choice(ENEMY_SHIPS)
        self.original_image = load_image(f'PNG/Default size/Ships/{ship_type}', random.uniform(0.5, 0.9))
        self.image = self.original_image
        
        # Spawn from edges
        side = random.choice(['top', 'right', 'bottom', 'left'])
        if side == 'top':
            x = random.randint(0, SCREEN_WIDTH)
            y = -50
        elif side == 'right':
            x = SCREEN_WIDTH + 50
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 'bottom':
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 50
        else:  # left
            x = -50
            y = random.randint(0, SCREEN_HEIGHT)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.uniform(1, 3)
        self.health = 30

    def update(self, player_pos):
        # Move towards player
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        
        if dist != 0:
            dx = dx / dist * self.speed
            dy = dy / dist * self.speed
            self.rect.x += dx
            self.rect.y += dy
        
        # Rotate towards movement
        self.angle = math.degrees(math.atan2(-dx, -dy))
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

# Game initialization
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Load animations
explosion_anim = load_explosion_animation()
fire_anim = load_fire_animation()

# Fire effect for bullets
class FireEffect(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.image = fire_anim[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # ms

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame = (self.frame + 1) % len(fire_anim)
            center = self.rect.center
            self.image = fire_anim[self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = center

player = Player()
all_sprites.add(player)

clock = pygame.time.Clock()
running = True
spawn_timer = 0
score = 0

# Game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # Додаємо постріл по натисканню пробілу для тестування
            elif event.key == pygame.K_SPACE:
                bullet = Bullet(player.rect.centerx, player.rect.centery, player.angle)
                all_sprites.add(bullet)
                bullets.add(bullet)
                print(f"Bullet fired with angle: {player.angle}")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click - постріл у напрямку миші
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - player.rect.centerx
                dy = mouse_y - player.rect.centery
                angle = math.degrees(math.atan2(-dx, dy))
                bullet = Bullet(player.rect.centerx, player.rect.centery, angle)
                all_sprites.add(bullet)
                bullets.add(bullet)
                print(f"Mouse shot at angle: {angle}")
    
    # Spawn enemies
    spawn_timer += 1
    if spawn_timer >= ENEMY_SPAWN_DELAY and len(enemies) < MAX_ENEMIES:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        spawn_timer = 0
    
    # Update
    # Update player and bullets
    player.update()
    bullets.update()
    
    # Update enemies with player position
    for enemy in enemies:
        enemy.update(player.rect.center)
        # Check bullet-enemy collisions
        hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
        for bullet, hit_enemies in hits.items():
            # Create explosion at bullet impact
            expl = Explosion(bullet.rect.center, 'lg')
            all_sprites.add(expl)
            
            for enemy in hit_enemies:
                enemy.health -= 10
                if enemy.health <= 0:
                    # Bigger explosion when enemy is destroyed
                    expl = Explosion(enemy.rect.center, 'lg')
                    all_sprites.add(expl)
                    enemy.kill()
                    score += 10
    
    # Check player-enemy collisions
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits:
        player.health -= 0.5
        if player.health <= 0:
            running = False
    
    # Draw
    screen.fill(BLUE)
    all_sprites.draw(screen)
    
    # Draw UI
    health_text = f"HP: {int(player.health)}"
    score_text = f"Рахунок: {score}"
    font = pygame.font.Font(None, 36)
    health_surface = font.render(health_text, True, WHITE)
    score_surface = font.render(score_text, True, WHITE)
    screen.blit(health_surface, (10, 10))
    screen.blit(score_surface, (10, 50))
    
    # Draw health bar
    pygame.draw.rect(screen, RED, (10, 40, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 40, 200 * (player.health/100), 20))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
