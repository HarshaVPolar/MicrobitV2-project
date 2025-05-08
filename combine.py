import random
from microbit import *
import music
import radio
import time

class DinoGame:
    def __init__(self):
        # ——— Game Variables ———
        self.ground_y = 3       # top row of the 2-pixel dino
        self.dino_y = self.ground_y  # current dino y position
        self.velocity = 0
        self.gravity = 0.2
        self.jump_force = -1.4
        self.is_jumping = False
        self.is_bending = False
        self.obstacle_x = 5
        self.bird_obstacle = False
        self.bird_y = 0
        self.score = 0
        self.frame_counter = 0
        self.speed = 150
    
    def draw_dino(self):
        display.clear()  # Ensure we clear the display before drawing
        y = int(self.dino_y) if self.is_jumping else self.ground_y
        if self.is_bending:
            display.set_pixel(0, 4, 9)  # Crouching dino (one pixel)
        else:
            display.set_pixel(0, y, 9)  # Standing dino (two pixels) 
            display.set_pixel(0, y + 1, 9)
    
    def draw_obstacle(self):
        if 0 <= self.obstacle_x <= 4:
            if self.bird_obstacle:
                display.set_pixel(self.obstacle_x, self.bird_y, 7)
                if self.obstacle_x - 1 >= 0:
                    display.set_pixel(self.obstacle_x - 1, self.bird_y, 7)
            else:
                display.set_pixel(self.obstacle_x, 4, 9)  # Tree base
                display.set_pixel(self.obstacle_x, 3, 7)  # Tree trunk
                if self.obstacle_x - 1 >= 0:              # Left branch
                    display.set_pixel(self.obstacle_x - 1, 3, 7)
                if self.obstacle_x + 1 <= 4:              # Right branch
                    display.set_pixel(self.obstacle_x + 1, 3, 7)
    
    def check_collision(self):
        if 0 <= self.obstacle_x <= 1:
            if self.is_bending:
                # Crouching dino is only at (0,4)
                if self.obstacle_x == 0:
                    # Check if obstacle collides with crouching dino at (0,4)
                    if self.bird_obstacle:
                        return self.bird_y == 4
                    else:
                        # Tree collision with crouching dino
                        return True  # Tree base is always at y=4
            else:
                # Standing dino takes up positions (0,dino_y) and (0,dino_y+1)
                dino_top = int(self.dino_y)
                dino_bottom = dino_top + 1
                
                if self.bird_obstacle:
                    return (self.bird_y == dino_top or self.bird_y == dino_bottom)
                else:
                    if self.obstacle_x == 0:
                        if dino_bottom == 4:
                            return True  # Collision with tree base
                        if dino_top == 3 or dino_bottom == 3:
                            return True  # Collision with tree trunk
                    elif self.obstacle_x == 1:
                        if dino_top == 3 or dino_bottom == 3:
                            return True  # Collision with branches
        return False
    
    def reset_game(self):
        self.dino_y = self.ground_y
        self.velocity = 0
        self.is_jumping = False
        self.is_bending = False
        self.obstacle_x = 5
        self.bird_obstacle = False
        self.bird_y = 0
        self.score = 0
        self.frame_counter = 0
        self.speed = 150
        
        display.clear()
        music.play(music.POWER_UP)
        display.scroll("DINO")
    
    def run(self):
        self.reset_game()
        
        while True:
            # Check for touch sensor to return to menu
            if pin_logo.is_touched():
                display.scroll("MENU")
                return
            
            # Check crouch state only if not jumping
            self.is_bending = button_b.is_pressed() and not self.is_jumping
            
            # Jump input (shout or button)
            sound = microphone.sound_level()
            if (sound > 125 or button_a.was_pressed()) and not self.is_jumping and not self.is_bending:
                self.is_jumping = True
                self.velocity = self.jump_force
                music.pitch(440, 100)
            
            # Physics update
            if self.is_jumping:
                self.dino_y += self.velocity
                self.velocity += self.gravity
                
                # Land or hit ceiling
                if self.dino_y >= self.ground_y:
                    self.dino_y = self.ground_y
                    self.is_jumping = False
                elif self.dino_y < 0:
                    self.dino_y = 0
            
            # Move obstacle
            self.frame_counter += 1
            if self.frame_counter >= 3:
                self.obstacle_x -= 1
                self.frame_counter = 0
            
            # Respawn obstacle
            if self.obstacle_x < -2:
                self.obstacle_x = 5 + random.randint(0, 1)
                self.bird_obstacle = random.choice([True, False])
                self.bird_y = random.choice([2, 3]) if self.bird_obstacle else 0
                self.score += 1
                music.pitch(660, 80)
                
                # Speed up every 5 points
                if self.score % 5 == 0 and self.speed > 60:
                    self.speed -= 10
            
            # Draw game elements
            self.draw_dino()
            self.draw_obstacle()
            
            # Check collision
            if self.check_collision():
                music.pitch(220, 400)
                display.scroll("Score: " + str(self.score))
                self.reset_game()
            
            sleep(self.speed)

