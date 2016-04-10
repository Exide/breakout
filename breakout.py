#!/usr/bin/env python

"""
Breakout
Copyright 2009 Ryan Zander

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import pygame, sys, os, math, random
from pygame.locals import *

class Brick(pygame.sprite.Sprite):
  def __init__(self, size, position):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface((size['x'], size['y']))
    #random_color = (random.randrange(50, 255), random.randrange(50, 255), random.randrange(50, 255))
    random_color = (0, random.randrange(100, 255), 0)
    self.image.fill(random_color)
    self.image.convert()
    self.position = {'x': position[0], 'y': position[1]}
    self.rect = self.image.get_rect()
    self.rect.centerx = self.position['x']+(size['x']/2)
    self.rect.centery = self.position['y']+(size['y']/2)

class Paddle(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface((100, 10))
    self.image.fill((100, 100, 100))
    self.image.convert()
    self.rect = self.image.get_rect()
    self.rect.topleft = ((screen.get_width()/2)-50, screen.get_height()-15)

  def move_left(self):
    "move the paddle left across the screen, stopping at the edge"
    self.rect.move_ip(-10, 0)
    if ball.speed == 0:
      ball.position['x'] -= 10
    if self.rect.left < screen.get_rect().left:
      self.rect.left = screen.get_rect().left+5
      if ball.speed == 0:
        ball.reset()

  def move_right(self):
    "move the paddle right across the screen, stopping at the edge"
    self.rect.move_ip(10, 0)
    if ball.speed == 0:
      ball.position['x'] += 10
    if self.rect.right > screen.get_rect().right:
      self.rect.right = screen.get_rect().right-5
      if ball.speed == 0:
        ball.reset()

class Ball(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface((10, 10))
    self.image.fill((200, 200, 200))
    self.image.convert()
    self.rect = self.image.get_rect()
    
    # start the ball centered 5px above the paddle
    self.position = {'x': paddle.rect.centerx, 'y': paddle.rect.top-5-(self.rect.height/2)}
    self.rect.topleft = (self.position['x']-(self.rect.height/2), self.position['y']-(self.rect.width/2))
    self.direction = 0
    self.speed = 0

  def update(self):
    # set the new position based on speed
    self.position['x'] += self.speed * math.sin(math.radians(self.direction))
    self.position['y'] -= self.speed * math.cos(math.radians(self.direction))

    # sync self.rect with the new position
    self.rect.centerx = self.position['x']
    self.rect.centery = self.position['y']

  def shoot(self):
    "launch the ball from the paddle"
    self.speed = 6

  def bounce(self, diff):
    "redirect the ball based on the direction of impact"
    self.direction = (180-self.direction)%360
    self.direction -= diff

  def reset(self):
    "stop the ball, set its direction up and return it to the middle of the paddle"
    self.speed = 0
    self.direction = 0
    self.position['x'] = paddle.rect.centerx
    self.position['y'] = paddle.rect.top-5-(self.rect.height/2)

# setup the required objects
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
screen = pygame.display.set_mode((800, 600), DOUBLEBUF|HWSURFACE)
pygame.display.set_caption('Breakout')
pygame.key.set_repeat(10, 10)
clock = pygame.time.Clock()
font = pygame.font.Font(os.path.join('data', 'Monaco.ttf'), 15)
bounce_sound = pygame.mixer.Sound(os.path.join('data', 'bonk.ogg'))
lose_sound = pygame.mixer.Sound(os.path.join('data', 'err.ogg'))
collide_sound = pygame.mixer.Sound(os.path.join('data', 'boop.ogg'))
paddle = Paddle()
ball = Ball()
score = 0

# define the bricks and their possible spawn locations
brick_size = {'x':40, 'y':15}

useable_space = screen.get_rect().inflate(-5, -(screen.get_height()/2))
rows = useable_space.height/brick_size['y']
columns = useable_space.width/brick_size['x']

brick_area_width = columns*brick_size['x']
brick_area_height = rows*brick_size['y']
brick_area = pygame.Rect(0, 0, brick_area_width, brick_area_height)
brick_area.top = 50
brick_area.centerx = screen.get_width()/2

def generate_bricks(sprite_group):
  "build a random array of Bricks"
  bricks = []
  for i in range(columns):
    for j in range(rows):
      if random.choice((True, False)):
        x = 0 + brick_area.left + (brick_size['x']*i)
        y = 0 + brick_area.top + (brick_size['y']*j)
        bricks.append(Brick(brick_size, (x, y)))
  sprite_group.empty()
  sprite_group.add(bricks)

# build the sprite group
static_sprites = pygame.sprite.RenderPlain()
moving_sprites = pygame.sprite.RenderPlain((paddle, ball))
generate_bricks(static_sprites)

# begin looping indefinitely
while True:
  clock.tick(60)
  
  # process all the events in the queue
  for event in pygame.event.get():
    if event.type == QUIT:
      sys.exit(0)
    elif event.type == KEYDOWN:
      if event.key == K_ESCAPE:
        sys.exit(0)
      elif event.key == K_SPACE and ball.speed == 0:
        ball.shoot()
      elif event.key == K_LEFT:
        paddle.move_left()
      elif event.key == K_RIGHT:
        paddle.move_right()
      elif event.key == K_r:
        ball.reset()
        generate_bricks(static_sprites)
        score = 0

  # have all the bricks been hit?
  if not len(static_sprites):
    ball.reset()
    generate_bricks(static_sprites)
    score += 500
  else:
    # is the ball touching a brick?
    hit_sprites = pygame.sprite.spritecollide(ball, static_sprites, True)
    if hit_sprites:
      collide_sound.play()
      ball.bounce(0)
      for sprite in hit_sprites:
        score += 10

    # is the ball touching the paddle?
    if ball.rect.colliderect(paddle.rect):
      bounce_sound.play()
      # bounce the paddle vertically
      ball.bounce((paddle.rect.left+(paddle.rect.width/2))-(ball.rect.left+(ball.rect.width/2)))
      # bounce the paddle horizontally
      ball.rect.top = screen.get_height()-paddle.rect.height-ball.rect.height-1

    # is the ball touching a wall?
    if ball.position['y'] < 5:
      # top
      bounce_sound.play()
      ball.bounce(0)
      ball.position['y'] = 5
    elif ball.position['x'] < 5:
      # left
      bounce_sound.play()
      ball.direction = (360-ball.direction)%360
      ball.position['x'] = 5
    elif ball.position['x'] > screen.get_width()-(ball.rect.width/2)-5:
      # right
      bounce_sound.play()
      ball.direction = (360-ball.direction)%360
      ball.position['x'] = screen.get_width()-(ball.rect.width/2)-5
    elif ball.position['y'] > screen.get_height():
      # bottom
      lose_sound.play()
      score -= 100
      if score < 0:
        score = 0
      ball.reset()

  # update the sprite groups
  static_sprites.update()
  moving_sprites.update()

  # clear the background
  screen.fill((0, 0, 0))

  # draw the sprite groups
  static_sprites.draw(screen)
  moving_sprites.draw(screen)

  # draw the score
  score_surface = font.render('Score: %d' % (score), 1, (50, 100, 50))
  score_rect = score_surface.get_rect()
  score_rect.topright = (screen.get_rect().right-10, 10)
  screen.blit(score_surface, score_rect)

  # flip the display buffer
  pygame.display.flip()
  