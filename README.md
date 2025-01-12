## Setup

### Backend (FastAPI)

can use a virtual environment also 

1. **Install dependencies**:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

2. **Run the server**:
    ```bash
    python -m uvicorn main:app --reload
    ```

3. Open `http://localhost:8000/?player=1` for Player 1 and `http://localhost:8000/?player=2` for Player 2.


## Things to Improve
- **Game Management**: Support multiple rooms (currently only 2 players per game).
- **Frontend**: Refactor the code using React or Vue for better structure and state management.
- **Containerize**: Containerize the app using docker.

---

## Video Link
https://www.loom.com/share/98a57ee2cace40b59a972a76083744e5