import os
import sys
import math
import time
import pygame as pg
current_path = os.getcwd()
import pymunk as pm
from characters import Bird
from level import Level

pg.init()

# Making the screen
screenWidth = 1200
screenHeight = 650
screen = pg.display.set_mode((screenWidth, screenHeight))
pg.display.set_caption("Angry Birds with Physical Quantities")

clock = pg.time.Clock()

# Loading images
redbird = pg.image.load("../resources/images/red-bird3.png").convert_alpha()
background2 = pg.image.load("../resources/images/background3.png").convert_alpha()
sling_image = pg.image.load("../resources/images/sling-3.png").convert_alpha()
full_sprite = pg.image.load("../resources/images/full-sprite.png").convert_alpha()
buttons = pg.image.load("../resources/images/selected-buttons.png").convert_alpha()
happy_pig = pg.image.load("../resources/images/pig_failed.png").convert_alpha()
stars = pg.image.load("../resources/images/stars-edited.png").convert_alpha()

# Making Pig image
pig_rect = pg.Rect(181, 1050, 50, 50)
pig_cropped = full_sprite.subsurface(pig_rect).copy()
pig_image = pg.transform.scale(pig_cropped, (30, 30))

# Making images of stars
star1_rect = pg.Rect(0, 0, 200, 200)
star1 = stars.subsurface(star1_rect).copy()
star2_rect = pg.Rect(204, 0, 200, 200)
star2 = stars.subsurface(star2_rect).copy()
star3_rect = pg.Rect(426, 0, 200, 200)
star3 = stars.subsurface(star3_rect).copy()

# Loading images of buttons
pause_button_rect = pg.Rect(164, 10, 60, 60)
pause_button = buttons.subsurface(pause_button_rect).copy()
replay_button_rect = pg.Rect(24, 4, 100, 100)
replay_button = buttons.subsurface(replay_button_rect).copy()
next_button_rect = pg.Rect(142, 365, 130, 100)
next_button = buttons.subsurface(next_button_rect).copy()
play_rect = pg.Rect(18, 212, 100, 100)
play_button = buttons.subsurface(play_rect).copy()

# Load background music
song1 = "../resources/sounds/angry-birds.ogg"
pg.mixer.music.load(song1)
pg.mixer.music.play(-1)

# The base of the physics
FPS = 60
space = pm.Space()
#space.damping = 0.98
space.gravity = (0.0, -700.0)
bird = None
pigs = []
birds = []
balls = []
polys = []
beams = []
columns = []
poly_points = []
ball_number = 0
polys_dict = {}
mouse_distance = 0
rope_length = 90
angle = 0
angle_bird_degrees = 0
Range = 0
velocity = 0
x_mouse , y_mouse = 0 , 0
count = 0
mouse_pressed = False
bird_hit = False
t1 = 0
tick_to_next_circle = 10
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
sling_x, sling_y = 135, 450
sling2_x, sling2_y = 160, 450
sling_center = (sling_x+sling2_x)//2
score = 0
game_state = 0
bird_path = []
counter = 0
restart_counter = False
bonus_score_once = True
time_of_flight = 0
Height = 0
x_Height = 0
speed = 0
bird_in_air = False
bird_on_ground = False
launch_time = 0
bird_launched = False

PPM = 50       # Conversion factor from pixels to meters (100 pix = 1 m)

# Loading fonts
quantity_font = pg.font.SysFont("Arial", 30)
bold_font = pg.font.SysFont("Arial", 30, bold=True)
bold_font2 = pg.font.SysFont("Arial", 40, bold=True)
bold_font3 = pg.font.SysFont("Arial", 50, bold=True)
wall = False

# Static floor
static_body = pm.Body(body_type=pm.Body.STATIC)

ground = pm.Segment(static_body, (0, 60), (5000, 60), 0)
ground.elasticity = 0.3
ground.friction = 5
ground.collision_type = 3

rightWall = pm.Segment(static_body, (screenWidth, 060.0), (screenWidth, 800.0), 0.0)
rightWall.elasticity = 0.3
rightWall.friction = 5
rightWall.collision_type = 3

space.add(static_body)
space.add(ground)

def to_pg(p):       # Convert pymunk to pygame coordinates
    return int(p.x), int(-p.y+600)

