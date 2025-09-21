#!/usr/bin/env python3
"""
Grade 6 Science Game - Panda3D
Nature Lab - Explore the natural world in 3D
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

class ScienceGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Game state
        self.score = 0
        self.level = 1
        self.specimens_collected = 0
        self.current_question = None
        self.game_running = True
        
        # Science topics for Grade 6
        self.science_topics = {
            'plants': {
                'questions': [
                    {'q': 'Which part of plant makes food?', 'a': 'leaves', 'options': ['roots', 'leaves', 'stem', 'flower']},
                    {'q': 'What do plants need for photosynthesis?', 'a': 'sunlight', 'options': ['darkness', 'sunlight', 'cold', 'noise']},
                    {'q': 'Which gas do plants release?', 'a': 'oxygen', 'options': ['carbon dioxide', 'oxygen', 'nitrogen', 'hydrogen']}
                ]
            },
            'animals': {
                'questions': [
                    {'q': 'Which animal is herbivore?', 'a': 'cow', 'options': ['lion', 'cow', 'tiger', 'eagle']},
                    {'q': 'What do fish use to breathe?', 'a': 'gills', 'options': ['lungs', 'gills', 'nose', 'skin']},
                    {'q': 'Which animal lays eggs?', 'a': 'bird', 'options': ['dog', 'bird', 'cat', 'cow']}
                ]
            },
            'water_cycle': {
                'questions': [
                    {'q': 'What happens when water heats up?', 'a': 'evaporation', 'options': ['freezing', 'evaporation', 'melting', 'condensation']},
                    {'q': 'What forms clouds?', 'a': 'water vapor', 'options': ['dust', 'water vapor', 'smoke', 'air']},
                    {'q': 'What comes down as rain?', 'a': 'water', 'options': ['ice', 'water', 'snow', 'hail']}
                ]
            }
        }
        
        # Setup the game
        self.setup_environment()
        self.setup_player()
        self.setup_specimens()
        self.setup_ui()
        self.setup_controls()
        self.generate_science_question()
        
        # Start the game loop
        self.taskMgr.add(self.game_loop, "game_loop")
        
    def setup_environment(self):
        """Setup the 3D nature environment"""
        # Disable the camera trackball controls
        self.disableMouse()
        
        # Set camera position
        self.camera.setPos(0, -25, 8)
        self.camera.lookAt(0, 0, 0)
        
        # Create a nature scene
        self.environment = self.render.attachNewNode("environment")
        
        # Create ground (grass)
        cm = CardMaker("ground")
        cm.setFrame(-30, 30, -30, 30)
        self.ground = self.environment.attachNewNode(cm.generate())
        self.ground.setP(-90)  # Rotate to be horizontal
        self.ground.setColor(0.2, 0.8, 0.2, 1)  # Green grass
        self.ground.setPos(0, 0, -1)
        
        # Create some trees
        self.create_trees()
        
        # Create a pond
        self.create_pond()
        
        # Add lighting
        alight = AmbientLight('alight')
        alight.setColor((0.3, 0.3, 0.3, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight('dlight')
        dlight.setDirection((-1, -1, -1))
        dlight.setColor((0.9, 0.9, 0.7, 1))  # Sunlight
        dlnp = self.render.attachNewNode(dlight)
        self.render.setLight(dlnp)
        
    def create_trees(self):
        """Create simple tree models"""
        for i in range(8):
            tree = self.environment.attachNewNode(f"tree_{i}")
            
            # Tree trunk
            trunk_cm = CardMaker("trunk")
            trunk_cm.setFrame(-0.3, 0.3, 0, 3)
            trunk = tree.attachNewNode(trunk_cm.generate())
            trunk.setColor(0.4, 0.2, 0.1, 1)  # Brown
            
            # Tree leaves (crown)
            crown_cm = CardMaker("crown")
            crown_cm.setFrame(-1.5, 1.5, -1.5, 1.5)
            crown = tree.attachNewNode(crown_cm.generate())
            crown.setPos(0, 0, 3.5)
            crown.setColor(0.1, 0.6, 0.1, 1)  # Dark green
            
            # Position trees randomly
            x = random.uniform(-20, 20)
            y = random.uniform(-20, 20)
            tree.setPos(x, y, 0)
            
    def create_pond(self):
        """Create a simple pond"""
        pond_cm = CardMaker("pond")
        pond_cm.setFrame(-4, 4, -3, 3)
        self.pond = self.environment.attachNewNode(pond_cm.generate())
        self.pond.setP(-90)
        self.pond.setPos(10, 10, -0.5)
        self.pond.setColor(0.2, 0.4, 0.8, 0.8)  # Blue water
        
    def setup_player(self):
        """Setup the player (nature explorer)"""
        self.player = self.render.attachNewNode("player")
        
        # Create a simple explorer character
        cm = CardMaker("explorer")
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        
        # Body
        body = self.player.attachNewNode(cm.generate())
        body.setColor(0.8, 0.4, 0.2, 1)  # Explorer outfit
        body.setPos(0, 0, 1)
        
        # Head
        head = self.player.attachNewNode(cm.generate())
        head.setColor(0.9, 0.7, 0.5, 1)  # Skin color
        head.setPos(0, 0, 2)
        head.setScale(0.6)
        
        self.player.setPos(0, 0, 0)
        
        # Player movement variables
        self.player_speed = 8
        self.player_pos = [0, 0, 0]
        
    def setup_specimens(self):
        """Setup collectible specimens around the environment"""
        self.specimens = []
        specimen_types = ['leaf', 'flower', 'rock', 'insect']
        colors = [(0.2, 0.8, 0.2, 1), (1, 0.8, 0.2, 1), (0.5, 0.5, 0.5, 1), (0.8, 0.2, 0.2, 1)]
        
        for i in range(12):
            specimen = self.render.attachNewNode(f"specimen_{i}")
            
            # Create specimen visual
            cm = CardMaker("specimen")
            cm.setFrame(-0.3, 0.3, -0.3, 0.3)
            spec_visual = specimen.attachNewNode(cm.generate())
            
            spec_type = random.choice(specimen_types)
            color_idx = specimen_types.index(spec_type)
            spec_visual.setColor(colors[color_idx])
            
            # Position randomly
            x = random.uniform(-15, 15)
            y = random.uniform(-15, 15)
            specimen.setPos(x, y, 0.5)
            
            # Add floating animation
            specimen.hprInterval(3, (360, 0, 0)).loop()
            
            self.specimens.append({
                'node': specimen,
                'type': spec_type,
                'collected': False
            })
            
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
        
        # Specimens collected
        self.specimens_text = OnscreenText(
            text=f"Specimens: {self.specimens_collected}/12",
            pos=(-1.3, 0.8),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )
        
        # Current question
        self.question_text = OnscreenText(
            text="",
            pos=(0, 0.6),
            scale=0.08,
            fg=(1, 1, 0, 1),
            align=TextNode.ACenter,
            wordwrap=40
        )
        
        # Answer options
        self.option_texts = []
        for i in range(4):
            option_text = OnscreenText(
                text="",
                pos=(-0.5 + (i % 2) * 1, 0.3 - (i // 2) * 0.15),
                scale=0.06,
                fg=(0.8, 0.8, 1, 1),
                align=TextNode.ALeft
            )
            self.option_texts.append(option_text)
        
        # Instructions
        self.instruction_text = OnscreenText(
            text="Move with arrow keys. Collect specimens and answer questions!\nPress 1-4 to answer questions.",
            pos=(0, -0.9),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter
        )
        
    def setup_controls(self):
        """Setup keyboard controls"""
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
        
        # Answer inputs
        self.accept("1", self.answer_question, [0])
        self.accept("2", self.answer_question, [1])
        self.accept("3", self.answer_question, [2])
        self.accept("4", self.answer_question, [3])
        
        self.accept("escape", sys.exit)
        self.accept("r", self.restart_game)
        
    def set_key(self, key, value):
        """Set key state for continuous movement"""
        self.keys[key] = value
        
    def generate_science_question(self):
        """Generate a new science question"""
        topic = random.choice(list(self.science_topics.keys()))
        question_data = random.choice(self.science_topics[topic]['questions'])
        
        self.current_question = question_data
        self.question_text.setText(question_data['q'])
        
        # Display options
        for i, option in enumerate(question_data['options']):
            self.option_texts[i].setText(f"{i+1}. {option}")
            
    def answer_question(self, option_index):
        """Handle question answering"""
        if not self.current_question:
            return
            
        selected_answer = self.current_question['options'][option_index]
        correct_answer = self.current_question['a']
        
        if selected_answer == correct_answer:
            self.correct_answer()
        else:
            self.wrong_answer()
            
    def correct_answer(self):
        """Handle correct answer"""
        self.score += 20
        self.update_ui()
        
        # Visual feedback
        self.player.setColor(0, 1, 0, 1)  # Green for correct
        
        # Reset color and generate new question
        Sequence(
            Wait(1.0),
            Func(self.player.setColor, 1, 1, 1, 1),
            Func(self.generate_science_question)
        ).start()
        
    def wrong_answer(self):
        """Handle wrong answer"""
        # Visual feedback
        self.player.setColor(1, 0, 0, 1)  # Red for wrong
        
        # Reset color and generate new question
        Sequence(
            Wait(1.0),
            Func(self.player.setColor, 1, 1, 1, 1),
            Func(self.generate_science_question)
        ).start()
        
    def check_specimen_collection(self):
        """Check if player is near any specimens"""
        player_pos = self.player.getPos()
        
        for specimen in self.specimens:
            if specimen['collected']:
                continue
                
            spec_pos = specimen['node'].getPos()
            distance = (player_pos - spec_pos).length()
            
            if distance < 2.0:  # Collection range
                self.collect_specimen(specimen)
                
    def collect_specimen(self, specimen):
        """Collect a specimen"""
        specimen['collected'] = True
        specimen['node'].hide()
        
        self.specimens_collected += 1
        self.score += 10
        self.update_ui()
        
        # Check if all specimens collected
        if self.specimens_collected >= 12:
            self.level_complete()
            
    def level_complete(self):
        """Handle level completion"""
        self.level += 1
        
        # Bonus points
        self.score += 100
        
        # Reset specimens for next level
        self.specimens_collected = 0
        for specimen in self.specimens:
            specimen['collected'] = False
            specimen['node'].show()
            
        self.update_ui()
        
    def update_ui(self):
        """Update the user interface"""
        self.score_text.setText(f"Score: {self.score}")
        self.specimens_text.setText(f"Specimens: {self.specimens_collected}/12")
        
    def game_loop(self, task):
        """Main game loop"""
        if not self.game_running:
            return task.done
            
        dt = globalClock.getDt()
        
        # Handle continuous movement
        if self.keys["up"]:
            self.player_pos[1] += self.player_speed * dt
        if self.keys["down"]:
            self.player_pos[1] -= self.player_speed * dt
        if self.keys["left"]:
            self.player_pos[0] -= self.player_speed * dt
        if self.keys["right"]:
            self.player_pos[0] += self.player_speed * dt
            
        # Keep player within bounds
        self.player_pos[0] = max(-25, min(25, self.player_pos[0]))
        self.player_pos[1] = max(-25, min(25, self.player_pos[1]))
        
        self.player.setPos(self.player_pos[0], self.player_pos[1], self.player_pos[2])
        
        # Check for specimen collection
        self.check_specimen_collection()
        
        return task.cont
        
    def restart_game(self):
        """Restart the game"""
        self.score = 0
        self.level = 1
        self.specimens_collected = 0
        self.game_running = True
        self.player_pos = [0, 0, 0]
        self.player.setPos(0, 0, 0)
        self.player.setColor(1, 1, 1, 1)
        
        # Reset specimens
        for specimen in self.specimens:
            specimen['collected'] = False
            specimen['node'].show()
            
        self.generate_science_question()
        self.update_ui()

def main():
    """Main function to run the game"""
    game = ScienceGame()
    game.run()

if __name__ == "__main__":
    main()