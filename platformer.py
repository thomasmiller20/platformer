import pygame
from pygame.locals import *
import sys

# Initialize Pygame
pygame.init()
vec = pygame.math.Vector2  # 2D vector for position, velocity, etc.

# Game constants
HEIGHT = 450
WIDTH = 400
ACC = 0.5        # Acceleration
FRIC = -0.12     # Friction
FPS = 60         # Frames per second
JUMP_VELOCITY = -10  # Jump force (negative because we move up)


# Set up the clock
FramePerSec = pygame.time.Clock()

# Create the display window
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((30, 30))
        self.surf.fill((128, 255, 40))  # Green color for the player
        self.rect = self.surf.get_rect()
        
        # Position, velocity, and acceleration
        self.pos = vec(10, 385)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def move(self):
        self.acc = vec(0, 0.5)  # Gravity effect
        
        # Get the pressed keys
        pressed_keys = pygame.key.get_pressed()
        
        # Movement controls
        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC
        if pressed_keys[K_SPACE] and self.pos.y == HEIGHT - self.rect.height:  # Check if on the ground
            self.vel.y = JUMP_VELOCITY
        
        # Apply friction to horizontal movement
        self.acc.x += self.vel.x * FRIC
        
        # Update velocity and position based on acceleration
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc  # Simplified physics equation
        
        # Ensure the player stays within the screen bounds
        if self.pos.x > WIDTH - self.rect.width:  # Right boundary
            self.pos.x = WIDTH - self.rect.width
        if self.pos.x < 0:  # Left boundary
            self.pos.x = 0

        # Ensure the player doesn't go below the platform
        if self.pos.y > HEIGHT - self.rect.height:  # Bottom boundary
            self.pos.y = HEIGHT - self.rect.height
            self.vel.y = 0  # Stop falling when on the ground

        # Update the rect object for drawing the player
        self.rect.midbottom = self.pos


class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill((255, 0, 0))  # Red color for the platform
        self.rect = self.surf.get_rect(center=(WIDTH / 2, HEIGHT - 10))


# Create the platform and player instances
PT1 = Platform()
P1 = Player()

# Create sprite groups for easy management
all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Move the player
    P1.move()

    # Update the display
    displaysurface.fill((0, 0, 0))  # Clear the screen with black color

    # Draw all sprites
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)

    # Update the display window
    pygame.display.update()

    # Set the frame rate
    FramePerSec.tick(FPS)
