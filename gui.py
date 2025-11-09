import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
import threading
import websocket
import json

# Простой WebSocket клиент
class SimpleWebSocket:
    def __init__(self):
        self.connect()
    
    def connect(self):
        def on_message(ws, message):
            data = json.loads(message)
            messagebox.showinfo("🔔 Уведомление", data['message'])
        
        def on_error(ws, error):
            print("WebSocket error:", error)
        
        ws = websocket.WebSocketApp("ws://127.0.0.1:5000",
                                  on_message=on_message,
                                  on_error=on_error)
        
        thread = threading.Thread(target=ws.run_forever)
        thread.daemon = True
        thread.start()

# Функции для работы с API
def get_bookings():
    try:
        response = requests.get("http://127.0.0.1:5000/bookings")
        if response.status_code == 200:
            bookings = response.json()
            text.delete(1.0, tk.END)
            for booking in bookings:
                text.insert(tk.END, f"ID: {booking['id']}\n")
                text.insert(tk.END, f"ФИО: {booking['full_name']}\n")
                text.insert(tk.END, f"Телефон: {booking['phone']}\n")
                text.insert(tk.END, f"Заезд: {booking['check_in_date']}\n")
                text.insert(tk.END, f"Выезд: {booking['check_out_date']}\n")
                text.insert(tk.END, "-" * 20 + "\n")
    except:
        messagebox.showerror("Ошибка", "Сервер недоступен")

def add_booking():
    number = simpledialog.askstring("Номер заявки", "Введите номер заявки:")
    full_name = simpledialog.askstring("ФИО", "Введите ФИО:")
    phone = simpledialog.askstring("Телефон", "Введите телефон:")
    check_in = simpledialog.askstring("Заезд", "Дата заезда (ГГГГ-ММ-ДД):")
    check_out = simpledialog.askstring("Выезд", "Дата выезда (ГГГГ-ММ-ДД):")
    
    if all([number, full_name, phone, check_in, check_out]):
        data = {
            "number": number,
            "full_name": full_name, 
            "phone": phone,
            "check_in_date": check_in,
            "check_out_date": check_out
        }
        
        try:
            response = requests.post("http://127.0.0.1:5000/add_booking", json=data)
            messagebox.showinfo("Успех", response.json()["message"])
            get_bookings()
        except:
            messagebox.showerror("Ошибка", "Ошибка при добавлении")
    else:
        messagebox.showwarning("Внимание", "Заполните все поля!")

def show_api_docs():
    try:
        response = requests.get("http://127.0.0.1:5000/api/docs")
        docs = response.json()
        
        docs_window = tk.Toplevel(root)
        docs_window.title("API Documentation")
        
        text_docs = tk.Text(docs_window, height=10, width=50)
        text_docs.pack(padx=10, pady=10)
        text_docs.insert(tk.END, json.dumps(docs, indent=2, ensure_ascii=False))
    except:
        messagebox.showerror("Ошибка", "Не удалось получить документацию")

# Создание GUI
root = tk.Tk()
root.title("Система бронирования")

# Запуск WebSocket
ws = SimpleWebSocket()

# Кнопки
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="📋 Все бронирования", command=get_bookings).pack(side=tk.LEFT, padx=5)
tk.Button(frame, text="➕ Добавить", command=add_booking).pack(side=tk.LEFT, padx=5)
tk.Button(frame, text="📖 API Docs", command=show_api_docs).pack(side=tk.LEFT, padx=5)

# Текстовое поле
text = tk.Text(root, height=15, width=60)
text.pack(padx=10, pady=10)

# Статус
status = tk.Label(root, text="✅ WebSocket подключен | Сервер: 127.0.0.1:5000", 
                 relief=tk.SUNKEN, bd=1)
status.pack(fill=tk.X, side=tk.BOTTOM)

root.mainloop()