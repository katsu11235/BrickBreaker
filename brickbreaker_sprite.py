import pygame
import sys
import pygame_menu
from pygame.locals import *
import pygame.gfxdraw
import math

# Colors  
white = (255, 255, 255)
purple = (91, 44, 111)
turquoise = (3, 155, 229)
red = (255, 0, 0)
yellow = (255, 255, 0)
shadow_color = (50, 50, 50)
green = (199, 237, 204)
outline_color = (0, 0, 0)

# States
state_ballinpaddle = 0
state_inplay = 1
state_won = 2
state_gameover = 3

# Frame rate and ball speed levels
fps_levels = [60, 120, 144, 165, 180, 240]
ball_speed_levels = [240, 480, 720, 960, 1280, 1440, 1920]

class BrickBreaker:
    def __init__(self):
        pygame.init()
        self.screen_size = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode(self.screen_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("BrickBreaker")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont('Lucida Sans Roman', 20)
        self.init_game()

    def init_game(self):
        # Initialize game state variables
        self.lives = 3
        self.score = 0
        self.state = state_ballinpaddle

        # Paddle and ball size
        self.paddle_width = self.screen_size[0] // 7
        self.paddle_height = self.screen_size[1] // 24
        self.ball_diameter = self.screen_size[1] // 20
        self.ball_radius = self.ball_diameter // 2

        # Boundary values for paddle and ball
        self.max_paddlex = self.screen_size[0] - self.paddle_width
        self.max_ballx = self.screen_size[0] - self.ball_diameter
        self.max_bally = self.screen_size[1] - self.ball_diameter

        # Initialize sprite group and objects
        self.sprite_group = pygame.sprite.Group()
        self.brick_group = pygame.sprite.Group() 
        self.fps = 60
        self.speed = 240  # Default ball speed
        self.paddley = self.screen_size[1] - self.paddle_height - 10


        self.paddle = Paddle(self)
        self.ball = Ball(self)
        self.sprite_group.add(self.paddle, self.ball)

        # Create bricks
        self.create_bricks()

        # FPS and ball speed
        self.update_ball_velocity()
        self.update_paddle_speed()

        self.menu_enabled = True
        self.mudeki = 0

        # Menu for settings
        self.menu = pygame_menu.Menu('Settings', 400, 300, theme=pygame_menu.themes.THEME_DARK)
        self.menu.add.selector('FPS: ', [(str(fps), fps) for fps in fps_levels], onchange=self.set_fps)
        self.menu.add.selector('Ball Speed: ', [(str(speed), speed) for speed in ball_speed_levels], onchange=self.set_ball_speed)
        self.menu.add.button('Play', self.start_game)

    def create_bricks(self):
        y_brick = 30
        brick_width = self.screen_size[0] // 10
        brick_height = self.screen_size[1] // 24

        for i in range(7):
            x_brick = 30
            for j in range(9):
                brick = Brick(x_brick, y_brick, brick_width, brick_height)
                self.brick_group.add(brick)
                self.sprite_group.add(brick)
                x_brick += brick_width + 8
            y_brick += brick_height + 6

    def check_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.paddle.move(-self.paddle_speed, 0)
        if keys[pygame.K_RIGHT]:
            self.paddle.move(self.paddle_speed, 0)
        if keys[pygame.K_SPACE] and self.state == state_ballinpaddle:
            self.state = state_inplay
        if keys[pygame.K_q] and (self.state == state_gameover or self.state == state_won):
            pygame.display.quit()
            pygame.quit()
            sys.exit()
        if keys[pygame.K_RETURN] and (self.state == state_gameover or self.state == state_won):
            self.init_game()
            self.state = state_ballinpaddle

        if keys[pygame.K_o]:
            self.mudeki = 1
        if keys[pygame.K_p]:
            self.mudeki = 0
        if keys[pygame.K_k]:
            self.init_game()

    def move_ball(self):
        self.ball.move()

    def handle_coll(self):
        if len(self.brick_group) == 0:
            self.state = state_won
        if pygame.sprite.spritecollide(self.ball, self.brick_group, True):
            self.score += 1
            self.ball.reverse_velocity()
        
        if pygame.sprite.collide_rect(self.ball,self.paddle):
            self.ball.bounce_off_paddle(self.paddle)

        elif self.ball.rect.top > self.paddle.rect.top:
            if self.mudeki:
                self.ball.bounce_off_paddle(self.paddle)
            else:
                self.lives -= 1
                if self.lives > 0:
                    self.state = state_ballinpaddle
                else:
                    self.state = state_gameover

    def show_stats(self):
        font_surface = self.font.render(f"speed:{self.ball.velocity} real-FPS-now:{int(self.clock.get_fps())} SCORE: {self.score}  LIVES: {self.lives}  FPS: {self.fps}  BALL SPEED: {self.speed} pixels per second Danger{self.mudeki}", False, white)
        self.screen.blit(font_surface, (self.screen_size[0] - 1000, 5))

    def show_message(self, message):
        size = self.font.size(message)
        font_surface = self.font.render(message, False, white)
        x = (self.screen_size[0] - size[0]) / 2
        y = (self.screen_size[1] - size[1]) / 2
        self.screen.blit(font_surface, (x, y))

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()

            if self.menu_enabled:
                self.menu.update(events)
                self.menu.draw(self.screen)
            else:
                if self.mudeki == 0:
                    self.screen.fill(turquoise)
                else:
                    self.screen.fill(green)

                self.check_input()

                if self.state == state_ballinpaddle:
                    self.ball.rect.center = self.paddle.rect.center
                    self.ball.rect.top = self.paddle.rect.top - self.ball.rect.height
                    self.show_message("Press Space to launch the ball")

                elif self.state == state_gameover:
                    self.show_message("Game Over, Press Enter to Play again or Q to quit")

                elif self.state == state_won:
                    self.show_message("You Won! Press Enter to play again or Q to quit")

                elif self.state == state_inplay:
                    self.move_ball()
                    self.handle_coll()

                self.sprite_group.update()
                self.sprite_group.draw(self.screen)
                self.show_stats()

            pygame.display.update()
            self.clock.tick(self.fps)

    def set_fps(self, value, fps):
        self.fps = fps
        self.update_ball_velocity()
        self.update_paddle_speed()

    def set_ball_speed(self, value, speed):
        self.speed = speed
        self.update_ball_velocity()

    def update_paddle_speed(self):
        self.paddle_speed = 25 * (60 / self.fps)

    def update_ball_velocity(self):
        speed_per_frame = self.speed / self.fps
        speed_per_frame = math.ceil(abs(speed_per_frame / 1.414))
        self.ball.velocity = [speed_per_frame, -speed_per_frame]

    def start_game(self):
        self.menu_enabled = False


class Ball(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game

        # 创建一个透明的 surface 用于绘制球
        self.image = pygame.Surface((self.game.screen_size[1] // 20, self.game.screen_size[1] // 20), pygame.SRCALPHA)

        # 绘制外轮廓 (3像素宽，颜色为深黄色)
        pygame.draw.circle(
            self.image,  # 目标 surface
            (0, 0, 0),  # 外轮廓颜色（深黄色）
            (self.image.get_width() // 2, self.image.get_height() // 2),  # 圆心
            self.image.get_width() // 2,  # 半径
            3  # 轮廓宽度
        )

        # 绘制球体 (内部填充颜色为黄色)
        pygame.draw.circle(
            self.image,  # 目标 surface
            yellow,  # 球体颜色
            (self.image.get_width() // 2, self.image.get_height() // 2),  # 圆心
            self.image.get_width() // 2 - 3  # 半径减去轮廓宽度
        )

        # 在球的中心绘制文本 "BOE"
        font = pygame.font.Font(None, self.image.get_width() // 2)  # 使用默认字体，字体大小为球的1/2宽度
        text_surface = font.render("BOE", True, (0, 0, 0))  # 渲染文本，颜色为黑色
        text_rect = text_surface.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))  # 将文本居中
        self.image.blit(text_surface, text_rect)  # 将文本绘制到球的 surface 上

        self.rect = self.image.get_rect()
        self.rect.center = (self.game.screen_size[0] // 2, self.game.paddley - self.image.get_height())
        self.speed = self.game.speed
        self.velocity = [self.game.speed / self.game.fps / 1.414, -self.game.speed / self.game.fps / 1.414]

    def move(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if self.rect.left <= 0 or self.rect.right >= self.game.screen_size[0]:
            self.velocity[0] = -self.velocity[0]
        if self.rect.top <= 0:
            self.velocity[1] = -self.velocity[1]

    def reverse_velocity(self):
        self.velocity[1] = -self.velocity[1]

    def bounce_off_paddle(self, paddle):
        self.rect.bottom = paddle.rect.top
        self.velocity[1] = -self.velocity[1]


class Paddle(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((self.game.paddle_width, self.game.paddle_height))
        self.image.fill(purple)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.game.screen_size[0] // 2
        self.rect.bottom = self.game.paddley

    def update(self):
        self.rect.clamp_ip(self.game.screen.get_rect())

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(red)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


# Start the game
game = BrickBreaker()
game.run()
