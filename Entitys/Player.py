import pygame, math, Textures
from threading import Timer
from Entity import Entity
from Point import Point
from Animation import Animation
from Directions import Directions

class Player(Entity):
    def __init__(self):
        super().__init__(Textures.PLAYER_DOWN.surface)
        self.invincible: bool = False
        self.maxHealth: int = 3
        self.health: int = self.maxHealth
        self.direction: Directions = Directions.DOWN
        self.movedLastFrame: bool = False
        self.walkUpAnimation = Animation(self, [ Textures.PLAYER_WALK_UP_0.surface, Textures.PLAYER_WALK_UP_1.surface ], 250)
        self.walkRightAnimation = Animation(self, [ Textures.PLAYER_WALK_RIGHT_0.surface, Textures.PLAYER_WALK_RIGHT_1.surface ], 250)
        self.walkDownAnimation = Animation(self, [ Textures.PLAYER_WALK_DOWN_0.surface, Textures.PLAYER_WALK_DOWN_1.surface ], 250)
        self.walkLeftAnimation = Animation(self, [ Textures.PLAYER_WALK_LEFT_0.surface, Textures.PLAYER_WALK_LEFT_1.surface ], 250)

    def update(self, time: int):
        keys = pygame.key.get_pressed()
        directionPoint: Point = Point(0, 0)
        if(keys[pygame.K_w] or keys[pygame.K_UP]):
            directionPoint.y += 1
        if(keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            directionPoint.x += 1
        if(keys[pygame.K_s] or keys[pygame.K_DOWN]):
            directionPoint.y -= 1
        if(keys[pygame.K_a] or keys[pygame.K_LEFT]):
            directionPoint.x -= 1

        if not directionPoint.equals(Point(0, 0)):
            self.movedLastFrame = True
            angle: int = -1
            if(directionPoint.x == 0):
                angle = 0 if directionPoint.y == 1 else 180
            elif(directionPoint.y == 0):
                angle = 90 if directionPoint.x == 1 else 270
            else:
                if(directionPoint.y > 0):
                    angle = math.degrees(math.atan(directionPoint.y / directionPoint.x))
                else:
                    angle = 180 + math.degrees(math.atan(directionPoint.y / directionPoint.x))
                if(angle < 0):
                    angle = 360 + angle
            self.x += math.sin(math.radians(angle)) * self.speed * time
            self.y -= math.cos(math.radians(angle)) * self.speed * time
            if(angle == 0):
                if(not self.walkUpAnimation.isRunning):
                    self.direction = Directions.UP
                    self.walkLeftAnimation.stop()
                    self.walkDownAnimation.stop()
                    self.walkRightAnimation.stop()
                    self.walkUpAnimation.play()
            elif(angle == 180):
                if(not self.walkDownAnimation.isRunning):
                    self.direction = Directions.DOWN
                    self.walkUpAnimation.stop()
                    self.walkLeftAnimation.stop()
                    self.walkRightAnimation.stop()
                    self.walkDownAnimation.play()
            elif(angle < 180):
                if(not self.walkRightAnimation.isRunning):
                    self.direction = Directions.RIGHT
                    self.walkUpAnimation.stop()
                    self.walkLeftAnimation.stop()
                    self.walkDownAnimation.stop()
                    self.walkRightAnimation.play()
            elif(not self.walkLeftAnimation.isRunning):
                self.direction = Directions.LEFT
                self.walkUpAnimation.stop()
                self.walkDownAnimation.stop()
                self.walkRightAnimation.stop()
                self.walkLeftAnimation.play()
        else:
            self.walkUpAnimation.stop()
            self.walkRightAnimation.stop()
            self.walkDownAnimation.stop()
            self.walkLeftAnimation.stop()
            if(self.movedLastFrame):
                match(self.direction):
                    case Directions.UP:
                        self.surface = Textures.PLAYER_UP.surface
                    case Directions.RIGHT:
                        self.surface = Textures.PLAYER_RIGHT.surface
                    case Directions.DOWN:
                        self.surface = Textures.PLAYER_DOWN.surface
                    case Directions.LEFT:
                        self.surface = Textures.PLAYER_LEFT.surface
            self.movedLastFrame = False

        super().update(time)

    def takeDamage(self, damageAmount: int):
        super().takeDamage(damageAmount)
        self.invincible = True
        timer = Timer(2, self.removeInvincability)
        timer.start()

    def removeInvincability(self):
        self.invincible = False

    def respawn(self):
        self.x = 0
        self.y = 0
        self.isAlive = True
        self.health = self.maxHealth