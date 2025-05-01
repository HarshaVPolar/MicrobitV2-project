from microbit import *
import radio
import time
import random

# --- Globals ---
board = [[0 for _ in range(5)] for _ in range(5)]  # Your board
enemy_board = [[0 for _ in range(5)] for _ in range(5)]  # What you know about opponent
ships = [4, 3, 2]  # Ship sizes
turn = False  # Whether it's your turn
reaction_timer = 0  # To time the happy/sad face

# --- Functions ---
def random_board():
    temp_board = [[0 for _ in range(5)] for _ in range(5)]
    for size in ships:
        placed = False
        while not placed:
            orientation = random.choice(['H', 'V'])
            if orientation == 'H':
                x = random.randint(0, 5 - size)
                y = random.randint(0, 4)
                if all(temp_board[y][x+i] == 0 for i in range(size)):
                    for i in range(size):
                        temp_board[y][x+i] = 1
                    placed = True
            else:
                x = random.randint(0, 4)
                y = random.randint(0, 5 - size)
                if all(temp_board[y+i][x] == 0 for i in range(size)):
                    for i in range(size):
                        temp_board[y+i][x] = 1
                    placed = True
    return temp_board

def show_board(b):
    display.clear()
    for y in range(5):
        for x in range(5):
            if b[y][x] == 1:
                display.set_pixel(x, y, 9)
            elif b[y][x] == 2:
                display.set_pixel(x, y, 5)
            elif b[y][x] == -1:
                display.set_pixel(x, y, 3)

def all_ships_sunk(b):
    for row in b:
        if 1 in row:
            return False
    return True

def startup():
    global board
    radio.on()
    radio.config(group=1)
    
    current_board = random_board()
    show_board(current_board)

    # Initial Board setup
    while True:
        if button_a.was_pressed():
            current_board = random_board()
            show_board(current_board)

        if button_b.was_pressed():
            board = current_board
            radio.send("READY")  # Signal Player A has finished setting up
            break
        sleep(100)

    # Synchronize turns between Player A and Player B
    while True:
        incoming = radio.receive()
        if incoming == "READY":
            display.scroll("Battle !", delay=50)
            break  # Player B is ready, both are synced
        display.scroll("WAIT", delay=50)
        sleep(100)

    sleep(500)
    game_logic()

def attack_select():
    x = 0
    y = 0
    blink = True
    selecting = True

    while selecting:
        display.clear()

        for j in range(5):
            for i in range(5):
                if enemy_board[j][i] == 1:
                    display.set_pixel(i, j, 9)
                elif enemy_board[j][i] == -1:
                    display.set_pixel(i, j, 3)

        if blink:
            display.set_pixel(x, y, 7)
        blink = not blink

        if button_a.was_pressed():
            x = (x + 1) % 5
        if button_b.was_pressed():
            y = (y + 1) % 5

        if accelerometer.was_gesture("shake"):
            selecting = False

        sleep(300)

    return x, y

def game_logic():
    global turn, reaction_timer

    # Synchronize turn based on who received "READY"
    my_id = random.randint(1, 1000)
    radio.send("ID:" + str(my_id))
    
    # Wait for opponent's ID
    opponent_id = None
    wait_start = running_time()
    
    while opponent_id is None:
        if (running_time() - wait_start) // 500 % 2 == 0:
            display.show("S")  # S for Sync
        else:
            display.show(".")
        
        message = radio.receive()
        if message and message.startswith("ID:"):
            opponent_id = int(message.split(":")[1])
        
        sleep(100)
    
    # Higher ID goes first
    turn = my_id > opponent_id
    
    if turn:
        display.scroll("Your Turn", delay=50)
    else:
        display.scroll("Enemy Turn", delay=50)

    while True:
        if turn:
            display.scroll("Attack!", delay=50)
            x, y = attack_select()

            if enemy_board[y][x] != 0:
                sleep(1000)
                continue

            radio.send("{}:{}".format(x, y))

            while True:
                result = radio.receive()
                if result == "HIT":
                    enemy_board[y][x] = 1
                    display.show(Image.YES)
                    sleep(1000)
                    break
                elif result == "MISS":
                    enemy_board[y][x] = -1
                    display.show(Image.NO)
                    sleep(1000)
                    turn = False  # End turn and pass to opponent
                    break  # FIX: Removed unnecessary "Enemy Turn" message
                elif result == "You won":
                    display.scroll("YOU WIN")
                    return

        else:
            incoming = radio.receive()
            if incoming:
                if incoming == "You won":
                    display.scroll("YOU LOSE")
                    return

                # Check if it's coordinates for an attack
                if ":" in incoming:
                    coords = incoming.split(":")
                    x = int(coords[0])
                    y = int(coords[1])

                    if board[y][x] == 1:
                        board[y][x] = 2  # Mark hit

                        if all_ships_sunk(board):
                            radio.send("You won")
                            display.scroll("YOU LOSE")
                            return
                        else:
                            radio.send("HIT")
                            display.show(Image.SAD)
                            reaction_timer = running_time() + 1000
                    else:
                        board[y][x] = -1  # Mark miss
                        radio.send("MISS")
                        display.show(Image.HAPPY)
                        reaction_timer = running_time() + 1000
                        turn = True  # FIX: Changed to your turn after sending MISS
                        
        if running_time() > reaction_timer:
            display.clear()
            blink = running_time() // 300 % 2 == 0
            for y in range(5):
                for x in range(5):
                    if board[y][x] == 1:
                        display.set_pixel(x, y, 9)
                    elif board[y][x] == 2:
                        if blink:
                            display.set_pixel(x, y, 9)
                        else:
                            display.set_pixel(x, y, 0)
                    elif board[y][x] == -1:
                        display.set_pixel(x, y, 3)

        sleep(100)

# --- Start ---
startup()
