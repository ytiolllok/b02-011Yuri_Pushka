import pygame as pg
import numpy as np
import os
from random import randint
from random import choice

SCREEN_SIZE = (800, 600)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]
pg.init()
all_sprites = pg.sprite.Group()
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')


class KeyCheck():
    def __init__(self, state):
        self.state = state
    def invert(self):
        self.state = not self.state
class Ball():
    def __init__(self, coord, vel, rad=15, color=None):
        if color == None:
            color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.color = color
        self.coord = coord
        self.vel = vel
        self.rad = rad
        self.is_alive = True
        self.timer = 0

    def draw(self, screen):
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def become_older(self):
        if(self.timer < 200):
            self.timer += 1
        else:
            self.is_alive = False
            
    def move(self, t_step=1., g=2.):
        self.vel[1] += int(g * t_step)
        for i in range(2):
            self.coord[i] += int(self.vel[i] * t_step)
        self.check_walls()
        if self.vel[0]**2 + self.vel[1]**2 < 2**2 and self.coord[1] > SCREEN_SIZE[1] - 2*self.rad:
               self.is_alive = False

    def check_walls(self):
        n = [[1, 0], [0, 1]]
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.flip_vel(n[i], 0.8, 0.9)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.flip_vel(n[i], 0.8, 0.9)

    def flip_vel(self, axis, coef_perp=1., coef_par=1.):
        vel = np.array(self.vel)
        n = np.array(axis)
        n = n / np.linalg.norm(n)
        vel_perp = vel.dot(n) * n
        vel_par = vel - vel_perp
        ans = -vel_perp * coef_perp + vel_par * coef_par
        self.vel = ans.astype(np.int).tolist()

class Hirrih(Ball):
    def __init__(self, coord, vel, rad = 35, color = BLACK):
        self.coord = coord
        self.vel = vel
        self.rad = rad
        self.trace =[]
        self.timer = 0
        self.alive = True
        
    def leave_trace(self):
        y = HirTrace(self.coord)
        self.trace.append(y)
        all_sprites.add(y)

    def become_older(self):
        if(self.timer < 200):
            self.timer += 1
        else:
            self.alive = False
            for i in self.trace:
                i.kill()
    
    def update_trace(self):
        for shadow in self.trace:
            shadow.become_older()
    def move(self):
        self.coord[0] += self.vel[0]
        self.coord[1] += self.vel[1]
class HirTrace(pg.sprite.Sprite):
    def __init__(self, coord):
        pg.sprite.Sprite.__init__(self)
        self.image = Hirrihpic
        self.rect = self.image.get_rect()
        self.coord = coord
        self.alive = True
        self.rect.center = self.coord
        self.timer = 0
    def draw(self, screen):
        pass
    def become_older(self):
        if(self.timer < 7):
            self.timer += 1
          #  print('I got older')
        else:
            self.kill()
            self.alive = False
           # print('I died')
class Table():
    pass
class TankSprite(pg.sprite.Sprite):
    def __init__(self, team_color):
        pg.sprite.Sprite.__init__(self)
        self.color = team_color
        if(self.color == RED):
            self.image = T90pic
        elif(self.color == BLUE):
            self.image = Abramspic
        self.rect = self.image.get_rect()
        self.rect.center = (30, 30)

    def update(self, xcor, ycor):
        self.rect.x = xcor - 70
        self.rect.y = ycor - 30
