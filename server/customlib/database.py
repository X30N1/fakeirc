import sqlite3
import asyncio
import bcrypt

# TODO: Inicializuj bazę danych, INSERT INTO, QUERY, 

def create_connection() -> sqlite3.Connection:
    """Creates a connection to the database. This will create the database should it not exist.
    
    You still need to use it to create a cursor to use the database."""
    conn = sqlite3.connect('server.db')
    return conn

def create_database(cursor: sqlite3.Cursor) -> None:
    """Creates the databases and relations required for fakeirc.
    
    requires a cursor to the database"""

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys=ON")

    # SQL queries for each table in database
    userssql = """CREATE TABLE IF NOT EXISTS users(
        userid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        username VARCHAR(25) NOT NULL,
        userpass TEXT NOT NULL,
        isadmin BOOLEAN NOT NULL DEFAULT 0,
        isonline BOOLEAN NOT NULL DEFAULT 0,
        reader TEXT NOT NULL,
        writer TEXT NOT NULL
    )"""

    chatssql = """CREATE TABLE IF NOT EXISTS chats(
        chatid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        chatname VARCHAR(30) NOT NULL,
        ownerid INTEGER NOT NULL,
        FOREIGN KEY (ownerid) REFERENCES users(userid)
    )"""

    chatlogssql = """CREATE TABLE IF NOT EXISTS chatlogs(
        messageid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        chatid INTEGER NOT NULL,
        userid INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        message TEXT NOT NULL,
        FOREIGN KEY (chatid) REFERENCES chats(chatid),
        FOREIGN KEY (userid) REFERENCES users(userid)
    )"""

    modlogsql = """CREATE TABLE IF NOT EXISTS modlogs(
        actionid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        userid INTEGER NOT NULL,
        chatid INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        kick BOOLEAN NOT NULL DEFAULT 0,
        ban DATETIME DEFAULT NULL,
        FOREIGN KEY (userid) REFERENCES users(userid),
        FOREIGN KEY (chatid) REFERENCES chats(chatid)
    )"""

    chatuserssql = """CREATE TABLE IF NOT EXISTS chatusers(
        userid INTEGER NOT NULL,
        chatid INTEGER NOT NULL,
        ismod BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (userid) REFERENCES users(userid),
        FOREIGN KEY (chatid) REFERENCES chats(chatid)
    )"""

    # Create tables
    cursor.execute(userssql)
    cursor.execute(chatssql)
    cursor.execute(chatlogssql)
    cursor.execute(modlogsql)
    cursor.execute(chatuserssql)

    # Commit changes
    cursor.connection.commit()

async def get(cursor: sqlite3.Cursor, query: str) -> list:
    """Generic GET request function."""

    cursor.execute(query)
    return cursor.fetchall()

async def post(cursor: sqlite3.Cursor, query: str) -> None:
    """Generic POST / EXECUTE request function."""

    cursor.execute(query)
    cursor.connection.commit()