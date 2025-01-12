import asyncio
from contextlib import asynccontextmanager
import random

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from state import PlayerState, GameState, BallState, game_height, game_width, paddle_height, paddle_width, ball_radius

state = GameState(
    player1=PlayerState(paddle_y=game_height // 2, score=0),
    player2=PlayerState(paddle_y=game_height // 2, score=0),
    ball=BallState(x=game_width // 2, y=game_height // 2, dx=5, dy=5),
    obstacles=[
        {"x": random.randint(100, game_width - 100), "y": random.randint(100, game_height - 100), "size": 50}
        for _ in range(2)
    ],
)

# Connected players
connected_clients = []

# Game logic
def handle_input(data):
    player = data.get("player")
    direction = data.get("direction")

    if player == 1:
        state.player1.paddle_y += 10 if direction == "down" else -10
        state.player1.paddle_y = max(0, min(game_height - paddle_height, state.player1.paddle_y))
    elif player == 2:
        state.player2.paddle_y += 10 if direction == "down" else -10
        state.player2.paddle_y = max(0, min(game_height - paddle_height, state.player2.paddle_y))

def move_ball():
    state.ball.x += state.ball.dx
    state.ball.y += state.ball.dy

    # Ball collision with top/bottom walls
    if state.ball.y - ball_radius <= 0 or state.ball.y + ball_radius >= game_height:
        state.ball.dy *= -1

    # Ball collision with paddles
    if (
        state.ball.x - ball_radius <= paddle_width
        and state.player1.paddle_y <= state.ball.y <= state.player1.paddle_y + paddle_height
    ) or (
        state.ball.x + ball_radius >= game_width - paddle_width
        and state.player2.paddle_y <= state.ball.y <= state.player2.paddle_y + paddle_height
    ):
        state.ball.dx *= -1

    # Ball out of bounds (score update)
    if state.ball.x - ball_radius <= 0:
        state.player2.score += 1
        reset_ball()
    elif state.ball.x + ball_radius >= game_width:
        state.player1.score += 1
        reset_ball()

    # Ball collision with obstacles
    for obstacle in state.obstacles:
        if (
            obstacle["x"] <= state.ball.x <= obstacle["x"] + obstacle["size"]
            and obstacle["y"] <= state.ball.y <= obstacle["y"] + obstacle["size"]
        ):
            state.ball.dx *= -1
            state.ball.dy *= -1


def reset_ball():
    state.ball.x = game_width // 2
    state.ball.y = game_height // 2
    state.ball.dx *= random.choice([-1, 1])
    state.ball.dy *= random.choice([-1, 1])

async def broadcast_state():
    game_state = state.model_dump()
    for client in connected_clients:
        await client.send_json(game_state)

# Background task to update game state
async def game_loop():
    while True:
        move_ball()
        await broadcast_state()
        await asyncio.sleep(0.03)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Load the ML model
    asyncio.create_task(game_loop())
    yield

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            handle_input(data)
            await broadcast_state()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)