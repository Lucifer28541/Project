import json
import os
import hashlib
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Путь к файлу с данными пользователей и сообщений
USERS_FILE = 'users.json'
MESSAGES_FILE = 'messages.json'

# Проверка, существуют ли файлы с данными, и создание пустых файлов, если они не существуют
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

if not os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, 'w') as f:
        json.dump([], f)

# Функция для хеширования паролей
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Функция для загрузки данных пользователей из файла
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

# Функция для сохранения данных пользователей в файл
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Функция для загрузки сообщений из файла
def load_messages():
    with open(MESSAGES_FILE, 'r') as f:
        return json.load(f)

# Функция для сохранения сообщений в файл
def save_messages(messages):
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=4)

# Функция для регистрации нового пользователя
def register(username, password):
    users = load_users()
    if username in users:
        messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует.")
        return
    users[username] = {
        'password': hash_password(password)
    }
    save_users(users)
    messagebox.showinfo("Успех", "Регистрация успешна!")

# Функция для авторизации пользователя
def login(username, password):
    users = load_users()
    if username not in users:
        messagebox.showerror("Ошибка", "Пользователь с таким именем не найден.")
        return
    if users[username]['password'] == hash_password(password):
        messagebox.showinfo("Успех", "Авторизация успешна!")
        open_chat_window(username)
    else:
        messagebox.showerror("Ошибка", "Неверный пароль.")

# Функция для открытия окна регистрации
def registration_window():
    reg_win = tk.Toplevel(root)
    reg_win.title("Регистрация")

    tk.Label(reg_win, text="Имя пользователя:").grid(row=0, column=0)
    username_entry = tk.Entry(reg_win)
    username_entry.grid(row=0, column=1)

    tk.Label(reg_win, text="Пароль:").grid(row=1, column=0)
    password_entry = tk.Entry(reg_win, show='*')
    password_entry.grid(row=1, column=1)

    tk.Button(reg_win, text="Регистрация", command=lambda: register(username_entry.get(), password_entry.get())).grid(row=2, columnspan=2)

# Функция для открытия окна авторизации
def login_window():
    login_win = tk.Toplevel(root)
    login_win.title("Авторизация")

    tk.Label(login_win, text="Имя пользователя:").grid(row=0, column=0)
    username_entry = tk.Entry(login_win)
    username_entry.grid(row=0, column=1)

    tk.Label(login_win, text="Пароль:").grid(row=1, column=0)
    password_entry = tk.Entry(login_win, show='*')
    password_entry.grid(row=1, column=1)

    tk.Button(login_win, text="Войти", command=lambda: login(username_entry.get(), password_entry.get())).grid(row=2, columnspan=2)

# Функция для открытия окна чата
def open_chat_window(username):
    chat_win = tk.Toplevel(root)
    chat_win.title("Чат")

    chat_text = scrolledtext.ScrolledText(chat_win, state='disabled')
    chat_text.grid(row=0, column=0, columnspan=2)

    message_entry = tk.Entry(chat_win)
    message_entry.grid(row=1, column=0)

    def send_message():
        message = message_entry.get()
        if message:
            messages = load_messages()
            messages.append({'user': username, 'message': message})
            save_messages(messages)
            update_chat(chat_text, messages)
            message_entry.delete(0, tk.END)

    tk.Button(chat_win, text="Отправить", command=send_message).grid(row=1, column=1)

    # Загрузка и отображение существующих сообщений
    messages = load_messages()
    update_chat(chat_text, messages)

def update_chat(chat_text, messages):
    chat_text.config(state='normal')
    chat_text.delete(1.0, tk.END)
    for msg in messages:
        chat_text.insert(tk.END, f"{msg['user']}: {msg['message']}\n")
    chat_text.config(state='disabled')

# Главное окно
root = tk.Tk()
root.title("Главное меню")

tk.Button(root, text="Регистрация", command=registration_window).pack(pady=10)
tk.Button(root, text="Авторизация", command=login_window).pack(pady=10)
tk.Button(root, text="Выйти", command=root.quit).pack(pady=10)

root.mainloop()
