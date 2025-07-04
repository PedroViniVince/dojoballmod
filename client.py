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
background = pygame.image.load('relva.jpg').convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
#baliza vermelha
baliza = pygame.image.load('goal.png').convert_alpha()
baliza = pygame.transform.rotate(baliza,90)
baliza = pygame.transform.scale(baliza, (300, 500)) 

baliza2 = pygame.image.load('goal.png').convert_alpha()
baliza2 = pygame.transform.rotate(baliza2,270)
baliza2 = pygame.transform.scale(baliza2, (300, 500)) 
pygame.font.init()
font1 = pygame.font.SysFont("comic sans", 24)
font2 = pygame.font.SysFont("comic sans",36)


from input import Input
running = True
clock = pygame.time.Clock()

while running:
    update_rects = []
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
    clock.tick(80)
    send_data(client_socket, inputs)
    state = receive_data(client_socket)

    #screen.fill("antiquewhite4")
    screen.blit(background,(0,0))

    #campo
    pygame.draw.rect(screen, "antiquewhite2", (state.field_coords[0],
                                               state.field_coords[1],
                                               state.field_coords[2]- state.field_coords[0],
                                               state.field_coords[3] - state.field_coords[1]), 3)
    field_x1, field_y1, field_x2, field_y2 = state.field_coords
    field_center_x = (field_x1 + field_x2) // 2
    pygame.draw.line(
        screen,
        pygame.Color("antiquewhite2"),
        (field_center_x, field_y1),
        (field_center_x, field_y2),
        width=3
    )

    # Draw circle outline in the center of the field
    field_center_y = (field_y1 + field_y2) // 2
    circle_radius = 100  # Adjust as needed
    pygame.draw.circle(
        screen,
        pygame.Color("antiquewhite2"),
        (field_center_x, field_center_y),
        circle_radius,
        width=3
    )

    # Jogadores
    for player in state.players.values():
        color = pygame.Color("cornflowerblue") if player.team == Team.BLUE else pygame.Color("crimson")
        coloroutline = pygame.Color("blue") if player.team == Team.BLUE else pygame.Color("red")
        name = player.name if player.name else "Unknown"
        name_text = font1.render(name, True, pygame.Color("white"))
        text_rect = name_text.get_rect(center=(int(player.x), int(player.y) - 50))
        screen.blit(name_text, text_rect)
        pygame.draw.circle(screen, color, (int(player.x), int(player.y)), 45)
        pygame.draw.circle(screen, coloroutline, (int(player.x), int(player.y)), 45, width=5)
        update_rects.append(pygame.Rect(player.x-45, player.y-45, 90, 90))
        update_rects.append(text_rect)
        
    # Postes
    for post in state.posts.values():
        pygame.draw.circle(screen, pygame.Color("cornsilk"), (int(post.x), int(post.y)), 15)
        
    red_baliza_post = next((post for post in state.posts.values() if post.team == Team.RED), None)
    blue_baliza_post = next((post for post in state.posts.values() if post.team == Team.BLUE), None)

    if red_baliza_post:
        baliza_rect = baliza.get_rect(center=(int(red_baliza_post.x-62), int(red_baliza_post.y + 150)))
        screen.blit(baliza, baliza_rect)
    if blue_baliza_post:
        # rodar baliza para a equipa azul
        baliza_rect = baliza2.get_rect(center=(int(blue_baliza_post.x+62), int(blue_baliza_post.y + 150)))
        screen.blit(baliza2, baliza_rect)
    
    # Bola
    pygame.draw.circle(screen, pygame.Color("white"), (int(state.ball.x), int(state.ball.y)), 30)
    update_rects.append(screen.get_rect())


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
    update_rects.append(text_clock_surface.get_rect(topleft=(200, 15)))
    
    # FPS
    fps_surface = font2.render(f"FPS: {int(clock.get_fps())}", True, pygame.Color("black"))
    fps_rect = fps_surface.get_rect(topleft=(1500, 15))
    screen.blit(fps_surface, fps_rect)
    update_rects.append(fps_rect)

    # Score
    score_text = f"{state.score_red} - {state.score_blue}"
    text_surface = font2.render(score_text, True, pygame.Color("black"))
    score_rect = text_surface.get_rect(center=(960, 30))
    screen.blit(text_surface, score_rect)
    update_rects.append(score_rect)
    
    pygame.display.update(update_rects)


client_socket.close()
pygame.quit()