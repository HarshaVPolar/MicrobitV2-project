from microbit import *
import radio

# Clear the display and show we're starting
display.clear()
display.scroll("BattleShip")

# Initialize radio with higher power and shorter range for more reliable communication
radio.on()
radio.config(group=1, power=7)

# Game states
PLACING_SHIPS = 0
WAITING_READY = 1
BATTLE = 2

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

# Ship lengths
ship_lengths = [2, 3, 3]  # Reversed order: place smallest ship first

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

def display_grid():
    display.clear()
    
    # Always show ships in placement phase
    if game_state == PLACING_SHIPS or game_state == WAITING_READY:
        for y in range(5):
            for x in range(5):
                if my_ships[y][x] == 1:
                    display.set_pixel(x, y, 5)  # Medium brightness for ships
    
    # In battle phase, show either attack or defense map
    elif game_state == BATTLE:
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
            
            # Show cursor in attack map only
            if cursor_blink and game_state == BATTLE:
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
    
    # Blinking waiting indicator
    if game_state == WAITING_READY:
        # Blink center pixel when waiting
        if cursor_blink:
            display.set_pixel(2, 2, 9)

# Function to handle incoming radio messages
def check_radio():
    global opponent_ready, game_state
    
    message = radio.receive()
    if message:
        # Ready message
        if message == "ready":
            opponent_ready = True
            if i_am_ready and game_state == WAITING_READY:
                game_state = BATTLE
                display.scroll("BATTLE!")
        
        # Attack message
        elif "," in message and len(message.split(",")) == 2:
            parts = message.split(",")
            try:
                x = int(parts[0])
                y = int(parts[1])
                
                # Check if bomb hit any of our ships
                hit = False
                if 0 <= x < 5 and 0 <= y < 5 and my_ships[y][x] == 1:
                    hit = True
                
                # Mark enemy attack
                enemy_attacks[y][x] = 1
                
                # Send result back
                if hit:
                    radio.send("hit," + str(x) + "," + str(y))
                else:
                    radio.send("miss," + str(x) + "," + str(y))
            except:
                pass
        
        # Results messages
        elif message.startswith("hit,") or message.startswith("miss,"):
            parts = message.split(",")
            if len(parts) == 3:
                try:
                    hit = (parts[0] == "hit")
                    x = int(parts[1])
                    y = int(parts[2])
                    
                    # Update my attacks map
                    my_attacks[y][x] = 2 if hit else 1
                except:
                    pass

# Main game loop
while True:
    # Button A pressed - move cursor
    if button_a.was_pressed():
        if direction == RIGHT:
            cursor_x = (cursor_x + 1) % 5
        elif direction == DOWN:
            cursor_y = (cursor_y + 1) % 5
        elif direction == LEFT:
            cursor_x = (cursor_x - 1) % 5
        else:  # UP
            cursor_y = (cursor_y - 1) % 5
    
    # Button B pressed - change direction (placement phase only)
    if button_b.was_pressed() and game_state == PLACING_SHIPS:
        direction = (direction + 1) % 4
    
    # Both buttons pressed
    if button_a.is_pressed() and button_b.is_pressed():
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
        
        elif game_state == WAITING_READY:
            # Send ready signal again
            radio.send("ready")
            i_am_ready = True
            if opponent_ready:
                game_state = BATTLE
                display.scroll("BATTLE!")
        
        elif game_state == BATTLE:
            # Only bomb if we haven't bombed this spot before
            if my_attacks[cursor_y][cursor_x] == 0:
                # Send bomb coordinates
                radio.send(str(cursor_x) + "," + str(cursor_y))
        
        # Wait until both buttons are released
        while button_a.is_pressed() or button_b.is_pressed():
            sleep(50)
    
    # Update display
    display_grid()
    
    # Check for radio messages
    check_radio()
    
    # Blink cursor
    cursor_blink = not cursor_blink
    
    # Brief delay
    sleep(100)