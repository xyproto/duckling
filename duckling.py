#!/usr/bin/python2
# -*- coding: utf-8 -*-
#vim: set enc=utf8:
#
# The advantage of sending the entire buffer to each sprite,
# instead of each sprite returning a small image,
# is that a sprite may, for instance, blur the whole screen.
# Or make fire-trails after oneself. Or shake the whole screen.
# That's the reason why I don't use the sprite-modules drawing.
#

from __future__ import print_function, unicode_literals
import sys
import random
import os.path

# --- Configuration ---

RES = (1024, 768)
USE_PSYCO = True
USE_BUFFER = False
USE_PBUFFER = True
USE_HWACCEL = False
USE_FULLSCREEN = True

# --- Info and intelligent imports ---

s = ""
s += USE_PSYCO * "psyco " + USE_BUFFER * "buffer " + USE_PBUFFER * "pbuffer " + USE_HWACCEL * "hwaccel "
if s:
    print("Using:" + s)

if USE_PSYCO:
    try:
        import psyco
        psyco.full()
        USE_UPDATE = True
    except ImportError:
        USE_UPDATE = False
else:
    USE_UPDATE = False

try:
    import pygame
    from pygame.locals import *
    from pygame import sprite
except ImportError:
    print("ERROR: Unable to import pygame.")
    sys.exit(1)

GFX_DIR = "gfx"


# --- Containers ---

class Resolution:
    """A class just to wrap up the two ints."""

    def __init__(self, width, height):
        self.x, self.width = width, width
        self.y, self.height = height, height
    
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y

    def __len__(self):
        return 2

class GameInfo(sprite.Group):
    """A container for the buffer, a dictionary of images and all the sprites"""

    def __init__(self, buffer, images):
        sprite.Group.__init__(self)
        self.buffer = buffer
        self.images = images


# --- Globals ---

RES = Resolution(*RES)

FLAGS = 0
if USE_FULLSCREEN:
    FLAGS = FLAGS | FULLSCREEN
if USE_HWACCEL:
    FLAGS = FLAGS | HWACCEL
if USE_PBUFFER:
    FLAGS = FLAGS | DOUBLEBUF

# --- Interfaces ---

class IGameObject(sprite.Sprite):
    """An interface that makes sure the gameobject has a minimum of methods"""

    def __init__(self):
        sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, 0, 0)
    
    def everytime(self):
        """Do this every gameloop, until I return False"""
        return True

    def draw(self):
        return []


class IPlayer:
    """An interface that makes it easy to find out if it's a player or not"""

    def __init__(self):
        pass


class IGrowable:
    """An interface for all things that can grow upwards"""

    def __init__(self):
        pass

    def grow(self):
        pass


class IStandable:
    """An interface for all things that can stand"""

    def __init__(self, standing=False):
        self.standing = standing


class IShootable:
    """An interface for all things that can be shot at"""

    def __init__(self):
        pass

    def hit(self, projectile):
        pass

class IProjectile:
    """An interface for all things that can be shot around"""

    def __init__(self):
        pass

class IBlocking:
    """An interface for all things that blocks other things"""

    def __init__(self):
        pass

class IForceField:
    """An interface for all things that makes other things fly"""

    def __init__(self):
        pass

class IMoveable:
    """An interface for all things that can move"""

    def __init__(self):
        pass

    def blocked(self, block):
        pass


# --- Gameobjects ---

class Grass(IBlocking):
    """Something invisible to stand on."""
    # not finished

    def __init__(self, ginfo, rect):
        IBlocking.__init__(self)
        self.rect = rect

class Wall(IGameObject, IGrowable, IBlocking, IShootable):
    """A strange piece of wall."""

    def __init__(self, ginfo):
        IGameObject.__init__(self)
        IGrowable.__init__(self)
        IBlocking.__init__(self)
        IShootable.__init__(self)

        self.buffer = ginfo.buffer
        self.tekstur = ginfo.images["player"]
        self.color = (80, 128, 255)
        self.rect = pygame.Rect(rect)
        self.xgrow = 0
        self.ygrow = 1
        self.numgrow = 0
        self.sizetemp = (0, 0)

    def grow(self):
        self.numgrow += 1
        x, y, w, h = self.rect
        xgrow = self.xgrow
        ygrow = self.ygrow
        x = max(0, x - xgrow)
        y = max(0, y - ygrow)
        w += xgrow * 2
        h += ygrow * 2
        if (w + x) > RES[0]:
            w -= xgrow * 2
        if (h + y) > RES[1]:
            h -= ygrow * 2
        self.rect = pygame.Rect(x, y, w, h)

    def hit(self, projectile):
        self.grow()

    def shrink(self):
        xgrow = self.xgrow
        ygrow = self.ygrow
        w = max(0, w - self.xgrow * 2)
        h = max(0, h - self.ygrow * 2)
        x += self.xgrow
        y += self.ygrow
        if x > RES[0]:
            x = RES[0]
        if y > RES[1]:
            y = RES[1]
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self):
        if self.sizetemp != self.rect[2:4]:
            self.veggtemp = pygame.transform.scale(self.tekstur, self.rect[2:4])
            self.veggrect = pygame.Rect(self.rect)
        return self.buffer.blit(self.veggtemp, self.rect[0:2])


