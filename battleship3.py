from microbit import *
import radio

# Clear the display and show we're starting
display.clear()
display.scroll("Battleship")

# Initialize radio
radio.on()
radio.config(group=1, power=7)

# Game states
PLACING_SHIPS = 0
WAITING_READY = 1
MY_TURN = 2
ENEMY_TURN = 3
GAME_OVER = 4

# Direction constants
RIGHT = 0
DOWN = 1
LEFT = 2
UP = 3

# Initialize variables
game_state = PLACING_SHIPS
cursor_x = 2
cursor_y = 2
direction = RIGHT
cursor_blink = True
current_ship_index = 0
opponent_ready = False
i_am_ready = False
my_hits = 0
enemy_hits = 0
total_ship_cells = 0
shake_cooldown = 0
waiting_for_attack_result = False  # IMPORTANT

# Ship lengths
ship_lengths = [2, 3, 3]

# Create 5x5 grids
my_ships = [[0]*5 for _ in range(5)]
enemy_attacks = [[0]*5 for _ in range(5)]
my_attacks = [[0]*5 for _ in range(5)]

def can_place_ship(length):
    for i in range(length):
        nx, ny = cursor_x, cursor_y
        if direction == RIGHT:
            nx += i
        elif direction == DOWN:
            ny += i
        elif direction == LEFT:
            nx -= i
        elif direction == UP:
            ny -= i
        if not (0 <= nx < 5 and 0 <= ny < 5):
            return False
        if my_ships[ny][nx] == 1:
            return False
    return True

def place_ship(length):
    global total_ship_cells
    for i in range(length):
        nx, ny = cursor_x, cursor_y
        if direction == RIGHT:
            nx += i
        elif direction == DOWN:
            ny += i
        elif direction == LEFT:
            nx -= i
        elif direction == UP:
            ny -= i
        my_ships[ny][nx] = 1
        total_ship_cells += 1

def display_grid():
    display.clear()
    
    if game_state in [PLACING_SHIPS, WAITING_READY]:
        for y in range(5):
            for x in range(5):
                if my_ships[y][x] == 1:
                    display.set_pixel(x, y, 5)

    elif game_state in [MY_TURN, ENEMY_TURN]:
        if pin_logo.is_touched():
            # Defense map
            for y in range(5):
                for x in range(5):
                    if my_ships[y][x] == 1:
                        if enemy_attacks[y][x] == 1:
                            display.set_pixel(x, y, 9)  # Hit
                        else:
                            display.set_pixel(x, y, 5)  # Safe
                    elif enemy_attacks[y][x] == 1:
                        display.set_pixel(x, y, 2)  # Miss
        else:
            # Attack map
            for y in range(5):
                for x in range(5):
                    if my_attacks[y][x] == 2:
                        display.set_pixel(x, y, 9)  # Hit
                    elif my_attacks[y][x] == 1:
                        display.set_pixel(x, y, 2)  # Miss

            # Always show cursor during MY_TURN
            if cursor_blink and game_state == MY_TURN:
                display.set_pixel(cursor_x, cursor_y, 7)

    # Preview placement
    if game_state == PLACING_SHIPS and current_ship_index < len(ship_lengths):
        length = ship_lengths[current_ship_index]
        brightness = 7 if can_place_ship(length) else 3
        for i in range(length):
            nx, ny = cursor_x, cursor_y
            if direction == RIGHT:
                nx += i
            elif direction == DOWN:
                ny += i
            elif direction == LEFT:
                nx -= i
            elif direction == UP:
                ny -= i
            if 0 <= nx < 5 and 0 <= ny < 5:
                display.set_pixel(nx, ny, brightness)

    if game_state == WAITING_READY and cursor_blink:
        display.set_pixel(2, 2, 9)
    
    if game_state == MY_TURN:
        display.set_pixel(0, 0, 9)
    elif game_state == ENEMY_TURN:
        display.set_pixel(4, 0, 9)

    if game_state == GAME_OVER:
        if my_hits >= total_ship_cells:
            display.scroll("You win!")
        else:
            display.scroll("You lose!")

