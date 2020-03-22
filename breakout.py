#!/usr/bin/env python3

import pygame
import random
import sys

"""class containing the lives and score overlays
lives and score variable are not held in this object
they are handled by the game object"""
class Overlay(pygame.sprite.Sprite):
    def __init__(self):
        super(pygame.sprite.Sprite, self).__init__()
        self.image = pygame.Surface((800, 20))
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

"""class containing ship object 
ship moves as directed by game object
fires projectiles in certain directions as directed by game object"""
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((25, 25))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = 375
        self.rect.y = 570
        self.shootingSound = pygame.mixer.Sound('assets/shooting.wav')
        self.projectile = None

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    #creates a projectile object from ship's position,
    #projectile moves vectx pixels on the x axis per update
    #and vecty pixels on the y axis per update
    def fire(self, vectx , vecty):
        self.shootingSound.play()
        self.projectile = Projectile()
        game.shipProjectiles.add(self.projectile)
        self.projectile.rect.x = self.rect.x + 12
        self.projectile.vector = [vectx, vecty]


"""class containing enemy object
object moves as directed by the game object
fires projectiles and powerups at random points as directed by game object"""
class Enemy(pygame.sprite.Sprite):
    right = True #bool to control whether the enemies are moving left or right
    pos = 200 #distance between first col of blocks and left edge, 200 is middle

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255) )
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.basePos = 0
        self.projectile = None

    def update(self):
        self.rect.x = self.basePos + Enemy.pos

    #creates projectile object from position of enemy object, adds projectile to game's update/draw groups
    def fire(self):
        self.projectile = Projectile()
        self.projectile.rect.x = self.rect.x + 25
        self.projectile.rect.y = self.rect.y - 25
        self.projectile.vector = [0, 8]
        game.enemyProjectiles.add(self.projectile)

    #creates powerup object from position of enemy object, adds powerup to game's update/draw groups
    def firePowerUp(self):
        self.projectile = ThreeShotPowerUp()
        self.projectile.rect.x = self.rect.x + 25
        self.projectile.rect.y = self.rect.y - 25
        self.projectile.vector = [0, 8]
        game.powerups.add(self.projectile)

