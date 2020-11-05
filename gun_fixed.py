import pygame as pg
import numpy as np
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


class Ball():
    def __init__(self, coord, vel, rad=15, color=None):
        if color == None:
            color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.color = color
        self.coord = coord
        self.vel = vel
        self.rad = rad
        self.is_alive = True

    def draw(self, screen):
        pg.draw.circle(screen, self.color, self.coord, self.rad)

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


class Table():
    pass
class Gun():
    def __init__(self, coord=[30, SCREEN_SIZE[1]//2], 
                 min_pow=20, max_pow=50):
        self.coord = coord
        self.angle = 0
        self.min_pow = min_pow
        self.max_pow = max_pow
        self.power = min_pow
        self.active = False

    def draw(self, screen):
        end_pos = [self.coord[0] + self.power*np.cos(self.angle), 
                   self.coord[1] + self.power*np.sin(self.angle)]
        pg.draw.line(screen, RED, self.coord, end_pos, 5)

    def strike(self):
        vel = [int(self.power * np.cos(self.angle)), int(self.power * np.sin(self.angle))]
        self.active = False
        self.power = self.min_pow
        return Ball(list(self.coord), vel)
        
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

class Manager():
    def __init__(self):
        self.gun = Gun()
        self.table = Table()
        self.balls = []
    
    def process(self, events, screen):
        done = self.handle_events(events)
        self.move()
        self.draw(screen)
        self.check_alive()
        krug1.paintcircle()
        krug2.paintcircle()
        krug1.move()
        krug2.move()
        for bullet in self.balls:
            krug1.hit_target(bullet.coord)
            krug2.hit_target(bullet.coord)
        return done

    def draw(self, screen):
        screen.fill(BLACK)
        for ball in self.balls:
            ball.draw(screen)
        self.gun.draw(screen)

    def move(self):
        for ball in self.balls:
            ball.move()
        self.gun.move()

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
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.gun.coord[1] -= 5
                elif event.key == pg.K_DOWN:
                    self.gun.coord[1] += 5
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.gun.active = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.balls.append(self.gun.strike())
        
        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            self.gun.set_angle(mouse_pos)

        return done

screen = pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption("The gun")
clock = pg.time.Clock()
krug1 = Target(screen)
krug1.paintcircle()
krug2 = Target(screen)
krug2.paintcircle()
mgr = Manager()

done = False

while not done:
    clock.tick(15)
    screen.fill(BLACK)
    done = mgr.process(pg.event.get(), screen)

    pg.display.flip()

   
