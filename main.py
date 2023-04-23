from typing import List

import pygame
import sys
import random

TIMER_ENEMY_SPAWN = pygame.USEREVENT
ENEMY_SPAWN_MS_PER_FRAME = 1500

TIMER_ANIMATION = pygame.USEREVENT + 1
ANIMATION_MS_PER_FRAME = 80  # Time (in milliseconds) for each frame


class SpaceShooter:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.player = Player(self)
        self.enemy = EnemyPool(self)
        self.projectile = ProjectilePool(self)
        self.background = Background(self)
        self.mixer = Mixer(self)
        self.ui = UI(self)
        self.score = 0
        self.lives = 3

        pygame.time.set_timer(TIMER_ENEMY_SPAWN, ENEMY_SPAWN_MS_PER_FRAME)
        pygame.time.set_timer(TIMER_ANIMATION, ANIMATION_MS_PER_FRAME)

    def run(self):
        while True:
            try:
                self.handle_events()
                self.update()
                self.draw()
            except Exception as error:
                print(error)

            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            self.player.handle_events(event)
            self.enemy.handle_events(event)
            self.projectile.handle_events(event)

    def update(self):
        self.background.update()
        self.player.update()
        self.enemy.update()
        self.projectile.update()

    def draw(self):
        self.screen.fill(self.BLACK)
        self.background.draw()
        self.player.draw()
        self.enemy.draw()
        self.projectile.draw()
        self.ui.display_score_and_lives()
        pygame.display.flip()


class AnimatedGameObject:
    def __init__(self, game: SpaceShooter, images: List[str], scale: int = 1):
        self.game = game
        self.frames = [pygame.image.load(img) for img in images]
        self.frames = [pygame.transform.scale(frame, (frame.get_width() * scale, frame.get_height() * scale)) for frame
                       in self.frames]
        self.frame_index = 0

    def update_animation(self, event):
        if event == TIMER_ANIMATION:
            self.frame_index = (self.frame_index + 1) % len(self.frames)


class Player(AnimatedGameObject):
    def __init__(self, game: SpaceShooter):
        images = ["assets/images/player/player_0.png", "assets/images/player/player_1.png"]
        super().__init__(game, images)
        self.rect = self.frames[0].get_rect(center=(game.width // 2, game.height - 50))
        self.speed = 15

    def handle_events(self, event):
        self.update_animation(event)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < self.game.width:
            self.rect.x += self.speed

    def draw(self):
        self.game.screen.blit(self.frames[self.frame_index], self.rect)


class EnemyPool(AnimatedGameObject):
    def __init__(self, game: SpaceShooter):
        images = [
            "assets/images/meteor/meteor_1.png",
            "assets/images/meteor/meteor_2.png",
            "assets/images/meteor/meteor_3.png",
            "assets/images/meteor/meteor_4.png",
            "assets/images/meteor/meteor_5.png",
        ]
        super().__init__(game, images, scale=3)
        self.rects = []
        self.enemy_speed = 5

    def create_enemy(self):
        enemy_rect = self.frames[0].get_rect(center=(random.randint(50, self.game.width - 50), 0))
        self.rects.append(enemy_rect)

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == TIMER_ENEMY_SPAWN:
            self.create_enemy()

        self.update_animation(event)

    def update(self):
        for enemy_rect in self.rects:
            enemy_rect.y += self.enemy_speed
            if enemy_rect.colliderect(self.game.player.rect):
                if self.game.lives > 1:
                    self.game.lives -= 1
                    self.rects.remove(enemy_rect)
                else:
                    pygame.quit()
                    sys.exit()
            if enemy_rect.top > self.game.height:
                self.rects.remove(enemy_rect)

    def draw(self):
        for enemy_rect in self.rects:
            self.game.screen.blit(self.frames[self.frame_index], enemy_rect)


class ProjectilePool(AnimatedGameObject):
    def __init__(self, game: SpaceShooter):
        images = ["assets/images/projectile.png"]
        super().__init__(game, images)
        self.rects = []
        self.speed = 10

    def shoot(self):
        projectile_rect = self.frames[0].get_rect(center=(self.game.player.rect.centerx, self.game.player.rect.top))
        self.rects.append(projectile_rect)
        self.game.mixer.shooting_sound.play()

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.shoot()

    def update(self):
        for projectile in self.rects[:]:
            projectile.y -= self.speed
            if projectile.bottom < 0:
                self.rects.remove(projectile)

            for enemy_rect in self.game.enemy.rects:
                if enemy_rect.colliderect(projectile):
                    self.rects.remove(projectile)
                    self.game.enemy.rects.remove(enemy_rect)
                    self.game.score += 10

    def draw(self):
        for projectile in self.rects:
            self.game.screen.blit(self.frames[0], projectile)


class Background:
    def __init__(self, game: SpaceShooter):
        self.game = game
        self.image = pygame.image.load("assets/images/sky.png")
        self.rect1 = self.image.get_rect()
        self.rect2 = self.image.get_rect(topleft=(0, -self.rect1.height))
        self.speed = 1

    def update(self):
        self.rect1.y += self.speed
        self.rect2.y += self.speed
        if self.rect1.top >= self.rect1.height:
            self.rect1.y = -self.rect1.height
        if self.rect2.top >= self.rect2.height:
            self.rect2.y = -self.rect2.height

    def draw(self):
        self.game.screen.blit(self.image, self.rect1)
        self.game.screen.blit(self.image, self.rect2)


class Mixer:
    def __init__(self, game: SpaceShooter):
        self.game = game
        pygame.mixer.init()
        pygame.mixer.music.load("assets/music/music.mp3")
        self.shooting_sound = pygame.mixer.Sound("assets/sounds/shooting_sound.wav")
        pygame.mixer.music.play(-1)


class UI:
    def __init__(self, game: SpaceShooter):
        self.game = game
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

    def display_score_and_lives(self):
        score_text = self.font.render(f"Score: {self.game.score}", True, self.game.WHITE)
        lives_text = self.font.render(f"Lives: {self.game.lives}", True, self.game.WHITE)
        self.game.screen.blit(score_text, (10, 10))
        self.game.screen.blit(lives_text, (self.game.width - lives_text.get_width() - 10, 10))


if __name__ == '__main__':
    game = SpaceShooter(800, 600)
    game.run()