'''class containing projectile object
both ship objects and enemy objects will create this object when directed by game
projectile kills objects it is targeting when it collides with them'''
class Projectile(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        pygame.draw.circle(self.image, (255, 255, 255), (5, 5), 5)
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 560
        self.vector = [0, 0]
        self.thud_sound = pygame.mixer.Sound('assets/thud.wav')
        self.deathSound = pygame.mixer.Sound('assets/Explosion2.wav')

    #kills targets upon determining firer
    def update(self, targets, firer):
        if self.rect.x < 1 or self.rect.x > 795:
            self.kill()
        if self.rect.y < 0:
            self.kill()
        if self.rect.y > 600:
            self.kill()
        if type(firer) == Ship:
            hitObject = pygame.sprite.spritecollideany(self, targets)
            if hitObject:
                self.thud_sound.play()
                hitObject.kill()
                self.kill()
                game.score += 1
        else:
            if pygame.sprite.collide_rect(self, targets):
                self.deathSound.play()
                pygame.event.post(game.new_life_event)
                self.kill()
        self.rect.x += self.vector[0]
        self.rect.y += self.vector[1]

'''class containing powerup object, 
enemy class will fire this object at random points,
when ship is hit, event threeShotPowerUp is created
and the ship object will fire 3 projectiles at a time for the next 5 shots'''
class ThreeShotPowerUp(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        pygame.draw.circle(self.image, (51, 85, 255), (5, 5), 5)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.vector = [0, 0]
        self.sound = pygame.mixer.Sound('assets/SFX_Powerup_01.wav')

    def update(self):
        if self.rect.x < 1 or self.rect.x > 795:
            self.kill()
        if self.rect.y < 0:
            self.kill()
        if self.rect.y > 600:
            self.kill()
        if pygame.sprite.collide_rect(self, game.ship):
            self.sound.play()
            pygame.event.post(game.threeShotPowerUp)
            self.kill()
        self.rect.x += self.vector[0]
        self.rect.y += self.vector[1]

'''class containing the entire game
creates, updates and draws all objects
handles events '''
class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(50)
        pygame.mixer.music.load('assets/TheOnlySongThatMatters.wav')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.6) #rasputin background music is a bit loud
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600)) #controls size of screen x, y pix
        self.shipProjectiles = pygame.sprite.Group() #all projectiles the ship has fired
        self.enemyProjectiles = pygame.sprite.Group() #all projectiles the enemies have fired
        self.powerups = pygame.sprite.Group() #all powerups the enemies have fired
        self.ship = Ship()
        self.new_life_event = pygame.event.Event(pygame.USEREVENT + 1)
        self.win = pygame.event.Event(pygame.USEREVENT + 2)
        self.threeShotPowerUp = pygame.event.Event(pygame.USEREVENT + 3)
        self.enemies = pygame.sprite.Group()
        self.overlay = Overlay()
        self.screen.fill((0, 0, 0)) #controls color of background updated in run
        self.score = 0
        self.lives = 5
        self.spacePressed = False #i have added this bool so people cant spam 100 projectiles at once
        self.powerup = 0 #controls the number of powerup shots left
        #creates enemies in 5x8 bloc
        for i in range(0, 5):
            for j in range(0, 8):
                enemy = Enemy()
                enemy.basePos = j * 50
                enemy.rect.y = i * 50
                self.enemies.add(enemy)

    def run(self):
        self.done = False
        while not self.done:
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
                    if event.key == pygame.K_SPACE:
                        self.spacePressed = True
                    if event.key == pygame.K_LEFT:
                        self.ship.rect.x -= 10
                        if self.ship.rect.x <= 0:
                            self.ship.rect.x = 0
                    if event.key == pygame.K_RIGHT:
                        self.ship.rect.x += 10
                        if self.ship.rect.x >= 750:
                            self.ship.rect.x = 750
                if event.type == self.threeShotPowerUp.type:
                    self.powerup = 5
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE and self.spacePressed == True:
                        self.spacePressed = False
                        if self.powerup > 0:
                            self.ship.fire(1, -8)
                            self.ship.fire(0, -8)
                            self.ship.fire(-1, -8)
                            self.powerup -= 1
                        else:
                            self.ship.fire(0, -8)
                if event.type == self.win.type:
                    pygame.quit()
                    sys.exit(0)

            if len(self.enemies.sprites()) == 0:
                pygame.event.post(self.win)
            if random.randint(0, 9) == 2: #10% chance for a projectile to be fired by a random enemy object
                self.enemies.sprites()[random.randint(0, len(self.enemies.sprites())-1)].fire()
            if random.randint(0, 49) == 2: #2% chance for powerup to be fired by random enemy object
                self.enemies.sprites()[random.randint(0, len(self.enemies.sprites())-1)].firePowerUp()

            #update all objects
            self.shipProjectiles.update(self.enemies, self.ship)
            self.enemyProjectiles.update(self.ship, self.enemies)
            self.powerups.update()
            self.overlay.update(self.score, self.lives)
            #controls the position of the entire block of enemy objects
            if Enemy.right:
                Enemy.pos += 5
                if Enemy.pos > 400:
                    Enemy.right = False
            else:
                Enemy.pos -= 5
                if Enemy.pos < 0:
                    Enemy.right = True
            self.enemies.update()

            #draw all objects onto screen, order executed determines layer of object
            self.shipProjectiles.draw(self.screen)
            self.ship.draw(self.screen)
            self.enemies.draw(self.screen)
            self.powerups.draw(self.screen)
            self.enemyProjectiles.draw(self.screen)
            self.overlay.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

"""main method that begins program"""
if __name__ == "__main__":
    game = Game()
    game.run()