class Bullet(IGameObject, IProjectile, IMoveable):
    """A single bullet."""

    def __init__(self, pos, ginfo, ax=0, ay=0):
        IGameObject.__init__(self)
        IProjectile.__init__(self)
        IMoveable.__init__(self)

        self.bulletsize = (3, 3)
        self.x, self.y = pos

        self.buffer = ginfo.buffer
        self.images = ginfo.images

        self.r = 90
        self.g = 255
        self.b = 90
        self.RMORE = True
        self.GMORE = True
        self.BMORE = True

        if ax == 0:
            self.ax = (random.random() * 4.0) - 2
            self.r = 255
            self.g = 90
        else:
            self.ax = ax * 3.0
        
        if ay == 0:
            self.ay = (random.random() * 4.0) - 2
        else:
            self.ay = ay * 3.0

        self.theimg = pygame.Surface(self.bulletsize)
        self.set_color()

        self.power = 100

        self.setrect()

    def bounds_ok(self):
        width, height = self.theimg.get_size()
        if (self.y >= RES[1] - height):
            return False
        elif self.y < 0:
            return False
        if (self.x >= RES[0] - width):
            return False
        elif self.x < 0:
            return False
        return True

    def set_color(self):
        r, g, b = self.r, self.g, self.b
        RMORE, GMORE, BMORE = self.RMORE, self.GMORE, self.BMORE
        if RMORE:
            r -= 3
            if r <= 0:
                r = 0
                RMORE = False
        if GMORE:
            g -= 3
            if g <= 0:
                g = 0
                GMORE = False
        if BMORE:
            b -= 3
            if b <= 0:
                b = 0
                BMORE = False
        self.r, self.g, self.b = r, g, b
        self.RMORE, self.BMORE, self.GMORE = RMORE, BMORE, GMORE
        self.theimg.fill((r, g, b))
        return RMORE or GMORE or BMORE
    
    def everytime(self):
        self.x += self.ax
        self.y += self.ay
        self.power = max(self.power - 10, 0)
        self.setrect()
        return self.bounds_ok() and self.set_color()

    def draw(self):
        return self.buffer.blit(self.theimg, (self.x, self.y))

    def setrect(self):
        self.rect = pygame.Rect(self.x, self.y, self.bulletsize[0], self.bulletsize[1])


class Player(IGameObject, IPlayer, IStandable, IMoveable):
    """The player"""

    def __init__(self, ginfo):
        IGameObject.__init__(self)
        IPlayer.__init__(self)
        IStandable.__init__(self)
        IMoveable.__init__(self)
        
        self.ginfo = ginfo

        self.x = int(RES[0] * 0.4)
        self.y = int(RES[1] * 0.8)
        self.ax = 0
        self.ay = 0
        self.gx = 0
        self.gy = 0.5

        self.inair = True

        self.leftkey = False
        self.rightkey = False
        self.downkey = False
        self.jumpkey = False
        self.shootkey = False

        self.rightimg = self.ginfo.images["player"]
        self.leftimg = pygame.transform.flip(self.rightimg, True, False)
        self.theimg = self.leftimg
