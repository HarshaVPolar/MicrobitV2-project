from microbit import *
import radio

# Clear the display and show we're starting
display.clear()
display.scroll("Battleship")

# Initialize radio with higher power for reliability
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

# Initialize game variables
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

# Ship lengths
ship_lengths = [2, 3, 3]  # Place smallest ship first

# Create 5x5 grids
my_ships = []
enemy_attacks = []
my_attacks = []

for i in range(5):
    my_ships.append([0, 0, 0, 0, 0])
    enemy_attacks.append([0, 0, 0, 0, 0])
    my_attacks.append([0, 0, 0, 0, 0])

def can_place_ship(length):
    for i in range(length):
        nx = cursor_x
        ny = cursor_y
        
        if direction == RIGHT:
            nx = nx + i
        elif direction == DOWN:
            ny = ny + i
        elif direction == LEFT:
            nx = nx - i
        else:  # UP
            ny = ny - i
            
        # Check if position is outside grid
        if nx < 0 or nx >= 5 or ny < 0 or ny >= 5:
            return False
            
        # Check if position already has a ship
        if my_ships[ny][nx] == 1:
            return False
            
    return True

def place_ship(length):
    global total_ship_cells
    for i in range(length):
        nx = cursor_x
        ny = cursor_y
        
        if direction == RIGHT:
            nx = nx + i
        elif direction == DOWN:
            ny = ny + i
        elif direction == LEFT:
            nx = nx - i
        else:  # UP
            ny = ny - i
            
        my_ships[ny][nx] = 1
        total_ship_cells += 1

def display_grid():
    display.clear()
    
    # Always show ships in placement phase
    if game_state == PLACING_SHIPS or game_state == WAITING_READY:
        for y in range(5):
            for x in range(5):
                if my_ships[y][x] == 1:
                    display.set_pixel(x, y, 5)  # Medium brightness for ships
    
    # In battle phase, show either attack or defense map
    elif game_state == MY_TURN or game_state == ENEMY_TURN:
        if pin_logo.is_touched():
            # Defense map (my ships and enemy attacks)
            for y in range(5):
                for x in range(5):
                    if my_ships[y][x] == 1:
                        if enemy_attacks[y][x] == 1:
                            display.set_pixel(x, y, 9)  # Hit ship
                        else:
                            display.set_pixel(x, y, 5)  # Unhit ship
                    elif enemy_attacks[y][x] == 1:
                        display.set_pixel(x, y, 2)  # Miss
        else:
            # Attack map (where I've bombed)
            for y in range(5):
                for x in range(5):
                    if my_attacks[y][x] == 2:
                        display.set_pixel(x, y, 9)  # Hit
                    elif my_attacks[y][x] == 1:
                        display.set_pixel(x, y, 2)  # Miss
            
            # Show cursor in attack map only during my turn
            if cursor_blink and game_state == MY_TURN:
                display.set_pixel(cursor_x, cursor_y, 7)

    # Show preview in ship placement
    if game_state == PLACING_SHIPS and current_ship_index < len(ship_lengths):
        length = ship_lengths[current_ship_index]
        brightness = 7 if can_place_ship(length) else 3
        
        for i in range(length):
            nx = cursor_x
            ny = cursor_y
            
            if direction == RIGHT:
                nx = nx + i
            elif direction == DOWN:
                ny = ny + i
            elif direction == LEFT:
                nx = nx - i
            else:  # UP
                ny = ny - i
                
            if 0 <= nx < 5 and 0 <= ny < 5:
                display.set_pixel(nx, ny, brightness)
    
    # Waiting indicator
    if game_state == WAITING_READY and cursor_blink:
        display.set_pixel(2, 2, 9)
    
    # Show turn indicator
    if game_state == MY_TURN:
        display.set_pixel(0, 0, 9)  # Bright pixel in top-left
    elif game_state == ENEMY_TURN:
        display.set_pixel(4, 0, 9)  # Bright pixel in top-right
    
    # Game over state
    if game_state == GAME_OVER:
        if my_hits >= total_ship_cells:
            display.scroll("You win!")
        else:
            display.scroll("You lose!")

