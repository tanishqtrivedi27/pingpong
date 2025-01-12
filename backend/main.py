from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game constants
GAME_WIDTH = 800
GAME_HEIGHT = 400
PADDLE_HEIGHT = 100
PADDLE_WIDTH = 20
BALL_RADIUS = 10

class GameManager:
    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.state = {
            "player1": {"paddle_y": GAME_HEIGHT // 2 - PADDLE_HEIGHT // 2, "score": 0},
            "player2": {"paddle_y": GAME_HEIGHT // 2 - PADDLE_HEIGHT // 2, "score": 0},
            "ball": {"x": GAME_WIDTH // 2, "y": GAME_HEIGHT // 2, "dx": 5, "dy": 5},
        }

    async def connect_player(self, websocket: WebSocket, player_id: int):
        await websocket.accept()
        if player_id == 1 and not self.player1:
            self.player1 = websocket
            return "player1"
        elif player_id == 2 and not self.player2:
            self.player2 = websocket
            return "player2"
        else:
            await websocket.close(code=1000)
            return None

    def disconnect_player(self, websocket: WebSocket):
        if websocket == self.player1:
            self.player1 = None
        elif websocket == self.player2:
            self.player2 = None

    def update_paddle(self, player, direction):
        movement = 15
        if player == "player1":
            self.state["player1"]["paddle_y"] = max(
                0,
                min(
                    GAME_HEIGHT - PADDLE_HEIGHT,
                    self.state["player1"]["paddle_y"] + (movement if direction == "down" else -movement),
                ),
            )
        elif player == "player2":
            self.state["player2"]["paddle_y"] = max(
                0,
                min(
                    GAME_HEIGHT - PADDLE_HEIGHT,
                    self.state["player2"]["paddle_y"] + (movement if direction == "down" else -movement),
                ),
            )

    def move_ball(self):
        ball = self.state["ball"]
        ball["x"] += ball["dx"]
        ball["y"] += ball["dy"]

        # Wall collision
        if ball["y"] - BALL_RADIUS <= 0 or ball["y"] + BALL_RADIUS >= GAME_HEIGHT:
            ball["dy"] *= -1

        # Paddle collision
        if (
            ball["x"] - BALL_RADIUS <= PADDLE_WIDTH
            and self.state["player1"]["paddle_y"] <= ball["y"] <= self.state["player1"]["paddle_y"] + PADDLE_HEIGHT
        ):
            ball["dx"] *= -1

        if (
            ball["x"] + BALL_RADIUS >= GAME_WIDTH - PADDLE_WIDTH
            and self.state["player2"]["paddle_y"] <= ball["y"] <= self.state["player2"]["paddle_y"] + PADDLE_HEIGHT
        ):
            ball["dx"] *= -1

        # Scoring
        if ball["x"] - BALL_RADIUS <= 0:
            self.state["player2"]["score"] += 1
            self.reset_ball()
        elif ball["x"] + BALL_RADIUS >= GAME_WIDTH:
            self.state["player1"]["score"] += 1
            self.reset_ball()

    def reset_ball(self):
        self.state["ball"] = {"x": GAME_WIDTH // 2, "y": GAME_HEIGHT // 2, "dx": 5, "dy": 5}

    async def broadcast_state(self):
        if self.player1:
            await self.player1.send_json(self.state)
        if self.player2:
            await self.player2.send_json(self.state)


game_manager = GameManager()

@app.get("/", response_class=HTMLResponse)
async def get_game_page():
    # Serve the game HTML page
    html_content = open("../frontend/game.html", "r").read()  # Make sure the HTML file is present
    return HTMLResponse(content=html_content, status_code=200)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, player: int):
    player_id = await game_manager.connect_player(websocket, player)
    if not player_id:
        return

    try:
        while True:
            data = await websocket.receive_json()
            direction = data.get("direction")
            if direction:
                game_manager.update_paddle(player_id, direction)
    except WebSocketDisconnect:
        game_manager.disconnect_player(websocket)

async def game_loop():
    while True:
        game_manager.move_ball()
        await game_manager.broadcast_state()
        await asyncio.sleep(1 / 60)

@app.on_event("startup")
async def startup():
    asyncio.create_task(game_loop())
