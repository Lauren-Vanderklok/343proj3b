#!/usr/bin/env python3

import pygame
import random
import sys


class Overlay(pygame.sprite.Sprite):
    def __init__(self):
        # Equivalent statements:
        #pygame.sprite.Sprite.__init__(self)
        super(pygame.sprite.Sprite, self).__init__()
        self.image = pygame.Surface((800, 20))
        #self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.font = pygame.font.Font('freesansbold.ttf', 18)
        self.render('Score: 0        Lives: 5')
        
    def render(self, text):
        self.text = self.font.render(text, True, (255, 255, 255 ))
        self.image.blit(self.text, self.rect)
    
    def draw(self, screen):
        screen.blit(self.text, (0, 0))

    def update(self, score, lives):
        self.render('Score: ' + str(score) + '        Lives: ' + str(lives))


class Ship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((25, 25))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = 375
        self.rect.y = 570

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    right = True
    pos = 200 #distance between first col of blocks and left edge, 200 is middle

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255) )
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.basePos = 0

    def update(self):
        self.rect.x = self.basePos + Enemy.pos


class Projectile(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        pygame.draw.circle(self.image, (255, 255, 255), (5, 5), 5)
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 560
        self.vector = [ 0, 0 ]
        self.thud_sound = pygame.mixer.Sound('assets/thud.wav')

    def update(self, game, enemies, ship):
        if self.rect.x < 1 or self.rect.x > 795:
            self.vector[0] *= -1
        if self.rect.y < 0:
            self.vector[1] *= -1
        if self.rect.y > ship.rect.y + 20:
            game.projectiles.remove(self)
            pygame.event.post(game.new_life_event)
        hitObject = pygame.sprite.spritecollideany(self, enemies)
        if hitObject:
            self.thud_sound.play()
            self.vector[0] *= -1.1
            self.vector[1] *= -1.1
            hitObject.kill()
            game.score += 1
        if pygame.sprite.collide_rect(self, ship):
            self.vector[1] *= -1.2
            self.vector[0] += random.random()
            if random.randint(0,1) == 1:
                self.vector[0] *= -1
        self.rect.x += self.vector[0]
        self.rect.y += self.vector[1]


class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(50)
        pygame.mixer.music.load('assets/TheOnlySongThatMatters.wav')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.4)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600)) #controls size of screen x, y pix
        self.projectiles = pygame.sprite.Group()
        #self.balls.add(Projectile())
        self.projectile = None
        self.ship = Ship()
        self.new_life_event = pygame.event.Event(pygame.USEREVENT + 1)
        self.enemies = pygame.sprite.Group()
        self.overlay = Overlay()
        self.screen.fill((0, 0, 0)) #controls color of background updated in run
        #self.ready = True
        self.score = 0
        self.lives = 5
        for i in range(0, 5):
            for j in range(0, 8):
                enemy = Enemy()
                enemy.basePos = j * 50
                enemy.rect.y = i * 50
                self.enemies.add(enemy)


    def run(self):
        self.done = False
        #self.spacePressed = False
        while not self.done:
            #self.spacePressed = False
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == self.new_life_event.type:
                    self.lives -= 1
                    if self.lives < 0:
                        pygame.quit()
                        sys.exit(0)
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a: #press a for SICKO MODE
                        self.lives += 1
                        ball = Projectile()
                        ball.vector = [ - random.randint(1, 10), -1 ]
                        #self.balls.add(ball)
                    if event.key == pygame.K_SPACE: #press space to fire
                        self.projectile = Projectile()
                        self.projectiles.add(self.projectile)
                        self.projectile.rect.x = self.ship.rect.x + 12
                        self.projectile.vector = [ 0, -1 ]
                        #self.spacePressed = True
                    if event.key == pygame.K_LEFT:
                        self.ship.rect.x -= 5
                        if self.ship.rect.x <= 0:
                            self.ship.rect.x = 0
                    if event.key == pygame.K_RIGHT:
                        self.ship.rect.x += 5
                        if self.ship.rect.x >= 750:
                            self.ship.rect.x = 750
                #if self.ready:
                 #   self.projectiles.sprites()[0].rect.x = self.ship.rect.x + 25
            
            self.projectiles.update(self, self.enemies, self.ship)
            self.overlay.update(self.score, self.lives)
            if Enemy.right:
                Enemy.pos += 5
                #self.rect.x = self.basePos + Enemy.pos
                if Enemy.pos > 400:
                    Enemy.right = False
            else:
                Enemy.pos -= 5
                #self.rect.x = self.basePos + Enemy.pos
                if Enemy.pos < 0:
                    Enemy.right = True
            self.enemies.update()
            self.projectiles.draw(self.screen)
            self.ship.draw(self.screen)
            self.enemies.draw(self.screen)
            self.overlay.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)


class Intro(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((800, 120))
        self.font = pygame.font.Font('freesansbold.ttf', 96)
        self.text = self.font.render('Breakout!', True, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.image.blit(self.text, self.rect)

    def draw(self, screen):
        screen.blit(self.text, (0, 0))


if __name__ == "__main__":
    game = Game()
    game.run()

