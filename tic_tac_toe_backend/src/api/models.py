"""
Models for Tic Tac Toe Backend.
Defines pydantic schemas and internal representations for Users, Games, Moves, Scores, and GameHistory.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# PUBLIC_INTERFACE
class UserCreateRequest(BaseModel):
    """Request schema for registering a new user."""
    username: str = Field(..., description="Unique username for registration")
    email: str = Field(..., description="User email address")

# PUBLIC_INTERFACE
class UserResponse(BaseModel):
    """Response schema for user data."""
    id: int = Field(..., description="User unique ID")
    username: str
    email: str
    created_at: datetime

# PUBLIC_INTERFACE
class GameCreateRequest(BaseModel):
    """Request schema for creating a new game."""
    player_x_id: int = Field(..., description="User ID for player X")
    player_o_id: int = Field(..., description="User ID for player O")

# PUBLIC_INTERFACE
class GameMoveRequest(BaseModel):
    """Request schema for making a move in a game."""
    user_id: int = Field(..., description="User making the move")
    game_id: int = Field(..., description="Game session ID")
    row: int = Field(..., description="Row index (0-2) of the move")
    col: int = Field(..., description="Col index (0-2) of the move")

# PUBLIC_INTERFACE
class GameMoveResponse(BaseModel):
    """Response schema for game move result."""
    board: List[List[Optional[str]]] = Field(..., description="Current board state after the move")
    winner: Optional[str] = Field(None, description="Winner (if any)")
    status: str = Field(..., description="Status of the game: ongoing, finished, draw, etc.")
    next_player: Optional[str] = Field(None, description="Next player to move")

# PUBLIC_INTERFACE
class GameStateResponse(BaseModel):
    """Response schema for current game state."""
    board: List[List[Optional[str]]]
    status: str
    winner: Optional[str]
    history: List[dict]
    next_player: Optional[str]

# PUBLIC_INTERFACE
class GameHistoryEntry(BaseModel):
    """Entry for a finished game history."""
    game_id: int
    started_at: datetime
    finished_at: Optional[datetime]
    player_x: str
    player_o: str
    winner: Optional[str]
    moves: List[dict]

# PUBLIC_INTERFACE
class ScoreEntry(BaseModel):
    """Entry for leaderboard or user score."""
    user_id: int
    username: str
    wins: int
    losses: int
    draws: int

# PUBLIC_INTERFACE
class LeaderboardResponse(BaseModel):
    """Response schema for leaderboard."""
    leaderboard: List[ScoreEntry]