def vector(p0, p1):     # Return the vector of the points: p0 = (xo,yo), p1 = (x1,y1)
    a = p1[0] - p0[0]
    b = p1[1] - p0[1]
    return (a, b)

def unit_vector(v):     # Return the unit vector of the points: v = (a,b)
    mag_v = ((v[0]**2)+(v[1]**2))**0.5
    if mag_v == 0:
        mag_v = 0.000000000000001
    return (v[0] / mag_v , v[1] / mag_v)

def distance(xo, yo, x, y):     # Distance between points
    return (((x - xo) ** 2) + ((y - yo) ** 2)) ** 0.5

def sling_action():     # Sling behavior
    global mouse_distance
    global rope_length
    global angle
    global x_mouse
    global y_mouse
    global speed
    global Range
    global Height
    global x_Height
    global bird
    v = vector((sling_x, sling_y), (x_mouse, y_mouse))
    unit_v = unit_vector(v)
    mouse_distance = distance(sling_x, sling_y, x_mouse, y_mouse)
    max_stretch = (unit_v[0]*rope_length+sling_x, unit_v[1]*rope_length+sling_y)
    x_redbird = x_mouse - 20
    y_redbird = y_mouse - 20
    if mouse_distance > rope_length:
        mouse_distance = rope_length
        x_redbird = unit_v[0]*rope_length+sling_x - 20
        y_redbird = unit_v[1]*rope_length+sling_y - 20
    pg.draw.line(screen, BLACK, (sling2_x , sling2_y), (unit_v[0]*(mouse_distance+10)+sling_x, unit_v[1]*(mouse_distance+10)+sling_y) , 5)
    screen.blit(redbird, (x_redbird , y_redbird))
    pg.draw.line(screen, BLACK, (sling_x, sling_y), (unit_v[0]*(mouse_distance+10)+sling_x, unit_v[1]*(mouse_distance+10)+sling_y), 5)
    # Angle of impulse
    dy = y_mouse - sling_y
    dx = x_mouse - sling_center
    if dx == 0:
        dx = 0.00000000000001
    angle = math.atan2(dy,dx) + math.pi
    if angle > math.pi:
        angle -= 2 * math.pi
    angle = max(-math.pi/2, min(math.pi/2, angle))
    speed = (mouse_distance * 53) / 5       # In pymunk: speed = magnitude of impulse / mass
    g = abs(space.gravity[1])
    vx = speed * math.cos(-angle)
    vy = speed * math.sin(-angle)
    if mouse_distance > 10:
        start_x, start_y = sling_center, sling_y
        for step in range(0, 600):
            t = step / 40
            x = start_x + vx * t
            y = start_y + (-vy) * t + 0.5 * g * (t ** 2)
            if y > screenHeight - 60:
                break
            pg.draw.circle(screen, (255, 255, 0), (int(x), int(y)), 3)

    if speed == 0:
        speed = 0.000000000000001
    Range = (vx / g) * ((vy + math.sqrt(vy**2 + 2 * g * (200-110))))

    landing_x = sling_center + Range
    ground_y = screenHeight - 110
    pg.draw.line(screen, RED, (sling_center, ground_y + 15), (landing_x, ground_y + 15), 2)
    pg.draw.line(screen, RED, (landing_x, ground_y), (landing_x, ground_y + 40), 3)

    Height = (vy**2)/(2*g)
    x_Height = (vx * vy)/g + sling_center
    if -angle < 0:
        Height = 0
        x_Height = sling_center
    pg.draw.line(screen , BLUE , (x_Height , 540) , (x_Height , 450 - Height) , 3)

def bird_landed(arbiter, space, data):
    global bird_in_air
    bird_in_air = False

def bird_collided(arbiter, space, data):
    global bird_hit
    bird_hit = True

# If bird touches anything then timer of Time of Flight stops
handler1 = space.on_collision(0, 0, begin = bird_collided)
handler2 = space.on_collision(0, 1, begin = bird_collided)
handler3 = space.on_collision(0, 2, begin = bird_collided)
handler4 = space.on_collision(0, 3, begin = bird_landed)

