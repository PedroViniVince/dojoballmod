SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

from enum import Enum, auto

class Team(Enum):
    RED = auto()
    BLUE = auto()

    def __str__(self) -> str:
        return self.name.lower()

class MatchState(Enum):
    PLAYING = auto()
    OVERTIME = auto()
    BREAK = auto()
    PAUSED = auto()

from dataclasses import dataclass

@dataclass
class Circle:
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    mass: float
    drag_coefficient: float

@dataclass
class Player(Circle):
    name: str
    team: Team
    kick: bool
    kick_locked: bool

@dataclass
class Ball(Circle):
    pass

@dataclass
class Post(Circle):
    team: Team

from typing import Optional

@dataclass
class MatchManager:
    state: MatchState
    match_duration: int
    break_duration: int
    overtime_duration: int
    time_remaining: int
    state_before_pause: Optional[MatchState]

@dataclass
class State:
    player_area_coords: tuple[int, int, int, int]
    field_coords: tuple[int, int, int, int]
    players: dict[tuple[str, int], Player]
    ball: Ball
    posts: dict[str, Post]
    score_red: int
    score_blue: int
    clock: int
    match_manager: MatchManager