class TagGame:
    def __init__(self):
        # --- Game Variables ---
        self.ROLE = None
        self.oppo_role = None
        self.x = 0
        self.y = 0
        self.oppo_x = -1
        self.oppo_y = -1
        self.old_x = 0
        self.old_y = 0
        self.start_time = 0
        self.last_radio_send = 0
        
    def setup_radio(self):
        # --- Radio Setup ---
        radio.on()
        radio.config(group=1)
        
    def select_role(self):
        # --- Role Selection ---
        display.scroll("A=H B=E")
        # Choose role
        while True:
            if pin_logo.is_touched():
                radio.off()
                display.scroll("MENU")
                return False
            
            if button_a.is_pressed():
                self.ROLE = "hunter"
                radio.send("H_SELECTED")
                display.show("H")
                break
            elif button_b.is_pressed():
                self.ROLE = "escaper"
                radio.send("E_SELECTED")
                display.show("E")
                break
            sleep(100)
        return True
    
    def wait_for_opponent(self):
        # Wait for opponent's role
        while True:
            if pin_logo.is_touched():
                radio.off()
                display.scroll("MENU")
                return False
                
            msg = radio.receive()
            if msg == "H_SELECTED":
                self.oppo_role = "hunter"
            elif msg == "E_SELECTED":
                self.oppo_role = "escaper"
            if self.oppo_role:
                if self.oppo_role == self.ROLE:
                    display.scroll("Same! Reselect")
                    self.ROLE = None
                    self.oppo_role = None
                    if not self.select_role():
                        return False
                else:
                    break
            sleep(100)
        return True
    
    def initialize_positions(self):
        # --- Initial Positions ---
        self.x, self.y = random.randint(1, 3), random.randint(1, 3)
        self.oppo_x, self.oppo_y = -1, -1
        self.old_x, self.old_y = self.x, self.y
        
    def initialize_timers(self):
        # --- Timers ---
        self.start_time = running_time()
        self.last_radio_send = running_time()
    
    def draw(self):
        display.clear()
        if self.oppo_x != -1:
            display.set_pixel(self.oppo_x, self.oppo_y, 3)
        display.set_pixel(self.x, self.y, 9)
        
    def move_player(self):
        moved = False
        acc = accelerometer.get_y()
        a, b = button_a.is_pressed(), button_b.is_pressed()
        if a and not b and self.x > 0:
            self.x -= 1
            moved = True
        elif b and not a and self.x < 4:
            self.x += 1
            moved = True
        elif a and b and self.y < 4:
            self.y += 1
            moved = True
        elif acc < -300 and self.y > 0:
            self.y -= 1
            moved = True
        if moved:
            sleep(100)
            
    def is_shrink_zone(self):
        return self.x == 0 or self.y == 0 or self.x == 4 or self.y == 4
    
    def send_position(self, now):
        if (self.x, self.y) != (self.old_x, self.old_y) or now - self.last_radio_send > 300:
            radio.send("{},{}".format(self.x, self.y))
            self.old_x, self.old_y = self.x, self.y
            self.last_radio_send = now
            
    def receive_position(self):
        msg = radio.receive()
        if msg:
            parts = msg.split(",")
            if len(parts) == 2:
                self.oppo_x, self.oppo_y = int(parts[0]), int(parts[1])
    
    def check_collision(self):
        if (self.x, self.y) == (self.oppo_x, self.oppo_y):
            radio.off()
            if self.ROLE == "hunter":
                display.scroll("Win!")
            else:
                display.scroll("Caught!")
            return True
        return False
    
    def check_boundary(self, elapsed):
        if elapsed > 30000 and self.is_shrink_zone():
            radio.off()
            display.scroll("Out!")
            return True
        return False
    
    def check_timeout(self, elapsed):
        if elapsed > 60000:
            radio.off()
            display.scroll("Time Up")
            return True
        return False
    
    def setup(self):
        self.setup_radio()
        if not self.select_role():
            return False
        if not self.wait_for_opponent():
            return False
        self.initialize_positions()
        self.initialize_timers()
        return True
    
    def run(self):
        if not self.setup():
            return
        
        # --- Game Loop ---
        while True:
            # Check for touch sensor to return to menu
            if pin_logo.is_touched():
                radio.off()
                display.scroll("MENU")
                return
                
            now = running_time()
            elapsed = now - self.start_time
            
            self.move_player()
            self.send_position(now)
            self.receive_position()
            self.draw()
            
            # Check end conditions
            if self.check_collision():
                break
                
            if self.check_boundary(elapsed):
                break
                
            if self.check_timeout(elapsed):
                break
                
            sleep(10)