class Gun():
    def __init__(self, team_color,  
                 min_pow=20, max_pow=50):
        self.color = team_color
        self.coord = [30, SCREEN_SIZE[1]//2]
        if (self.color == BLUE):
            self.coord[0] = 770
        self.angle = 0
        self.min_pow = min_pow
        self.max_pow = max_pow
        self.power = min_pow
        self.active = False
        self.alive = True
        self.sprite = TankSprite(self.color)
        self.radius = 30

    def hit_target(self, hit_coord):
        if ((hit_coord[0]-self.coord[0])**2 + (hit_coord[1]-self.coord[1])**2
            <= (self.radius + 15)**2):
            self.coord = [30, SCREEN_SIZE[1]//2]
            if (self.color == BLUE):
                self.coord[0] = 770
            return(1)
        else:
            return(0)
    

    def draw(self, screen):
        end_pos = [self.coord[0] + self.power*np.cos(self.angle), 
                   self.coord[1] + self.power*np.sin(self.angle)]
        pg.draw.line(screen, self.color, self.coord, end_pos, 5)
        self.sprite.update(self.coord[0], self.coord[1])

    def strike(self):
        vel = [int(self.power * np.cos(self.angle)), int(self.power * np.sin(self.angle))]
        self.active = False
        self.power = self.min_pow
        return Ball(list(self.coord), vel)

    def Hirstrike(self):
        vel = [int(self.power * np.cos(self.angle)), int(self.power * np.sin(self.angle))]
        self.active = False
        self.power = self.min_pow
        return Hirrih(list(self.coord), vel)
    def move(self):
        if self.active and self.power < self.max_pow:
            self.power += 1

    def set_angle(self, mouse_pos):
        self.angle = np.arctan2(mouse_pos[1] - self.coord[1], 
                                mouse_pos[0] - self.coord[0])


class Target():
    def __init__ (self, screen):
            self.color = choice(COLORS)
            self.radius = randint(10, 100)
            self.coords = [randint(100, 700), randint(100, 500)]
            self.speed = [randint(-10, 10), randint(-10, 10)]
            self.screen = screen
    def paintcircle(self):
            pg.draw.circle(self.screen, self.color, self.coords, self.radius)
    def hit_target(self, hit_coords):
        if ((hit_coords[0]-self.coords[0])**2 + (hit_coords[1]-self.coords[1])**2
            <= (self.radius + 15)**2):
            pg.draw.circle(self.screen, BLACK, self.coords, self.radius)
            self.color = choice(COLORS)
            self.radius = randint(10, 100)
            self.coords = [randint(100, 700), randint(100, 500)]
            self.speed = [randint(-10, 10), randint(-10, 10)]
            self.paintcircle()
            pg.display.update()
            return(1)
        else:
            return(0)
    def move(self):
        if (0 < self.coords[0] + self.speed[0] < 800):
            a = 1
        else:
            a = -1
        if (0 < self.coords[1] + self.speed[1] < 600):
            b = 1
        else:
            b = -1
        self.speed = [a*self.speed[0], b*self.speed[1]]
        self.coords = [self.coords[0] + self.speed[0],
        self.coords[1] + self.speed[1]]
class Bomber(Target):
    def __init__ (self, screen):
            self.color = choice(COLORS)
            self.radius = randint(10, 100)
            self.coords = [randint(100, 700), 100]
            self.speed = [randint(-10, 10), 0]
            self.screen = screen
    def move(self):
        if (0 < self.coords[0] + self.speed[0] < 800):
            a = 1
        else:
            a = -1
        if (0 < self.coords[1] + self.speed[1] < 600):
            b = 1
        else:
            b = -1
        self.speed = [a*self.speed[0], b*self.speed[1]]
        self.coords = [self.coords[0] + self.speed[0],
        self.coords[1] + self.speed[1]]
    def hit_target(self, hit_coords):
        if ((hit_coords[0]-self.coords[0])**2 + (hit_coords[1]-self.coords[1])**2
            <= (self.radius + 15)**2):
            self.coords = [randint(100, 700), 100]
            pg.display.update()
            return(1)
        else:
            return(0)
        
    def draw(self):
        pg.draw.polygon(screen, RED, ((self.coords[0] - 20, self.coords[1]), (self.coords[0] + 20, self.coords[1]), (self.coords[0] +20 , self.coords[1] + 10)))

    def bomb(self):
            return(Bomb(self.coords))
class Bomb(Ball):

    def __init__(self, coord):
        self.color = BLUE
        self.coord = coord
        self.vel = [0,0]
        self.rad = 10
        self.is_alive = True
        self.timer = 0
    def move(self):
        self.coord[0] += self.vel[0]
        self.coord[1] += self.vel[1]
        self.vel[1] += 1
    
class Manager():
    def __init__(self):
        self.guns = [Gun(RED), Gun(BLUE)]
        self.table = Table()
        self.balls = []
        self.hirrs = []
        self.i = 0
    def process(self, events, screen):
        done = self.handle_events(events)
        self.move()
        self.draw(screen)
        self.check_alive()
        krug1.paintcircle()
        krug2.paintcircle()
        krug1.move()
        krug2.move()
        self.head_update()
        bomb1.move()
        bomb2.move()
        self.bomb_count(bomb1)
        self.bomb_count(bomb2)
        for ball in self.balls:
            ball.become_older()
        for bullet in self.balls:
            bullet.is_alive = not(krug1.hit_target(bullet.coord))
            bullet.is_alive = not(krug2.hit_target(bullet.coord))
            for gun in self.guns:
                    if(bullet.timer>3):
                        bullet.is_alive = not(gun.hit_target(bullet.coord))
        for head in self.hirrs:
            bomb1.hit_target(head.coord)
            bomb2.hit_target(head.coord)
            if (head.timer>3):
                for gun in self.guns:
                    gun.hit_target(head.coord)
        return done
        
    def draw(self, screen):
        screen.fill(BLACK)
        for ball in self.balls:
            ball.draw(screen)
        all_sprites.draw(screen)
        for gun in self.guns:
            gun.draw(screen)
        bomb1.draw()
        bomb2.draw()    
    def move(self):
        for ball in self.balls:
            ball.move()
        for gun in self.guns:
            gun.move()

    def head_update(self):
        for head in self.hirrs:
            head.become_older()
            if (head.alive == False):
                self.hirrs.remove(head)
                
            head.leave_trace()
            head.move()
            head.update_trace()

    def bomb_count(self, bober):
        if(self.i<70):
            self.i += 1
        else:
            self.balls.append(bober.bomb())
            self.i = 0
    def check_alive(self):
        dead_balls = []
        for i, ball in enumerate(self.balls):
            if not ball.is_alive:
                dead_balls.append(i)

        for i in reversed(dead_balls):
            self.balls.pop(i)
    
    def handle_events(self, events):
        done = False
        for event in events:
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.KEYUP:
                if event.key == pg.K_LSHIFT:
                    shiftdown.state = False
             
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.guns[1].coord[1] -= 15
                elif event.key == pg.K_DOWN:
                    self.guns[1].coord[1] += 15
                elif event.key == pg.K_LEFT:
                    self.guns[1].coord[0] -= 15
                elif event.key == pg.K_RIGHT:
                    self.guns[1].coord[0] += 15
                if event.key == pg.K_w:
                    self.guns[0].coord[1] -= 15
                elif event.key == pg.K_s:
                    self.guns[0].coord[1] += 15
                elif event.key == pg.K_a:
                    self.guns[0].coord[0] -= 15
                elif event.key == pg.K_d:
                    self.guns[0].coord[0] += 15
                elif event.key == pg.K_LSHIFT:
                    shiftdown.state = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.guns[0].active = True
                if event.button == 3:
                    self.guns[1].active = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    if (shiftdown.state == True):
                        x = self.guns[0].Hirstrike()
                        self.hirrs.append(x)
                    else:
                        self.balls.append(self.guns[0].strike())
                if event.button == 3:
                    if (shiftdown.state == True):
                        x = self.guns[1].Hirstrike()
                        self.hirrs.append(x)
                    else:
                        self.balls.append(self.guns[1].strike())
        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            for gun in self.guns:
                gun.set_angle(mouse_pos)

        return done

screen = pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption("The gun")
T90pic = pg.image.load(os.path.join(img_folder, 'T90.png')).convert()
Abramspic = pg.image.load(os.path.join(img_folder, 'Abrams.png')).convert()
Hirrihpic = pg.image.load(os.path.join(img_folder, 'hirrih.png')).convert()
Hirrihpic.set_colorkey((255, 255, 255))
clock = pg.time.Clock()
krug1 = Target(screen)
krug1.paintcircle()
krug2 = Target(screen)
krug2.paintcircle()
bomb1 = Bomber(screen)
bomb2 = Bomber(screen)
mgr = Manager()
all_sprites.add(mgr.guns[0].sprite, mgr.guns[1].sprite)
shiftdown = KeyCheck(False)

done = False
while not done:
    clock.tick(15)
    screen.fill(BLACK)
    done = mgr.process(pg.event.get(), screen)
    print()
    pg.display.flip()
   
   
