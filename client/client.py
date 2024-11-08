import asyncio
import yaml
import socket
import sqlite3

with open('config.yaml','r') as file: # Wczytujemy plik konfiguracyjny
    config = yaml.safe_load(file)
print("Wczytano plik konfiguracyjny")

con = sqlite3.connect('user.db') # Łączymy się z bazą danych
cur = con.cursor()
print("Połączono z bazą danych")

# Tworzymy bazę danych do przechowywania znanych loginów w serwerach
cur.execute('''CREATE TABLE IF NOT EXISTS known
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    serverip TEXT NOT NULL)''')

con.commit()

class User{
    def __init__(self,config):
        # WSTAW TUTAJ USTAWIENIA GRAFICZNE JAK CHCESZ ITP
}
