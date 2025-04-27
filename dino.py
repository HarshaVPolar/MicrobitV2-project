import random
from microbit import *
import music

# ——— Game Variables ———
ground_y = 3       # top row of the 2-pixel dino
dino_y = ground_y  # current dino y position
velocity = 0
gravity = 0.2
jump_force = -1.4
is_jumping = False
is_bending = False
obstacle_x = 5
bird_obstacle = False
bird_y = 0
score = 0
frame_counter = 0
speed = 150

def draw_dino():
    display.clear()  # Ensure we clear the display before drawing
    y = int(dino_y) if is_jumping else ground_y
    if is_bending:
        display.set_pixel(0, 4, 9)  # Crouching dino (one pixel)
    else:
        display.set_pixel(0, y, 9)  # Standing dino (two pixels)
        display.set_pixel(0, y + 1, 9)

def draw_obstacle():
    if 0 <= obstacle_x <= 4:
        if bird_obstacle:
            display.set_pixel(obstacle_x, bird_y, 7)
            if obstacle_x - 1 >= 0:
                display.set_pixel(obstacle_x - 1, bird_y, 7)
        else:
            display.set_pixel(obstacle_x, 4, 9)  # Tree base
            display.set_pixel(obstacle_x, 3, 7)  # Tree trunk
            if obstacle_x - 1 >= 0:              # Left branch
                display.set_pixel(obstacle_x - 1, 3, 7)
            if obstacle_x + 1 <= 4:              # Right branch
                display.set_pixel(obstacle_x + 1, 3, 7)

def check_collision():
    if 0 <= obstacle_x <= 1:
        dino_top = int(dino_y)
        dino_bottom = dino_top + (0 if is_bending else 1)
        
        if bird_obstacle:
            return (bird_y == dino_top or bird_y == dino_bottom)
        else:
            if obstacle_x == 0:
                if dino_bottom == 4:
                    return True
                if dino_top == 3 or dino_bottom == 3:
                    return True
            elif obstacle_x == 1:
                if dino_top == 3 or dino_bottom == 3:
                    return True
    return False

def reset_game():
    global dino_y, velocity, is_jumping, is_bending
    global obstacle_x, bird_obstacle, bird_y
    global score, frame_counter, speed
    
    dino_y = ground_y
    velocity = 0
    is_jumping = is_bending = False
    obstacle_x = 5
    bird_obstacle = False
    bird_y = 0
    score = frame_counter = 0
    speed = 150
    
    display.clear()
    music.play(music.POWER_UP)
    display.scroll("DINO")

# ——— Main Loop ———
reset_game()

while True:
    # Check crouch state only if not jumping
    is_bending = button_b.is_pressed() and not is_jumping

    # Jump input (shout or button)
    sound = microphone.sound_level()
    if (sound > 125 or button_a.was_pressed()) and not is_jumping and not is_bending:
        is_jumping = True
        velocity = jump_force
        music.pitch(440, 100)
    
    # Physics update
    if is_jumping:
        dino_y += velocity
        velocity += gravity
        
        # Land or hit ceiling
        if dino_y >= ground_y:
            dino_y = ground_y
            is_jumping = False
        elif dino_y < 0:
            dino_y = 0
    
    # Move obstacle
    frame_counter += 1
    if frame_counter >= 3:
        obstacle_x -= 1
        frame_counter = 0
    
    # Respawn obstacle
    if obstacle_x < -2:
        obstacle_x = 5 + random.randint(0, 1)
        bird_obstacle = random.choice([True, False])
        bird_y = random.choice([2, 3]) if bird_obstacle else 0
        score += 1
        music.pitch(660, 80)
        
        # Speed up every 5 points
        if score % 5 == 0 and speed > 60:
            speed -= 10
    
    # Draw game elements
    draw_dino()
    draw_obstacle()
    
    # Check collision
    if check_collision():
        music.pitch(220, 400)
        display.scroll("Score: " + str(score))
        reset_game()
    
    sleep(speed)