class GameMenu:
    def __init__(self):
        self.menu_options = ["DINO", "TAG"]
        self.current_option = 0
    
    def display_menu(self):
        display.scroll(self.menu_options[self.current_option])
    
    def show_menu_icon(self):
        display.clear()
        # Show different icon depending on current selection
        if self.menu_options[self.current_option] == "DINO":
            # Dino icon
            display.set_pixel(0, 3, 9)
            display.set_pixel(0, 4, 9)
            display.set_pixel(1, 3, 5)
        else:  # TAG
            # Tag icon
            display.set_pixel(1, 1, 9)
            display.set_pixel(3, 3, 5)
            display.set_pixel(2, 2, 3)
    
    def run(self):
        while True:
            self.show_menu_icon()
            
            # Navigate menu with buttons
            if button_a.was_pressed():
                self.current_option = (self.current_option - 1) % len(self.menu_options)
                self.display_menu()
            
            if button_b.was_pressed():
                self.current_option = (self.current_option + 1) % len(self.menu_options)
                self.display_menu()
            
            # Select game with both buttons
            if button_a.is_pressed() and button_b.is_pressed():
                display.clear()
                selected_game = self.menu_options[self.current_option]
                
                if selected_game == "DINO":
                    game = DinoGame()
                    game.run()
                elif selected_game == "TAG":
                    game = TagGame()
                    game.run()
                
                # After game returns to menu
                display.scroll("MENU")
                sleep(500)
            
            sleep(100)

def main():
    """
    Main function that displays a menu and launches selected game.
    Button A for Dino Game, Button B for Tag Game.
    Touch sensor always returns to menu.
    """
    while True:
        # Display menu
        display.scroll("MENU")
        display.show("?")
        
        # Wait for button press
        while True:
            # Button A for Dino Game
            if button_a.was_pressed():
                display.clear()
                display.show("D")
                sleep(500)
                game = DinoGame()
                game.run()
                break  # Return to main menu after game
            
            # Button B for Tag Game
            if button_b.was_pressed():
                display.clear()
                display.show("T")
                sleep(500)
                game = TagGame()
                game.run()
                break  # Return to main menu after game
            
            sleep(100)

