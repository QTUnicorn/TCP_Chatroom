import threading
import socket
import tkinter as tk
from datetime import datetime

def receive():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == "alias?":
                client_socket.send(alias.encode('utf-8'))
            else:
                messages_list.insert(tk.END, message)
                with open("chat_history.txt", "a", encoding='utf-8') as file:
                    file.write(f"{message}\n")
        except ConnectionAbortedError:
            break
        except:
            print('Error!')
            client_socket.close()
            break

def send(event=None):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    selected_user = users_listbox.get(tk.ACTIVE)
    message = f'{alias} ({current_time}) to {selected_user}: {my_message.get()}'
    my_message.set("")
    client_socket.send(message.encode('utf-8'))

def show_chat_history():
    try:
        with open("chat_history.txt", "r", encoding='utf-8') as file:
            chat_history = file.readlines()
            for message in chat_history:
                messages_list.insert(tk.END, message.strip())
    except FileNotFoundError:
        print("No chat history found.")

def on_closing(event=None):
    my_message.set("exit")
    send()

def show_user_list(event=None):
    users_listbox.delete(0, tk.END)
    for user in active_users:
        users_listbox.insert(tk.END, user)

def start_private_chat(event=None):
    selected_user = users_listbox.get(tk.ACTIVE)
    entry_field.delete(0, tk.END)
    entry_field.insert(tk.END, f"@{selected_user}: ")
    entry_field.focus()

alias = input('Choose name >>> ')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 59000))
client_socket.send(alias.encode('utf-8'))

active_users = client_socket.recv(1024).decode('utf-8').split(',')

root = tk.Tk()
root.title("Chat Client")

messages_frame = tk.Frame(root)
my_message = tk.StringVar()
scrollbar = tk.Scrollbar(messages_frame)

messages_list = tk.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
messages_list.pack(side=tk.LEFT, fill=tk.BOTH)
messages_list.pack()
messages_frame.pack()

entry_field = tk.Entry(root, textvariable=my_message)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tk.Button(root, text="Send", command=send)
send_button.pack()

root.protocol("WM_DELETE_WINDOW", on_closing)

show_chat_history()

receive_thread = threading.Thread(target=receive)
receive_thread.start()

private_chat_frame = tk.Frame(root)
users_label = tk.Label(private_chat_frame, text="Select user to chat with:")
users_label.pack()

users_listbox = tk.Listbox(private_chat_frame, height=5)
users_listbox.pack()

entry_field.bind("<Button-1>", show_user_list)
users_listbox.bind("<Double-Button-1>", start_private_chat)

private_chat_button = tk.Button(private_chat_frame, text="Send Private Message", command=send)
private_chat_button.pack()
private_chat_frame.pack()

tk.mainloop()
