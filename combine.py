import random
from microbit import *
import music
import radio

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

# Start the application
if __name__ == "__main__":
    main()
