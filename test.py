import tkinter as tk
import os.path
import sqlite3

def clear_window():
    for widget in root.winfo_children():  # Przechodzi przez wszystkie dzieci (widgety) okna
        widget.pack_forget() 
# Funkcja, która pobiera tekst z pola wejściowego i wyświetla go w etykiecie
def submit(event=None):
    entered_text = lista.get()  # Pobranie tekstu z pola wejściowego
    label.config(text=f"Z wpisanym tekstem: {entered_text}")  # Wyświetlenie tekstu w etykiecie

def open_new_window(event=None):
    global selected_server,entry_username,entry_password

# Tworzymy pole do wprowadzenia adresu serwera
    selected_server = lista.get(lista.curselection())
# Tworzymy pole do wprowadzenia nazwy użytkownika
    username_label = tk.Label(root, text="Wprowadź nazwę użytkownika:")
    username_label.pack(pady=10)

    entry_username = tk.Entry(root, width=30)
    entry_username.pack(pady=10)

    passord_label = tk.Label(root, text="Wprowadź haslo:")
    passord_label.pack(pady=10)

    entry_password = tk.Entry(root, width=30)
    entry_password.pack(pady=10)

# Bindowanie Entera do wysyłania danych
    entry_username.bind('<Return>', submit_credentials1)
    entry_password.bind('<Return>', submit_credentials1)

    submit_button = tk.Button(root, text="Zatwierdź", command=submit_credentials1)
    submit_button.pack(pady=10)

# Ustawiamy fokus na pole do wprowadzania adresu serwera od razu
    entry_username.focus_set()
    root.deiconify()

def submit_credentials1(event=None):
    global server_address, username ,password
    server_address = selected_server # Zapisujemy adres serwera do zmiennej
    username = entry_username.get()  # Zapisujemy nazwę użytkownika do zmiennej
    password = entry_password.get()
    print(f"Adres serwera: {server_address}")  # Wyświetlamy adres serwera w terminalu
    print(f"Nazwa użytkownika: {username}")  # Wyświetlamy nazwę użytkownika w terminalu
    entry_username.delete(0, tk.END)  # Czyszczenie pola po zatwierdzeniu
    clear_window()
    root.withdraw() 
    ask_message() # Otwórz drugie okno, w którym pytamy o wiadomość
def submit_credentials(event=None):
    global server_address, username ,password
    server_address = entry_server.get()  # Zapisujemy adres serwera do zmiennej
    username = entry_username.get()  # Zapisujemy nazwę użytkownika do zmiennej
    password = entry_password.get()
    server_address = str(server_address)
    conn = sqlite3.connect('servery.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS servery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serwer TEXT NOT NULL
        )
    ''')
    conn.commit()
    cursor.execute("INSERT INTO servery (serwer) VALUES (?)", (server_address,))
    conn.commit()
    conn.close()
    print(f"Adres serwera: {server_address}")  # Wyświetlamy adres serwera w terminalu
    print(f"Nazwa użytkownika: {username}")  # Wyświetlamy nazwę użytkownika w terminalu
    entry_username.delete(0, tk.END)  # Czyszczenie pola po zatwierdzeniu
    entry_server.delete(0, tk.END)  # Czyszczenie pola po zatwierdzeniu
    clear_window()
    root.withdraw() 
    ask_message() # Otwórz drugie okno, w którym pytamy o wiadomość
def ask_message():

    message_label = tk.Label(root, text="Wprowadź wiadomość:")
    message_label.pack(pady=20)

    global entry_message
    entry_message = tk.Entry(root, width=30)
    entry_message.pack(pady=10)
    
    # Bindowanie Entera do wysyłania wiadomości
    entry_message.bind('<Return>', submit_message)

    submit_button = tk.Button(root, text="Zatwierdź", command=submit_message)
    submit_button.pack(pady=10)

    # Ustawiamy fokus na pole do wprowadzania wiadomości od razu
    entry_message.focus_set()
    root.deiconify()
def submit_message(event=None):
    global message
    message = entry_message.get()  # Zapisujemy wiadomość do zmiennej
    print(f"{username}: {message}")  # Wyświetlamy wiadomość w terminalu
    entry_message.delete(0, tk.END)  # Czyszczenie pola po zatwierdzeniu

def server_pytanie():
    global entry_server,entry_username,entry_password

# Tworzymy pole do wprowadzenia adresu serwera
    server_label = tk.Label(root, text="Wprowadź adres serwera:")
    server_label.pack(pady=10)

    entry_server = tk.Entry(root, width=30)
    entry_server.pack(pady=10)

# Tworzymy pole do wprowadzenia nazwy użytkownika
    username_label = tk.Label(root, text="Wprowadź nazwę użytkownika:")
    username_label.pack(pady=10)

    entry_username = tk.Entry(root, width=30)
    entry_username.pack(pady=10)

    passord_label = tk.Label(root, text="Wprowadź haslo:")
    passord_label.pack(pady=10)

    entry_password = tk.Entry(root, width=30)
    entry_password.pack(pady=10)

# Bindowanie Entera do wysyłania danych
    entry_username.bind('<Return>', submit_credentials)
    entry_server.bind('<Return>', submit_credentials)
    entry_password.bind('<Return>', submit_credentials)

    submit_button = tk.Button(root, text="Zatwierdź", command=submit_credentials)
    submit_button.pack(pady=10)

# Ustawiamy fokus na pole do wprowadzania adresu serwera od razu
    entry_server.focus_set()
    root.deiconify()
def nowy_serwer():
    clear_window()
    root.withdraw()
    server_pytanie()

def nowy_serwer1(event):
    clear_window()
    root.withdraw()
    open_new_window()

# Tworzenie głównego okna aplikacji
root = tk.Tk()
root.title("Najprostszy Input Box")
root.geometry("400x400")
# Tworzenie pola tekstowego (input box)
choice_label = tk.Label(root, text="wybierz serwer lub dodaj nowy")
# Tworzenie przycisku, który wywoła funkcję submit()
submit_button = tk.Button(root, text="Wyślij", command=nowy_serwer)
submit_button.pack(pady=10)
# Tworzenie etykiety, która będzie wyświetlała wprowadzony tekst
label = tk.Label(root, text="")
label.pack(pady=20)
lista = tk.Listbox(root,selectmode=tk.SINGLE)
if os.path.isfile("servery.db") == True:
    conn = sqlite3.connect('servery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id,serwer FROM servery")
    serwery = cursor.fetchall()
    for serwer in serwery:
        lista.insert(tk.END,serwer[1])
    conn.close()
else:
    pass

lista.pack()
lista.bind('<Double-1>', nowy_serwer1)
# Uruchomienie pętli głównej aplikacji
root.mainloop()
