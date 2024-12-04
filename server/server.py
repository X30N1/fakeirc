import asyncio
import bcrypt
import yaml
import sqlite3
import customlib.tcolor as tcolor
tc = tcolor.color

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
              currentuser string DEFAULT 'None',
              last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

cur.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              message TEXT,
              timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(id))''')

cur.execute('''CREATE TABLE IF NOT EXISTS kicks
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              reason TEXT,
              timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(id))''')

cur.execute('''CREATE TABLE IF NOT EXISTS bans
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              reason TEXT,
              timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(id))''')

con.commit()

# Odczytujemy dane z configu
host = config['host']
port = config['port']
limit = config['limit']
name = config['name']
format = "utf-8"


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    data = None

    while data != b'exit':
        data = await reader.read(1024)
        msg = data.decode(format)
        addr, port = writer.get_extra_info('peername')
        print(f"Received message from {addr}:{port}: {msg!r}")

        writer.write(data)
        await writer.drain()

    writer.close()
    await writer.wait_closed()

async def run_server() -> None:
    server = await asyncio.start_server(handle_client, host, port)
    async with server:
        await server.serve_forever()
        
        
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_server())