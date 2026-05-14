import math
import random
import sys
from dataclasses import dataclass

import pygame

# ------------------------------------------------------------
# Dungeon Dodge
# Kleines 2D-Arcade-Spiel als Game-Development-Arbeitsprobe.
# ------------------------------------------------------------

WIDTH = 900
HEIGHT = 600
FPS = 60

PLAYER_SIZE = 34
COIN_SIZE = 22
ENEMY_SIZE = 30

BACKGROUND_COLOR = (24, 24, 32)
PLAYER_COLOR = (80, 180, 255)
COIN_COLOR = (255, 210, 80)
ENEMY_COLOR = (240, 80, 90)
TEXT_COLOR = (240, 240, 245)
GRID_COLOR = (35, 35, 48)


@dataclass
class Player:
    rect: pygame.Rect
    speed: int = 5

    def move(self, keys: pygame.key.ScancodeWrapper) -> None:
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed

        # Diagonale Bewegung normalisieren, damit sie nicht schneller ist.
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.rect.x += int(dx)
        self.rect.y += int(dy)
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))


@dataclass
class Enemy:
    rect: pygame.Rect
    speed: float

    def update(self, player_rect: pygame.Rect) -> None:
        # Einfaches Gegnerverhalten: Gegner verfolgt den Spieler.
        enemy_center = pygame.Vector2(self.rect.center)
        player_center = pygame.Vector2(player_rect.center)
        direction = player_center - enemy_center

        if direction.length() > 0:
            direction = direction.normalize()
            self.rect.x += int(direction.x * self.speed)
            self.rect.y += int(direction.y * self.speed)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Dungeon Dodge")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 26)
        self.big_font = pygame.font.SysFont("arial", 56, bold=True)
        self.reset()

    def reset(self) -> None:
        self.player = Player(
            pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
        )
        self.coin = self.spawn_rect(COIN_SIZE)
        self.enemies: list[Enemy] = []
        self.score = 0
        self.level = 1
        self.game_over = False
        self.spawn_enemy()

    def spawn_rect(self, size: int) -> pygame.Rect:
        margin = 40
        return pygame.Rect(
            random.randint(margin, WIDTH - size - margin),
            random.randint(margin, HEIGHT - size - margin),
            size,
            size,
        )

    def spawn_enemy(self) -> None:
        # Gegner erscheinen am Rand, damit der Start fair bleibt.
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x, y = random.randint(0, WIDTH - ENEMY_SIZE), 0
        elif side == "bottom":
            x, y = random.randint(0, WIDTH - ENEMY_SIZE), HEIGHT - ENEMY_SIZE
        elif side == "left":
            x, y = 0, random.randint(0, HEIGHT - ENEMY_SIZE)
        else:
            x, y = WIDTH - ENEMY_SIZE, random.randint(0, HEIGHT - ENEMY_SIZE)

        speed = 2.0 + self.level * 0.25
        self.enemies.append(Enemy(pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE), speed))

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.game_over and event.key == pygame.K_r:
                    self.reset()

    def update(self) -> None:
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys)

        for enemy in self.enemies:
            enemy.update(self.player.rect)
            if enemy.rect.colliderect(self.player.rect):
                self.game_over = True

        if self.player.rect.colliderect(self.coin):
            self.score += 1
            self.coin = self.spawn_rect(COIN_SIZE)

            # Alle 5 Münzen steigt das Level und ein neuer Gegner kommt dazu.
            if self.score % 5 == 0:
                self.level += 1
                self.spawn_enemy()

    def draw_grid(self) -> None:
        for x in range(0, WIDTH, 40):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WIDTH, y))

    def draw_text(self, text: str, font: pygame.font.Font, x: int, y: int) -> None:
        surface = font.render(text, True, TEXT_COLOR)
        self.screen.blit(surface, (x, y))

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_grid()

        pygame.draw.rect(self.screen, COIN_COLOR, self.coin, border_radius=8)
        pygame.draw.rect(self.screen, PLAYER_COLOR, self.player.rect, border_radius=8)

        for enemy in self.enemies:
            pygame.draw.rect(self.screen, ENEMY_COLOR, enemy.rect, border_radius=8)

        self.draw_text(f"Score: {self.score}", self.font, 20, 16)
        self.draw_text(f"Level: {self.level}", self.font, 20, 46)

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.screen.blit(overlay, (0, 0))

            title = self.big_font.render("GAME OVER", True, TEXT_COLOR)
            info = self.font.render("Drücke R zum Neustart oder ESC zum Beenden", True, TEXT_COLOR)
            final_score = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)

            self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))
            self.screen.blit(final_score, final_score.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            self.screen.blit(info, info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

        pygame.display.flip()

    def run(self) -> None:
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()


if __name__ == "__main__":
    Game().run()
