"""
Modern Pong Game
A modernized version of the classic Pong game with multiple game modes,
AI difficulty levels, and visual effects.

Author: Claude AI Assistant
License: MIT
Requirements: Python 3.7+, Pygame 2.0+
"""

import pygame
import random
import math
import sys
from enum import Enum
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FPS = 60
BALL_SIZE = 15
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 8
BALL_SPEED_INITIAL = 6
BALL_SPEED_MAX = 15
BALL_SPEED_INCREMENT = 0.5
WINNING_SCORE = 7
GAME_TIME_LIMIT = 180  # 3 minutes in seconds

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
DARK_BLUE = (0, 0, 139)
NEON_GREEN = (57, 255, 20)
NEON_PINK = (255, 20, 147)

class GameState(Enum):
    """Enumeration for different game states"""
    SPLASH = 0
    MENU = 1
    MODE_SELECT = 2
    DIFFICULTY_SELECT = 3
    PLAYING = 4
    PAUSED = 5
    GAME_OVER = 6

class GameMode(Enum):
    """Enumeration for different game modes"""
    PVP = 1  # Player vs Player
    PVE = 2  # Player vs AI
    AVA = 3  # AI vs AI

class Difficulty(Enum):
    """Enumeration for AI difficulty levels"""
    EASY = 1
    MEDIUM = 2
    HARD = 3
    IMPOSSIBLE = 4

class Particle:
    """Particle class for visual effects"""
    def __init__(self, x, y, vx, vy, color, lifetime=30, size=3, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = gravity
        
    def update(self):
        """Update particle position and lifetime"""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        self.vx *= 0.98  # Friction
        self.vy *= 0.98
        
    def draw(self, screen):
        """Draw the particle with fading effect"""
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
            
            # Create a surface for the particle with per-pixel alpha
            particle_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*self.color, alpha), (size, size), size)
            screen.blit(particle_surf, (int(self.x - size), int(self.y - size)))
            
    def is_alive(self):
        """Check if particle is still active"""
        return self.lifetime > 0

class Star:
    """Background star for visual effect"""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.uniform(0.5, 2)
        self.speed = random.uniform(0.1, 0.5)
        self.brightness = random.randint(100, 255)
        self.twinkle_speed = random.uniform(0.01, 0.05)
        self.twinkle_phase = random.uniform(0, 2 * math.pi)
        
    def update(self):
        """Update star position and twinkle effect"""
        self.x -= self.speed
        if self.x < 0:
            self.x = SCREEN_WIDTH
            self.y = random.randint(0, SCREEN_HEIGHT)
            
        self.twinkle_phase += self.twinkle_speed
        
    def draw(self, screen):
        """Draw the star with twinkle effect"""
        twinkle = 0.7 + 0.3 * math.sin(self.twinkle_phase)
        brightness = int(self.brightness * twinkle)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))

