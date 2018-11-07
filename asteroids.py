# program template for Spaceship
try:
    import simplegui
except:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
start = 0

# I don't know where to put this
explosion_group = set()

# Spaceship constants
FRICTION = 0.03
SPEED = 0.3
MISSILE_SPEED = 15
TURN_SPEED = 0.1


class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")
#splash_image = simplegui.load_image("matt_rocks.png")
# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 20)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
#soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")
soundtrack.set_volume(.2)

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            ship_info.center[0] = 135
        else:
            ship_info.center[0] = 45
        canvas.draw_image(self.image, self.image_center, self.image_size,
                          self.pos, self.image_size, self.angle)
    def update(self):
        if self.thrust:
            vec = angle_to_vector(self.angle)
            self.vel[0] += vec[0] * SPEED
            self.vel[1] += vec[1] * SPEED
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
            #ship_thrust_sound.rewind()
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        friction = [self.vel[0] * FRICTION, self.vel[1] * FRICTION]
        self.vel[0] -= friction[0]
        self.vel[1] -= friction[1]
        for i in range(2):
            if self.vel[i] <= 0.1 and self.vel[i] >= -0.1:
                self.vel[i] = 0
        self.pos[0] = self.pos[0] % WIDTH
        self.pos[1] = self.pos[1] % HEIGHT
        self.angle += self.angle_vel
        
    def go(self):
        self.thrust = True
        
    def shoot(self):
        global missile_group
        vec = angle_to_vector(self.angle)
        position = [self.pos[0] + 45 * vec[0], self.pos[1] + 45 * vec[1]]
        velocity = [vec[0] * MISSILE_SPEED + self.vel[0], vec[1] * MISSILE_SPEED + self.vel[1]]
        missile_group.add(Sprite(position, velocity, 0, 0, missile_image, missile_info, missile_sound))
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None, age = 0):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size,
                          self.pos, self.image_size, self.angle)
        if self.animated:
            self.image_center[0] = self.age * self.image_size[0] + self.image_size[0] * 0.5
            
        
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos[0] = self.pos[0] % WIDTH
        self.pos[1] = self.pos[1] % HEIGHT
        self.angle += self.angle_vel
        self.age += 1
        #print self.angle_vel, self.angle

    def collide(self, other):
        return dist(self.get_position(), other.get_position()) <= (self.get_radius() + other.get_radius())
        
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    def get_age(self):
        return self.age
    
    def get_lifespan(self):
        return self.lifespan
    
def draw(canvas):
    global time, rock_count, start, lives, score
    
    # animate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    if not start:
        my_ship.update()
        canvas.draw_image(splash_image, splash_info.get_center(), splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH * 0.75, HEIGHT * 0.75])      
    else:
    # draw ship and sprites
        soundtrack.play()
        my_ship.draw(canvas)
        # update ship and sprites
        my_ship.update()
        process_sprite_group(canvas, rock_group)
        process_sprite_group(canvas, missile_group)
        process_sprite_group(canvas, explosion_group)
        if group_collide(rock_group, my_ship):
            lives -= 1
        score += group_group_collide(missile_group, rock_group)
    canvas.draw_text("Lives: " + str(lives), [10,50], 20, 'white', 'monospace')
    canvas.draw_text("Score: " + str(score), [WIDTH - 150, 50], 20, 'white', 'monospace')    
    if lives == 0:
        start = False
        timer.stop()
        soundtrack.pause()
        reset()
        
# Helper functions
def process_sprite_group(canvas, group):
    for item in set(group):
        item.update()
        item.draw(canvas)
        if item.get_age() >= item.get_lifespan():
            item.age = 0
            group.remove(item)
            
def group_collide(group, other):
    collision = False
    for item in set(group):
        if item.collide(other):
            collision = True
            explosion_group.add(Sprite(item.get_position(), [0,0], 0, 0, explosion_image, explosion_info, sound=explosion_sound, age=0))
            #explosion_sound.play()
            group.remove(item)
    return collision

def group_group_collide(group1, group2):
    global score
    collisions = 0
    for item in set(group1):
        if group_collide(group2, item):
            collisions += 1
            group1.discard(item)
    return collisions
    
def reset():
    global lives, my_ship, rock_group, missile_group, score, start
    start = False
    lives = 3
    score = 0
    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0,0], 0, ship_image, ship_info)
    rock_group = set()
    missile_group = set()
    soundtrack.rewind()
    ship_thrust_sound.rewind()
    
# keyboard handlers
def keydown(key):
    if start:
        if key == simplegui.KEY_MAP['up']:
            my_ship.go()
        elif key == simplegui.KEY_MAP['left']:
            my_ship.angle_vel -= TURN_SPEED
        elif key == simplegui.KEY_MAP['right']:
            my_ship.angle_vel += TURN_SPEED
        if key == simplegui.KEY_MAP['space']:
            my_ship.shoot()

def keyup(key):
    if start:
        if key == simplegui.KEY_MAP['up']:
            my_ship.thrust = False
        elif key == simplegui.KEY_MAP['left']:
            my_ship.angle_vel = 0
        elif key == simplegui.KEY_MAP['right']:
            my_ship.angle_vel = 0
    
# mouseclick handler

def click(pos):
    global start, score
    if not start:
        start = True
        timer.start()
    
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group
    rock_speed = 1
    rock_count = 0
    for rock in rock_group:
        rock_count += 1
    if rock_count < 12:
        position = [random.randrange(WIDTH), random.randrange(HEIGHT)]
        if score > 0 and score % 5 == 0:
            rock_speed += score / 5
        velocity = [random.randrange(-rock_speed, rock_speed) for i in range(2)]
        angle = 0
        angle_velocity = random.randrange(-6,6) / 50.0
        if dist(position, my_ship.pos) <= asteroid_info.get_radius() + 2 * my_ship.get_radius():
            pass
        else:
            rock_group.add(Sprite(position, velocity, angle, angle_velocity, asteroid_image, asteroid_info))
            rock_count += 1
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# start a new game
reset()

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)
timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling

frame.start()