# Handle incoming radio messages
def check_radio():
    global opponent_ready, game_state, enemy_hits, my_hits
    
    message = radio.receive()
    if message:
        # Ready message
        if message == "ready":
            opponent_ready = True
            if i_am_ready and game_state == WAITING_READY:
                # Randomly decide who goes first
                if running_time() % 2 == 0:
                    game_state = MY_TURN
                    display.scroll("Your turn!")
                else:
                    game_state = ENEMY_TURN
                    display.scroll("Wait...")
        
        # Attack message
        elif message.startswith("attack:"):
            parts = message.split(":")
            try:
                x = int(parts[1])
                y = int(parts[2])
                
                # Check if bomb hit any of our ships
                hit = False
                if 0 <= x < 5 and 0 <= y < 5:
                    if my_ships[y][x] == 1 and enemy_attacks[y][x] == 0:
                        hit = True
                        enemy_hits += 1
                
                # Mark enemy attack
                enemy_attacks[y][x] = 1
                
                # Send result back
                if hit:
                    radio.send("hit:" + str(x) + ":" + str(y))
                else:
                    radio.send("miss:" + str(x) + ":" + str(y))
                
                # Check for game over
                if enemy_hits >= total_ship_cells:
                    game_state = GAME_OVER
                    radio.send("gameover")
                else:
                    # Switch to my turn
                    game_state = MY_TURN
            except:
                pass
        
        # Results messages
        elif message.startswith("hit:") or message.startswith("miss:"):
            parts = message.split(":")
            if len(parts) == 3:
                try:
                    hit = (parts[0] == "hit")
                    x = int(parts[1])
                    y = int(parts[2])
                    
                    # Update my attacks map
                    my_attacks[y][x] = 2 if hit else 1
                    
                    if hit:
                        my_hits += 1
                        # Check for win
                        if my_hits >= total_ship_cells:
                            game_state = GAME_OVER
                            radio.send("gameover")
                        else:
                            # Get another turn on hit
                            game_state = MY_TURN
                    else:
                        # Switch to enemy turn on miss
                        game_state = ENEMY_TURN
                except:
                    pass
        
        # Game over message
        elif message == "gameover":
            game_state = GAME_OVER

# Main game loop
while True:
    # Handle shake gesture
    if accelerometer.was_gesture("shake") and shake_cooldown <= 0:
        shake_cooldown = 10  # Prevent multiple triggers
        
        if game_state == PLACING_SHIPS:
            # Try to place ship
            if current_ship_index < len(ship_lengths):
                length = ship_lengths[current_ship_index]
                if can_place_ship(length):
                    place_ship(length)
                    current_ship_index += 1
                    
                    # If all ships placed, move to ready state
                    if current_ship_index >= len(ship_lengths):
                        game_state = WAITING_READY
                        radio.send("ready")
                        i_am_ready = True
                        display.scroll("Ready!")
        
        elif game_state == MY_TURN:
            # Only bomb if we haven't bombed this spot before
            if my_attacks[cursor_y][cursor_x] == 0:
                # Send bomb coordinates
                radio.send("attack:" + str(cursor_x) + ":" + str(cursor_y))
                game_state = ENEMY_TURN  # Wait for response
    
    # Handle cursor movement with buttons
    if button_a.was_pressed():
        if game_state == PLACING_SHIPS:
            # In ship placement, move based on direction
            if direction == RIGHT:
                cursor_x = (cursor_x + 1) % 5
            elif direction == DOWN:
                cursor_y = (cursor_y + 1) % 5
            elif direction == LEFT:
                cursor_x = (cursor_x - 1) % 5
            else:  # UP
                cursor_y = (cursor_y - 1) % 5
        elif game_state == MY_TURN:
            # In attack phase, move cursor horizontally
            cursor_x = (cursor_x + 1) % 5
    
    if button_b.was_pressed():
        if game_state == PLACING_SHIPS:
            # Change ship direction in placement phase
            direction = (direction + 1) % 4
        elif game_state == WAITING_READY:
            # Send ready signal again
            radio.send("ready")
            i_am_ready = True
            if opponent_ready:
                # Randomly decide who goes first
                if running_time() % 2 == 0:
                    game_state = MY_TURN
                    display.scroll("Your turn!")
                else:
                    game_state = ENEMY_TURN
                    display.scroll("Wait...")
        elif game_state == MY_TURN:
            # In attack phase, move cursor vertically
            cursor_y = (cursor_y + 1) % 5
        elif game_state == GAME_OVER:
            # Reset game
            display.scroll("New game")
            # Reset logic would go here
            # For now, just reset the device
            reset()
    
    # Update display
    display_grid()
    
    # Check for radio messages
    check_radio()
    
    # Blink cursor
    cursor_blink = not cursor_blink
    
    # Update cooldown
    if shake_cooldown > 0:
        shake_cooldown -= 1
    
    # Brief delay
    sleep(100)