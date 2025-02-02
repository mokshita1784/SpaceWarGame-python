import turtle
import time
import random
import pygame  # Import pygame for sound playback
import threading

# Initialize pygame mixer for sound
pygame.mixer.init()

# Initialize the screen
turtle.bgpic("bg.gif")  # Set the background image
turtle.setundobuffer(1)
turtle.tracer(0)
turtle.title("SpaceWar")
turtle.bgcolor("black")

# Define the Sprite class (Base Class)
class Sprite(turtle.Turtle):
    def __init__(self, spriteshape, color, startx, starty):
        super().__init__(shape=spriteshape)
        self.speed(0)
        self.penup()
        self.color(color)
        self.goto(startx, starty)

    def is_collision(self, other):
        return (self.xcor() - other.xcor())**2 + (self.ycor() - other.ycor())**2 <= 400

# Define the Enemy class (Inherits from Sprite)
class Enemy(Sprite):
    def __init__(self, spriteshape, color, startx, starty):
        super().__init__(spriteshape, color, startx, starty)
        self.movespeed = random.randint(5, 10)  # Randomized enemy speed
        self.setheading(random.randint(0, 360))  # Start in a random direction

    def move(self):
        self.forward(self.movespeed)

        # Boundary detection (Bounces off edges)
        if self.xcor() > 290 or self.xcor() < -290:
            self.setx(min(max(self.xcor(), -290), 290))
            self.right(random.randint(0, 360))

        if self.ycor() > 290 or self.ycor() < -290:
            self.sety(min(max(self.ycor(), -290), 290))
            self.right(random.randint(0, 360))

# Create a particle class 
class Particle(Sprite):
    def __init__(self, spriteshape, color, startx, starty):
        super().__init__(spriteshape, color, startx, starty)
        self.shapesize(stretch_wid=0.1, stretch_len=0.1, outline=None)  # Small size
        self.goto(-1000, -1000)  # Initially hide particles off-screen
        self.frame = 0  # Initialize frame to track the particle's lifespan

    def explode(self, startx, starty):
        self.goto(startx, starty)  # Position particles at the explosion site
        self.setheading(random.randint(0, 360))  # Random direction for particles
        self.frame = 1

    def move(self):
        if self.frame > 0:  # Particles move for 15 frames (about 15 seconds)
            self.fd(10)  # Small movement to simulate explosion

        if self.frame > 20:
            self.frame = 0
            self.goto(-1000, -1000)

# Define the Player class (Inherits from Sprite)
class Player(Sprite):
    def __init__(self, spriteshape, color, startx, starty):
        super().__init__(spriteshape, color, startx, starty)
        self.shapesize(stretch_wid=0.6, stretch_len=1.1, outline=None)
        self.movespeed = 2  
        self.turnspeed = 10  
        self.setheading(90)  # Face upwards initially

    def turn_left(self):
        self.left(self.turnspeed)

    def turn_right(self):
        self.right(self.turnspeed)

    def move(self):
        self.forward(self.movespeed)

        # Boundary detection (Stops player from going off-screen)
        if self.xcor() > 290 or self.xcor() < -290:
            self.setx(min(max(self.xcor(), -290), 290))
            self.right(60)

        if self.ycor() > 290 or self.ycor() < -290:
            self.sety(min(max(self.ycor(), -290), 290))
            self.right(60)

    def accelerate(self):  
        self.movespeed += 1

    def decelerate(self):  
        if self.movespeed > 0:
            self.movespeed -= 1

# Define the Missile class (Inherits from Sprite)
class Missile(Sprite):
    def __init__(self, spriteshape, color, startx, starty):
        super().__init__(spriteshape, color, startx, starty)
        self.shapesize(stretch_wid=0.3, stretch_len=0.4, outline=None)
        self.speed = 20
        self.status = "ready"
        self.goto(-1000, 1000)

    def fire(self):
        if self.status == "ready":
            # Play missile sound asynchronously using pygame
            threading.Thread(target=self.play_sound).start()  # Start a new thread to play sound
            self.goto(player.xcor(), player.ycor())
            self.setheading(player.heading())
            self.status = "firing"

    def play_sound(self):
        pygame.mixer.Sound("laser.mp3").play()  # Play laser sound in a separate thread

    def move(self):
        if self.status == "firing":
            self.forward(self.speed)

        if self.xcor() < -290 or self.xcor() > 290 or self.ycor() < -290 or self.ycor() > 290:
            self.goto(-1000, 1000)
            self.status = "ready"

    def play_explosion_sound(self):
        # Play explosion sound in a separate thread when missile hits enemy
        threading.Thread(target=self.explosion_sound).start()

    def explosion_sound(self):
        pygame.mixer.Sound("explosion.mp3").play()  # Play explosion sound

