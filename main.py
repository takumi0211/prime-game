import pygame
import sys
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Prime Factorization Game")

# Colors
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
BLUE = (70, 130, 180)
BUTTON_COLOR = (60, 179, 113)
BUTTON_HOVER_COLOR = (32, 178, 170)

# Fonts
FONT = pygame.font.SysFont("arial", 32, bold=True)
LARGE_FONT = pygame.font.SysFont("arial", 72, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 24)

# Clock
CLOCK = pygame.time.Clock()
FPS = 30

# Prime numbers to use for factorization
PRIMES = [2, 3, 5, 7, 11]

# Game settings
INITIAL_TIME = 60  # 60 seconds time limit

# Button Class
class Button:
    def __init__(self, x, y, width, height, text, callback, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)  # Rounded corners
        text_surf = FONT.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

# GameManager Class
class GameManager:
    def __init__(self):
        self.current_number = self.generate_valid_number()
        self.internal_number = self.current_number  # Track the number internally
        self.feedback = ""
        self.show_next_button = False
        self.start_time = time.time()
        self.time_remaining = INITIAL_TIME
        self.score = 0  # Initialize the score
        self.last_interaction_time = time.time()  # To track last interaction time
        self.game_over = False  # Flag to indicate the game is over
        self.game_over_time = None  # Time when the game ended

        # コンボ関連の属性を追加
        self.combo = 0  # 現在のコンボ数
        self.combo_multiplier = 1  # コンボによるスコア倍率
        self.combo_bonus = 0  # コンボボーナスのスコア

        # Create prime number buttons
        self.prime_buttons = [
            Button(50 + i * 130, 300, 100, 50, str(prime), lambda p=prime: self.divide_number(p))
            for i, prime in enumerate(PRIMES)
        ]

    def generate_valid_number(self):
        # Generate a valid number that is divisible by one of the primes 1-11 and between 100 and 5000
        while True:
            selected_primes = random.choices(PRIMES, k=random.randint(2, 5))  # Choose between 2 and 5 primes
            number = math.prod(selected_primes)
            if 100 <= number <= 5000:
                return number

    def divide_number(self, prime):
        if self.game_over:
            return  # Do nothing if the game is already over

        if self.internal_number % prime == 0:
            self.internal_number //= prime
            self.feedback = f"Divided by {prime}!"
            self.score += prime  # Add the prime value to the score

            # コンボを増加
            self.combo += 1
            self.combo_multiplier = 1 + (self.combo // 5) * 0.5  # 5コンボごとに50%ボーナス
            self.combo_bonus = int(prime * (self.combo // 5) * 0.5)  # ボーナススコアの計算
            self.score += self.combo_bonus  # ボーナスをスコアに追加

            self.feedback += f" Combo x{self.combo_multiplier}!"
            self.last_interaction_time = time.time()  # Reset interaction timer

            if self.internal_number == 1:
                self.feedback = "Correct! You fully factorized the number!"
                self.show_next_button = True
        else:
            self.feedback = f"Cannot divide by {prime}. Try another number."
            self.time_remaining -= 3  # Penalty for incorrect answer

            # コンボをリセット
            self.combo = 0
            self.combo_multiplier = 1
            self.combo_bonus = 0

    def load_next_level(self):
        self.current_number = self.generate_valid_number()
        self.internal_number = self.current_number  # Reset internal number
        self.feedback = ""
        self.show_next_button = False
        self.start_time = time.time()  # Reset the start time for the new question

    def draw(self, surface):
        if self.game_over:
            # Display the final score in large text
            self.draw_final_score(surface)
            return

        # Draw number
        number_text = FONT.render(f"Number to factorize: {self.current_number}", True, BLACK)
        surface.blit(number_text, (250, 150))

        # Draw prime number buttons
        for button in self.prime_buttons:
            button.draw(surface)

        # Draw feedback
        feedback_color = GREEN if "Correct" in self.feedback else RED
        feedback_text = SMALL_FONT.render(self.feedback, True, feedback_color)
        surface.blit(feedback_text, (250, 250))

        # Draw score
        score_text = SMALL_FONT.render(f"Score: {self.score}", True, BLACK)
        surface.blit(score_text, (10, 50))

        # Draw combo
        combo_text = SMALL_FONT.render(f"Combo: {self.combo}", True, BLUE)
        surface.blit(combo_text, (10, 80))

        # Draw time progress bar and remaining time
        self.draw_time_bar(surface)
        self.draw_time_text(surface)

    def draw_final_score(self, surface):
        # Draw the final score in large text in the center of the screen
        final_score_text = LARGE_FONT.render(f"Final Score: {self.score}", True, BLACK)
        text_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(final_score_text, text_rect)

    def draw_time_bar(self, surface):
        # Determine bar width based on time remaining
        bar_width = int((self.time_remaining / INITIAL_TIME) * SCREEN_WIDTH)
        bar_height = 20
        bar_x = 0
        bar_y = 10

        # Calculate color based on time remaining (Green to Red gradient)
        red = min(255, int(255 * (1 - self.time_remaining / INITIAL_TIME)))
        green = min(255, int(255 * (self.time_remaining / INITIAL_TIME)))
        color = (red, green, 0)

        # Draw the progress bar
        pygame.draw.rect(surface, color, (bar_x, bar_y, bar_width, bar_height), border_radius=10)

    def draw_time_text(self, surface):
        # Draw the remaining time text below the progress bar
        time_text = FONT.render(f"Time Remaining: {int(self.time_remaining)}s", True, BLACK)
        surface.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 40))

    def handle_event(self, event):
        if self.game_over:
            return  # Ignore events if the game is over

        if not self.show_next_button:  # Only allow button presses if not awaiting next level
            for button in self.prime_buttons:
                button.handle_event(event)

    def update(self):
        if self.game_over:
            # If the game is over, wait for 5 seconds before closing
            if time.time() - self.game_over_time >= 5:
                pygame.quit()
                sys.exit()
            return

        # Update the remaining time
        self.time_remaining -= 1 / FPS
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.feedback = "Time's up! Game Over!"
            self.game_over = True
            self.game_over_time = time.time()
            return

        # Update the screen with the internal number if 2 seconds have passed since the last interaction
        if time.time() - self.last_interaction_time >= 2:
            self.current_number = self.internal_number
            self.last_interaction_time = time.time()  # Reset interaction time to avoid multiple updates

        # Automatically move to the next question if factorization is complete
        if self.show_next_button:
            self.load_next_level()

# Main Game Loop
def main():
    game_manager = GameManager()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game_manager.handle_event(event)

        # Update game state
        game_manager.update()

        # Fill the screen with background color
        SCREEN.fill(WHITE)

        # Draw game elements
        game_manager.draw(SCREEN)

        # Update the display
        pygame.display.flip()

        # Tick the clock
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()