# For flipped images
#        self.hflip()
#        self.theimg = self.rightimg

        self.standmap = self.ginfo.images["standmap"]

        self.left_and_not_right = False

        self.bullets = []

        self.setrect()

    def hflip(self):
        """Swaps the right and left images"""
        self.leftimg, self.rightimg = self.rightimg, self.leftimg

    def loadpng(self, filename):
        trollimg = pygame.image.load(filename, "png").convert()
        colorkey = trollimg.get_at((0, 0))
        trollimg.set_colorkey(colorkey, RLEACCEL)
        return trollimg

    def setpos(self, x, y):
        self.x = x
        self.y = y
        self.setrect()
    
    def setAcc(self, ax, ay):
        self.ax = ax
        self.ay = ay

    def setGrav(self, gx, gy):
        self.gx = gx
        self.gy = gy

    def doMove(self):
        self.x += self.ax
        self.y += self.ay
        if not self.onGround():
            self.ax += self.gx
            self.ay += self.gy
        self.setrect()

    def onGround(self):
        return (self.y >= RES[1] - self.theimg.get_height()) or self.standing

    def bounds(self):
        width, height = self.theimg.get_size()
        if (self.y >= RES[1] - height):
            self.y = RES[1] - height
        elif self.y < 0:
            self.y = 0
        if (self.x >= RES[0] - width):
            self.x = RES[0] - width
        elif self.x < 0:
            self.x = 0

        try:
            ix = int(self.x + width / 2)
            iy = int(self.y)
            feet_in_wall = (self.standmap.get_at((ix, int(iy + height)))[0] == 0)
            head_in_wall = (self.standmap.get_at((ix, iy))[0] == 0)
            feet_on_wall = (self.standmap.get_at((ix, int(iy + height + 1)))[0] == 0)
            self.standing = False
            if head_in_wall:
                self.ay = 1
            elif feet_in_wall and (not head_in_wall):
                self.ay -= 1
                self.standing = True
            elif feet_on_wall and (not head_in_wall):
                self.standing = True
        except IndexError:
            pass
            
        self.setrect()
    
    def jump(self):
        self.jumpkey = True
        width, height = self.theimg.get_size()
        try:
            almost = (self.standmap.get_at((int(self.x), int(self.y + height + 5)))[0] == 0)
        except IndexError:
            almost = True
        if self.onGround() or almost:
            self.ay -= 50
            self.y -= 5
            self.ax *= 3
            if self.ax > 20:
                self.ax = 20
        
        if self.jumpkey and (not self.left_and_not_right):
            self.theimg = pygame.transform.rotozoom(self.rightimg, 20, 1.0)
        elif self.jumpkey and (self.left_and_not_right):
            self.theimg = pygame.transform.rotozoom(self.leftimg, -20, 1.0)
        
        self.setrect()
    
    def left(self):
        self.left_and_not_right = True
        self.theimg = self.leftimg
        self.leftkey = True
        if self.onGround():
            self.ax = -3
            self.ax -= 0.5
            self.ay *= 0.5
        else:
            self.ax -= 5
            self.ay *= 0.5
        self.setrect()

    def right(self):
        self.left_and_not_right = False
        self.theimg = self.rightimg
        self.rightkey = True
        if self.onGround():
            self.ax = 3
            self.ax += 0.5
            self.ay *= 0.5
        else:
            self.ax += 5
            self.ay *= 0.5
        self.setrect()

    def down(self):
        self.downkey = True
        self.ay = 10 
        self.ax = 0
        self.setrect()

    def shoot(self, ginfo):
        bullets = []
        self.shootkey = True
        if self.shootkey and (not self.left_and_not_right):
            self.theimg = pygame.transform.rotozoom(self.rightimg, -30, 0.5)
        elif self.shootkey and (self.left_and_not_right):
            self.theimg = pygame.transform.rotozoom(self.leftimg, 30, 0.5)

        if self.jumpkey:
            if self.left_and_not_right:
                pos = (self.x + 14, self.y + 2)
                bullets.append(Bullet(pos, ginfo, ay=min(-3, self.ay)))
            else:
                pos = (self.x + 6, self.y + 2)
                bullets.append(Bullet(pos, ginfo, ay=min(-3, self.ay)))
        else:
            if self.left_and_not_right:
                pos = (self.x + 14, self.y + 2)
                bullets.append(Bullet(pos, ginfo, ax=min(-3, self.ax)))
            else:
                pos = (self.x + 6, self.y + 2)
                bullets.append(Bullet(pos, ginfo, ax=max(3, self.ax)))
        ginfo.add(bullets)
        self.setrect()

    def stopright(self):
        self.rightkey = False

    def stopleft(self):
        self.leftkey = False

    def stopdown(self):
        self.downkey = False
    
    def stopjump(self):
        self.jumpkey = False

    def stopshoot(self):
        self.shootkey = False
        if self.left_and_not_right:
            self.theimg = self.leftimg
        else:
            self.theimg = self.rightimg

    def hitground(self):
        self.friction()
        if self.leftkey and not self.rightkey:
            self.ax = 0
            self.left()
        elif self.rightkey and not self.leftkey:
            self.ax = 0
            self.right()
        elif not self.rightkey and not self.leftkey:
            self.ax *= 0.5
        self.bounce()

        if self.left_and_not_right:
            self.theimg = self.leftimg
        else:
            self.theimg = self.rightimg

        self.setrect()

    def bounce(self):
        self.ay = 0

    def friction(self):

        if not self.onGround():
            self.ax *= 0.95
            self.ay *= 0.95
        elif not self.rightkey and not self.leftkey:
            self.ax *= 0.8
            self.ay *= 0.8
        elif self.onGround() and (self.leftkey or self.rightkey):
            tresh = 2.3
            if not ((self.ay > tresh) or (self.ay < -tresh)):
                self.ay = 0
        maxaxx = 8
        if self.ax > maxaxx:
            self.ax = maxaxx
        elif self.ax < -maxaxx:
            self.ax = -maxaxx
        if self.ay > maxaxx:
            self.ay = maxaxx
        elif self.ay < -maxaxx:
            self.ay = -maxaxx


    def everytime(self):
        self.doMove()
        self.friction()
        self.bounds()

        # hitground-calls using self.inair
        if self.inair and self.onGround():
            self.inair = False
            self.hitground()
        elif (not self.inair) and (not self.onGround()):
            self.inair = True

        if self.shootkey:
            self.shoot(self.ginfo)

        self.setrect()

        return True
        
    def draw(self):
        return self.ginfo.buffer.blit(self.theimg, (int(self.x), int(self.y)))

    def setrect(self):
        self.rect = pygame.Rect(int(self.x), int(self.y), self.theimg.get_width(), self.theimg.get_height())

