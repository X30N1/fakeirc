import asyncio
import sys

host = '127.0.0.1'
port = 45255

# Funkcja do wysyłania wiadomości
async def write_message(writer) -> None:
    while True:
         try:
             sys.stdout.write("\033[2K")
             sys.stdout.write("\033[1000B")
             sys.stdout.flush()
             
             try:
                message = await asyncio.to_thread(input,">> ")
             except asyncio.CancelledError:
                 break
             
             if message.lower() == "/exit":
                 print("Rozłączanie...")
                 break
             writer.write(message.encode('utf-8'))
             await writer.drain()
         except Exception as e:
             print(e)
             break
         
# Funkcja do odbierania wiadomości od serwera
async def read_message(reader) -> None:
    while True:
        try:
            message = await reader.read(1024)
            if message:
                decoded_message = message.decode('utf-8')
                print(decoded_message)
        except Exception as e:
            print(e)
            break

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
    recievetask = asyncio.create_task(read_message(reader))
    await write_message(writer)

    recievetask.cancel()

    # Zamykamy połączenie
    writer.close()
    await writer.wait_closed()

# Uruchomienie klienta
if __name__ == '__main__':
    asyncio.run(run_client())
