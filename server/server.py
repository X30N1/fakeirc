import asyncio
import yaml
import socket
import sqlite3
import customlib.tcolor as tcolor
tc = tcolor.color

print(tc.HEADER + "URUCHAMIAM SERWER" + tc.END)

with open('config.yaml','r') as file: # Wczytujemy plik konfiguracyjny
    config = yaml.safe_load(file)
print(tc.OKCYAN + "Wczytano plik konfiguracyjny" + tc.END)

con = sqlite3.connect('serwer.db') # Łączymy się z bazą danych
cur = con.cursor()
print(tc.OKCYAN + "Połączono z bazą danych" + tc.END)

# Tworzymy tabele dla użytkowników i wiadomości JEŻELI nie istnieje
cur.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              password TEXT NOT NULL,
              privilege INT NOT NULL,
              last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

cur.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              message TEXT,
              timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(id))''')

con.commit()


class ICRServer:
    def __init__(self, config, cur):
        self.port = config['port']
        self.join = config['join']
        self.msgpass = config['msgpass']
        self.adress = config['host']
        self.interval = config['interval']
        self.cur = cur
