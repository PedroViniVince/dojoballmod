import socket
import pickle
import pygame

def send_data(client_socket, data):
    data = pickle.dumps(data)  # Serializa os dados
    data = len(data).to_bytes(4, "big") + data  # Prefixa com o tamanho
    client_socket.sendall(data)

def receive_data(client_socket):
    size = int.from_bytes(client_socket.recv(4), "big")
    data = bytearray()
    while len(data) < size:
        chunk = client_socket.recv(size - len(data))
        data.extend(chunk)
    return pickle.loads(data)

client_socket = socket.create_connection(("193.136.19.129", 4005))
player_id = receive_data(client_socket)
initial_info = receive_data(client_socket)

# Nome
while True:
    name = input("Nick: ")
    send_data(client_socket, name)
    name_info = receive_data(client_socket)
    if name_info.get("error"):
        print(name_info["error"])
        exit()
    if name_info["validity"]:
        break
    else:
        print("Nome já escolhido. Tenta outro.")

# Equipa
from state import Team
while True:
    team_input = input("Equipa ([b]lue/[r]ed): ").strip().lower()
    if team_input in ["blue", "b"]:
        team = Team.BLUE
    elif team_input in ["red", "r"]:
        team = Team.RED
    else:
        print("Equipa inválida. Tente novamente.")
        continue
    send_data(client_socket, team)
    team_info = receive_data(client_socket)
    if team_info.get("error"):
        print(team_info["error"])
        exit()
    if team_info["validity"]:
        break
    else:
        print("Equipa indisponível. Tente outra.")
        

from state import SCREEN_WIDTH, SCREEN_HEIGHT, MatchManager, MatchState

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.image.load('image.png').convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.font.init()
font1 = pygame.font.SysFont("comic sans", 24)
font2 = pygame.font.SysFont("comic sans",36)


from input import Input
running = True
clock = pygame.time.Clock()

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
        pygame.display.get_window_size()[0],
        pygame.display.get_window_size()[1],
    )
    clock.tick(120)
    send_data(client_socket, inputs)
    state = receive_data(client_socket)

   # screen.fill("antiquewhite4")
    screen.blit(background,(0,0))



    #campo
    pygame.draw.rect(screen, "antiquewhite3", (state.field_coords[0],state.field_coords[1],
                                               state.field_coords[2]- state.field_coords[0],
                                               state.field_coords[3] - state.field_coords[1]), 3)

	
    # Bola
    pygame.draw.circle(screen, pygame.Color("white"), (int(state.ball.x), int(state.ball.y)), 30)

    # Jogadores
    for player in state.players.values():
        color = pygame.Color("cornflowerblue") if player.team == Team.BLUE else pygame.Color("crimson")
        coloroutline = pygame.Color("blue") if player.team == Team.BLUE else pygame.Color("red")
        name = player.name if player.name else "Unknown"
        name_text = font1.render(name, True, pygame.Color("black"))
        text_rect = name_text.get_rect(center=(int(player.x), int(player.y) - 50))
        screen.blit(name_text, text_rect)
        pygame.draw.circle(screen, color, (int(player.x), int(player.y)), 45)
        pygame.draw.circle(screen, coloroutline, (int(player.x), int(player.y)), 45, width=5)

    # Postes
    for post in state.posts.values():
        pygame.draw.circle(screen, pygame.Color("cornsilk"), (int(post.x), int(post.y)), 15)
    
    #menu
    pygame.draw.rect(screen, "antiquewhite4", [0, 0, 1920, 50])
    pygame.draw.rect(screen, "antiquewhite3", [0, 0, 1920, 50], 3)
    
    #clock
    clock_text = int(state.match_manager.time_remaining)
    if state.match_manager.state == MatchState.PLAYING:
        clock_state = "Playing"
    elif state.match_manager.state == MatchState.OVERTIME:
        clock_state = "Overtime"
    elif state.match_manager.state == MatchState.BREAK:
        clock_state = "Break"
        pygame.draw.rect(screen, "antiquewhite4", [0, 500, 1920, 80])
        screen.blit(font2.render("Break", True, pygame.Color("black")), (900, 520))
    elif state.match_manager.state == MatchState.PAUSED:
        clock_state = "Paused"
    text_clock_surface = font2.render(f"{clock_state} : {clock_text}", True, pygame.Color("black"))
    screen.blit(text_clock_surface, (200, 15))
    
    #FPS
    screen.blit(font2.render(f"FPS: {int(clock.get_fps())}", True, pygame.Color("black")), (1500, 15))
    
    #Score
    score_text = f"{state.score_red} - {state.score_blue}"
    text_surface = font2.render(score_text, True, pygame.Color("black"))
    screen.blit(text_surface, (960, 15))
    
    pygame.display.flip()


client_socket.close()
pygame.quit()