class Fps(IGameObject, IShootable):

    # One loop is supposed to take minimum X ms (1000/24 = ca 41 ms),
    # but 41 ms doesn't look smooth enough. Perhaps 35 is a good choice?

    def __init__(self, ginfo, stats=True):
        IGameObject.__init__(self)

        self.MS_PER_LOOP = 35
        self.minfps = 999999.0
        self.maxfps = 0.0
        self.avgfps = 0.0    
        self.clock = pygame.time.Clock()
        self.buffer = ginfo.buffer
        self.images = ginfo.images
        self.mindiff = 999999.0
        self.maxdiff = 0
        self.avgdiff = 0
        self.stats = stats
        self.fps = 0
        self.color = (255, 0, 0)

        self.setrect()

    def everytime(self):
        self.clock.tick()

        if self.stats:
            fps = self.clock.get_fps()
            if (fps < self.minfps) and (fps > 0):
                self.minfps = fps
            if fps > self.maxfps:
                self.maxfps = fps
            self.avgfps = (self.avgfps + fps) / 2.0
            self.fps = fps

        diff = self.MS_PER_LOOP - self.clock.get_time()
        self.LAG = False
        if diff > 10:
            #open("nolag.log", "a").write(str(diff) + "\n")
            pygame.time.delay(diff - 3)
            self.avgdiff = (self.avgdiff + diff) / 2.0
            if diff < self.mindiff:
                self.mindiff = diff
            if diff > self.maxdiff:
                self.maxdiff = diff
        elif diff < -10:
            #open("lag.log", "a").write(str(diff) + "\n")
            self.LAG = True

        self.setrect()

        return True

    def draw(self):
        # Can be used to draw the fps on the screen
        return pygame.draw.line(self.buffer, self.color, (0, self.fps), (100, self.fps), 3)

    def hit(self, projectile):
        self.color = (int(random.random() * 255), int(random.random() * 255), int(random.random() * 255))

    def setrect(self):
        self.rect = pygame.Rect(0, 100, self.fps, self.fps)

    def quit(self):
        if self.stats:
            if self.minfps and (self.minfps != 999999.0):
                print("Min FPS:", self.minfps)
            if self.maxfps:
                print("Max FPS:", self.maxfps)
            if self.avgfps:
                print("Avg FPS:", self.avgfps)
        if self.mindiff and (self.mindiff != 999999.0):
            print("Minimum time to spare: %i ms"%(int(self.mindiff)))
        if self.maxdiff:
            print("Maximum time to spare: %i ms"%(int(self.maxdiff)))
        if self.avgdiff:
            print("Average time to spare: %i ms"%(int(self.avgdiff)))

# --- The sprite-manager ---

