import socket
import json
import sqlite3
import threading
import hashlib
import secrets
from datetime import datetime

class ChatServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        # Connected clients dictionary: {socket: username}
        self.clients = {}
        
        # Initialize database
        self.init_database()
        
        print(f"Server started on {host}:{port}")

    def init_database(self):
        with sqlite3.connect('chat.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users (username)
                )
            ''')
            conn.commit()

    def hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt

    def register_user(self, username, password):
        try:
            password_hash, salt = self.hash_password(password)
            with sqlite3.connect('chat.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
                             (username, password_hash, salt))
                conn.commit()
            return True, "Registration successful"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"

    def authenticate_user(self, username, password):
        try:
            if username in self.clients.values():
                print(f"Authentication failed: {username} already logged in")
                return False, "User already logged in", None
            
            with sqlite3.connect('chat.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT password_hash, salt FROM users WHERE username = ?', (username,))
                result = cursor.fetchone()
                
                if not result:
                    print(f"Authentication failed: User {username} not found")
                    return False, "User not found"
                
                stored_hash, salt = result
                password_hash, _ = self.hash_password(password, salt)
                
                if secrets.compare_digest(password_hash, stored_hash):
                    print(f"Authentication successful: {username}")
                    return True, "Authentication successful"
                print(f"Authentication failed: Invalid password for {username}")
                return False, "Invalid password"
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False, f"Authentication failed: {str(e)}"

    def broadcast(self, message, exclude=None):
        """Send message to all connected clients except the sender"""
        for client in self.clients:
            if client != exclude:
                try:
                    client.send(json.dumps(message).encode())
                except:
                    self.remove_client(client)

    def remove_client(self, client_socket):
        """Remove client and broadcast updated user list"""
        if client_socket in self.clients:
            username = self.clients[client_socket]
            del self.clients[client_socket]
            self.broadcast({
                "type": "user_disconnected",
                "username": username,
                "users": list(self.clients.values())
            })
            client_socket.close()

    def save_message(self, username, content, timestamp):
        try:
            with sqlite3.connect('chat.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO messages (username, content, timestamp)
                    VALUES (?, ?, ?)
                ''', (username, content, timestamp))
                conn.commit()
        except Exception as e:
            print(f"Error saving message: {str(e)}")

    def get_recent_messages(self, limit=50):
        try:
            with sqlite3.connect('chat.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT username, content, timestamp 
                    FROM messages 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                messages = cursor.fetchall()
                return [{
                    "type": "message",
                    "username": msg[0],
                    "content": msg[1],
                    "timestamp": msg[2]
                } for msg in reversed(messages)]
        except Exception as e:
            print(f"Error fetching messages: {str(e)}")
            return []

    def handle_client(self, client_socket):
        """Handle individual client connection"""
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if not message:
                    break
                
                data = json.loads(message)
                
                if data["type"] == "register":
                    success, msg = self.register_user(data["username"], data["password"])
                    response = {
                        "type": "register_response",
                        "success": success,
                        "message": msg
                    }
                    client_socket.send(json.dumps(response).encode())

                elif data["type"] == "login":
                    success, msg = self.authenticate_user(data["username"], data["password"])
                    if success:
                        self.clients[client_socket] = data["username"]
                        # Send message history first
                        history_response = {
                            "type": "message_history",
                            "messages": self.get_recent_messages()
                        }
                        client_socket.send(json.dumps(history_response).encode())
                        # Then send login response
                        response = {
                            "type": "login_response",
                            "success": True,
                            "message": msg,
                            "users": list(self.clients.values())
                        }
                        client_socket.send(json.dumps(response).encode())
                        # Broadcast new user to others
                        self.broadcast({
                            "type": "user_connected",
                            "username": data["username"],
                            "users": list(self.clients.values())
                        }, client_socket)
                    else:
                        response = {
                            "type": "login_response",
                            "success": False,
                            "message": msg
                        }
                        client_socket.send(json.dumps(response).encode())

                elif data["type"] == "message":
                    if client_socket in self.clients:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        message = {
                            "type": "message",
                            "username": self.clients[client_socket],
                            "content": data["content"],
                            "timestamp": timestamp
                        }
                        # Save message to database
                        self.save_message(
                            self.clients[client_socket],
                            data["content"],
                            timestamp
                        )
                        self.broadcast(message)

            except json.JSONDecodeError:
                break
            except Exception as e:
                print(f"Error handling client: {str(e)}")
                break
        
        self.remove_client(client_socket)

    def start(self):
        """Start the server and accept connections"""
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"New connection from {address}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = ChatServer()
    server.start()