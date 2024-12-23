import tkinter as tk
import random
import math
import time
from tkinter import messagebox

CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400
ENEMY_SIZE = 20
TOWER_SIZE = 30
TOWER_RANGE = 75
ENEMY_SPEED = 2.75
FIRE_RATE = 1000
INITIAL_LIVES = 5
TOWER_LIMIT = 3

score = 0
lives = INITIAL_LIVES
tower_count = 0
towers = []
enemies = []
projectiles = []

root = tk.Tk()
root.title("Tower Defense Game")

canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.pack()

score_label = tk.Label(root, text=f"Score: {score}")
score_label.pack()
lives_label = tk.Label(root, text=f"Lives: {lives}")
lives_label.pack()

class Enemy:
    def __init__(self):
        self.health = 1
        self.x = 0
        self.y = random.randint(0, CANVAS_HEIGHT - ENEMY_SIZE)
        self.id = canvas.create_oval(self.x, self.y, self.x + ENEMY_SIZE, self.y + ENEMY_SIZE, fill="red")

    def move(self):
        self.x += ENEMY_SPEED
        canvas.coords(self.id, self.x, self.y, self.x + ENEMY_SIZE, self.y + ENEMY_SIZE)
        if self.x > CANVAS_WIDTH:
            global lives
            lives -= 1
            update_lives()
            canvas.delete(self.id)
            return False
        return True

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = canvas.create_rectangle(x, y, x + TOWER_SIZE, y + TOWER_SIZE, fill="blue")
        self.last_fired = time.time()

    def in_range(self, enemy):
        return math.hypot(enemy.x - self.x, enemy.y - self.y) < TOWER_RANGE

    def fire(self):
        now = time.time()
        if now - self.last_fired >= FIRE_RATE / 1000.0:
            self.last_fired = now
            for enemy in enemies:
                if self.in_range(enemy):
                    projectile = Projectile(self.x + TOWER_SIZE // 2, self.y + TOWER_SIZE // 2, enemy)
                    projectiles.append(projectile)
                    break

class Projectile:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target
        self.id = canvas.create_oval(x, y, x + 5, y + 5, fill="black")

    def move(self):
        if not self.target or self.target.health <= 0:
            canvas.delete(self.id)
            return False

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 5:
            self.target.health -= 1
            if self.target.health <= 0:
                global score
                score += 10
                update_score()
                canvas.delete(self.target.id)
                enemies.remove(self.target)
            canvas.delete(self.id)
            return False

        self.x += (dx / dist) * 10
        self.y += (dy / dist) * 10
        canvas.coords(self.id, self.x, self.y, self.x + 5, self.y + 5)
        return True

def update_score():
    score_label.config(text=f"Score: {score}")

def update_lives():
    lives_label.config(text=f"Lives: {lives}")
    if lives <= 0:
        game_over()

def game_over():
    canvas.delete("all")
    canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, text="Game Over", font=("Arial", 24), fill="red")

def game_loop():
    if lives > 0:
        for enemy in enemies[:]:
            if not enemy.move():
                enemies.remove(enemy)

        for projectile in projectiles[:]:
            if not projectile.move():
                projectiles.remove(projectile)

        root.after(50, game_loop)

def fire_towers(event=None):
    for tower in towers:
        tower.fire()

def add_tower(event):
    global tower_count
    if tower_count < TOWER_LIMIT:
        tower_count += 1
        x = (event.x // TOWER_SIZE) * TOWER_SIZE
        y = (event.y // TOWER_SIZE) * TOWER_SIZE
        towers.append(Tower(x, y))
    else:
        messagebox.showinfo("Limit Reached", "No more towers can be added.")

def spawn_enemy():
    if lives > 0:
        enemies.append(Enemy())
        root.after(750, spawn_enemy)

canvas.bind("<Button-1>", add_tower)
root.bind("<space>", fire_towers)

spawn_enemy()
game_loop()
root.mainloop()