def draw_level_cleared():
    """Draw level cleared"""
    global game_state
    global bonus_score_once
    global score
    level_cleared = bold_font3.render("Level Cleared!", 1, WHITE)
    score_level_cleared = bold_font2.render(str(score), 1, WHITE)
    if level.is_practice:
        return
    if level.number_of_birds >= 0 and len(pigs) == 0:
        if bonus_score_once:
            score += (level.number_of_birds-1) * 10000
            bonus_score_once = False
        game_state = 4
        rect = pg.Rect(300, 0, 600, 800)
        pg.draw.rect(screen, BLACK, rect)
        screen.blit(level_cleared, (450, 90))
        if score >= level.one_star and score <= level.two_star:
            screen.blit(star1, (310, 190))
        if score >= level.two_star and score <= level.three_star:
            screen.blit(star1, (310, 190))
            screen.blit(star2, (500, 170))
        if score >= level.three_star:
            screen.blit(star1, (310, 190))
            screen.blit(star2, (500, 170))
            screen.blit(star3, (700, 200))
        screen.blit(score_level_cleared, (550, 400))
        screen.blit(replay_button, (510, 480))
        screen.blit(next_button, (620, 480))


def draw_level_failed():
    """Draw level failed"""
    global game_state
    failed = bold_font3.render("Level Failed", 1, WHITE)
    if level.number_of_birds <= 0 and time.time() - t2 > 5 and len(pigs) > 0:
        game_state = 3
        rect = pg.Rect(300, 0, 600, 800)
        pg.draw.rect(screen, BLACK, rect)
        screen.blit(failed, (450, 90))
        screen.blit(happy_pig, (380, 120))
        screen.blit(replay_button, (520, 460))


def restart():
    """Delete all objects of the level"""
    pigs_to_remove = []
    birds_to_remove = []
    columns_to_remove = []
    beams_to_remove = []
    for pig in pigs:
        pigs_to_remove.append(pig)
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)
    for bird in birds:
        birds_to_remove.append(bird)
    for bird in birds_to_remove:
        space.remove(bird.shape, bird.shape.body)
        birds.remove(bird)
    for column in columns:
        columns_to_remove.append(column)
    for column in columns_to_remove:
        space.remove(column.shape, column.shape.body)
        columns.remove(column)
    for beam in beams:
        beams_to_remove.append(beam)
    for beam in beams_to_remove:
        space.remove(beam.shape, beam.shape.body)
        beams.remove(beam)


def post_solve_bird_pig(arbiter, space, _):
    """Collision between bird and pig"""
    surface=screen
    a, b = arbiter.shapes
    bird_body = a.body
    pig_body = b.body
    p = to_pg(bird_body.position)
    p2 = to_pg(pig_body.position)
    r = 30
    pg.draw.circle(surface, BLACK, p, r, 4)
    pg.draw.circle(surface, RED, p2, r, 4)
    pigs_to_remove = []
    for pig in pigs:
        if pig_body == pig.body:
            pig.life -= 20
            pigs_to_remove.append(pig)
            global score
            score += 10000
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)


def post_solve_bird_wood(arbiter, space, _):
    """Collision between bird and wood"""
    poly_to_remove = []
    if arbiter.total_impulse.length > 1100:
        a, b = arbiter.shapes
        for column in columns:
            if b == column.shape:
                poly_to_remove.append(column)
        for beam in beams:
            if b == beam.shape:
                poly_to_remove.append(beam)
        for poly in poly_to_remove:
            if poly in columns:
                columns.remove(poly)
            if poly in beams:
                beams.remove(poly)
        space.remove(b, b.body)
        global score
        score += 5000


def post_solve_pig_wood(arbiter, space, _):
    """Collision between pig and wood"""
    pigs_to_remove = []
    if arbiter.total_impulse.length > 700:
        pig_shape, wood_shape = arbiter.shapes
        for pig in pigs:
            if pig_shape == pig.shape:
                pig.life -= 20
                global score
                score += 10000
                if pig.life <= 0:
                    pigs_to_remove.append(pig)
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)


# bird and pigs
space.on_collision(0, 1 , None , None , post_solve=post_solve_bird_pig)
# bird and wood
space.on_collision(0, 2 , None , None , post_solve=post_solve_bird_wood)
# pig and wood
space.on_collision(1, 2 , None , None , post_solve=post_solve_pig_wood)
level = Level(pigs, columns, beams, space)
level.number = 0
level.load_level()