class Battleship:
    def __init__(self):
        # --- Globals ---
        self.board = [[0 for _ in range(5)] for _ in range(5)]  # Your board
        self.enemy_board = [[0 for _ in range(5)] for _ in range(5)]  # What you know about opponent
        self.ships = [4, 3, 2]  # Ship sizes
        self.turn = False  # Whether it's your turn
        self.reaction_timer = 0  # To time the happy/sad face

    def random_board(self):
        temp_board = [[0 for _ in range(5)] for _ in range(5)]
        for size in self.ships:
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

    def show_board(self, b):
        display.clear()
        for y in range(5):
            for x in range(5):
                if b[y][x] == 1:
                    display.set_pixel(x, y, 9)
                elif b[y][x] == 2:
                    display.set_pixel(x, y, 5)
                elif b[y][x] == -1:
                    display.set_pixel(x, y, 3)

    def all_ships_sunk(self, b):
        for row in b:
            if 1 in row:
                return False
        return True

    def startup(self):
        radio.on()
        radio.config(group=1)
        
        current_board = self.random_board()
        self.show_board(current_board)

        # Initial Board setup
        while True:
            if button_a.was_pressed():
                current_board = self.random_board()
                self.show_board(current_board)

            if button_b.was_pressed():
                self.board = current_board
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
        self.game_logic()

    def attack_select(self):
        x = 0
        y = 0
        blink = True
        selecting = True

        while selecting:
            display.clear()

            for j in range(5):
                for i in range(5):
                    if self.enemy_board[j][i] == 1:
                        display.set_pixel(i, j, 9)
                    elif self.enemy_board[j][i] == -1:
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

    def game_logic(self):
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
        self.turn = my_id > opponent_id
        
        if self.turn:
            display.scroll("Your Turn", delay=50)
        else:
            display.scroll("Enemy Turn", delay=50)

        while True:
            if self.turn:
                display.scroll("Attack!", delay=50)
                x, y = self.attack_select()

                if self.enemy_board[y][x] != 0:
                    sleep(1000)
                    continue

                radio.send("{}:{}".format(x, y))

                while True:
                    result = radio.receive()
                    if result == "HIT":
                        self.enemy_board[y][x] = 1
                        display.show(Image.YES)
                        sleep(1000)
                        break
                    elif result == "MISS":
                        self.enemy_board[y][x] = -1
                        display.show(Image.NO)
                        sleep(1000)
                        self.turn = False  # End turn and pass to opponent
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

                        if self.board[y][x] == 1:
                            self.board[y][x] = 2  # Mark hit

                            if self.all_ships_sunk(self.board):
                                radio.send("You won")
                                display.scroll("YOU LOSE")
                                return
                            else:
                                radio.send("HIT")
                                display.show(Image.SAD)
                                self.reaction_timer = running_time() + 1000
                        else:
                            self.board[y][x] = -1  # Mark miss
                            radio.send("MISS")
                            display.show(Image.HAPPY)
                            self.reaction_timer = running_time() + 1000
                            self.turn = True  # FIX: Changed to your turn after sending MISS
                            
            if running_time() > self.reaction_timer:
                display.clear()
                blink = running_time() // 300 % 2 == 0
                for y in range(5):
                    for x in range(5):
                        if self.board[y][x] == 1:
                            display.set_pixel(x, y, 9)
                        elif self.board[y][x] == 2:
                            if blink:
                                display.set_pixel(x, y, 9)
                            else:
                                display.set_pixel(x, y, 0)
                        elif self.board[y][x] == -1:
                            display.set_pixel(x, y, 3)

            sleep(100)

    def run(self):
        self.startup()


# Start the application
if __name__ == "__main__":
    main()
