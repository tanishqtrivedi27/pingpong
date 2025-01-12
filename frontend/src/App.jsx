import React, { useState, useEffect, useCallback } from "react";

const styles = {
    gameContainer: {
        width: "800px",
        height: "400px",
        position: "relative",
        border: "1px solid black",
        margin: "20px auto",
        background: "#f0f0f0",
    },
    paddle: {
        width: "20px",
        height: "100px",
        position: "absolute",
        backgroundColor: "black",
    },
    ball: {
        width: "10px",
        height: "10px",
        position: "absolute",
        backgroundColor: "red",
        borderRadius: "50%",
        transform: "translate(-50%, -50%)",
    },
};

const PingPong = () => {
    const [gameState, setGameState] = useState(null);
    const [playerId, setPlayerId] = useState(null);
    const [status, setStatus] = useState("Connecting...");
    const [ws, setWs] = useState(null);

    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8000/ws");
        socket.onopen = () => setStatus("Connected");
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setGameState(data);
        };
        socket.onclose = () => setStatus("Disconnected");
        setWs(socket);
        return () => socket.close();
    }, []);

    const handleKeyPress = useCallback(
        (e) => {
            if (!ws || ws.readyState !== WebSocket.OPEN) return;
            if (e.key === "ArrowUp" || e.key === "ArrowDown") {
                ws.send(JSON.stringify({ direction: e.key === "ArrowUp" ? "up" : "down" }));
            }
        },
        [ws]
    );

    useEffect(() => {
        window.addEventListener("keydown", handleKeyPress);
        return () => window.removeEventListener("keydown", handleKeyPress);
    }, [handleKeyPress]);

    if (!gameState) return <div>Loading...</div>;

    return (
        <div>
            <div>Score - Player 1: {gameState.player1.score} Player 2: {gameState.player2.score}</div>
            <div>Status: {status}</div>
            {playerId && <div>You are Player: {playerId}</div>}

            <div style={styles.gameContainer}>
                <div
                    style={{
                        ...styles.paddle,
                        left: 0,
                        top: gameState.player1.paddle_y,
                    }}
                />
                <div
                    style={{
                        ...styles.paddle,
                        right: 0,
                        top: gameState.player2.paddle_y,
                    }}
                />
                <div
                    style={{
                        ...styles.ball,
                        left: gameState.ball.x,
                        top: gameState.ball.y,
                    }}
                />
            </div>
        </div>
    );
};

export default PingPong;
