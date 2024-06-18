import psycopg2
import hashlib
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Настройки подключения к базе данных
DB_NAME = "NewBD1"
DB_USER = "postgres"
DB_PASSWORD = "123"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Функция для хеширования паролей
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Функция для регистрации нового пользователя
def register(username, password):
    conn = connect_db()
    cur = conn.cursor()
    try:
        password_hash = hash_password(password)
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        messagebox.showinfo("Успех", "Регистрация успешна!")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует.")
    finally:
        cur.close()
        conn.close()

# Функция для авторизации пользователя
def login(username, password):
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user and user[1] == hash_password(password):
            messagebox.showinfo("Успех", "Авторизация успешна!")
            return user[0]  # Возвращаем user_id
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")
            return None
    finally:
        cur.close()
        conn.close()

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

    def attempt_login():
        user_id = login(username_entry.get(), password_entry.get())
        if user_id:
            chat_window(username_entry.get(), user_id)

    tk.Button(login_win, text="Войти", command=attempt_login).grid(row=2, columnspan=2)

# Функция для окна чата
def chat_window(username, user_id):
    chat_win = tk.Toplevel(root)
    chat_win.title(f"Чат - {username}")

    messages_frame = tk.Frame(chat_win)
    scrollbar = tk.Scrollbar(messages_frame)
    msg_list = tk.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
    msg_list.pack()
    messages_frame.pack()

    def send_message():
        message = message_entry.get()
        if message:
            conn = connect_db()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO messages (user_id, message) VALUES (%s, %s)", (user_id, message))
                conn.commit()
                update_messages()
                message_entry.delete(0, tk.END)
            finally:
                cur.close()
                conn.close()

    def update_messages():
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT u.username, m.message 
                FROM messages m
                JOIN users u ON m.user_id = u.id
                ORDER BY m.created_at
            """)
            messages = cur.fetchall()
            msg_list.delete(0, tk.END)
            for msg in messages:
                msg_list.insert(tk.END, f"{msg[0]}: {msg[1]}")
        finally:
            cur.close()
            conn.close()

    message_entry = tk.Entry(chat_win)
    message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    send_button = tk.Button(chat_win, text="Отправить", command=send_message)
    send_button.pack(side=tk.RIGHT)

    update_messages()

# Функция для запуска тестов
def run_tests():
    test_win = tk.Toplevel(root)
    test_win.title("Запуск тестов")

    # Список тестов
    tests = ["test_hash_password", "test_register", "test_login_success", "test_login_fail_wrong_password", "test_login_fail_no_user", "test_chat_message"]

    # Множество для хранения выбранных тестов
    selected_tests = set()

    def toggle_test(test):
        if test in selected_tests:
            selected_tests.remove(test)
        else:
            selected_tests.add(test)

    def run_selected_tests():
        import unittest
        import test_module
        suite = unittest.TestSuite()
        for test in selected_tests:
            suite.addTest(test_module.TestUserFunctions(test))
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Run: {result.testsRun}\n")
        if result.wasSuccessful():
            result_text.insert(tk.END, "All tests passed!\n")
        else:
            result_text.insert(tk.END, f"Failures: {len(result.failures)}\n")
            for test, err in result.failures:
                result_text.insert(tk.END, f"{test.id()}: {err}\n")
            result_text.insert(tk.END, f"Errors: {len(result.errors)}\n")
            for test, err in result.errors:
                result_text.insert(tk.END, f"{test.id()}: {err}\n")

    # Добавление чекбоксов для выбора тестов
    for test in tests:
        chk = tk.Checkbutton(test_win, text=test, command=lambda t=test: toggle_test(t))
        chk.pack(anchor='w')

    # Кнопка для запуска выбранных тестов
    run_button = tk.Button(test_win, text="Запустить тесты", command=run_selected_tests)
    run_button.pack()

    # Текстовое поле для отображения результатов
    result_text = scrolledtext.ScrolledText(test_win, height=10, width=50)
    result_text.pack()

# Главное окно
root = tk.Tk()
root.title("Главное меню")

tk.Button(root, text="Регистрация", command=registration_window).pack(pady=10)
tk.Button(root, text="Авторизация", command=login_window).pack(pady=10)
tk.Button(root, text="Тесты", command=run_tests).pack(pady=10)
tk.Button(root, text="Выйти", command=root.quit).pack(pady=10)

root.mainloop()
