import socket
import asyncio
import customlib.tcolor as tcolor
tc = tcolor.color

# CONFIG
host = ""
port = 45255
format = 'utf-8'

# Zmienne do przechowywania danych
usernames = []
clients = []

async def login(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> bool:
    """Promptuje użytkownika do zalogowania, po czym sprawdza wprowadzone dane z bazą kont
    
    W razie pomyślnego zalogowania zwraca True, w przeciwieństwie False"""

    writer.write("Podaj nazwę użytkownika: ".encode(format))
    await writer.drain()

    data = await reader.read(1024)
    username = data.decode(format).strip()
    
    # Moduł sprawdzania nazwy użytkownika
    while len(username) == 0 or len(username) > 30:
        writer.write("Nazwa użytkownika nie może być pusta lub przekroczyć 30 znaków. Spróbuj ponownie.".encode(format))
        await writer.drain()
        data = await reader.read(1024)
        username = data.decode(format).strip()

    if username in usernames:
        writer.write("Ktoś już jest")
     


async def register(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> bool:
    """Promptuje użytkownika do podania danych w celu rejestracji.
    
    Jeżeli dane zostały poprawnie wprowadzone i użytkownik jest zarejestrowany zwraca True, w przeciwieństwie False"""

    #TODO: Ta funkcja


async def new_user(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> str:
    servermessage = "Podaj nazwę użytkownika: "
    writer.write(servermessage.encode(format))
    await writer.drain()

    data = await reader.read(1024)
    username = data.decode(format).strip()
    if username in usernames:
        writer.write("Nazwa użytkownika zajęta. Spróbuj ponownie.".encode(format))
        await writer.drain()
        return None
    else:
        writer.write("Połączono pomyślnie".encode(format))
        await writer.drain()
        usernames.append(username)
        return username

async def broadcast(message: str, writer: asyncio.StreamWriter) -> None:
    try:
        for client in clients:
            if client['writer'] != writer:
                client['writer'].write(message.encode(format))
                await client['writer'].drain()
    except Exception as e:
        print(f"{tc.WARNING} Błąd: {e} {tc.END}")

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        username = await new_user(reader, writer)
        if not username:
            writer.close()
            await writer.wait_closed()
            return

        welcome_message = f"{tc.WARNING}Użytkownik {username} dołączył do czatu!{tc.END}\n"
        print(welcome_message.strip())
        for client in clients:
            client['writer'].write(welcome_message.encode(format))
            await client['writer'].drain()

        clients.append({'reader': reader, 'writer': writer, 'username': username})

        while True:
            data = await reader.read(1024)
            if not data:
                break
            msg = f"{username}: {data.decode(format)}"
            print(msg.strip())
            await broadcast(msg, writer)

    except Exception as e:
        print(f"{tc.WARNING} Błąd: {e} {tc.END}")
    finally:
        if username in usernames:
            usernames.remove(username)
        clients.remove({'reader': reader, 'writer': writer, 'username': username})
        writer.close()
        await writer.wait_closed()
        print(f"{tc.WARNING}Użytkownik {username} opuścił czat {tc.END}")
        await broadcast(f"{tc.WARNING}{username} opućł czat{tc.END}", writer)


async def run_server(launch_function) -> None:
    """Zdobywa IP serwera i uruchamia proces rozruchowy launch_function()"""

    host = socket.gethostbyname(socket.gethostname())
    server = await asyncio.start_server(launch_function, host, port)
    print(f"{tc.OKGREEN}Serwer działa na adresie {host} a porcie {port}{tc.END}")
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(run_server(handle_client))