class Sprites:

    def __init__(self, ginfo):
        self.ginfo = ginfo
        # map-initialization goes here
        #wants = [Player, Wall, Fps]
        wants = [Player, Fps]
        self.ginfo.empty()
        self.ginfo.add([Cl(ginfo) for Cl in wants])
        # Use the first Player gameobject as the player
        self.player = self.getone(IPlayer)
        # Is the game running?
        self.running = True

    def getall(self, cl):
        """Returns all the sprites found of a given class, as a Group"""
        return sprite.Group([object for object in self.ginfo.sprites() if isinstance(object, cl)])

    def getone(self, Cl):
        """Returns the first object found of the given class."""
        for object in self.ginfo.sprites():
            if isinstance(object, Cl):
                return object
        else:
            return None
    
    def quit(self):
        fps = self.getone(Fps)
        fps.quit()
        self.running = False

    def pointinrect(self, px, py, x, y, w, h):
        return ((px < (x)) and (px > x)) and ((py < (y)) and (py > y))

    def collides(self, ox, oy, ow, oh, x, y, w, h):
        return self.pointinrect(ox, oy, x, y, w, h) and (((x + w - ox) < ow) and ((y + h - oy) < oh))

    def everytime(self):
        # Delete the sprites that are unable to .everytime()
        for gobj in self.ginfo.sprites():
            if not gobj.everytime():
                self.ginfo.remove(gobj)

        # Let the players be blocked by the blocking
        hitdict = sprite.groupcollide(self.getall(IPlayer), self.getall(IBlocking), False, False).items()
        for player, block in hitdict:
            player.blocked(block)

        # Let the shootables be shot by the projectiles
        hitdict = sprite.groupcollide(self.getall(IShootable), self.getall(IProjectile), False, True).items()
        for shootable, projectile in hitdict:
            shootable.hit(projectile)

        # Remove the moveables that are off the screen
        for moveable in self.getall(IMoveable).sprites():
            x, y, w, h = moveable.rect
            if x < 0 or (x + w) > RES[0] or y < 0 or (y + h) > RES[1]:
                self.ginfo.remove(moveable)
        
        return True

    def draw(self):
        # Draw all subobjects
        return [x.draw() for x in self.ginfo.sprites()]


# --- Functions ---

def load_images(name_transp):
    images = {}
    for name, transp in dict(name_transp).items():
        print("Loading %s..." % (name))
        filename = os.path.join(GFX_DIR, name + ".png")
        img = pygame.image.load(filename, "png").convert()
        if transp:
            colorkey = img.get_at((0, 0))
            img.set_colorkey(colorkey, RLEACCEL)
        images[name] = img
    print("Done loading images.")
    return images

def main():
    
    # I don't need sequencer and such just yet
    #pygame.init()
    pygame.display.init()
    pygame.mouse.set_visible(False)
    
    #pygame.event.set_grab(True)
    pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    screen = pygame.display.set_mode(RES, FLAGS, 16)
    screen.set_alpha(None)

    images = load_images([("duckup", True), ("player", True), ("bg", False), ("standmap", False)])

    if USE_BUFFER:
        buffer = pygame.Surface(RES)
        buffer.set_alpha(None)
    else:
        buffer = screen

    sprites = Sprites(GameInfo(buffer, images))

    oldrects = []

    pygame.event.set_allowed(KEYUP)

    bgimg = images["bg"]

    screen.blit(bgimg, (0, 0, RES.width, RES.height))
    buffer.blit(bgimg, (0, 0, RES.width, RES.height))
    pygame.display.flip()

    troll = sprites.player

    # --- The mainloop ---
    while sprites.running:
    
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                break
            elif event.type == KEYDOWN:
                if event.key == K_UP: troll.jump()
                elif event.key == K_LEFT: troll.left()
                elif event.key == K_RIGHT: troll.right()
                elif event.key == K_DOWN: troll.down()
                elif event.key == K_SPACE: troll.shoot(sprites.ginfo)
                elif event.key == K_ESCAPE: sprites.quit()
            elif event.type == KEYUP:
                if event.key == K_UP: troll.stopjump()
                elif event.key == K_LEFT: troll.stopleft()
                elif event.key == K_RIGHT: troll.stopright()
                elif event.key == K_DOWN: troll.stopdown()
                elif event.key == K_SPACE: troll.stopshoot()

        pygame.event.pump()

        sprites.everytime()

        # --- Draw the sprites, and do some game-logic ---

        # It's important that rect is cleared/overwritten each time
        rects = sprites.draw()

        # --- Copy the buffer to the screen ---

        # This one was faster than filtrating out the redunant ones
        activerects = rects + oldrects
        activerects = filter(bool, activerects)

        # Draw the new graphics
        if USE_BUFFER:
            # Draw the buffer to the screen
            [screen.blit(buffer, rect, rect) for rect in activerects]

        # --- Update the screen ---
    
        # Update the new graphics
        if USE_UPDATE:
            pygame.display.update(activerects)
        else:
            pygame.display.flip()
        
        # Save the old coordinates
        oldrects = rects[:]

        # --- Clear/reset the buffer ---

        for rect in rects:
            buffer.blit(bgimg, rect, rect)

    # --- Out of the main loop, quit the game ---

    pygame.quit()


if __name__ == "__main__":
    main()
