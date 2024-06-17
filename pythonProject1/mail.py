import json
import os
import hashlib
import tkinter as tk
from tkinter import messagebox

# Путь к файлу с данными пользователей
USERS_FILE = 'users.json'

# Проверка, существует ли файл с данными пользователей, и создание пустого файла, если не существует
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

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
        json.dump(users, f)

# Функция для регистрации нового пользователя
def register(username, password):
    users = load_users()
    if username in users:
        messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует.")
        return
    users[username] = hash_password(password)
    save_users(users)
    messagebox.showinfo("Успех", "Регистрация успешна!")

# Функция для авторизации пользователя
def login(username, password):
    users = load_users()
    if username not in users:
        messagebox.showerror("Ошибка", "Пользователь с таким именем не найден.")
        return
    if users[username] == hash_password(password):
        messagebox.showinfo("Успех", "Авторизация успешна!")
    else:
        messagebox.showerror("Ошибка", "Неверный пароль.")

# Функция для окна регистрации
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

# Функция для окна авторизации
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

# Главное окно
root = tk.Tk()
root.title("Главное меню")

tk.Button(root, text="Регистрация", command=registration_window).pack(pady=10)
tk.Button(root, text="Авторизация", command=login_window).pack(pady=10)
tk.Button(root, text="Выйти", command=root.quit).pack(pady=10)

root.mainloop()
