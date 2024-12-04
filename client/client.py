import asyncio

host = '127.0.0.1'
port = 45255

# Funkcja do wysyłania wiadomości
async def write_message(writer) -> None:
    while True:
        message = input('>> ')  # Czeka na wiadomość od użytkownika
        writer.write(message.encode('utf-8'))  # Wysyła wiadomość
        await writer.drain()  # Czeka na potwierdzenie, że wiadomość została wysłana

# Funkcja do odbierania wiadomości od serwera
async def read_message(reader) -> None:
    while True:
        data = await reader.read(1024)
        if not data:  # Jeśli brak danych (połączenie zostało zamknięte)
            print("Rozłączono z serwerem.")
            break
        print(data.decode('utf-8'))  # Drukuje wiadomość z serwera

# Główna funkcja klienta
async def run_client() -> None:
    reader, writer = await asyncio.open_connection(host, port)  # Łączy się z serwerem

    # Odbierz wiadomość od serwera (np. "Podaj nazwę użytkownika")
    server_message = await reader.read(1024)
    print(server_message.decode('utf-8'))

    # Wprowadź nazwę użytkownika
    username = input()
    writer.write(username.encode('utf-8'))  # Wysyła nazwę użytkownika do serwera
    await writer.drain()

    # Odbierz odpowiedź od serwera (np. potwierdzenie lub błąd)
    response = await reader.read(1024)
    print(response.decode('utf-8'))

    # Jeśli nazwa użytkownika była zajęta, zamykamy połączenie
    if "zajęta" in response.decode('utf-8'):
        print("Rozłączanie...")
        writer.close()
        await writer.wait_closed()
        return

    # Uruchamiamy dwa zadania asynchroniczne: jedno do pisania, drugie do odbierania wiadomości
    asyncio.create_task(write_message(writer))
    await read_message(reader)  # Czeka na wiadomości z serwera i je wyświetla

# Uruchomienie klienta
if __name__ == '__main__':
    asyncio.run(run_client())
