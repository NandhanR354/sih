// Game Runner for Panda3D Games
// Handles communication between web interface and Python games

class GameRunner {
    constructor() {
        this.currentGame = null;
        this.gameProcess = null;
        this.gameStatus = 'stopped';
    }
    
    async startGame(grade, subject) {
        try {
            console.log(`Starting ${subject} game for grade ${grade}`);
            
            // Update UI to show game is starting
            this.updateGameStatus('starting', `Loading ${subject} game...`);
            
            // Call the API to start the game
            const response = await fetch('/api/run-game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    grade: grade, 
                    subject: subject 
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.currentGame = { grade, subject };
                this.gameStatus = 'running';
                this.updateGameStatus('running', 'Game is running!');
                
                // Start monitoring game status
                this.monitorGame();
                
                return true;
            } else {
                this.updateGameStatus('error', result.error);
                return false;
            }
            
        } catch (error) {
            console.error('Error starting game:', error);
            this.updateGameStatus('error', 'Failed to start game');
            return false;
        }
    }
    
    stopGame() {
        if (this.currentGame) {
            this.gameStatus = 'stopped';
            this.currentGame = null;
            this.updateGameStatus('stopped', 'Game stopped');
        }
    }
    
    monitorGame() {
        // Monitor game status (in a real implementation, this would
        // communicate with the Python process)
        const checkInterval = setInterval(() => {
            if (this.gameStatus === 'stopped') {
                clearInterval(checkInterval);
                return;
            }
            
            // Simulate game monitoring
            console.log('Game is running...');
            
        }, 5000);
    }
    
    updateGameStatus(status, message) {
        const statusElement = document.getElementById('gameStatus');
        if (statusElement) {
            statusElement.textContent = message;
        }
        
        // Update button states
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const restartBtn = document.getElementById('restartBtn');
        
        if (startBtn && pauseBtn && restartBtn) {
            switch (status) {
                case 'starting':
                    startBtn.disabled = true;
                    pauseBtn.disabled = true;
                    restartBtn.disabled = true;
                    break;
                case 'running':
                    startBtn.disabled = true;
                    pauseBtn.disabled = false;
                    restartBtn.disabled = false;
                    break;
                case 'stopped':
                case 'error':
                    startBtn.disabled = false;
                    pauseBtn.disabled = true;
                    restartBtn.disabled = true;
                    break;
            }
        }
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('gameStatusChanged', {
            detail: { status, message, game: this.currentGame }
        }));
    }
    
    // Game control methods
    pauseGame() {
        if (this.gameStatus === 'running') {
            this.gameStatus = 'paused';
            this.updateGameStatus('paused', 'Game paused');
        } else if (this.gameStatus === 'paused') {
            this.gameStatus = 'running';
            this.updateGameStatus('running', 'Game resumed');
        }
    }
    
    restartGame() {
        if (this.currentGame) {
            this.stopGame();
            setTimeout(() => {
                this.startGame(this.currentGame.grade, this.currentGame.subject);
            }, 1000);
        }
    }
    
    // Utility methods
    getAvailableGames(grade) {
        // Return list of available games for a grade
        const gamesByGrade = {
            6: ['mathematics', 'science', 'english', 'odia', 'social'],
            7: ['mathematics', 'science', 'english', 'odia', 'social'],
            8: ['mathematics', 'science', 'english', 'odia', 'social'],
            9: ['mathematics', 'science', 'english', 'odia', 'social'],
            10: ['mathematics', 'science', 'english', 'odia', 'social'],
            11: ['mathematics', 'physics', 'chemistry', 'biology', 'english', 'computer_science'],
            12: ['mathematics', 'physics', 'chemistry', 'biology', 'english', 'computer_science']
        };
        
        return gamesByGrade[grade] || [];
    }
    
    isGameAvailable(grade, subject) {
        const availableGames = this.getAvailableGames(grade);
        return availableGames.includes(subject);
    }
}

// Initialize game runner when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.gameRunner = new GameRunner();
    
    // Listen for game status changes
    window.addEventListener('gameStatusChanged', (event) => {
        console.log('Game status changed:', event.detail);
    });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GameRunner;
}