# Define the Ally class (Friendly NPC)
class Ally(Sprite):
    def __init__(self, spriteshape, color, startx, starty):
        super().__init__(spriteshape, color, startx, starty)
        self.movespeed = 4
        self.setheading(random.randint(0, 360))  

    def move(self):
        self.forward(self.movespeed)

        # Boundary detection (Bounces off edges)
        if self.xcor() > 290 or self.xcor() < -290:
            self.setx(min(max(self.xcor(), -290), 290))
            self.right(random.randint(0, 360))

        if self.ycor() > 290 or self.ycor() < -290:
            self.sety(min(max(self.ycor(), -290), 290))
            self.right(random.randint(0, 360))

# Define the Game class
class Game:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.state = "playing"
        self.pen = turtle.Turtle()
        self.lives = 5  # Player starts with 5 lives

    def draw_border(self):
        # Draw border
        self.pen.speed(0)
        self.pen.color("white")
        self.pen.pensize(3)
        self.pen.penup()
        self.pen.goto(-300, 300)
        self.pen.pendown()

        for _ in range(4):
            self.pen.forward(600)
            self.pen.right(90)

        self.pen.penup()
        self.pen.hideturtle()

    def show_status(self):
        self.pen.undo()
        msg = f"Score : {self.score}  Lives: {self.lives}"
        self.pen.penup()
        self.pen.goto(-300, 300)
        self.pen.color("white")
        self.pen.write(msg, font=("Arial", 10, "normal"))

    def show_game_over(self):
        self.pen.goto(0, 0)
        self.pen.color("red")
        self.pen.write("GAME OVER", align="center", font=("Arial", 24, "bold"))
        self.pen.goto(0, -30)
        self.pen.write(f"Score: {self.score}", align="center", font=("Arial", 18, "normal"))
        self.pen.goto(0, -60)
        self.pen.write("Press 'r' to Restart", align="center", font=("Arial", 14, "normal"))

    def restart(self):
        # Reset all necessary variables
        self.score = 0
        self.lives = 5
        self.state = "playing"
        player.goto(0, 0)
        missile.goto(-1000, 1000)
        
        # Reset all enemies, allies, and particles
        for enemy in enemies:
            enemy.goto(random.randint(-250, 250), random.randint(-250, 250))
            enemy.setheading(random.randint(0, 360))
        for ally in allies:
            ally.goto(random.randint(-250, 250), random.randint(-250, 250))
            ally.setheading(random.randint(0, 360))
        for particle in particles:
            particle.goto(-1000, -1000)

        game.show_status()
        turtle.update()

        # Start the game loop again
        main_game_loop()

# Create game object and draw the border
game = Game()
game.draw_border()

# Show the game status 
game.show_status()

# Create sprites
player = Player("triangle", "white", 0, 0)
missile = Missile("triangle", "yellow", 0, 0)
particles = []
for i in range(20):
    particles.append(Particle("circle", "green", 0, 0))  # Changed from "circles" to "circle"

# Create 4 allies
allies = []
for i in range(4):
    allies.append(Ally("square", "blue", random.randint(-250, 250), random.randint(-250, 250)))

# Create enemies
enemies = []
for i in range(6):
    enemies.append(Enemy("circle", "red", random.randint(-250, 250), random.randint(-250, 250)))


# Key bindings
turtle.listen()
turtle.onkey(player.turn_left, "Left")     
turtle.onkey(player.turn_right, "Right")   
turtle.onkey(player.accelerate, "Up")      
turtle.onkey(player.decelerate, "Down")    
turtle.onkey(missile.fire, "space")        
turtle.onkey(game.restart, "r")  # Restart the game with 'r'


# Main game loop
def main_game_loop():
    running = True
    while running:
        player.move()
        missile.move()

        # Move allies
        for ally in allies:
            ally.move()

        for enemy in enemies[:]:
            enemy.move()

            # Check for collision with the player
            if enemy.is_collision(player):
                game.lives -= 1  # Deduct a life for colliding with an enemy
                game.show_status()

                if game.lives <= 0:
                    game.state = "game_over"
                    game.show_game_over()
                    running = False

                x, y = random.randint(-250, 250), random.randint(-250, 250)
                enemy.goto(x, y)

            # Check for collision between missile and enemy
            if missile.is_collision(enemy):
                enemy.hideturtle()  # Hide the enemy from the screen
                enemies.remove(enemy)  # Remove the enemy from the list
                missile.goto(-1000, 1000)  # Move missile out of view
                missile.status = "ready"
                missile.play_explosion_sound()  # Play explosion sound
                game.score += 100  # Player gains 100 points for shooting an enemy
                game.show_status()

                # Activate the particles (set them to explode)
                for particle in particles:
                    particle.explode(enemy.xcor(), enemy.ycor())

        # Check for collision with ally
        for ally in allies: 
            if missile.is_collision(ally):
                x, y = random.randint(-250, 250), random.randint(-250, 250)
                ally.goto(x, y)
                missile.goto(-1000, 1000)  # Move missile out of view
                missile.status = "ready"
                game.score -= 2  # Player loses 2 points for hitting an ally
                game.show_status()

        # Move particles and check their lifespan
        for particle in particles:
            particle.move()

        turtle.update()  
        time.sleep(0.06)

main_game_loop()
