import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import json
import threading
from datetime import datetime

class ChatClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None

        self.host = "localhost"
        self.port = 5555

        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Chat Application")
        self.root.geometry("800x600")
        
        # Create and show login frame
        self.create_login_frame()
        
        # Create but don't show chat frame yet
        self.create_chat_frame()
        
        # Start with login frame
        self.show_login_frame()
        
    def create_login_frame(self):
        self.login_frame = ttk.Frame(self.root, padding="20")

        # Server address field
        ttk.Label(self.login_frame, text="Server Address:").grid(row=0, column=0, sticky="w", pady=5)
        self.server_address_entry = ttk.Entry(self.login_frame, width=30)
        self.server_address_entry.insert(0, self.host)
        self.server_address_entry.grid(row=0, column=1, pady=5)

        # Server port field
        ttk.Label(self.login_frame, text="Server Port:").grid(row=1, column=0, sticky="w", pady=5)
        self.server_port_entry = ttk.Entry(self.login_frame, width=30)
        self.server_port_entry.insert(0, self.port)
        self.server_port_entry.grid(row=1, column=1, pady=5)

        # Username field
        ttk.Label(self.login_frame, text="Username:").grid(row=2, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.grid(row=2, column=1, pady=5)
        
        # Password field
        ttk.Label(self.login_frame, text="Password:").grid(row=3, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(self.login_frame, width=30, show="*")
        self.password_entry.grid(row=3, column=1, pady=5)
        
        # Login and Register buttons
        button_frame = ttk.Frame(self.login_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Login", command=self.login).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Register", command=self.register).pack(side=tk.LEFT)

    def create_chat_frame(self):
        self.chat_frame = ttk.Frame(self.root, padding="10")
        
        # Create main chat area with messages and user list
        paned_window = ttk.PanedWindow(self.chat_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Chat messages
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=3)
        
        # Message display area
        self.message_area = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, height=20)
        self.message_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.message_area.config(state=tk.DISABLED)
        
        # Message input area
        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.message_input = ttk.Entry(input_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_input.bind("<Return>", lambda e: self.send_message())
        
        ttk.Button(input_frame, text="Send", command=self.send_message).pack(side=tk.RIGHT)
        
        # Right side - User list
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Online Users").pack(pady=(0, 5))
        
        self.users_listbox = tk.Listbox(right_frame, height=20)
        self.users_listbox.pack(fill=tk.BOTH, expand=True)

    def show_login_frame(self):
        self.chat_frame.pack_forget()
        self.login_frame.pack(expand=True)

    def show_chat_frame(self):
        self.login_frame.pack_forget()
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

    def connect_to_server(self, host=None, port=None):
        if not host or not port:
            messagebox.showerror("Error", "Please fill in server address and port")
            return False
        
        self.host = host
        self.port = int(port)
        
        try:
            self.socket.connect((self.host, self.port))
            # Start listening for messages
            self.listener_thread = threading.Thread(target=self.listen_for_messages)
            self.listener_thread.daemon = True
            self.listener_thread.start()
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {str(e)}")
            return False

    def login(self):
        server = self.server_address_entry.get()
        port = self.server_port_entry.get()

        if not hasattr(self, 'socket_connected'):
            self.socket_connected = self.connect_to_server(server, port)
            if not self.socket_connected:
                return

        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        login_data = {
            "type": "login",
            "username": username,
            "password": password
        }
        
        try:
            self.socket.send(json.dumps(login_data).encode())
        except Exception as e:
            messagebox.showerror("Error", f"Could not send login request: {str(e)}")

    def register(self):
        server = self.server_address_entry.get()
        port = self.server_port_entry.get()

        if not hasattr(self, 'socket_connected'):
            self.socket_connected = self.connect_to_server(server,port)
            if not self.socket_connected:
                return

        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        register_data = {
            "type": "register",
            "username": username,
            "password": password
        }
        
        try:
            self.socket.send(json.dumps(register_data).encode())
        except Exception as e:
            messagebox.showerror("Error", f"Could not send registration request: {str(e)}")

    def send_message(self):
        message = self.message_input.get().strip()
        if message:
            message_data = {
                "type": "message",
                "content": message
            }
            try:
                self.socket.send(json.dumps(message_data).encode())
                self.message_input.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Could not send message: {str(e)}")

    def update_message_area(self, message):
        self.message_area.config(state=tk.NORMAL)
        self.message_area.insert(tk.END, message + "\n")
        self.message_area.see(tk.END)
        self.message_area.config(state=tk.DISABLED)

    def update_user_list(self, users):
        self.users_listbox.delete(0, tk.END)
        for user in users:
            self.users_listbox.insert(tk.END, user)

    def listen_for_messages(self):
        while True:
            try:
                message = self.socket.recv(1024).decode()
                if not message:
                    break
                
                data = json.loads(message)
                
                if data["type"] == "message_history":
                    for msg in data["messages"]:
                        self.update_message_area(
                            f"[{msg['timestamp']}] {msg['username']}: {msg['content']}"
                        )
                elif data["type"] == "login_response":
                    if data["success"]:
                        self.username = self.username_entry.get()
                        self.show_chat_frame()
                        self.update_user_list(data["users"])
                    messagebox.showinfo("Login", data["message"])

                elif data["type"] == "register_response":
                    messagebox.showinfo("Registration", data["message"])

                elif data["type"] == "message":
                    timestamp = data["timestamp"]
                    username = data["username"]
                    content = data["content"]
                    self.update_message_area(f"[{timestamp}] {username}: {content}")

                elif data["type"] in ["user_connected", "user_disconnected"]:
                    self.update_user_list(data["users"])
                    if data["type"] == "user_connected":
                        self.update_message_area(f"System: {data['username']} has joined the chat")
                    else:
                        self.update_message_area(f"System: {data['username']} has left the chat")

            except json.JSONDecodeError:
                break
            except Exception as e:
                print(f"Error receiving message: {str(e)}")
                break
        
        messagebox.showerror("Connection Lost", "Lost connection to server")
        self.root.quit()

    def run(self):
        self.root.mainloop()
        if hasattr(self, 'socket'):
            self.socket.close()

if __name__ == "__main__":
    client = ChatClient()
    client.run()