from flask import Flask, request, jsonify
import sqlite3
import time
import os
from datetime import datetime

app = Flask(__name__)

# Настройки базы данных
DATABASE = 'casino.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Инициализация базы данных"""
    if not os.path.exists(DATABASE):
        print("Создание новой базы данных...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                balance INTEGER DEFAULT 1000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица транзакций
        cursor.execute('''
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                type TEXT,
                game_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Добавляем тестовых пользователей
        test_users = [
            ('Player1', 1500),
            ('Player2', 800),
            ('Player3', 2500),
            ('TestUser', 1000)
        ]
        for username, balance in test_users:
            cursor.execute('INSERT OR IGNORE INTO users (username, balance) VALUES (?, ?)', (username, balance))
        
        conn.commit()
        conn.close()
        print("✅ База данных создана успешно!")
    else:
        print("✅ База данных уже существует")

# API endpoints
@app.route('/users/get', methods=['GET'])
def get_user_balance():
    """Получить баланс пользователя"""
    username = request.args.get('name')
    
    if not username:
        return "Error: username required", 400
    
    print(f"📊 Запрос баланса для: {username}")
    
    conn = get_db_connection()
    
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    
    if user:
        balance = user['balance']
        print(f"💰 Баланс {username}: {balance}")
    else:
        # Создаем нового пользователя со стартовым балансом
        print(f"👤 Создание нового пользователя: {username}")
        conn.execute(
            'INSERT INTO users (username, balance) VALUES (?, 1000)',
            (username,)
        )
        conn.commit()
        balance = 1000
    
    conn.close()
    return str(balance)

@app.route('/users/pay', methods=['GET'])
def pay_user():
    """Списать средства с пользователя"""
    username = request.args.get('name')
    money = int(request.args.get('money'))
    
    if not username or money <= 0:
        return "False"
    
    print(f"➖ Списание {money} у: {username}")
    
    conn = get_db_connection()
    
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    
    if user and user['balance'] >= money:
        new_balance = user['balance'] - money
        conn.execute(
            'UPDATE users SET balance = ? WHERE username = ?',
            (new_balance, username)
        )
        
        # Записываем транзакцию
        conn.execute(
            'INSERT INTO transactions (user_id, amount, type) VALUES (?, ?, "pay")',
            (user['id'], money)
        )
        
        conn.commit()
        conn.close()
        print(f"✅ Успешное списание: {username} -> {new_balance}")
        return "True"
    
    conn.close()
    print(f"❌ Ошибка списания: {username}")
    return "False"

@app.route('/users/give', methods=['GET'])
def give_user():
    """Начислить средства пользователю"""
    username = request.args.get('name')
    money = int(request.args.get('money'))
    
    if not username or money <= 0:
        return "False"
    
    print(f"➕ Начисление {money} для: {username}")
    
    conn = get_db_connection()
    
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    
    if user:
        new_balance = user['balance'] + money
        conn.execute(
            'UPDATE users SET balance = ? WHERE username = ?',
            (new_balance, username)
        )
        
        # Записываем транзакцию
        conn.execute(
            'INSERT INTO transactions (user_id, amount, type) VALUES (?, ?, "give")',
            (user['id'], money)
        )
        
        conn.commit()
        conn.close()
        print(f"✅ Успешное начисление: {username} -> {new_balance}")
        return "True"
    else:
        # Создаем пользователя если не существует
        conn.execute(
            'INSERT INTO users (username, balance) VALUES (?, ?)',
            (username, 1000 + money)
        )
        conn.commit()
        conn.close()
        print(f"✅ Создан новый пользователь с начислением: {username}")
        return "True"

@app.route('/users/top', methods=['GET'])
def get_top_users():
    """Получить топ пользователей по балансу"""
    print("🏆 Запрос топа пользователей")
    
    conn = get_db_connection()
    
    top_users = conn.execute('''
        SELECT username, balance 
        FROM users 
        ORDER BY balance DESC 
        LIMIT 10
    ''').fetchall()
    
    result = []
    for user in top_users:
        result.append({
            'username': user['username'],
            'balance': user['balance']
        })
    
    conn.close()
    return jsonify(result)

@app.route('/get/time', methods=['GET'])
def get_server_time():
    """Получить серверное время"""
    return str(int(time.time()))

@app.route('/admin/users', methods=['GET'])
def get_all_users():
    """Получить всех пользователей (для админа)"""
    conn = get_db_connection()
    
    users = conn.execute('''
        SELECT username, balance, created_at 
        FROM users 
        ORDER BY balance DESC
    ''').fetchall()
    
    result = []
    for user in users:
        result.append({
            'username': user['username'],
            'balance': user['balance'],
            'created_at': user['created_at']
        })
    
    conn.close()
    return jsonify(result)

@app.route('/admin/reset/<username>', methods=['POST'])
def reset_user_balance(username):
    """Сбросить баланс пользователя"""
    conn = get_db_connection()
    
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    
    if user:
        conn.execute(
            'UPDATE users SET balance = 1000 WHERE username = ?',
            (username,)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Баланс {username} сброшен до 1000"})
    
    conn.close()
    return jsonify({"status": "error", "message": "Пользователь не найден"})

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Casino Server</title>
        <meta charset="utf-8">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            h1 { text-align: center; font-size: 2.5em; }
            .endpoint { 
                background: rgba(255,255,255,0.2); 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 8px;
                border-left: 4px solid #00ff88;
            }
            code { 
                background: rgba(0,0,0,0.3); 
                padding: 5px 10px; 
                border-radius: 4px; 
                font-family: monospace;
            }
            .status { 
                text-align: center; 
                padding: 20px; 
                background: rgba(0,255,136,0.2);
                border-radius: 10px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎰 Casino Server</h1>
            <div class="status">
                <h2>✅ Сервер работает!</h2>
                <p>Сервер запущен на вашем компьютере</p>
            </div>
            
            <h3>📡 Доступные endpoints:</h3>
            <div class="endpoint">
                <code>GET /users/get?name=USERNAME</code><br>
                <small>Получить баланс пользователя</small>
            </div>
            <div class="endpoint">
                <code>GET /users/pay?name=USERNAME&money=AMOUNT</code><br>
                <small>Списать средства</small>
            </div>
            <div class="endpoint">
                <code>GET /users/give?name=USERNAME&money=AMOUNT</code><br>
                <small>Начислить средства</small>
            </div>
            <div class="endpoint">
                <code>GET /users/top</code><br>
                <small>Топ игроков</small>
            </div>
            <div class="endpoint">
                <code>GET /get/time</code><br>
                <small>Серверное время</small>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                <h4>🔗 Для OpenComputers используйте URL:</h4>
                <code style="font-size: 1.2em;">http://localhost:5000</code>
                <p><small>или IP вашего компьютера в локальной сети</small></p>
            </div>
        </div>
    </body>
    </html>
    """

def get_local_ip():
    """Получить локальный IP адрес"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "не удалось получить"

if __name__ == '__main__':
    # Инициализируем базу данных
    init_database()
    
    # Получаем IP адрес
    local_ip = get_local_ip()
    
    print("\n" + "="*60)
    print("🎰 CASINO SERVER ЗАПУЩЕН НА ВАШЕМ ПК!")
    print("="*60)
    print("🌐 Локальный URL: http://localhost:5000")
    print("🌐 Сетевой URL:   http://" + local_ip + ":5000")
    print("📁 База данных:   casino.db")
    print("🔐 Аутентификация: НЕ ТРЕБУЕТСЯ")
    print("="*60)
    print("📋 Доступные endpoints:")
    print("   • GET /users/get?name=USERNAME")
    print("   • GET /users/pay?name=USERNAME&money=AMOUNT") 
    print("   • GET /users/give?name=USERNAME&money=AMOUNT")
    print("   • GET /users/top")
    print("   • GET /get/time")
    print("="*60)
    print("🚀 Сервер запущен! Для остановки нажмите Ctrl+C")
    print("="*60 + "\n")
    
    # Запускаем сервер
    app.run(host='0.0.0.0', port=5000, debug=False)