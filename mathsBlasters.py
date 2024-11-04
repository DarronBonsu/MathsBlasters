import pygame 
import os 
import random
from tkinter import *
pygame.font.init()
import sqlite3


# Define game window dimensions and create window
WIDTH, HEIGHT = 1199, 635
WIN= pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Maths blasters")

# Load game assets
user_ship= pygame.image.load(os.path.join("assets","user_ship.png"))
enemy_ship= pygame.image.load(os.path.join("assets","enemy_ship.png"))
user_laser= pygame.image.load(os.path.join("assets","user_laser.png"))
enemy_laser= pygame.image.load(os.path.join("assets","enemy_laser.png"))
heart = pygame.image.load(os.path.join("assets","lives.png"))

# Load background image
bg=pygame.image.load(os.path.join("background2.jpg"))


def random_question(db_filename):
    conn = sqlite3.connect(db_filename)
    cur = conn.cursor()
    # select a random question from the database
    cur.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()

    # extract the question and answer from the row
    question, ans, wrong1, wrong2,total, answerd_correctly = row

    conn.close()

    return (question, ans, wrong1, wrong2, total, answerd_correctly)



# Define Ship class
class Ship:
    COOLDOWN = 30 # laser cooldown

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y)) # Draw ship 
        for laser in self.lasers:
            laser.draw(window) # Draw laser fired by ship

    def move_lasers(self, vel, obj):
        self.cooldown() # Check laser cooldown
        for laser in self.lasers:
            laser.move(vel) # laser move by vel
            if laser.off_screen(HEIGHT):#remove laser when of  screen
                self.lasers.remove(laser) 
            elif laser.collision(obj):
                obj.health -= 10 # lose health if hit
                self.lasers.remove(laser) # Remove laser after hit


    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0 # Reset cooldown counter
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1 # increment cooldown 

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2, self.y, self.laser_img)#fire laser from center of ship
            self.lasers.append(laser)
            self.cool_down_counter = 1 # Fire laser if off cooldown

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()
    

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)# Call parent constructor with x, y, and health arguments
        self.ship_img = user_ship
        self.laser_img = user_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, enemies,score,lives,question,incorrect_questions,question_right):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel) #move laser up
            if laser.off_screen(HEIGHT):#remove if off screen
                self.lasers.remove(laser)

            right_enemy = enemies[0]
            wrong_Enemy_1 = enemies[1]
            wrong_Enemy_2 = enemies[2]
            if laser.collision(right_enemy):#check if right enemy is shot
                enemies = [] #remove all enemies from the screen
                score = score + 1 #increment score
                question_right +=1 #increment question answered right 
                if laser in self.lasers:
                            self.lasers.remove(laser)#remove laser when collide with enemy
            elif laser.collision(wrong_Enemy_1) or laser.collision(wrong_Enemy_2):#check if woring enemy is shot
                lives = lives - 1 #decrement lives
                enemies = [] #remove enemies off screen
                score = score
                if question not in incorrect_questions:
                    incorrect_questions.append(question)
                if laser in self.lasers:
                            self.lasers.remove(laser)# remove laser when collide with enemy

        return (score, enemies, lives,incorrect_questions,question_right)

    def draw(self, window):# draw user ship and healthbar 
        super().draw(window)
        self.healthbar(window)   

    def healthbar(self, window):#healthbar 
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))#red
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10)) #greem


# Define Laser class
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img) # Create laser hitbox

    def draw(self, window):
        window.blit(self.img, (self.x, self.y)) # Draw laser on screen

    def move(self, vel):
        self.y += vel # Move laser by given velocity

    def off_screen(self, height):
            return not(self.y <= height and self.y >= 0) # Check if laser has gone off screen

    def collision(self, obj):
        return collide(self, obj) # Check if laser has collided with object
    
