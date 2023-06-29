import pygame, Textures
from LevelObject import LevelObject
from Point import Point

class Water(LevelObject):
    id = "woodWall"
    layer = 0
    surface = Textures.WOOD_WALL.surface

    def __init__(self, pos: Point):
        super().__init__(pos)
        self.collisionRect = pygame.Rect(0, 0, 50, 50)