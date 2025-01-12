import React, { useState, useEffect, useRef } from "react";
import "./App.css";

const canvasWidth = 800;
const canvasHeight = 400;
const paddleWidth = 20;
const paddleHeight = 100;
const ballRadius = 10;

const App = () => {
    const canvasRef = useRef(null);
    const [gameState, setGameState] = useState(null);
    const [websocket, setWebSocket] = useState(null);
    const [player, setPlayer] = useState(1); // Default player 1

    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8000/ws");

        ws.onopen = () => {
            console.log("Connected to server");
        };

        ws.onmessage = (event) => {
            const state = JSON.parse(event.data);
            setGameState(state);
        };

        ws.onclose = () => {
            console.log("Disconnected from server");
        };

        setWebSocket(ws);

        return () => {
            ws.close();
        };
    }, []);

    useEffect(() => {
        const handleKeyDown = (event) => {
            if (!websocket) return;

            if (event.key === "ArrowUp") {
                websocket.send(JSON.stringify({ player, direction: "up" }));
            } else if (event.key === "ArrowDown") {
                websocket.send(JSON.stringify({ player, direction: "down" }));
            }
        };

        window.addEventListener("keydown", handleKeyDown);

        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };
    }, [websocket, player]);

    const drawGame = () => {
        if (!gameState || !canvasRef.current) return;

        const ctx = canvasRef.current.getContext("2d");
        ctx.clearRect(0, 0, canvasWidth, canvasHeight);

        // Draw paddles
        ctx.fillStyle = "blue";
        ctx.fillRect(0, gameState.player1.paddle_y, paddleWidth, paddleHeight);
        ctx.fillStyle = "red";
        ctx.fillRect(
            canvasWidth - paddleWidth,
            gameState.player2.paddle_y,
            paddleWidth,
            paddleHeight
        );

        // Draw ball
        ctx.fillStyle = "black";
        ctx.beginPath();
        ctx.arc(gameState.ball.x, gameState.ball.y, ballRadius, 0, Math.PI * 2);
        ctx.fill();

        // Draw obstacles
        ctx.fillStyle = "green";
        gameState.obstacles.forEach((obstacle) => {
            ctx.fillRect(obstacle.x, obstacle.y, obstacle.size, obstacle.size);
        });

        // Draw scores
        ctx.fillStyle = "black";
        ctx.font = "20px Arial";
        ctx.fillText(`Player 1: ${gameState.player1.score}`, 50, 30);
        ctx.fillText(`Player 2: ${gameState.player2.score}`, canvasWidth - 150, 30);
    };

    useEffect(() => {
        drawGame();
    }, [gameState]);

    return (
        <div className="App">
            <h1>Ping Pong Game</h1>
            <canvas
                ref={canvasRef}
                width={canvasWidth}
                height={canvasHeight}
                style={{ border: "1px solid black" }}
            ></canvas>
            <div>
                <button onClick={() => setPlayer(1)}>Play as Player 1</button>
                <button onClick={() => setPlayer(2)}>Play as Player 2</button>
            </div>
        </div>
    );
};

export default App;
