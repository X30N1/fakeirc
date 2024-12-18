import socket
import asyncio
import json
import customlib.database as db
import customlib.tcolor as tcolor
tc = tcolor.color

# CONFIG
host = ""
port = 45255
format = 'utf-8'
name = "fakeirc"
# MESSAGE OF THE DAY
MOTD = "Welcome to fakeirc!"

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Handles a single client connection."""

    writer.write({"messasge": MOTD}.encode(format))


async def run_server() -> None:
    """Initialises server with all dependent modules and variables."""
    
    # Create connection & database if it doesn't exist
    conn = db.create_connection()
    if conn:
        print(f"{tc.OKGREEN}Connected to database.{tc.END}")
    else:
        print(f"{tc.FAIL}Failed to connect to database, exiting.....{tc.END}")
        return
    cur = conn.cursor()
    db.create_database(cur, conn)

    # Get IP of server using socket
    host = socket.gethostbyname(socket.gethostname())
    server = await asyncio.start_server(handle_client, host, port)
    print(f"{tc.OKGREEN}The server is working at {host} on port {port}{tc.END}")
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(run_server())
