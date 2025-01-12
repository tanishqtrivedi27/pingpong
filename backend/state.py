# constants and dimensions
from pydantic import BaseModel

game_height = 800
game_width = 800
paddle_height = 100
paddle_width = 20
ball_radius = 10

class PlayerState(BaseModel):
    paddle_y: int
    score: float

class BallState(BaseModel):
    x: int
    y: int
    dx: int
    dy: int

class GameState(BaseModel):
    player1: PlayerState
    player2: PlayerState
    ball: BallState
    obstacles: list