while True:
    # Input handling
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            pg.quit()
            sys.exit()

        elif event.type == pg.KEYDOWN and event.key == pg.K_i:
            level.number = -1
            level.load_level()
        elif event.type == pg.KEYDOWN and event.key == pg.K_w:
            # Toggle wall
            if wall:
                space.remove(rightWall)
                wall = False
            else:
                space.add(rightWall)
                wall = True

        elif event.type == pg.KEYDOWN and event.key == pg.K_s:
            space.gravity = (0.0, -10.0)
            level.bool_space = True
        elif event.type == pg.KEYDOWN and event.key == pg.K_n:
            space.gravity = (0.0, -700.0)
            level.bool_space = False
        if (pg.mouse.get_pressed()[0] and x_mouse > 100 and x_mouse < 250 and y_mouse > 370 and y_mouse < 550):
            mouse_pressed = True
        if (event.type == pg.MOUSEBUTTONUP and event.button == 1 and mouse_pressed):
            # Release new bird
            mouse_pressed = False
            bird_in_air = True
            bird_hit = False
            launch_time = time.time()
            time_of_flight = 0
            if level.number_of_birds > 0:
                level.number_of_birds -= 1
                t1 = time.time()*1000
                xo = sling_center
                yo = 156
                if mouse_distance > rope_length:
                    mouse_distance = rope_length
                if x_mouse < sling_x + 5:
                    bird = Bird(mouse_distance, angle, xo, yo, space)
                    birds.append(bird)
                else:
                    bird = Bird(-mouse_distance, angle, xo, yo, space)
                    birds.append(bird)
                if level.number_of_birds == 0:
                    t2 = time.time()

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if (x_mouse < 60 and y_mouse < 155 and y_mouse > 90):
                game_state = 1
            if game_state == 1:
                if x_mouse > 500 and y_mouse > 200 and y_mouse < 300:
                    # Resume in the paused screen
                    game_state = 0
                if x_mouse > 500 and y_mouse > 300:
                    # Restart in the paused screen
                    restart()
                    level.load_level()
                    game_state = 0
                    bird_path = []
            if game_state == 3:
                # Restart in the failed level screen
                if x_mouse > 500 and x_mouse < 620 and y_mouse > 450:
                    restart()
                    level.load_level()
                    game_state = 0
                    bird_path = []
                    score = 0
            if game_state == 4:
                # Build next level
                if x_mouse > 610 and y_mouse > 450:
                    restart()
                    level.number += 1
                    game_state = 0
                    level.load_level()
                    score = 0
                    bird_path = []
                    bonus_score_once = True
                if x_mouse < 610 and x_mouse > 500 and y_mouse > 450:
                    # Restart in the level cleared screen
                    restart()
                    level.load_level()
                    game_state = 0
                    bird_path = []
                    score = 0

    if bird_in_air and not bird_hit:
        time_of_flight = time.time() - launch_time

    # for slowing down the bird when it touches the ground
    if not bird_in_air and birds:
        for bird in birds:
            if bird.body.velocity.length > 5:
                vx, vy = bird.body.velocity
                bird.body.velocity = vx * 0.9, vy
            else:
                bird.body.velocity = (0,vy)

    x_mouse, y_mouse = pg.mouse.get_pos()
    # Draw background
    screen.fill((130, 200, 100))
    screen.blit(background2, (0, -50))

    # Draw first part of the sling
    rect = pg.Rect(50, 0, 70, 220)
    screen.blit(sling_image, (138, 420), rect)
    # Drawing second part of the sling
    rect = pg.Rect(0, 0, 60, 200)
    screen.blit(sling_image, (120, 420), rect)
    # Draw the trail left behind
    for point in bird_path:
        pg.draw.circle(screen, WHITE, point, 3, 0)
    # Draw the birds in the wait line
    if level.number_of_birds > 0:
        for i in range(level.number_of_birds-1):
            x = 100 - (i*35)
            screen.blit(redbird, (x, 508))
    # Draw sling behavior
    if mouse_pressed and level.number_of_birds > 0:
        sling_action()

    else:
        if time.time()*1000 - t1 > 300 and level.number_of_birds > 0:
            screen.blit(redbird, (130, 426))
        else:
            pg.draw.line(screen, (0, 0, 0), (sling_x, sling_y-18),
                             (sling2_x, sling2_y-7), 5)

    birds_to_remove = []
    pigs_to_remove = []
    counter += 1
    # Draw birds
    for bird in birds:
        if bird.shape.body.position.y < 0:
            birds_to_remove.append(bird)
        p = to_pg(bird.shape.body.position)
        x, y = p
        x -= 22
        y -= 20
        screen.blit(redbird, (x, y))
        if counter >= 3 and time.time() - t1 < 5 and not bird.body.velocity.length == 0:
            bird_path.append(p)
            restart_counter = True
    if restart_counter:
        counter = 0
        restart_counter = False
    # Remove birds and pigs
    for bird in birds_to_remove:
        space.remove(bird.shape, bird.shape.body)
        birds.remove(bird)
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)
    # Draw static lines
    body = ground.body
    pv1 = body.position + ground.a.rotated(body.angle)
    pv2 = body.position + ground.b.rotated(body.angle)
    p1 = to_pg(pv1)
    p2 = to_pg(pv2)
    pg.draw.lines(screen, (150, 150, 150), False, [p1, p2])
    i = 0
    # Draw pigs
    for pig in pigs:
        i += 1
        pig = pig.shape
        if pig.body.position.y < 0:
            pigs_to_remove.append(pig)

        p = to_pg(pig.body.position)
        x, y = p
        angle_degrees = math.degrees(pig.body.angle)
        img = pg.transform.rotate(pig_image, angle_degrees)
        w, h = img.get_size()
        x -= w * 0.5
        y -= h * 0.5
        screen.blit(img, (x, y))

    # Showing physical quantities
    angle_bird_degrees = math.degrees(angle)
    angle_surface = quantity_font.render(f"Launch Angle: {-angle_bird_degrees:.2f}°", True, (0, 0, 0))
    angle_rect = angle_surface.get_rect()
    angle_rect.x , angle_rect.y = 80, 80
    screen.blit(angle_surface, angle_rect)

    speed_surface = quantity_font.render(f"Launch Speed: {(speed/PPM):.2f} m/s OR {((speed/PPM)*3.6):.2f} km/h" , True , (0,0,0))
    speed_rect = speed_surface.get_rect()
    speed_rect.x , speed_rect.y = 80 , 115
    screen.blit(speed_surface , speed_rect)

    range_surface = quantity_font.render(f"Range: {(Range/PPM):.2f} m", True, (0, 0, 0))
    range_rect = range_surface.get_rect()
    range_rect.x , range_rect.y = 80 , 150
    screen.blit(range_surface , range_rect)

    height_surface = quantity_font.render(f"Maximum Height: {((Height+90)/PPM):.2f} m", True, (0, 0, 0))
    height_rect = height_surface.get_rect()
    height_rect.x, height_rect.y = 80, 185
    screen.blit(height_surface, height_rect)

    tof_surface = quantity_font.render(f"Time of Flight: {time_of_flight:.2f}s", True, BLACK)
    tof_rect = tof_surface.get_rect()
    tof_rect.x , tof_rect.y = 80 , 220
    screen.blit(tof_surface, tof_rect)

    # Draw columns and Beams
    for column in columns:
        column.draw_poly('columns', screen)
    for beam in beams:
        beam.draw_poly('beams', screen)
    # Update physics
    dt = 1.0/60.0/2.
    for x in range(2):
        space.step(dt) # Make two updates per frame for better stability

    # Draw score
    score_font = bold_font.render("SCORE", 1, WHITE)
    number_font = bold_font.render(str(score), 1, WHITE)
    screen.blit(score_font, (1060, 90))
    if score == 0:
        screen.blit(number_font, (1100, 130))
    else:
        screen.blit(number_font, (1060, 130))
    screen.blit(pause_button, (10, 90))
    # Pause option
    if game_state == 1:
        screen.blit(play_button, (500, 200))
        screen.blit(replay_button, (500, 300))

    draw_level_cleared()
    draw_level_failed()
    pg.display.update()
    clock.tick(FPS)
