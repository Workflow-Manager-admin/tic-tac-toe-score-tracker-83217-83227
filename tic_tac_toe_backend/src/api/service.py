"""
Service layer for Tic Tac Toe backend.
Implements business logic and database operations. Stubbed for now, to be integrated with the tic_tac_toe_database container.
"""

from .models import (
    UserCreateRequest, UserResponse,
    GameCreateRequest, GameMoveRequest, GameMoveResponse,
    GameStateResponse, GameHistoryEntry, ScoreEntry, LeaderboardResponse
)
from datetime import datetime
from typing import List, Optional

# For simulating in-memory storage (replace with DB integration)
users = []
games = []
game_histories = []
leaderboard = []

# PUBLIC_INTERFACE
def create_user(user: UserCreateRequest) -> UserResponse:
    """Create a new user in the database."""
    new_user = UserResponse(
        id=len(users) + 1,
        username=user.username,
        email=user.email,
        created_at=datetime.utcnow()
    )
    users.append(new_user)
    return new_user

# PUBLIC_INTERFACE
def get_user(user_id: int) -> Optional[UserResponse]:
    """Retrieve a user by ID."""
    for u in users:
        if u.id == user_id:
            return u
    return None

# PUBLIC_INTERFACE
def list_users() -> List[UserResponse]:
    """List all users."""
    return users

# PUBLIC_INTERFACE
def create_game(game: GameCreateRequest) -> dict:
    """Start a new game session."""
    new_game = {
        "game_id": len(games) + 1,
        "player_x_id": game.player_x_id,
        "player_o_id": game.player_o_id,
        "board": [[None for _ in range(3)] for _ in range(3)],
        "moves": [],
        "status": "ongoing",
        "winner": None,
        "created_at": datetime.utcnow(),
        "finished_at": None,
        "next_player": "X"
    }
    games.append(new_game)
    return new_game

# PUBLIC_INTERFACE
def make_move(move: GameMoveRequest) -> GameMoveResponse:
    """
    Make a move on the board, check win condition, and update the game state.
    """
    # Find game
    game = next((g for g in games if g["game_id"] == move.game_id), None)
    if not game:
        raise ValueError("Invalid game_id")
    board = game["board"]
    player = "X" if game["player_x_id"] == move.user_id else "O"
    if board[move.row][move.col] is not None or game["status"] != "ongoing":
        raise ValueError("Invalid move")
    board[move.row][move.col] = player
    game["moves"].append(dict(user_id=move.user_id, row=move.row, col=move.col, player=player))
    # Check for winner
    def check_winner(board):
        for mark in ["X", "O"]:
            # Rows, columns, diagonals
            for i in range(3):
                if all(board[i][j] == mark for j in range(3)):
                    return mark
                if all(board[j][i] == mark for j in range(3)):
                    return mark
            if all(board[i][i] == mark for i in range(3)):
                return mark
            if all(board[i][2 - i] == mark for i in range(3)):
                return mark
        return None

    winner = check_winner(board)
    draw = all(cell is not None for row in board for cell in row)
    if winner:
        game["status"] = "finished"
        game["winner"] = winner
        game["finished_at"] = datetime.utcnow()
    elif draw:
        game["status"] = "draw"
        game["winner"] = None
        game["finished_at"] = datetime.utcnow()
    else:
        # Switch next player
        game["next_player"] = "O" if player == "X" else "X"

    return GameMoveResponse(
        board=board,
        winner=game["winner"],
        status=game["status"],
        next_player=game["next_player"],
    )

# PUBLIC_INTERFACE
def get_game_state(game_id: int) -> GameStateResponse:
    """Fetch current board and game state."""
    game = next((g for g in games if g["game_id"] == game_id), None)
    if not game:
        raise ValueError("Invalid game_id")
    return GameStateResponse(
        board=game["board"],
        status=game["status"],
        winner=game["winner"],
        history=game["moves"],
        next_player=game["next_player"],
    )

# PUBLIC_INTERFACE
def get_game_history(user_id: int) -> List[GameHistoryEntry]:
    """Get game history for a user."""
    results = []
    for g in games:
        if g["player_x_id"] == user_id or g["player_o_id"] == user_id:
            results.append(
                GameHistoryEntry(
                    game_id=g["game_id"],
                    started_at=g["created_at"],
                    finished_at=g["finished_at"],
                    player_x=get_user(g["player_x_id"]).username,
                    player_o=get_user(g["player_o_id"]).username,
                    winner=g["winner"],
                    moves=g["moves"],
                )
            )
    return results

# PUBLIC_INTERFACE
def get_leaderboard() -> LeaderboardResponse:
    """
    Compute and return leaderboard (in-memory, to be replaced by DB aggregate).
    """
    stats = {}
    for g in games:
        if g["status"] not in ["finished", "draw"]:
            continue
        px, po = g["player_x_id"], g["player_o_id"]
        winner = g["winner"] or "draw"
        for pid, uname in [(px, get_user(px).username), (po, get_user(po).username)]:
            if pid not in stats:
                stats[pid] = dict(user_id=pid, username=uname, wins=0, losses=0, draws=0)
        if winner == "X":
            stats[px]["wins"] += 1
            stats[po]["losses"] += 1
        elif winner == "O":
            stats[po]["wins"] += 1
            stats[px]["losses"] += 1
        elif winner == "draw":
            stats[px]["draws"] += 1
            stats[po]["draws"] += 1
    scored = [ScoreEntry(**s) for s in stats.values()]
    scored.sort(key=lambda e: -e.wins)
    return LeaderboardResponse(leaderboard=scored)
