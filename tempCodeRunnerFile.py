import threading
import socket
import tkinter as tk

host = '127.0.0.1'
port = 59000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
aliases = []
private_rooms = {}

def broadcast(message):
    for client in clients:
        client.send(message.encode('utf-8'))  # Encode message with UTF-8 before sending

def handle_client(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')  # Decode received message with UTF-8
            if message.startswith('@'):
                recipient_alias, private_message = message.split(' ', 1)
                room_key = tuple(sorted([aliases[clients.index(client)], recipient_alias]))
                if room_key not in private_rooms:
                    private_rooms[room_key] = []
                private_rooms[room_key].append(client)
                for room_client in private_rooms[room_key]:
                    if room_client != client:
                        room_client.send(f"{aliases[clients.index(client)]} to {recipient_alias}: {private_message}".encode('utf-8'))
            elif message == "exit":
                index = clients.index(client)
                alias = aliases[index]
                broadcast(f'{alias} has left the chat room!')
                aliases.remove(alias)
                del clients[index]
                break
            else:
                broadcast(message)
        except:
            index = clients.index(client)
            alias = aliases[index]
            broadcast(f'{alias} has left the chat room!')
            aliases.remove(alias)
            del clients[index]
            break

def receive():
    while True:
        print('Server is running and listening ...')
        client, address = server.accept()
        print(f'connection is established with {str(address)}')
        client.send('alias?'.encode('utf-8'))
        alias = client.recv(1024).decode('utf-8')  # Decode alias with UTF-8
        aliases.append(alias)
        clients.append(client)
        print(f'The alias of this client is {alias}')
        broadcast(f'{alias} has connected to the chat room')
        client.send('you are now connected!'.encode('utf-8'))
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

# Creating a simple tkinter GUI
def start_server():
    receive()

root = tk.Tk()
root.title("Server - Chat Room")
start_button = tk.Button(root, text="Start Server", command=start_server)
start_button.pack()

root.mainloop()
