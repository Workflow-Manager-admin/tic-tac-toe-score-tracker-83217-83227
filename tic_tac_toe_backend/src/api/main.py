from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    UserCreateRequest, UserResponse,
    GameCreateRequest, GameMoveRequest, GameMoveResponse,
    GameStateResponse, GameHistoryEntry, LeaderboardResponse
)
from . import service
from typing import List

openapi_tags = [
    {"name": "Users", "description": "User management (registration, list, details)"},
    {"name": "Games", "description": "Create game, play moves, get game state"},
    {"name": "Leaderboard", "description": "Leaderboards and user scores"},
    {"name": "History", "description": "Per-user game history"},
]

app = FastAPI(
    title="Tic Tac Toe API",
    version="1.0.0",
    description="REST API for classic tic tac toe game logic, user management, scoring, and history.",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    Returns simple message if backend is running.
    """
    return {"message": "Healthy"}


# ----------------- USER ROUTES ------------------------
# PUBLIC_INTERFACE
@app.post("/users/", response_model=UserResponse, status_code=201, summary="Register new user", tags=["Users"])
def register_user(user: UserCreateRequest):
    """
    Register a new user.
    - **username**: unique username
    - **email**: user email
    """
    u = service.create_user(user)
    return u

# PUBLIC_INTERFACE
@app.get("/users/", response_model=List[UserResponse], summary="List all users", tags=["Users"])
def list_users():
    """
    List all users.
    """
    return service.list_users()

# PUBLIC_INTERFACE
@app.get("/users/{user_id}", response_model=UserResponse, summary="Get user details", tags=["Users"])
def get_user(user_id: int):
    """
    Get user details by user ID.
    """
    u = service.get_user(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u

# ----------------- GAME ROUTES ------------------------
# PUBLIC_INTERFACE
@app.post("/games/", summary="Start a new game", tags=["Games"])
def start_game(game: GameCreateRequest):
    """
    Start a new tic tac toe game between two users.
    - **player_x_id**: User ID for X
    - **player_o_id**: User ID for O
    Returns: game state.
    """
    try:
        g = service.create_game(game)
        return g
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# PUBLIC_INTERFACE
@app.post("/games/move/", response_model=GameMoveResponse, summary="Make a move", tags=["Games"])
def play_move(move: GameMoveRequest):
    """
    Make a move on a board in a specific game session.
    - **user_id**: User making the move
    - **game_id**: Game session ID
    - **row, col**: Move coordinates (0-2)
    """
    try:
        resp = service.make_move(move)
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# PUBLIC_INTERFACE
@app.get("/games/{game_id}/state/", response_model=GameStateResponse, summary="Get current game state", tags=["Games"])
def get_game_state(game_id: int):
    """
    Get the current state of the board and game session.
    """
    try:
        return service.get_game_state(game_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# ----------------- LEADERBOARD ------------------------
# PUBLIC_INTERFACE
@app.get("/leaderboard/", response_model=LeaderboardResponse, summary="Leaderboard", tags=["Leaderboard"])
def leaderboard():
    """
    View the leaderboard (top scores).
    Sorted in descending order by wins.
    """
    return service.get_leaderboard()

# ----------------- GAME HISTORY ------------------------
# PUBLIC_INTERFACE
@app.get("/users/{user_id}/history/", response_model=List[GameHistoryEntry], summary="User's game history", tags=["History"])
def user_game_history(user_id: int):
    """
    View a user's completed games and history.
    """
    return service.get_game_history(user_id)
