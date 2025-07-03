import pygame

from state import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.image.load('pygame.jpg')
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
screen.blit(background,(0,0))

from input import Input
running = True

from state import State, Player, Ball, Post, Team, MatchManager, MatchState

# Create mock players
players = {
    ("Alice", 1): Player(
        x=400, y=300, vx=0, vy=0, radius=45, mass=1, drag_coefficient=0.1,
        name="Alice", team=Team.RED, kick=False, kick_locked=False
    ),
    ("Bob", 2): Player(
        x=800, y=300, vx=0, vy=0, radius=45, mass=1, drag_coefficient=0.1,
        name="Bob", team=Team.BLUE, kick=False, kick_locked=False
    ),
}

# Create mock ball
ball = Ball(x=600, y=400, vx=0, vy=0, radius=30, mass=0.5, drag_coefficient=0.05)

# Create mock posts
posts = {
    "red_post1": Post(x=100, y=540, vx=0, vy=0, radius=15, mass=10, drag_coefficient=0.1, team=Team.RED),
    "red_post2": Post(x=100, y=440, vx=0, vy=0, radius=15, mass=10, drag_coefficient=0.1, team=Team.RED),
    "blue_post1": Post(x=1820, y=540, vx=0, vy=0, radius=15, mass=10, drag_coefficient=0.1, team=Team.BLUE),
    "blue_post2": Post(x=1820, y=440, vx=0, vy=0, radius=15, mass=10, drag_coefficient=0.1, team=Team.BLUE),
}

# Create a match manager
match_manager = MatchManager(
    state=MatchState.PLAYING,
    match_duration=600,
    break_duration=60,
    overtime_duration=120,
    time_remaining=600,
    state_before_pause=None
)

# Create the game state
state = State(
    player_area_coords=(0, 0, 1920, 1080),
    field_coords=(100, 100, 1720, 880),
    players=players,
    ball=ball,
    posts=posts,
    score_red=2,
    score_blue=0,
    clock=100,
    match_manager=match_manager
)

pygame.font.init()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    inputs = Input(
        keys[pygame.K_w],
        keys[pygame.K_s],
        keys[pygame.K_a],
        keys[pygame.K_d],
        keys[pygame.K_SPACE],
    )

    # Score
    pygame.draw.rect(screen, "antiquewhite3", state.field_coords, 3)

    font = pygame.font.SysFont("papyrus",36)
    score_text = f"{state.score_red} - {state.score_blue}"
    text_surface = font.render(score_text, True, pygame.Color("black"))
    screen.blit(text_surface, (80, 10))
    
    # Bola
    pygame.draw.circle(screen, pygame.Color("white"), (int(state.ball.x), int(state.ball.y)), 30)

    # Jogadores
    for player in state.players.values():
        color = pygame.Color("cornflowerblue") if player.team == Team.BLUE else pygame.Color("crimson")
        pygame.draw.circle(screen, color, (int(player.x), int(player.y)), 45)

    # Postes
    for post in state.posts.values():
        pygame.draw.circle(screen, pygame.Color("cornsilk"), (int(post.x), int(post.y)), 15)

    pygame.display.flip()


pygame.quit()