class Enemy(Ship):
     
    def __init__(self, x, y,answer):
        super().__init__(x, y)
        self.ship_img = enemy_ship
        self.laser_img= enemy_laser
        self.mask= pygame.mask.from_surface(self.ship_img)#colsission mask
        self.answer=answer


    def draw(self,window):
        super().draw(window)
        font = pygame.font.Font(None, 40)
        text = font.render(str(self.answer), True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x + self.get_width() // 2, self.y + self.get_height() //2))
        window.blit(text, text_rect)

    def move(self, vel):#move down
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2, self.y + self.get_height(), self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1      
    
def collide(obj1, obj2):
     offset_x =obj2.x - obj1.x
     offset_y =obj2.y - obj1.y
     # Check if obj1 and obj2 overlap at the given offsets renturn boolean value if collisison or not
     return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def game():
    def pause():
        paused = True
        
        pause_screen_font=pygame.font.SysFont("arial,", 40, "bold")
        paused_font=pygame.font.SysFont("arial,", 50, "bold")

        paused_label = paused_font.render("Pause Menu", True, (255, 255, 255))
        resume_button = pause_screen_font.render("Resume", True, (255, 255, 255))
        resume_rect = resume_button.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 30))

        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if resume_rect.collidepoint(event.pos):
                        paused = False  # Resume game

            WIN.blit(bg, (0, 0))
            WIN.blit(paused_label, paused_label.get_rect(center=(WIDTH / 2, 50)))
            WIN.blit(resume_button, resume_rect)
            pygame.display.update()
            clock.tick(60)

    run=True
    FPS=60
    lives=3
    score=0
    clock=pygame.time.Clock()
    player_vel = 8
    question, answer, choice1, choice2, question_total, question_right= random_question('questions.db')#call randomised question
    display_question=question
    font=pygame.font.SysFont("arial,", 30, "bold")
    incorrect_questions = []

    
    
    player = Player(500,500)# player place 

    enemies = []
    laser_vel=5

    # Pause button
    pause_button = font.render("Pause", 1, (255,255,255))
    pause_rect = pause_button.get_rect(topleft=(50, 50))
    
    def redraw_window():
        WIN.blit(bg,(0,0))

        pygame.draw.line(WIN, (255,255,255),(0,480),(WIDTH,480))

        for enemy in enemies:
                    enemy.draw(WIN)

        for i in range(lives):
            WIN.blit(heart, (WIDTH/2-((heart.get_width())*lives)//2+(i*heart.get_width()), 100))
                
        # Draw ship
        player.draw(WIN)
    
    
        # question and score labels
        question_label =  font.render(f"{display_question}", 1, (255,255,255))
        score_label=  font.render(f"Score:{score}", 1, (255,255,255))


        # Draw pause button and labels
        WIN.blit(pause_button, pause_rect)
        WIN.blit(question_label, (WIDTH/2-question_label.get_width()/2, 50))
        WIN.blit(score_label, (WIDTH-score_label.get_width()-50, 50)) 

        pygame.display.update()

    while run:
        clock.tick(FPS) #check for interrupts
        redraw_window()
        

        if lives <= 0 or player.health <= 0:
            run=False 
            

        


        if len(enemies) < 1:
            question, answer, choice1, choice2, question_total, question_right = random_question('questions.db')
            display_question = question
            question_total = question_total + 1 #increment the total aount of times the question has appeared 

            enemy_place = random.randrange(0, WIDTH-100)
            enemy1_run = True
            while enemy1_run:
                enemy1_place = random.randrange(0,WIDTH-100)
                if enemy1_place >= enemy_place - 100 and enemy1_place <= enemy_place + 100:
                    enemy1_place = random.randrange(0,WIDTH-100)
                else:
                    enemy1_run = False
            enemy2_run = True
            while enemy2_run:
                enemy2_place = random.randrange(0,WIDTH-100)
                if enemy2_place >= enemy_place - 100 and enemy2_place <= enemy_place + 100 or enemy2_place >= enemy1_place - 100 and enemy2_place <= enemy1_place + 100:
                    enemy2_place = random.randrange(0,WIDTH-100)
                else:
                    enemy2_run = False

            enemy = Enemy(enemy_place, -198,answer)
            enemy1 = Enemy(enemy1_place, -200,choice1)
            enemy2 = Enemy(enemy2_place, -200,choice2)
            
            enemies.append(enemy)
            enemies.append(enemy1)
            enemies.append(enemy2)

        enemy_vel_multiplier = int(score//5)*0.25
        if enemy_vel_multiplier > 0.75:
            enemy_vel_multiplier = 0.75
        enemy_vel = 1+enemy_vel_multiplier 

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel,player)
            
            if random.randrange(0, 180) == 1:
                enemy.shoot()

            if enemy.y + enemy.get_height() > 490:
                if display_question not in incorrect_questions:
                    incorrect_questions.append(display_question)
                enemies=[]
                lives -= 1
                
        for event in pygame.event.get(): #exit
            if event.type == pygame.QUIT:
                quit() 
            elif event.type == pygame.MOUSEBUTTONDOWN:#pause button
                if pause_rect.collidepoint(event.pos):
                    pause()

        keys = pygame.key.get_pressed()#player movement
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: #left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:#right
            player.x += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        score, enemies,lives,incorrect_questions, question_right = player.move_lasers(-laser_vel,enemies,score,lives,display_question, incorrect_questions,question_right)
       

        if run == False:
            over_run = True
        
    while over_run: 
        over_screen_font=pygame.font.SysFont("arial,", 40, "bold")
        over_font=pygame.font.SysFont("arial,", 50, "bold")
        over_label = over_font.render("GAME OVER", True, (255, 255, 255))
        play_again_button = over_screen_font.render("Play again", True, (255, 255, 255))
        play_again_rect = play_again_button.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
        score_label=  font.render(f"Score: {score}", 1, (255,255,255))
        view_answer_button = over_screen_font.render("Correct answer", True, (255, 255, 255))
        view_answer_rect = view_answer_button.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 70))
        WIN.blit(bg, (0, 0))
        WIN.blit(score_label, (WIDTH-score_label.get_width()-50, 50))
        WIN.blit(over_label, over_label.get_rect(center=(WIDTH / 2, 75)))
        WIN.blit(play_again_button, play_again_rect)
        WIN.blit(view_answer_button, view_answer_rect)  

        def view_answer():
            view_answer_run = True
            while view_answer_run:
                WIN.blit(bg, (0, 0))
                for i in range(0,len(incorrect_questions)):
                    view_question = incorrect_questions[i]
                    con=sqlite3.connect('questions.db')
                    c=con.cursor()
                    c.execute("SELECT * FROM questions WHERE question=?",(view_question,))
                    question_answer = c.execute("SELECT answer FROM questions WHERE question=?",(view_question,)).fetchone()[0]
                    con.close
                    answer_label = font.render(f"answer: {question_answer}", 1, (255,255,255))
                    WIN.blit(answer_label, ((WIDTH/2)+answer_label.get_width()+50, HEIGHT/3+i*80))


                    question_label=  font.render(f"question: {view_question}", 1, (255,255,255)) 
                    WIN.blit(question_label, ((WIDTH/2)-question_label.get_width()-50, HEIGHT/3+i*80))
                back_button = font.render("Back", True, (255, 255, 255))
                back_rect = back_button.get_rect(topleft=(50, 50))
                WIN.blit(back_button, back_rect)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if back_rect.collidepoint(event.pos):
                            view_answer_run = False 

                pygame.display.update()
                clock.tick(60)
                
                

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(event.pos):
                    over_run = False
                    start_menu()

                elif view_answer_rect.collidepoint(event.pos):
                    view_answer()

        pygame.display.update()
        clock.tick(60) 
            

def start_menu():#start page
    title_font = pygame.font.SysFont("arial", 40)
    instructions_font = pygame.font.SysFont("arial", 22)
    run = True
    instructions = ("Use arrow keys to evade enemy fire and spacebar to shoot the correct enemy spaceship before its too late")
    while run:
        WIN.blit(bg, (0,0))
        instructions_label = instructions_font.render(f"{instructions}", 1, (255,255,255))
        WIN.blit(instructions_label, (WIDTH/2 - instructions_label.get_width()/2, HEIGHT/2 - 50))
        title_label = title_font.render("Press any key to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, HEIGHT/2 ))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                game()
    pygame.quit()    


start_menu()
