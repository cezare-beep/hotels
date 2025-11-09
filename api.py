from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# База данных
def create_database():
    conn = sqlite3.connect('hotel_booking.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  number TEXT, full_name TEXT, phone TEXT,
                  check_in_date TEXT, check_out_date TEXT)''')
    conn.commit()
    conn.close()

# Repository Pattern - простой класс
class BookingRepository:
    @staticmethod
    def get_all():
        conn = sqlite3.connect('hotel_booking.db')
        c = conn.cursor()
        c.execute("SELECT * FROM bookings")
        rows = c.fetchall()
        conn.close()
        return rows
    
    @staticmethod
    def add_booking(data):
        conn = sqlite3.connect('hotel_booking.db')
        c = conn.cursor()
        c.execute('''INSERT INTO bookings 
                     (number, full_name, phone, check_in_date, check_out_date)
                     VALUES (?, ?, ?, ?, ?)''',
                  (data['number'], data['full_name'], data['phone'],
                   data['check_in_date'], data['check_out_date']))
        conn.commit()
        conn.close()

# WebSocket - простое уведомление
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('notification', {'message': 'Connected!'})

# REST API Documentation
@app.route('/api/docs')
def api_docs():
    return jsonify({
        "message": "API Documentation",
        "endpoints": {
            "GET /bookings": "Get all bookings",
            "POST /add_booking": "Add new booking"
        }
    })

# Получение бронирований
@app.route('/bookings', methods=['GET'])
def get_bookings():
    rows = BookingRepository.get_all()
    bookings = []
    for row in rows:
        bookings.append({
            "id": row[0], "number": row[1], "full_name": row[2],
            "phone": row[3], "check_in_date": row[4], "check_out_date": row[5]
        })
    return jsonify(bookings)

# Добавление бронирования
@app.route('/add_booking', methods=['POST'])
def add_booking():
    data = request.json
    BookingRepository.add_booking(data)
    
    # WebSocket уведомление
    socketio.emit('new_booking', {'message': f'New booking: {data["full_name"]}'})
    
    return jsonify({"message": "Бронирование добавлено!"})

if __name__ == '__main__':
    create_database()
    # ДОБАВЛЕНО: allow_unsafe_werkzeug=True
    socketio.run(app, debug=True, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)