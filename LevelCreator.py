import pygame, json, math, Game, MenuManager, LevelObjects.SchokoDrink, LevelObjects.Palm, LevelObjects.Tree, LevelObjects.Grass, LevelObjects.House, LevelObjects.MonsterBaseEntry, LevelObjects.House2, CoordUtils, LevelObjects.MonsterbaseFloor, LevelObjects.WoodFloor, LevelObjects.Water, LevelObjects.House3
from GameObject import GameObject
from Point import Point
from LevelObjects.RemoveObject import RemoveObject
from io import TextIOWrapper
from LevelObject import LevelObject

class LevelCreator:
    def __init__(self):
        self.levelObjects: list[LevelObject] = []
        self.selectObjectBgPanel: GameObject = GameObject(pygame.Surface((Game.screen.get_width() / 5, Game.screen.get_height())), Point(0, 0))
        self.selectObjectBgPanel.surface.fill((40, 40, 40))
        self.selectObjectBgPanel.surface.set_alpha(200)
        self.selectableObjects: list[LevelObject] = []
        self.selectedType: type[LevelObject] = None
        self.rightDownMousePos: Point = Point(0, 0)
        self.rightDownCamPos: Point = Point(0, 0)
        self.cameraPos: Point = Point(0, 0)
        for levelObjectClass in LevelObject.__subclasses__():
            object: levelObjectClass = levelObjectClass(Point(0, 0))
            object.pos = Point(self.selectObjectBgPanel.surface.get_width() / 2 - object.surface.get_width() / 2, 50 if len(self.selectableObjects) == 0 else self.selectableObjects[-1].pos.y + self.selectableObjects[-1].surface.get_height() + 50)
            self.selectableObjects.append(object)

    def render(self, screen: pygame.Surface):
        for levelObject in self.levelObjects:
            levelObject.renderOffset(screen, self.cameraPos.reverseSign())
        self.selectObjectBgPanel.render(screen)
        for selectableObject in self.selectableObjects:
            selectableObject.render(screen)

    def update(self):
        mouse: tuple[bool, bool, bool] = pygame.mouse.get_pressed(3)
        if(mouse[0]):
            self.leftHeld()
        if(mouse[2]):
            self.rightHeld()

    def keyPressed(self, key: int):
        match(key):
            case pygame.K_ESCAPE:
                self.openMenu(True)
    
    def mousePressed(self, button: int, pos: Point):
        if(button == 1):
            if(self.selectObjectBgPanel.collidepoint(pos)):
                for selectableObject in self.selectableObjects:
                    if(selectableObject.collidepoint(pos)):
                        self.selectedType = type(selectableObject)
                        break
        elif(button == 3):
            self.rightDownMousePos = pos
            self.rightDownCamPos = self.cameraPos
    
    def mouseWheel(self, y: int):
        mousePos: Point = Point.fromTuple(pygame.mouse.get_pos())
        if(not self.selectObjectBgPanel.collidepoint(mousePos)):
            return
        for selectableObject in self.selectableObjects:
            selectableObject.pos.y += 20 if y > 0 else -20
        if(self.selectableObjects[0].pos.y > 50):
            offset: int = 50 - self.selectableObjects[0].pos.y
            for selectableObject in self.selectableObjects:
                selectableObject.pos.y += offset
        maxOffset: int = Game.screen.get_height() - self.selectableObjects[-1].surface.get_height() - 50
        if self.selectableObjects[-1].pos.y < maxOffset:
            offset: int = maxOffset - self.selectableObjects[-1].pos.y
            for selectableObject in self.selectableObjects:
                selectableObject.pos.y += offset

    def leftHeld(self):
        mousePos: Point = Point.fromTuple(pygame.mouse.get_pos())
        worldMousePos: Point = mousePos.offset(self.cameraPos)
        if(self.selectObjectBgPanel.collidepoint(mousePos) or self.selectedType == None):
            return
        for levelObject in self.levelObjects:
            if(self.selectedType == RemoveObject and CoordUtils.blockFromPoint(levelObject.pos).equals(CoordUtils.blockFromPoint(worldMousePos))):
                self.levelObjects.remove(levelObject)
                return
            if(type(levelObject) == self.selectedType and CoordUtils.blockFromPoint(levelObject.pos).equals(CoordUtils.blockFromPoint(worldMousePos))):
                return
            if(levelObject.layer != self.selectedType.layer or not CoordUtils.blockFromPoint(levelObject.pos).equals(CoordUtils.blockFromPoint(worldMousePos))):
                continue
            self.levelObjects.remove(levelObject)
        if(self.selectedType == RemoveObject):
            return
        self.levelObjects.append(self.selectedType(CoordUtils.snapToLevelGrid(worldMousePos)))

    def rightHeld(self):
        mousePos: Point = Point.fromTuple(pygame.mouse.get_pos())
        self.cameraPos = self.rightDownCamPos.offset(Point(self.rightDownMousePos.x - mousePos.x, self.rightDownMousePos.y - mousePos.y))

    def openMenu(self, open: bool):
        if(open):
            Game.state = Game.state.IN_MENU
            MenuManager.setMenu(MenuManager.Menus.LevelCreatorMenu)
        else:
            Game.state = Game.state.IN_LEVEL_CREATOR
            MenuManager.setMenu(None)

    def saveToFile(self, path: str):
        level: dict[str, list[tuple[int, int]]] = {}
        for levelObject in self.levelObjects:
            if not levelObject.id in level:
                level[levelObject.id]: list[tuple[int, int]] = []
            level[levelObject.id].append(CoordUtils.blockFromPoint(levelObject.pos).asTuple())
        levelFile: TextIOWrapper = open(path, "w")
        json.dump(level, levelFile)
        levelFile.close()

    def loadFromFile(self, path: str):
        self.levelObjects = []
        levelFile: TextIOWrapper = open(path, "r")
        level: dict[str, list[tuple[int, int]]] = json.loads(levelFile.read())
        for id in level.keys():
            objectType: type[LevelObject] = LevelObject.getClassById(id)
            for pos in level[id]:
                self.levelObjects.append(objectType(CoordUtils.pointFromBlock(Point.fromTuple(pos))))
        self.openMenu(False)