class Ball:
    """Ball class with physics and collision detection"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = BALL_SPEED_INITIAL * random.choice([-1, 1])
        self.vy = random.uniform(-3, 3)
        self.speed = BALL_SPEED_INITIAL
        self.radius = BALL_SIZE // 2
        self.trail = []  # For trail effect
        self.max_trail_length = 20
        self.particles = []
        self.glow_radius = 20
        self.hit_effect = 0
        
    def update(self):
        """Update ball position and handle boundary collisions"""
        # Store position for trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
            
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Top and bottom boundary collision
        if self.y - self.radius <= 0 or self.y + self.radius >= SCREEN_HEIGHT:
            self.vy = -self.vy
            self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))
            self.create_impact_particles()
            self.hit_effect = 10
            
        # Update particles
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
            
        # Decrease hit effect
        if self.hit_effect > 0:
            self.hit_effect -= 1
    
    def create_impact_particles(self):
        """Create particle effects on impact"""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice([YELLOW, CYAN, WHITE, NEON_GREEN])
            self.particles.append(Particle(self.x, self.y, vx, vy, color, 25, random.uniform(2, 4)))
    
    def create_score_particles(self, x, y, color):
        """Create particle effects for scoring"""
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, vx, vy, color, 40, random.uniform(2, 5), 0.1))
    
    def check_paddle_collision(self, paddle):
        """Check and handle collision with a paddle"""
        # Simple rectangle-circle collision
        if (paddle.x <= self.x <= paddle.x + PADDLE_WIDTH and
            paddle.y <= self.y <= paddle.y + PADDLE_HEIGHT):
            
            # Calculate hit position relative to paddle center
            paddle_center = paddle.y + PADDLE_HEIGHT / 2
            hit_position = (self.y - paddle_center) / (PADDLE_HEIGHT / 2)
            
            # Reverse horizontal direction and add spin
            self.vx = -self.vx
            self.vy = hit_position * 5  # Add vertical velocity based on hit position
            
            # Increase speed slightly
            self.speed = min(self.speed + BALL_SPEED_INCREMENT, BALL_SPEED_MAX)
            
            # Normalize velocity to maintain speed
            magnitude = math.sqrt(self.vx ** 2 + self.vy ** 2)
            self.vx = (self.vx / magnitude) * self.speed
            self.vy = (self.vy / magnitude) * self.speed
            
            # Prevent ball from getting stuck in paddle
            if paddle.x < SCREEN_WIDTH / 2:
                self.x = paddle.x + PADDLE_WIDTH + self.radius
            else:
                self.x = paddle.x - self.radius
                
            # Create impact particles
            self.create_impact_particles()
            self.hit_effect = 15
            return True
        return False
    
    def reset(self):
        """Reset ball to center with random direction"""
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.vx = BALL_SPEED_INITIAL * random.choice([-1, 1])
        self.vy = random.uniform(-3, 3)
        self.speed = BALL_SPEED_INITIAL
        self.trail.clear()
        self.particles.clear()
        self.hit_effect = 0
    
    def draw(self, screen):
        """Draw the ball with trail and glow effect"""
        # Draw trail with gradient
        for i, pos in enumerate(self.trail):
            alpha = int(150 * (i / len(self.trail))) if self.trail else 150
            size = int(self.radius * (i / len(self.trail))) if self.trail else self.radius
            
            # Create a surface for the trail segment with per-pixel alpha
            trail_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*CYAN, alpha), (size, size), size)
            screen.blit(trail_surf, (int(pos[0] - size), int(pos[1] - size)))
        
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw glow effect
        glow_surf = pygame.Surface((self.glow_radius*2, self.glow_radius*2), pygame.SRCALPHA)
        for i in range(self.glow_radius, 0, -2):
            alpha = int(100 * (i / self.glow_radius))
            pygame.draw.circle(glow_surf, (*CYAN, alpha), (self.glow_radius, self.glow_radius), i)
        screen.blit(glow_surf, (int(self.x - self.glow_radius), int(self.y - self.glow_radius)))
        
        # Draw main ball with highlight
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        
        # Draw hit effect
        if self.hit_effect > 0:
            effect_radius = self.radius + self.hit_effect
            effect_alpha = int(200 * (self.hit_effect / 15))
            effect_surf = pygame.Surface((effect_radius*2, effect_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(effect_surf, (*WHITE, effect_alpha), (effect_radius, effect_radius), effect_radius)
            screen.blit(effect_surf, (int(self.x - effect_radius), int(self.y - effect_radius)))

class Paddle:
    """Paddle class with smooth movement and visual effects"""
    def __init__(self, x, y, color=WHITE):
        self.x = x
        self.y = y
        self.vy = 0
        self.color = color
        self.score = 0
        self.wins = 0
        self.glow_radius = 10
        self.hit_effect = 0
        
    def update(self):
        """Update paddle position with boundary checking"""
        self.y += self.vy
        self.y = max(0, min(SCREEN_HEIGHT - PADDLE_HEIGHT, self.y))
        
        # Decrease hit effect
        if self.hit_effect > 0:
            self.hit_effect -= 1
    
    def move_up(self):
        """Move paddle up"""
        self.vy = -PADDLE_SPEED
    
    def move_down(self):
        """Move paddle down"""
        self.vy = PADDLE_SPEED
    
    def stop(self):
        """Stop paddle movement"""
        self.vy = 0
    
    def hit(self):
        """Trigger hit effect"""
        self.hit_effect = 10
    
    def draw(self, screen):
        """Draw the paddle with gradient and glow effect"""
        # Draw glow effect
        if self.hit_effect > 0:
            glow_surf = pygame.Surface((PADDLE_WIDTH + self.glow_radius*2, 
                                       PADDLE_HEIGHT + self.glow_radius*2), pygame.SRCALPHA)
            for i in range(self.glow_radius, 0, -2):
                alpha = int(150 * (i / self.glow_radius) * (self.hit_effect / 10))
                pygame.draw.rect(glow_surf, (*self.color, alpha), 
                                (self.glow_radius - i, self.glow_radius - i, 
                                 PADDLE_WIDTH + i*2, PADDLE_HEIGHT + i*2), 
                                border_radius=5)
            screen.blit(glow_surf, (self.x - self.glow_radius, self.y - self.glow_radius))
        
        # Draw main paddle with gradient
        pygame.draw.rect(screen, self.color, 
                        (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT), border_radius=5)
        
        # Add highlight
        highlight_height = min(10, PADDLE_HEIGHT // 4)
        pygame.draw.rect(screen, WHITE,
                        (self.x + 2, self.y + 2, PADDLE_WIDTH - 4, highlight_height), border_radius=3)

class AIController:
    """AI Controller for computer-controlled paddles"""
    def __init__(self, paddle, difficulty=Difficulty.MEDIUM):
        self.paddle = paddle
        self.difficulty = difficulty
        self.reaction_time = self.get_reaction_time()
        self.error_margin = self.get_error_margin()
        self.prediction_depth = self.get_prediction_depth()
        self.last_update = 0
        self.color = PURPLE if difficulty == Difficulty.IMPOSSIBLE else GREEN
        
    def get_reaction_time(self):
        """Get reaction time based on difficulty"""
        times = {
            Difficulty.EASY: 15,
            Difficulty.MEDIUM: 8,
            Difficulty.HARD: 3,
            Difficulty.IMPOSSIBLE: 0
        }
        return times.get(self.difficulty, 8)
    
    def get_error_margin(self):
        """Get error margin based on difficulty"""
        margins = {
            Difficulty.EASY: 40,
            Difficulty.MEDIUM: 20,
            Difficulty.HARD: 10,
            Difficulty.IMPOSSIBLE: 0
        }
        return margins.get(self.difficulty, 20)
    
    def get_prediction_depth(self):
        """Get prediction depth based on difficulty"""
        depths = {
            Difficulty.EASY: 0,
            Difficulty.MEDIUM: 5,
            Difficulty.HARD: 10,
            Difficulty.IMPOSSIBLE: 20
        }
        return depths.get(self.difficulty, 5)
    
    def predict_ball_position(self, ball):
        """Predict where the ball will be"""
        # Simple prediction based on current velocity
        frames_ahead = self.prediction_depth
        predicted_y = ball.y + (ball.vy * frames_ahead)
        
        # Account for bouncing off walls
        if predicted_y < 0 or predicted_y > SCREEN_HEIGHT:
            predicted_y = ball.y
            
        return predicted_y
    
    def update(self, ball, frame_count):
        """Update AI paddle based on ball position"""
        # Add reaction delay
        if frame_count - self.last_update < self.reaction_time:
            return
            
        self.last_update = frame_count
        
        # Get target position
        if self.difficulty == Difficulty.IMPOSSIBLE:
            target_y = ball.y - PADDLE_HEIGHT // 2
        else:
            predicted_y = self.predict_ball_position(ball)
            target_y = predicted_y - PADDLE_HEIGHT // 2
            
        # Add error margin for easier difficulties
        if self.difficulty != Difficulty.IMPOSSIBLE:
            error = random.uniform(-self.error_margin, self.error_margin)
            target_y += error
        
        # Move paddle towards target
        paddle_center = self.paddle.y + PADDLE_HEIGHT // 2
        
        if abs(paddle_center - (target_y + PADDLE_HEIGHT // 2)) > 5:
            if paddle_center < target_y + PADDLE_HEIGHT // 2:
                self.paddle.move_down()
            else:
                self.paddle.move_up()
        else:
            self.paddle.stop()

class PongGame:
    """Main game class managing all game logic and states"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Modern Pong")
        self.clock = pygame.time.Clock()
        
        # Load custom fonts
        try:
            self.font_large = pygame.font.Font(None, 72)
            self.font_medium = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 36)
            self.font_tiny = pygame.font.Font(None, 24)
            # Add monospace font for timer
            self.font_mono = pygame.font.SysFont('Courier New', 36, bold=True)
        except:
            self.font_large = pygame.font.SysFont('Arial', 72, bold=True)
            self.font_medium = pygame.font.SysFont('Arial', 48, bold=True)
            self.font_small = pygame.font.SysFont('Arial', 36, bold=True)
            self.font_tiny = pygame.font.SysFont('Arial', 24)
            self.font_mono = pygame.font.SysFont('Courier New', 36, bold=True)
        
        # Game objects
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.paddle_left = Paddle(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, BLUE)
        self.paddle_right = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH, 
                                  SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, RED)
        
        # Game state
        self.state = GameState.SPLASH
        self.mode = None
        self.difficulty = Difficulty.MEDIUM
        self.ai_left = None
        self.ai_right = None
        self.running = True
        self.frame_count = 0
        self.game_timer = 0
        self.round_number = 1
        self.max_rounds = 3
        self.splash_timer = 180  # 3 seconds
        self.score_effect_timer = 0
        self.score_effect_side = None
        
        # Visual effects
        self.stars = [Star() for _ in range(100)]
        self.screen_flash = 0
        
    def draw_text_with_glow(self, text, font, color, glow_color, pos, center=True):
        """Draw text with a glow effect"""
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=pos) if center else text_surf.get_rect(topleft=pos)
        
        # Create glow effect
        glow_surf = pygame.Surface((text_rect.width + 20, text_rect.height + 20), pygame.SRCALPHA)
        for i in range(10, 0, -2):
            alpha = int(100 * (i / 10))
            glow_text = font.render(text, True, (*glow_color, alpha))
            glow_rect = glow_text.get_rect(center=(text_rect.width//2 + 10, text_rect.height//2 + 10))
            glow_surf.blit(glow_text, glow_rect)
        
        self.screen.blit(glow_surf, (text_rect.x - 10, text_rect.y - 10))
        self.screen.blit(text_surf, text_rect)
        
        return text_rect
    
    def draw_button(self, text, font, color, hover_color, pos, size, hover=False):
        """Draw a button with hover effect"""
        button_rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        
        # Draw button background
        button_color = hover_color if hover else color
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, button_rect, 2, border_radius=10)
        
        # Draw button text
        text_surf = font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)
        
        return button_rect
    
    def handle_menu_input(self, event):
        """Handle input in menu state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = GameState.MODE_SELECT
            elif event.key == pygame.K_ESCAPE:
                self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Start button
            start_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 60)
            if start_rect.collidepoint(mouse_pos):
                self.state = GameState.MODE_SELECT
            # Exit button
            exit_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 450, 200, 60)
            if exit_rect.collidepoint(mouse_pos):
                self.running = False
    
    def handle_mode_select_input(self, event):
        """Handle input in mode selection state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.mode = GameMode.PVP
                self.start_game()
            elif event.key == pygame.K_2:
                self.mode = GameMode.PVE
                self.state = GameState.DIFFICULTY_SELECT
            elif event.key == pygame.K_3:
                self.mode = GameMode.AVA
                self.state = GameState.DIFFICULTY_SELECT
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # PVP button
            pvp_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 250, 300, 60)
            if pvp_rect.collidepoint(mouse_pos):
                self.mode = GameMode.PVP
                self.start_game()
            # PVE button
            pve_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 320, 300, 60)
            if pve_rect.collidepoint(mouse_pos):
                self.mode = GameMode.PVE
                self.state = GameState.DIFFICULTY_SELECT
            # AVA button
            ava_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 390, 300, 60)
            if ava_rect.collidepoint(mouse_pos):
                self.mode = GameMode.AVA
                self.state = GameState.DIFFICULTY_SELECT
            # Back button
            back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 60)
            if back_rect.collidepoint(mouse_pos):
                self.state = GameState.MENU
    
    def handle_difficulty_select_input(self, event):
        """Handle input in difficulty selection state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.difficulty = Difficulty.EASY
                self.start_game()
            elif event.key == pygame.K_2:
                self.difficulty = Difficulty.MEDIUM
                self.start_game()
            elif event.key == pygame.K_3:
                self.difficulty = Difficulty.HARD
                self.start_game()
            elif event.key == pygame.K_4:
                self.difficulty = Difficulty.IMPOSSIBLE
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MODE_SELECT
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Easy button
            easy_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 220, 300, 60)
            if easy_rect.collidepoint(mouse_pos):
                self.difficulty = Difficulty.EASY
                self.start_game()
            # Medium button
            medium_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 290, 300, 60)
            if medium_rect.collidepoint(mouse_pos):
                self.difficulty = Difficulty.MEDIUM
                self.start_game()
            # Hard button
            hard_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 360, 300, 60)
            if hard_rect.collidepoint(mouse_pos):
                self.difficulty = Difficulty.HARD
                self.start_game()
            # Impossible button
            impossible_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 430, 300, 60)
            if impossible_rect.collidepoint(mouse_pos):
                self.difficulty = Difficulty.IMPOSSIBLE
                self.start_game()
            # Back button
            back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 520, 200, 60)
            if back_rect.collidepoint(mouse_pos):
                self.state = GameState.MODE_SELECT
    
    def start_game(self):
        """Initialize and start a new game"""
        self.state = GameState.PLAYING
        self.paddle_left.score = 0
        self.paddle_right.score = 0
        self.round_number = 1
        self.game_timer = 0
        self.ball.reset()
        self.score_effect_timer = 0
        self.score_effect_side = None
        
        # Set up AI controllers based on mode
        if self.mode == GameMode.PVE:
            self.ai_left = None
            self.ai_right = AIController(self.paddle_right, self.difficulty)
        elif self.mode == GameMode.AVA:
            self.ai_left = AIController(self.paddle_left, self.difficulty)
            self.ai_right = AIController(self.paddle_right, self.difficulty)
        else:
            self.ai_left = None
            self.ai_right = None
    
    def handle_game_input(self, event):
        """Handle input during gameplay"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                elif self.state == GameState.PAUSED:
                    self.state = GameState.PLAYING
            elif event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                self.start_game()
            elif event.key == pygame.K_m and self.state == GameState.GAME_OVER:
                self.state = GameState.MENU
        elif event.type == pygame.MOUSEBUTTONDOWN and self.state == GameState.GAME_OVER:
            mouse_pos = pygame.mouse.get_pos()
            # Restart button
            restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 430, 200, 60)
            if restart_rect.collidepoint(mouse_pos):
                self.start_game()
            # Menu button
            menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 60)
            if menu_rect.collidepoint(mouse_pos):
                self.state = GameState.MENU
    
    def update_game(self):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
        
        self.frame_count += 1
        self.game_timer += 1/FPS
        
        # Update ball
        self.ball.update()
        
        # Check paddle collisions
        if self.ball.check_paddle_collision(self.paddle_left):
            self.paddle_left.hit()
        if self.ball.check_paddle_collision(self.paddle_right):
            self.paddle_right.hit()
        
        # Check scoring
        if self.ball.x <= 0:
            self.paddle_right.score += 1
            self.ball.create_score_particles(50, SCREEN_HEIGHT // 2, RED)
            self.score_effect_timer = 30
            self.score_effect_side = "right"
            self.screen_flash = 10
            self.check_win_condition()
            self.ball.reset()
        elif self.ball.x >= SCREEN_WIDTH:
            self.paddle_left.score += 1
            self.ball.create_score_particles(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2, BLUE)
            self.score_effect_timer = 30
            self.score_effect_side = "left"
            self.screen_flash = 10
            self.check_win_condition()
            self.ball.reset()
        
        # Update paddles
        keys = pygame.key.get_pressed()
        
        # Player controls
        if not self.ai_left:
            if keys[pygame.K_w]:
                self.paddle_left.move_up()
            elif keys[pygame.K_s]:
                self.paddle_left.move_down()
            else:
                self.paddle_left.stop()
        
        if not self.ai_right:
            if keys[pygame.K_UP]:
                self.paddle_right.move_up()
            elif keys[pygame.K_DOWN]:
                self.paddle_right.move_down()
            else:
                self.paddle_right.stop()
        
        # Update AI controllers
        if self.ai_left:
            self.ai_left.update(self.ball, self.frame_count)
        if self.ai_right:
            self.ai_right.update(self.ball, self.frame_count)
        
        # Update paddles
        self.paddle_left.update()
        self.paddle_right.update()
        
        # Update stars
        for star in self.stars:
            star.update()
        
        # Update score effect timer
        if self.score_effect_timer > 0:
            self.score_effect_timer -= 1
        
        # Update screen flash
        if self.screen_flash > 0:
            self.screen_flash -= 1
    
    def check_win_condition(self):
        """Check if someone has won the game"""
        if self.paddle_left.score >= WINNING_SCORE:
            self.paddle_left.wins += 1
            self.end_round("Player 1" if not self.ai_left else "AI Left")
        elif self.paddle_right.score >= WINNING_SCORE:
            self.paddle_right.wins += 1
            self.end_round("Player 2" if not self.ai_right else "AI Right")
        elif self.game_timer >= GAME_TIME_LIMIT:
            if self.paddle_left.score > self.paddle_right.score:
                self.paddle_left.wins += 1
                self.end_round("Player 1" if not self.ai_left else "AI Left")
            elif self.paddle_right.score > self.paddle_left.score:
                self.paddle_right.wins += 1
                self.end_round("Player 2" if not self.ai_right else "AI Right")
            else:
                self.end_round("Draw")
    
    def end_round(self, winner):
        """End the current round"""
        if self.round_number >= self.max_rounds:
            self.state = GameState.GAME_OVER
        else:
            self.round_number += 1
            self.paddle_left.score = 0
            self.paddle_right.score = 0
            self.game_timer = 0
            self.ball.reset()
    
    def draw_splash(self):
        """Draw the splash screen"""
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Draw logo
        self.draw_text_with_glow("MODERN PONG", self.font_large, WHITE, CYAN, 
                                (SCREEN_WIDTH // 2, 200))
        
        # Draw loading bar
        bar_width = 400
        bar_height = 20
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = 400
        
        # Background
        pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=10)
        
        # Progress
        progress = (180 - self.splash_timer) / 180
        progress_width = int(bar_width * progress)
        progress_color = (
            int(255 * progress),
            int(255 * (1 - progress)),
            0
        )
        pygame.draw.rect(self.screen, progress_color, 
                        (bar_x, bar_y, progress_width, bar_height), border_radius=10)
        
        # Loading text
        loading_text = "LOADING..." if self.splash_timer > 30 else "PRESS ANY KEY"
        self.draw_text_with_glow(loading_text, self.font_small, WHITE, CYAN, 
                                (SCREEN_WIDTH // 2, 450))
        
        # Update splash timer
        self.splash_timer -= 1
        if self.splash_timer <= 0:
            self.state = GameState.MENU
    
    def draw_menu(self):
        """Draw the main menu"""
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Title
        self.draw_text_with_glow("MODERN PONG", self.font_large, WHITE, CYAN, 
                                (SCREEN_WIDTH // 2, 150))
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Start button
        start_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 350, 200, 60)
        start_hover = start_rect.collidepoint(mouse_pos)
        self.draw_button("START", self.font_medium, DARK_BLUE, BLUE, 
                        (SCREEN_WIDTH//2 - 100, 350), (200, 60), start_hover)
        
        # Exit button
        exit_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 450, 200, 60)
        exit_hover = exit_rect.collidepoint(mouse_pos)
        self.draw_button("EXIT", self.font_medium, (139, 0, 0), RED, 
                        (SCREEN_WIDTH//2 - 100, 450), (200, 60), exit_hover)
        
        # Credits
        credit_text = "Created with Python & Pygame"
        credit_surf = self.font_tiny.render(credit_text, True, GRAY)
        credit_rect = credit_surf.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(credit_surf, credit_rect)
    
    def draw_mode_select(self):
        """Draw mode selection screen"""
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Title
        self.draw_text_with_glow("SELECT GAME MODE", self.font_large, WHITE, CYAN, 
                                (SCREEN_WIDTH // 2, 100))
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Mode options - increased button width to accommodate text
        pvp_rect = pygame.Rect(SCREEN_WIDTH//2 - 180, 250, 360, 60)
        pvp_hover = pvp_rect.collidepoint(mouse_pos)
        self.draw_button("PLAYER VS PLAYER", self.font_medium, BLUE, NEON_GREEN, 
                        (SCREEN_WIDTH//2 - 180, 250), (360, 60), pvp_hover)
        
        pve_rect = pygame.Rect(SCREEN_WIDTH//2 - 180, 320, 360, 60)
        pve_hover = pve_rect.collidepoint(mouse_pos)
        self.draw_button("PLAYER VS AI", self.font_medium, GREEN, NEON_GREEN, 
                        (SCREEN_WIDTH//2 - 180, 320), (360, 60), pve_hover)
        
        ava_rect = pygame.Rect(SCREEN_WIDTH//2 - 180, 390, 360, 60)
        ava_hover = ava_rect.collidepoint(mouse_pos)
        self.draw_button("AI VS AI", self.font_medium, PURPLE, NEON_PINK, 
                        (SCREEN_WIDTH//2 - 180, 390), (360, 60), ava_hover)
        
        # Back button
        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 60)
        back_hover = back_rect.collidepoint(mouse_pos)
        self.draw_button("BACK", self.font_medium, GRAY, LIGHT_GRAY, 
                        (SCREEN_WIDTH//2 - 100, 500), (200, 60), back_hover)
    
    def draw_difficulty_select(self):
        """Draw difficulty selection screen"""
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Title
        self.draw_text_with_glow("SELECT DIFFICULTY", self.font_large, WHITE, CYAN, 
                                (SCREEN_WIDTH // 2, 100))
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Difficulty options - increased button width to accommodate text
        easy_rect = pygame.Rect(SCREEN_WIDTH//2 - 180, 220, 360, 60)
        easy_hover = easy_rect.collidepoint(mouse_pos)
        self.draw_button("EASY", self.font_medium, GREEN, NEON_GREEN, 
                        (SCREEN_WIDTH//2 - 180, 220), (360, 60), easy_hover)
        
        medium_rect = pygame.Rect(SCREEN_WIDTH//2 - 180, 290, 360, 60)
        medium_hover = medium_rect.collidepoint(mouse_pos)
        self.draw_button("MEDIUM", self.font_medium, YELLOW, GOLD, 
                        (SCREEN_WIDTH//2 - 180, 290), (360, 60), medium_hover)
        
        hard_rect = pygame.Rect(SCREEN_WIDTH//2 - 180, 360, 360, 60)
        hard_hover = hard_rect.collidepoint(mouse_pos)
        self.draw_button("HARD", self.font_medium, (255, 128, 0), RED, 
                        (SCREEN_WIDTH//2 - 180, 360), (360, 60), hard_hover)
        
        impossible_rect = pygame.Rect(SCREEN_WIDTH//2 - 180, 430, 360, 60)
        impossible_hover = impossible_rect.collidepoint(mouse_pos)
        self.draw_button("IMPOSSIBLE", self.font_medium, PURPLE, NEON_PINK, 
                        (SCREEN_WIDTH//2 - 180, 430), (360, 60), impossible_hover)
        
        # Back button
        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 520, 200, 60)
        back_hover = back_rect.collidepoint(mouse_pos)
        self.draw_button("BACK", self.font_medium, GRAY, LIGHT_GRAY, 
                        (SCREEN_WIDTH//2 - 100, 520), (200, 60), back_hover)
    
    def draw_game(self):
        """Draw the game screen"""
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Draw screen flash effect
        if self.screen_flash > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(100 * (self.screen_flash / 10))
            flash_surf.fill((255, 255, 255, alpha))
            self.screen.blit(flash_surf, (0, 0))
        
        # Draw center line with glow
        for y in range(0, SCREEN_HEIGHT, 20):
            line_surf = pygame.Surface((4, 10), pygame.SRCALPHA)
            pygame.draw.rect(line_surf, (*WHITE, 150), (0, 0, 4, 10))
            self.screen.blit(line_surf, (SCREEN_WIDTH // 2 - 2, y))
        
        # Draw scores with glow
        score_left = self.font_large.render(str(self.paddle_left.score), True, WHITE)
        score_right = self.font_large.render(str(self.paddle_right.score), True, WHITE)
        
        # Left score
        left_score_rect = score_left.get_rect(center=(SCREEN_WIDTH // 4, 80))
        self.draw_text_with_glow(str(self.paddle_left.score), self.font_large, 
                                BLUE, CYAN, (SCREEN_WIDTH // 4, 80))
        
        # Right score
        self.draw_text_with_glow(str(self.paddle_right.score), self.font_large, 
                                RED, YELLOW, (3 * SCREEN_WIDTH // 4, 80))
        
        # Draw timer with color based on remaining time
        time_remaining = max(0, GAME_TIME_LIMIT - int(self.game_timer))
        minutes = time_remaining // 60
        seconds = time_remaining % 60
        
        # Change color when time is running out
        if time_remaining < 30:
            timer_color = RED
            glow_color = YELLOW
        elif time_remaining < 60:
            timer_color = YELLOW
            glow_color = RED
        else:
            timer_color = WHITE
            glow_color = CYAN
            
        # Fixed timer formatting to ensure consistent width
        timer_text = f"{minutes:02d}:{seconds:02d}"
        timer_surf = self.font_mono.render(timer_text, True, timer_color)
        timer_rect = timer_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        
        # Draw timer with glow effect
        glow_surf = pygame.Surface((timer_rect.width + 20, timer_rect.height + 20), pygame.SRCALPHA)
        for i in range(10, 0, -2):
            alpha = int(100 * (i / 10))
            glow_text = self.font_mono.render(timer_text, True, (*glow_color, alpha))
            glow_rect = glow_text.get_rect(center=(timer_rect.width//2 + 10, timer_rect.height//2 + 10))
            glow_surf.blit(glow_text, glow_rect)
        
        self.screen.blit(glow_surf, (timer_rect.x - 10, timer_rect.y - 10))
        self.screen.blit(timer_surf, timer_rect)
        
        # Draw round info
        self.draw_text_with_glow(f"ROUND {self.round_number}/{self.max_rounds}", 
                                self.font_small, CYAN, WHITE, (SCREEN_WIDTH // 2, 60))
        
        # Draw score effect
        if self.score_effect_timer > 0 and self.score_effect_side:
            effect_text = "SCORE!"
            effect_color = BLUE if self.score_effect_side == "left" else RED
            effect_glow = CYAN if self.score_effect_side == "left" else YELLOW
            
            if self.score_effect_side == "left":
                effect_pos = (SCREEN_WIDTH // 4, 150)
            else:
                effect_pos = (3 * SCREEN_WIDTH // 4, 150)
                
            # Pulsing effect
            scale = 1.0 + 0.2 * math.sin(self.score_effect_timer * 0.5)
            self.draw_text_with_glow(effect_text, self.font_medium, 
                                    effect_color, effect_glow, effect_pos)
        
        # Draw game objects
        self.paddle_left.draw(self.screen)
        self.paddle_right.draw(self.screen)
        self.ball.draw(self.screen)
        
        # Draw controls hint
        if not self.ai_left:
            controls_left = self.font_tiny.render("W/S", True, GRAY)
            self.screen.blit(controls_left, (10, SCREEN_HEIGHT - 30))
        if not self.ai_right:
            controls_right = self.font_tiny.render("↑/↓", True, GRAY)
            self.screen.blit(controls_right, (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 30))
        
        # Draw difficulty indicator for AI games
        if self.mode == GameMode.PVE or self.mode == GameMode.AVA:
            diff_text = f"AI: {self.difficulty.name}"
            diff_color = {
                Difficulty.EASY: GREEN,
                Difficulty.MEDIUM: YELLOW,
                Difficulty.HARD: (255, 128, 0),
                Difficulty.IMPOSSIBLE: PURPLE
            }.get(self.difficulty, WHITE)
            
            diff_surf = self.font_tiny.render(diff_text, True, diff_color)
            diff_rect = diff_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
            self.screen.blit(diff_surf, diff_rect)
    
    def draw_paused(self):
        """Draw pause overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        self.draw_text_with_glow("PAUSED", self.font_large, WHITE, CYAN, 
                                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        # Resume instruction
        self.draw_text_with_glow("Press ESC to Resume", self.font_small, 
                                LIGHT_GRAY, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Determine winner
        if self.paddle_left.wins > self.paddle_right.wins:
            winner = "Player 1" if not self.ai_left else "AI Left"
            color = BLUE
            glow_color = CYAN
        elif self.paddle_right.wins > self.paddle_left.wins:
            winner = "Player 2" if not self.ai_right else "AI Right"
            color = RED
            glow_color = YELLOW
        else:
            winner = "Draw"
            color = YELLOW
            glow_color = GOLD
        
        # Game over text
        self.draw_text_with_glow("GAME OVER", self.font_large, WHITE, CYAN, 
                                (SCREEN_WIDTH // 2, 150))
        
        # Winner text
        if winner != "Draw":
            winner_text = f"{winner} WINS!"
        else:
            winner_text = "IT'S A DRAW!"
            
        self.draw_text_with_glow(winner_text, self.font_medium, 
                                color, glow_color, (SCREEN_WIDTH // 2, 250))
        
        # Final scores
        final_score = self.font_medium.render(
            f"{self.paddle_left.wins} - {self.paddle_right.wins}", 
            True, WHITE
        )
        score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, 330))
        self.screen.blit(final_score, score_rect)
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Restart button
        restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 430, 200, 60)
        restart_hover = restart_rect.collidepoint(mouse_pos)
        self.draw_button("RESTART", self.font_medium, GREEN, NEON_GREEN, 
                        (SCREEN_WIDTH//2 - 100, 430), (200, 60), restart_hover)
        
        # Menu button
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 500, 200, 60)
        menu_hover = menu_rect.collidepoint(mouse_pos)
        self.draw_button("MENU", self.font_medium, DARK_BLUE, BLUE, 
                        (SCREEN_WIDTH//2 - 100, 500), (200, 60), menu_hover)
    
    def draw(self):
        """Main draw method routing to appropriate screen"""
        if self.state == GameState.SPLASH:
            self.draw_splash()
        elif self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.MODE_SELECT:
            self.draw_mode_select()
        elif self.state == GameState.DIFFICULTY_SELECT:
            self.draw_difficulty_select()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_paused()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.state == GameState.SPLASH:
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        if self.splash_timer <= 30:
                            self.state = GameState.MENU
                elif self.state == GameState.MENU:
                    self.handle_menu_input(event)
                elif self.state == GameState.MODE_SELECT:
                    self.handle_mode_select_input(event)
                elif self.state == GameState.DIFFICULTY_SELECT:
                    self.handle_difficulty_select_input(event)
                else:
                    self.handle_game_input(event)
            
            # Update game logic
            self.update_game()
            
            # Draw everything
            self.draw()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # Cleanup
        pygame.quit()
        sys.exit()

def main():
    """Main entry point for the game"""
    try:
        game = PongGame()
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()