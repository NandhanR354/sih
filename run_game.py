#!/usr/bin/env python3
"""
Game Runner Script for Shiksha Leap
Runs Panda3D games based on grade and subject
"""

import sys
import os
import importlib.util

def run_game(grade, subject):
    """Run a specific game based on grade and subject"""
    try:
        # Construct the game module path
        game_file = f"games/grade_{grade}/{subject}_game.py"
        
        if not os.path.exists(game_file):
            print(f"Game not found: {game_file}")
            return False
        
        # Load the game module dynamically
        spec = importlib.util.spec_from_file_location(f"{subject}_game", game_file)
        game_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(game_module)
        
        # Run the game's main function
        if hasattr(game_module, 'main'):
            game_module.main()
        else:
            print(f"No main function found in {game_file}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error running game: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python run_game.py <grade> <subject>")
        print("Example: python run_game.py 6 mathematics")
        sys.exit(1)
    
    grade = sys.argv[1]
    subject = sys.argv[2]
    
    print(f"Starting {subject} game for grade {grade}...")
    success = run_game(grade, subject)
    
    if not success:
        print("Failed to start game")
        sys.exit(1)