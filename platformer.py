import pygame
from pygame.locals import *
import sys
import random

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

        # State to handle grace period
        self.grace_period = 0

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

        # If in grace period, don't check for boundary collision or game over
        if self.grace_period > 0:
            self.grace_period -= 1  # Countdown to end grace period

        # Check for left and right screen boundaries, teleport if at boundary
        if self.pos.x >= WIDTH - self.rect.width:  # Right boundary
            if self.grace_period <= 0:
                self.teleport_to_random_room()

        if self.pos.x <= 0:  # Left boundary
            if self.grace_period <= 0:
                self.teleport_to_random_room()

        # Ensure the player doesn't go below the platform
        if self.pos.y > HEIGHT - self.rect.height:  # Bottom boundary
            self.pos.y = HEIGHT - self.rect.height
            self.vel.y = 0  # Stop falling when on the ground

        # Update the rect object for drawing the player
        self.rect.midbottom = self.pos

    def teleport_to_random_room(self):
        """Teleports the player to a random location and creates new platforms and enemies."""
        new_x = random.randint(0, WIDTH - self.rect.width)  # Random horizontal position
        self.pos.x = new_x  # Teleport the player to a random x-coordinate
        self.pos.y = HEIGHT - self.rect.height  # Keep the y-coordinate at the bottom

        # Reset the grace period
        self.grace_period = 60  # Give the player 1 second of immunity

        # Clear the previous platforms and enemies and generate new ones
        generate_platforms_and_enemies()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((30, 30))
        self.surf.fill((255, 255, 40))  # Yellow color for the enemy
        self.rect = self.surf.get_rect()

        # Random initial position for the enemy
        self.pos = vec(random.randint(50, WIDTH - 50), random.randint(100, HEIGHT - 50))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        # Movement direction (1 for right, -1 for left)
        self.direction = 1

    def move(self):
        self.acc = vec(0, 0.5)  # Gravity effect

        # Automatic movement logic (left and right)
        self.acc.x = ACC * self.direction  # Move in the current direction

        # Jumping logic: make the enemy jump at random intervals
        if self.pos.y == HEIGHT - self.rect.height and random.random() < 0.01:  # Small chance to jump
            self.vel.y = JUMP_VELOCITY

        # Apply friction to horizontal movement
        self.acc.x += self.vel.x * FRIC

        # Update velocity and position based on acceleration
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc  # Simplified physics equation

        # Ensure the enemy stays within the screen bounds
        if self.pos.x > WIDTH - self.rect.width:  # Right boundary
            self.pos.x = WIDTH - self.rect.width
            self.direction = -1  # Reverse direction to move left
        if self.pos.x < 0:  # Left boundary
            self.pos.x = 0
            self.direction = 1  # Reverse direction to move right

        # Ensure the enemy doesn't go below the platform
        if self.pos.y > HEIGHT - self.rect.height:  # Bottom boundary
            self.pos.y = HEIGHT - self.rect.height
            self.vel.y = 0  # Stop falling when on the ground

        # Update the rect object for drawing the enemy
        self.rect.midbottom = self.pos


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.surf = pygame.Surface((random.randint(50, 150), 20))  # Random platform width
        self.surf.fill("red")  # Red color for the platform
        self.rect = self.surf.get_rect(center=(x, y))


# Create the platform, player, and enemy instances
PT1 = Platform(WIDTH / 2, HEIGHT - 10)
P1 = Player()
E1 = Enemy()

# Create sprite groups for easy management
all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)
all_sprites.add(E1)

# Function to generate random platforms and enemies
def generate_platforms_and_enemies():
    global all_sprites
    # Remove previous platforms and enemies
    for sprite in all_sprites:
        if isinstance(sprite, Platform) or isinstance(sprite, Enemy):
            sprite.kill()

    # Random number of platforms (between 3 and 5)
    num_platforms = random.randint(3, 5)
    platform_positions = []
    
    # Generate random platforms with enough space for the player to land
    for _ in range(num_platforms):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(100, HEIGHT - 100)  # Avoid placing platforms too close to the edges
        platform_positions.append((x, y))
        new_platform = Platform(x, y)
        all_sprites.add(new_platform)

    # Random number of enemies (between 2 and 4)
    num_enemies = random.randint(2, 4)
    for _ in range(num_enemies):
        # Ensure enemies are placed on or above the platforms
        x = random.choice(platform_positions)[0]  # Position enemy on a platform
        y = random.randint(100, HEIGHT - 50)  # Slightly above the platform
        new_enemy = Enemy()
        new_enemy.pos = vec(x, y)
        all_sprites.add(new_enemy)


# Game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Move the player
    P1.move()

    # Move all enemies
    for enemy in all_sprites:
        if isinstance(enemy, Enemy):
            enemy.move()

    # Check for collisions between player and enemies, only if outside grace period
    if P1.grace_period <= 0:
        for enemy in all_sprites:
            if isinstance(enemy, Enemy):
                if pygame.sprite.collide_rect(P1, enemy):
                    print("Game Over!")
                    pygame.quit()
                    sys.exit()

    # Update the display
    displaysurface.fill((0, 0, 0))  # Clear the screen with black color

    # Draw all sprites
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)

    # Update the display window
    pygame.display.update()

    # Set the frame rate
    FramePerSec.tick(FPS)
