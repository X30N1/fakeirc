import asyncio

host = '127.0.0.1'
port = 45255

async def run_client() -> None:
    reader, writer = await asyncio.open_connection(host, port)
    await writer.write(b'hello world')
    await writer.drain()
    
    while True:
        data = await reader.read(1024)
        
        if not data:
            raise Exception('Connection closed')
        
        print(data.decode('utf-8'))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_client())