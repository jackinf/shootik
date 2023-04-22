import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Player
player_image = pygame.image.load("player.png")
player_rect = player_image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
player_speed = 15

# Enemy
enemy_image = pygame.image.load("enemy.png")
enemy_rects = []

# Projectile
projectile_image = pygame.image.load("projectile.png")
projectile_speed = 10
projectiles = []

# Load background images
background_image = pygame.image.load("background.png")
bg_rect1 = background_image.get_rect()
bg_rect2 = background_image.get_rect(topleft=(0, -bg_rect1.height))
scroll_speed = 1


# Function to create an enemy
def create_enemy():
    enemy_rect = enemy_image.get_rect(center=(random.randint(50, WIDTH - 50), 0))
    enemy_rects.append(enemy_rect)


# Function to shoot a projectile
def shoot_projectile():
    projectile_rect = projectile_image.get_rect(center=(player_rect.centerx, player_rect.top))
    projectiles.append(projectile_rect)
    shooting_sound.play()


def display_score_and_lives():
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))


# Initialize the mixer
pygame.mixer.init()

# Load background music
background_music = pygame.mixer.music.load("music.mp3")

# Load shooting sound effect
shooting_sound = pygame.mixer.Sound("shooting_sound.wav")

# Play background music in a loop
pygame.mixer.music.play(-1)

# Initialize font module
pygame.font.init()

# Set up score and lives variables
score = 0
lives = 3

# Load a font
font = pygame.font.Font(None, 36)  # Use a default font with size 36


# Game loop
clock = pygame.time.Clock()
enemy_timer = pygame.USEREVENT
pygame.time.set_timer(enemy_timer, 1500)


def update():
    # Update background rects
    bg_rect1.y += scroll_speed
    bg_rect2.y += scroll_speed

    # Reset rects when they go off the screen
    if bg_rect1.top >= bg_rect1.height:
        bg_rect1.y = -bg_rect1.height
    if bg_rect2.top >= bg_rect2.height:
        bg_rect2.y = -bg_rect2.height

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == enemy_timer:
            create_enemy()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shoot_projectile()

    # Handle player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += player_speed

    # Move enemies
    for enemy_rect in enemy_rects:
        enemy_rect.y += 3
        if enemy_rect.colliderect(player_rect):
            global lives
            if lives > 1:
                lives -= 1
                enemy_rects.remove(enemy_rect)
            else:
                pygame.quit()
                sys.exit()
        if enemy_rect.top > HEIGHT:
            enemy_rects.remove(enemy_rect)

    # Update projectiles position in the game loop
    for projectile in projectiles[:]:
        projectile.y -= projectile_speed
        if projectile.bottom < 0:
            projectiles.remove(projectile)

        for enemy_rect in enemy_rects:
            if enemy_rect.colliderect(projectile):
                projectiles.remove(projectile)
                enemy_rects.remove(enemy_rect)

                global score
                score += 10


def draw():
    # Draw
    screen.fill(BLACK)

    # Draw background rects
    screen.blit(background_image, bg_rect1)
    screen.blit(background_image, bg_rect2)

    # Draw player
    screen.blit(player_image, player_rect)

    # Draw enemies in the game loop
    for enemy_rect in enemy_rects:
        screen.blit(enemy_image, enemy_rect)

    # Draw projectiles in the game loop
    for projectile in projectiles:
        screen.blit(projectile_image, projectile)

    # Display score and lives
    display_score_and_lives()

    pygame.display.flip()


while True:
    update()
    draw()

    clock.tick(60)
