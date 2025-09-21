#!/usr/bin/env python3
"""
Grade 6 Mathematics Game - Panda3D
Number Ninja - Learn arithmetic through 3D adventures
"""

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
import random
import math
import sys

class MathematicsGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Game state
        self.score = 0
        self.level = 1
        self.lives = 3
        self.current_problem = None
        self.game_running = True
        
        # Setup the game
        self.setup_environment()
        self.setup_player()
        self.setup_ui()
        self.setup_controls()
        self.generate_math_problem()
        
        # Start the game loop
        self.taskMgr.add(self.game_loop, "game_loop")
        
    def setup_environment(self):
        """Setup the 3D environment"""
        # Disable the camera trackball controls
        self.disableMouse()
        
        # Set camera position
        self.camera.setPos(0, -20, 4)
        self.camera.lookAt(0, 0, 0)
        
        # Create a simple ground plane
        self.ground = self.loader.loadModel("environment")
        if not self.ground:
            # Create a simple colored plane if model doesn't exist
            self.ground = self.render.attachNewNode("ground")
            # Add a simple colored quad
            cm = CardMaker("ground")
            cm.setFrame(-20, 20, -20, 20)
            ground_card = self.ground.attachNewNode(cm.generate())
            ground_card.setP(-90)  # Rotate to be horizontal
            ground_card.setColor(0.2, 0.8, 0.2, 1)  # Green ground
        
        self.ground.reparentTo(self.render)
        self.ground.setScale(1, 1, 1)
        self.ground.setPos(0, 0, -2)
        
        # Add some lighting
        alight = AmbientLight('alight')
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight('dlight')
        dlight.setDirection((-1, -1, -1))
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        self.render.setLight(dlnp)
        
    def setup_player(self):
        """Setup the player character"""
        # Create a simple player representation
        self.player = self.render.attachNewNode("player")
        
        # Create a simple cube for the player
        from panda3d.core import CardMaker
        cm = CardMaker("player_cube")
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        
        # Create 6 faces of a cube
        faces = []
        for i in range(6):
            face = self.player.attachNewNode(cm.generate())
            face.setColor(0.2, 0.4, 0.8, 1)  # Blue player
            faces.append(face)
        
        # Position faces to form a cube
        faces[0].setPos(0, 0.5, 0)  # Front
        faces[1].setPos(0, -0.5, 0)  # Back
        faces[2].setPos(0.5, 0, 0); faces[2].setH(90)  # Right
        faces[3].setPos(-0.5, 0, 0); faces[3].setH(90)  # Left
        faces[4].setPos(0, 0, 0.5); faces[4].setP(90)  # Top
        faces[5].setPos(0, 0, -0.5); faces[5].setP(90)  # Bottom
        
        self.player.setPos(0, 0, 0)
        
        # Player movement variables
        self.player_speed = 5
        self.player_pos = [0, 0, 0]
        
    def setup_ui(self):
        """Setup the user interface"""
        # Score display
        self.score_text = OnscreenText(
            text=f"Score: {self.score}",
            pos=(-1.3, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )
        
        # Level display
        self.level_text = OnscreenText(
            text=f"Level: {self.level}",
            pos=(-1.3, 0.8),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )
        
        # Lives display
        self.lives_text = OnscreenText(
            text=f"Lives: {self.lives}",
            pos=(-1.3, 0.7),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )
        
        # Math problem display
        self.problem_text = OnscreenText(
            text="",
            pos=(0, 0.5),
            scale=0.1,
            fg=(1, 1, 0, 1),
            align=TextNode.ACenter
        )
        
        # Instructions
        self.instruction_text = OnscreenText(
            text="Use arrow keys to move. Press number keys to answer!",
            pos=(0, -0.9),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter
        )
        
    def setup_controls(self):
        """Setup keyboard controls"""
        self.accept("arrow_up", self.move_player, [0, 1, 0])
        self.accept("arrow_down", self.move_player, [0, -1, 0])
        self.accept("arrow_left", self.move_player, [-1, 0, 0])
        self.accept("arrow_right", self.move_player, [1, 0, 0])
        
        # Number key inputs for answers
        for i in range(10):
            self.accept(str(i), self.input_answer, [i])
        
        self.accept("escape", sys.exit)
        self.accept("r", self.restart_game)
        
        # Movement state
        self.keys = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }
        
        self.accept("arrow_up", self.set_key, ["up", True])
        self.accept("arrow_up-up", self.set_key, ["up", False])
        self.accept("arrow_down", self.set_key, ["down", True])
        self.accept("arrow_down-up", self.set_key, ["down", False])
        self.accept("arrow_left", self.set_key, ["left", True])
        self.accept("arrow_left-up", self.set_key, ["left", False])
        self.accept("arrow_right", self.set_key, ["right", True])
        self.accept("arrow_right-up", self.set_key, ["right", False])
        
    def set_key(self, key, value):
        """Set key state for continuous movement"""
        self.keys[key] = value
        
    def move_player(self, dx, dy, dz):
        """Move the player"""
        self.player_pos[0] += dx
        self.player_pos[1] += dy
        self.player_pos[2] += dz
        
        # Keep player within bounds
        self.player_pos[0] = max(-10, min(10, self.player_pos[0]))
        self.player_pos[1] = max(-10, min(10, self.player_pos[1]))
        
        self.player.setPos(self.player_pos[0], self.player_pos[1], self.player_pos[2])
        
    def generate_math_problem(self):
        """Generate a new math problem based on current level"""
        if self.level <= 3:
            # Addition problems
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            self.current_problem = {
                'question': f"{a} + {b} = ?",
                'answer': a + b,
                'type': 'addition'
            }
        elif self.level <= 6:
            # Subtraction problems
            a = random.randint(10, 50)
            b = random.randint(1, a)
            self.current_problem = {
                'question': f"{a} - {b} = ?",
                'answer': a - b,
                'type': 'subtraction'
            }
        elif self.level <= 9:
            # Multiplication problems
            a = random.randint(2, 12)
            b = random.randint(2, 12)
            self.current_problem = {
                'question': f"{a} × {b} = ?",
                'answer': a * b,
                'type': 'multiplication'
            }
        else:
            # Division problems
            b = random.randint(2, 12)
            answer = random.randint(2, 20)
            a = b * answer
            self.current_problem = {
                'question': f"{a} ÷ {b} = ?",
                'answer': answer,
                'type': 'division'
            }
        
        self.problem_text.setText(self.current_problem['question'])
        self.current_input = ""
        
    def input_answer(self, digit):
        """Handle number input for answers"""
        if not self.game_running:
            return
            
        self.current_input += str(digit)
        
        # Check if answer is complete (assuming max 3 digits)
        if len(self.current_input) >= len(str(self.current_problem['answer'])):
            self.check_answer()
            
    def check_answer(self):
        """Check if the input answer is correct"""
        try:
            user_answer = int(self.current_input)
            correct_answer = self.current_problem['answer']
            
            if user_answer == correct_answer:
                self.correct_answer()
            else:
                self.wrong_answer()
                
        except ValueError:
            self.wrong_answer()
            
        self.current_input = ""
        
    def correct_answer(self):
        """Handle correct answer"""
        self.score += 10 * self.level
        self.update_ui()
        
        # Visual feedback
        self.player.setColor(0, 1, 0, 1)  # Green for correct
        
        # Reset color after a moment
        Sequence(
            Wait(0.5),
            Func(self.player.setColor, 0.2, 0.4, 0.8, 1)
        ).start()
        
        # Generate new problem
        self.taskMgr.doMethodLater(1.0, self.next_problem, "next_problem")
        
    def wrong_answer(self):
        """Handle wrong answer"""
        self.lives -= 1
        self.update_ui()
        
        # Visual feedback
        self.player.setColor(1, 0, 0, 1)  # Red for wrong
        
        # Reset color after a moment
        Sequence(
            Wait(0.5),
            Func(self.player.setColor, 0.2, 0.4, 0.8, 1)
        ).start()
        
        if self.lives <= 0:
            self.game_over()
        else:
            # Generate new problem
            self.taskMgr.doMethodLater(1.0, self.next_problem, "next_problem")
            
    def next_problem(self, task):
        """Generate the next problem"""
        # Increase level every 5 correct answers
        if self.score > 0 and (self.score // (10 * self.level)) >= 5:
            self.level += 1
            
        self.generate_math_problem()
        return task.done
        
    def update_ui(self):
        """Update the user interface"""
        self.score_text.setText(f"Score: {self.score}")
        self.level_text.setText(f"Level: {self.level}")
        self.lives_text.setText(f"Lives: {self.lives}")
        
    def game_loop(self, task):
        """Main game loop"""
        if not self.game_running:
            return task.done
            
        dt = globalClock.getDt()
        
        # Handle continuous movement
        if self.keys["up"]:
            self.move_player(0, self.player_speed * dt, 0)
        if self.keys["down"]:
            self.move_player(0, -self.player_speed * dt, 0)
        if self.keys["left"]:
            self.move_player(-self.player_speed * dt, 0, 0)
        if self.keys["right"]:
            self.move_player(self.player_speed * dt, 0, 0)
            
        return task.cont
        
    def game_over(self):
        """Handle game over"""
        self.game_running = False
        
        # Display game over message
        OnscreenText(
            text=f"GAME OVER!\nFinal Score: {self.score}\nPress 'R' to restart or 'ESC' to quit",
            pos=(0, 0),
            scale=0.1,
            fg=(1, 0, 0, 1),
            align=TextNode.ACenter
        )
        
    def restart_game(self):
        """Restart the game"""
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_running = True
        self.player_pos = [0, 0, 0]
        self.player.setPos(0, 0, 0)
        self.player.setColor(0.2, 0.4, 0.8, 1)
        
        # Clear any existing UI
        for child in self.render2d.getChildren():
            if child.getName().startswith("OnscreenText"):
                child.removeNode()
                
        self.setup_ui()
        self.generate_math_problem()
        self.update_ui()

def main():
    """Main function to run the game"""
    game = MathematicsGame()
    game.run()

if __name__ == "__main__":
    main()