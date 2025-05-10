from microbit import *
import radio
import random

# --- Radio Setup ---
radio.on()
radio.config(group=1)

# --- Role Selection ---
display.scroll("A=H B=E")
ROLE = None

# Choose role
while True:
    if button_a.is_pressed():
        ROLE = "hunter"
        radio.send("H_SELECTED")
        display.show("H")
        break
    elif button_b.is_pressed():
        ROLE = "escaper"
        radio.send("E_SELECTED")
        display.show("E")
        break
    sleep(100)

# Wait for opponent's role
oppo_role = None
while True:
    msg = radio.receive()
    if msg == "H_SELECTED":
        oppo_role = "hunter"
    elif msg == "E_SELECTED":
        oppo_role = "escaper"

    if oppo_role:
        if oppo_role == ROLE:
            display.scroll("Same! Reselect")
            ROLE = None
            oppo_role = None
            display.scroll("A=H B=E")
            while True:
                if button_a.is_pressed():
                    ROLE = "hunter"
                    radio.send("H_SELECTED")
                    display.show("H")
                    break
                elif button_b.is_pressed():
                    ROLE = "escaper"
                    radio.send("E_SELECTED")
                    display.show("E")
                    break
                sleep(100)
        else:
            break
    sleep(100)

# --- Initial Positions ---
x, y = random.randint(1, 3), random.randint(1, 3)
oppo_x, oppo_y = -1, -1
old_x, old_y = x, y

# --- Timers ---
start_time = running_time()
last_radio_send = running_time()

# --- Functions ---
def draw():
    display.clear()
    if oppo_x != -1:
        display.set_pixel(oppo_x, oppo_y, 3)
    display.set_pixel(x, y, 9)

def move_player():
    global x, y
    moved = False
    acc = accelerometer.get_y()
    a, b = button_a.is_pressed(), button_b.is_pressed()

    if a and not b and x > 0:
        x -= 1
        moved = True
    elif b and not a and x < 4:
        x += 1
        moved = True
    elif a and b and y < 4:
        y += 1
        moved = True
    elif acc < -300 and y > 0:
        y -= 1
        moved = True

    if moved:
        sleep(100)

def is_shrink_zone():
    return x == 0 or y == 0 or x == 4 or y == 4

# --- Game Loop ---
while True:
    now = running_time()
    elapsed = now - start_time

    move_player()

    # Send position if changed
    if (x, y) != (old_x, old_y) or now - last_radio_send > 300:
        radio.send("{},{}".format(x, y))
        old_x, old_y = x, y
        last_radio_send = now

    # Receive opponent's position
    msg = radio.receive()
    if msg:
        parts = msg.split(",")
        if len(parts) == 2:
            oppo_x, oppo_y = int(parts[0]), int(parts[1])

    draw()

    # Check for collision (tag)
    if (x, y) == (oppo_x, oppo_y):
        radio.off()
        if ROLE == "hunter":
            display.scroll("Win!")
        else:
            display.scroll("Caught!")
        break

    # Shrinking arena after 30 seconds
    if elapsed > 30000 and is_shrink_zone():
        radio.off()
        display.scroll("Out!")
        break

    # Timeout at 60 seconds
    if elapsed > 60000:
        radio.off()
        display.scroll("Time Up")
        break

    sleep(10)