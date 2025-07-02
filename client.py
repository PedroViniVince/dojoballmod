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
        

from state import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.image.load('pygame.jpg')
screen.blit(background,(0,0))

from input import Input
running = True

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

    send_data(client_socket, inputs)
    state = receive_data(client_socket)

    
#    screen.fill("antiquewhite4")

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


client_socket.close()
pygame.quit()