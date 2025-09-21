#!/usr/bin/env python3
"""
Grade 11 Physics Game - Panda3D
Mechanics Lab - Advanced physics simulation
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

class PhysicsGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Game state
        self.score = 0
        self.level = 1
        self.experiments_completed = 0
        self.current_experiment = None
        self.game_running = True
        
        # Physics experiments for Grade 11
        self.physics_experiments = {
            'projectile_motion': {
                'name': 'Projectile Motion',
                'description': 'Calculate trajectory of projectiles',
                'problems': [
                    {
                        'question': 'A ball is thrown at 45° with velocity 20 m/s. What is the range?',
                        'answer': 40.8,
                        'tolerance': 2.0,
                        'formula': 'R = v²sin(2θ)/g'
                    }
                ]
            },
            'circular_motion': {
                'name': 'Circular Motion',
                'description': 'Study centripetal force and acceleration',
                'problems': [
                    {
                        'question': 'A 2kg mass moves in circle of radius 5m at 10 m/s. Find centripetal force.',
                        'answer': 40.0,
                        'tolerance': 2.0,
                        'formula': 'F = mv²/r'
                    }
                ]
            },
            'waves': {
                'name': 'Wave Motion',
                'description': 'Analyze wave properties',
                'problems': [
                    {
                        'question': 'A wave has frequency 50 Hz and wavelength 2m. Find wave speed.',
                        'answer': 100.0,
                        'tolerance': 5.0,
                        'formula': 'v = fλ'
                    }
                ]
            }
        }
        
        # Setup the game
        self.setup_environment()
        self.setup_lab_equipment()
        self.setup_ui()
        self.setup_controls()
        self.start_experiment()
        
        # Start the game loop
        self.taskMgr.add(self.game_loop, "game_loop")
        
    def setup_environment(self):
        """Setup the physics laboratory environment"""
        # Disable the camera trackball controls
        self.disableMouse()
        
        # Set camera position
        self.camera.setPos(0, -30, 10)
        self.camera.lookAt(0, 0, 0)
        
        # Create laboratory environment
        self.lab = self.render.attachNewNode("laboratory")
        
        # Lab floor
        floor_cm = CardMaker("floor")
        floor_cm.setFrame(-20, 20, -20, 20)
        self.floor = self.lab.attachNewNode(floor_cm.generate())
        self.floor.setP(-90)
        self.floor.setColor(0.8, 0.8, 0.9, 1)  # Light blue lab floor
        self.floor.setPos(0, 0, -1)
        
        # Lab walls
        self.create_lab_walls()
        
        # Lab bench
        self.create_lab_bench()
        
        # Add professional lighting
        alight = AmbientLight('alight')
        alight.setColor((0.4, 0.4, 0.4, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Bright lab lighting
        dlight = DirectionalLight('dlight')
        dlight.setDirection((-1, -1, -1))
        dlight.setColor((1, 1, 1, 1))
        dlnp = self.render.attachNewNode(dlight)
        self.render.setLight(dlnp)
        
    def create_lab_walls(self):
        """Create laboratory walls"""
        wall_cm = CardMaker("wall")
        wall_cm.setFrame(-20, 20, 0, 10)
        
        # Back wall
        back_wall = self.lab.attachNewNode(wall_cm.generate())
        back_wall.setPos(0, 20, 0)
        back_wall.setColor(0.9, 0.9, 0.9, 1)
        
        # Side walls
        wall_cm.setFrame(-20, 0, 0, 10)
        left_wall = self.lab.attachNewNode(wall_cm.generate())
        left_wall.setPos(-20, 0, 0)
        left_wall.setH(90)
        left_wall.setColor(0.9, 0.9, 0.9, 1)
        
        right_wall = self.lab.attachNewNode(wall_cm.generate())
        right_wall.setPos(20, 0, 0)
        right_wall.setH(-90)
        right_wall.setColor(0.9, 0.9, 0.9, 1)
        
    def create_lab_bench(self):
        """Create laboratory bench"""
        bench_cm = CardMaker("bench")
        bench_cm.setFrame(-8, 8, -2, 2)
        self.bench = self.lab.attachNewNode(bench_cm.generate())
        self.bench.setP(-90)
        self.bench.setPos(0, 5, 1)
        self.bench.setColor(0.6, 0.4, 0.2, 1)  # Wood color
        
    def setup_lab_equipment(self):
        """Setup physics lab equipment"""
        self.equipment = self.render.attachNewNode("equipment")
        
        # Projectile launcher
        self.create_projectile_launcher()
        
        # Pendulum setup
        self.create_pendulum()
        
        # Wave generator
        self.create_wave_generator()
        
        # Measuring instruments
        self.create_instruments()
        
    def create_projectile_launcher(self):
        """Create projectile motion equipment"""
        launcher_cm = CardMaker("launcher")
        launcher_cm.setFrame(-0.5, 0.5, -0.2, 0.2)
        
        self.launcher = self.equipment.attachNewNode("launcher")
        launcher_body = self.launcher.attachNewNode(launcher_cm.generate())
        launcher_body.setColor(0.3, 0.3, 0.3, 1)  # Dark gray
        launcher_body.setPos(-5, 5, 2)
        
        # Projectile
        proj_cm = CardMaker("projectile")
        proj_cm.setFrame(-0.1, 0.1, -0.1, 0.1)
        self.projectile = self.launcher.attachNewNode(proj_cm.generate())
        self.projectile.setColor(1, 0, 0, 1)  # Red ball
        self.projectile.setPos(-5, 5, 2.5)
        
    def create_pendulum(self):
        """Create pendulum for circular motion"""
        # Pendulum string
        string_cm = CardMaker("string")
        string_cm.setFrame(-0.02, 0.02, -3, 0)
        self.pendulum_string = self.equipment.attachNewNode(string_cm.generate())
        self.pendulum_string.setColor(0.8, 0.8, 0.8, 1)
        self.pendulum_string.setPos(0, 5, 5)
        
        # Pendulum bob
        bob_cm = CardMaker("bob")
        bob_cm.setFrame(-0.2, 0.2, -0.2, 0.2)
        self.pendulum_bob = self.equipment.attachNewNode(bob_cm.generate())
        self.pendulum_bob.setColor(0.8, 0.6, 0.2, 1)  # Golden bob
        self.pendulum_bob.setPos(0, 5, 2)
        
        # Start pendulum motion
        self.pendulum_bob.hprInterval(2, (30, 0, 0)).loop()
        
    def create_wave_generator(self):
        """Create wave motion demonstration"""
        # Wave medium
        self.wave_points = []
        for i in range(20):
            point_cm = CardMaker(f"wave_point_{i}")
            point_cm.setFrame(-0.1, 0.1, -0.1, 0.1)
            point = self.equipment.attachNewNode(point_cm.generate())
            point.setColor(0, 0.5, 1, 1)  # Blue wave
            point.setPos(i - 10, 10, 2)
            self.wave_points.append(point)
            
        # Animate wave
        self.taskMgr.add(self.animate_wave, "animate_wave")
        
    def create_instruments(self):
        """Create measuring instruments"""
        # Ruler
        ruler_cm = CardMaker("ruler")
        ruler_cm.setFrame(-5, 5, -0.1, 0.1)
        self.ruler = self.equipment.attachNewNode(ruler_cm.generate())
        self.ruler.setColor(1, 1, 0, 1)  # Yellow ruler
        self.ruler.setPos(5, 8, 1.5)
        
        # Stopwatch
        watch_cm = CardMaker("stopwatch")
        watch_cm.setFrame(-0.3, 0.3, -0.3, 0.3)
        self.stopwatch = self.equipment.attachNewNode(watch_cm.generate())
        self.stopwatch.setColor(0.2, 0.2, 0.2, 1)  # Black stopwatch
        self.stopwatch.setPos(3, 8, 2)
        
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
        
        # Experiments completed
        self.experiments_text = OnscreenText(
            text=f"Experiments: {self.experiments_completed}",
            pos=(-1.3, 0.7),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )
        
        # Current experiment
        self.experiment_text = OnscreenText(
            text="",
            pos=(0, 0.6),
            scale=0.08,
            fg=(1, 1, 0, 1),
            align=TextNode.ACenter,
            wordwrap=50
        )
        
        # Problem display
        self.problem_text = OnscreenText(
            text="",
            pos=(0, 0.3),
            scale=0.06,
            fg=(0.8, 1, 0.8, 1),
            align=TextNode.ACenter,
            wordwrap=60
        )
        
        # Formula display
        self.formula_text = OnscreenText(
            text="",
            pos=(0, 0.1),
            scale=0.05,
            fg=(0.8, 0.8, 1, 1),
            align=TextNode.ACenter
        )
        
        # Input prompt
        self.input_text = OnscreenText(
            text="Enter your answer and press ENTER",
            pos=(0, -0.2),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter
        )
        
        # Answer display
        self.answer_display = OnscreenText(
            text="Answer: ",
            pos=(0, -0.4),
            scale=0.06,
            fg=(1, 1, 0, 1),
            align=TextNode.ACenter
        )
        
        # Instructions
        self.instruction_text = OnscreenText(
            text="Use number keys to input answers. Press ENTER to submit. ESC to quit.",
            pos=(0, -0.9),
            scale=0.04,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter
        )
        
    def setup_controls(self):
        """Setup keyboard controls"""
        # Number inputs
        for i in range(10):
            self.accept(str(i), self.input_digit, [str(i)])
        
        self.accept("period", self.input_digit, ["."])
        self.accept("minus", self.input_digit, ["-"])
        self.accept("backspace", self.delete_digit)
        self.accept("enter", self.submit_answer)
        self.accept("escape", sys.exit)
        self.accept("r", self.restart_game)
        
        self.current_input = ""
        
    def input_digit(self, digit):
        """Handle digit input"""
        if len(self.current_input) < 10:  # Limit input length
            self.current_input += digit
            self.answer_display.setText(f"Answer: {self.current_input}")
            
    def delete_digit(self):
        """Delete last digit"""
        if self.current_input:
            self.current_input = self.current_input[:-1]
            self.answer_display.setText(f"Answer: {self.current_input}")
            
    def submit_answer(self):
        """Submit the current answer"""
        if not self.current_input or not self.current_experiment:
            return
            
        try:
            user_answer = float(self.current_input)
            self.check_physics_answer(user_answer)
        except ValueError:
            self.wrong_answer("Invalid number format")
            
        self.current_input = ""
        self.answer_display.setText("Answer: ")
        
    def start_experiment(self):
        """Start a new physics experiment"""
        experiment_key = random.choice(list(self.physics_experiments.keys()))
        experiment = self.physics_experiments[experiment_key]
        
        self.current_experiment = {
            'key': experiment_key,
            'data': experiment,
            'problem': random.choice(experiment['problems'])
        }
        
        # Update UI
        self.experiment_text.setText(f"Experiment: {experiment['name']}")
        self.problem_text.setText(self.current_experiment['problem']['question'])
        self.formula_text.setText(f"Formula: {self.current_experiment['problem']['formula']}")
        
    def check_physics_answer(self, user_answer):
        """Check if the physics answer is correct"""
        correct_answer = self.current_experiment['problem']['answer']
        tolerance = self.current_experiment['problem']['tolerance']
        
        if abs(user_answer - correct_answer) <= tolerance:
            self.correct_answer()
        else:
            self.wrong_answer(f"Correct answer: {correct_answer}")
            
    def correct_answer(self):
        """Handle correct answer"""
        self.score += 50 * self.level
        self.experiments_completed += 1
        self.update_ui()
        
        # Visual feedback - make equipment glow
        self.equipment.setColor(0, 1, 0, 1)  # Green glow
        
        # Reset color and start new experiment
        Sequence(
            Wait(1.5),
            Func(self.equipment.setColor, 1, 1, 1, 1),
            Func(self.next_experiment)
        ).start()
        
    def wrong_answer(self, message=""):
        """Handle wrong answer"""
        # Visual feedback - red glow
        self.equipment.setColor(1, 0, 0, 1)  # Red glow
        
        # Show correct answer briefly
        if message:
            temp_text = OnscreenText(
                text=message,
                pos=(0, -0.6),
                scale=0.06,
                fg=(1, 0.5, 0.5, 1),
                align=TextNode.ACenter
            )
            
            Sequence(
                Wait(2.0),
                Func(temp_text.removeNode)
            ).start()
        
        # Reset color and start new experiment
        Sequence(
            Wait(2.0),
            Func(self.equipment.setColor, 1, 1, 1, 1),
            Func(self.next_experiment)
        ).start()
        
    def next_experiment(self):
        """Move to next experiment"""
        # Increase level every 5 experiments
        if self.experiments_completed > 0 and self.experiments_completed % 5 == 0:
            self.level += 1
            
        self.start_experiment()
        
    def animate_wave(self, task):
        """Animate wave motion"""
        time = task.time
        
        for i, point in enumerate(self.wave_points):
            # Sine wave motion
            y_offset = math.sin(time * 2 + i * 0.5) * 0.5
            point.setZ(2 + y_offset)
            
        return task.cont
        
    def update_ui(self):
        """Update the user interface"""
        self.score_text.setText(f"Score: {self.score}")
        self.level_text.setText(f"Level: {self.level}")
        self.experiments_text.setText(f"Experiments: {self.experiments_completed}")
        
    def game_loop(self, task):
        """Main game loop"""
        if not self.game_running:
            return task.done
            
        # Rotate some equipment for visual appeal
        if hasattr(self, 'pendulum_bob'):
            # Pendulum motion is handled by intervals
            pass
            
        return task.cont
        
    def restart_game(self):
        """Restart the game"""
        self.score = 0
        self.level = 1
        self.experiments_completed = 0
        self.game_running = True
        self.current_input = ""
        
        self.equipment.setColor(1, 1, 1, 1)
        self.answer_display.setText("Answer: ")
        
        self.start_experiment()
        self.update_ui()

def main():
    """Main function to run the game"""
    game = PhysicsGame()
    game.run()

if __name__ == "__main__":
    main()