def check_radio():
    global opponent_ready, game_state, enemy_hits, my_hits, waiting_for_attack_result

    message = radio.receive()
    if message:
        if message == "ready":
            opponent_ready = True
            if i_am_ready and game_state == WAITING_READY:
                if running_time() % 2 == 0:
                    game_state = MY_TURN
                    display.scroll("Your turn")
                else:
                    game_state = ENEMY_TURN
                    display.scroll("Wait")

        elif message.startswith("attack:"):
            parts = message.split(":")
            try:
                x, y = int(parts[1]), int(parts[2])
                hit = False
                if 0 <= x < 5 and 0 <= y < 5:
                    if my_ships[y][x] == 1 and enemy_attacks[y][x] == 0:
                        hit = True
                        enemy_hits += 1
                enemy_attacks[y][x] = 1
                if hit:
                    radio.send("hit:{}:{}".format(x, y))
                else:
                    radio.send("miss:{}:{}".format(x, y))
                
                if enemy_hits >= total_ship_cells:
                    game_state = GAME_OVER
                    radio.send("gameover")
                else:
                    game_state = MY_TURN
            except:
                pass

        elif message.startswith("hit:") or message.startswith("miss:"):
            parts = message.split(":")
            if len(parts) == 3:
                try:
                    hit = (parts[0] == "hit")
                    x, y = int(parts[1]), int(parts[2])
                    my_attacks[y][x] = 2 if hit else 1

                    waiting_for_attack_result = False  # Attack done
                    
                    if hit:
                        my_hits += 1
                        if my_hits >= total_ship_cells:
                            game_state = GAME_OVER
                            radio.send("gameover")
                        else:
                            game_state = MY_TURN  # get extra chance
                    else:
                        game_state = ENEMY_TURN  # switch to enemy
                except:
                    pass

        elif message == "gameover":
            game_state = GAME_OVER

# Main loop
while True:
    if accelerometer.was_gesture("shake") and shake_cooldown <= 0:
        shake_cooldown = 10
        if game_state == PLACING_SHIPS:
            if current_ship_index < len(ship_lengths):
                length = ship_lengths[current_ship_index]
                if can_place_ship(length):
                    place_ship(length)
                    current_ship_index += 1
                    if current_ship_index >= len(ship_lengths):
                        game_state = WAITING_READY
                        i_am_ready = True
                        radio.send("ready")
                        display.scroll("Ready")

        elif game_state == MY_TURN and not waiting_for_attack_result:
            if my_attacks[cursor_y][cursor_x] == 0:
                radio.send("attack:{}:{}".format(cursor_x, cursor_y))
                waiting_for_attack_result = True

    # Button controls
    if button_a.was_pressed():
        if game_state == PLACING_SHIPS:
            if direction == RIGHT:
                cursor_x = (cursor_x + 1) % 5
            elif direction == DOWN:
                cursor_y = (cursor_y + 1) % 5
            elif direction == LEFT:
                cursor_x = (cursor_x - 1) % 5
            elif direction == UP:
                cursor_y = (cursor_y - 1) % 5
        elif game_state == MY_TURN:
            cursor_x = (cursor_x + 1) % 5

    if button_b.was_pressed():
        if game_state == PLACING_SHIPS:
            direction = (direction + 1) % 4
        elif game_state == WAITING_READY:
            radio.send("ready")
            i_am_ready = True
            if opponent_ready:
                if running_time() % 2 == 0:
                    game_state = MY_TURN
                    display.scroll("Your turn")
                else:
                    game_state = ENEMY_TURN
                    display.scroll("Wait")
        elif game_state == MY_TURN:
            cursor_y = (cursor_y + 1) % 5
        elif game_state == GAME_OVER:
            display.scroll("New Game")
            reset()

    display_grid()
    check_radio()

    cursor_blink = not cursor_blink
    if shake_cooldown > 0:
        shake_cooldown -= 1
    sleep(100)
