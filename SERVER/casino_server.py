from flask import Flask, request, jsonify
import sqlite3
import time
import os
from datetime import datetime

app = Flask(__name__)
DATABASE = 'casino.db'

# Настройки администратора
ADMIN_USERNAME = "Tintur"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    if not os.path.exists(DATABASE):
        print("Создание новой базы данных...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                balance INTEGER DEFAULT 1000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        
        cursor.execute('''
            CREATE TABLE system_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем администратора с большим балансом
        test_users = [
            (ADMIN_USERNAME, 10000),  # Администратор
            ('Player1', 1500),
            ('Player2', 800),
            ('Player3', 2500),
            ('TestUser', 1000)
        ]
        for username, balance in test_users:
            cursor.execute('INSERT OR IGNORE INTO users (username, balance) VALUES (?, ?)', (username, balance))
        
        # Логируем создание системы
        cursor.execute('INSERT INTO system_log (message) VALUES (?)', 
                      (f'Система запущена. Администратор: {ADMIN_USERNAME}',))
        
        conn.commit()
        conn.close()
        print("✅ База данных создана успешно!")
        print(f"👑 Администратор системы: {ADMIN_USERNAME}")
    else:
        print("✅ База данных уже существует")

@app.route('/users/get', methods=['GET'])
def get_user_balance():
    username = request.args.get('name')
    if not username:
        return "Error: username required", 400
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if user:
        balance = user['balance']
        print(f"💰 Запрос баланса: {username} = {balance}")
    else:
        conn.execute('INSERT INTO users (username, balance) VALUES (?, 1000)', (username,))
        conn.commit()
        balance = 1000
        print(f"👤 Создан новый пользователь: {username}")
    
    conn.close()
    return str(balance)

@app.route('/users/pay', methods=['GET'])
def pay_user():
    username = request.args.get('name')
    money = int(request.args.get('money'))
    
    if not username or money <= 0:
        return "False"
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if user and user['balance'] >= money:
        new_balance = user['balance'] - money
        conn.execute('UPDATE users SET balance = ? WHERE username = ?', (new_balance, username))
        conn.execute('INSERT INTO transactions (user_id, amount, type) VALUES (?, ?, "pay")', (user['id'], money))
        
        # Логируем операцию
        if username == ADMIN_USERNAME:
            conn.execute('INSERT INTO system_log (message) VALUES (?)', 
                        (f'Админ {username}: списание {money}',))
        
        conn.commit()
        conn.close()
        print(f"✅ Списание: {username} -{money} = {new_balance}")
        return "True"
    
    conn.close()
    print(f"❌ Ошибка списания: {username}")
    return "False"

@app.route('/users/give', methods=['GET'])
def give_user():
    username = request.args.get('name')
    money = int(request.args.get('money'))
    
    if not username or money <= 0:
        return "False"
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if user:
        new_balance = user['balance'] + money
        conn.execute('UPDATE users SET balance = ? WHERE username = ?', (new_balance, username))
        conn.execute('INSERT INTO transactions (user_id, amount, type) VALUES (?, ?, "give")', (user['id'], money))
        
        # Логируем операцию админа
        if username == ADMIN_USERNAME:
            conn.execute('INSERT INTO system_log (message) VALUES (?)', 
                        (f'Админ {username}: начисление {money}',))
        
        conn.commit()
        conn.close()
        print(f"✅ Начисление: {username} +{money} = {new_balance}")
        return "True"
    else:
        conn.execute('INSERT INTO users (username, balance) VALUES (?, ?)', (username, 1000 + money))
        conn.commit()
        conn.close()
        print(f"✅ Создан новый пользователь: {username} с балансом {1000 + money}")
        return "True"

@app.route('/users/top', methods=['GET'])
def get_top_users():
    conn = get_db_connection()
    top_users = conn.execute('SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10').fetchall()
    
    result = []
    for user in top_users:
        result.append({'username': user['username'], 'balance': user['balance']})
    
    conn.close()
    print("🏆 Запрос топа игроков")
    return jsonify(result)

@app.route('/get/time', methods=['GET'])
def get_server_time():
    return str(int(time.time()))

# Админские endpoints
@app.route('/admin/info', methods=['GET'])
def admin_info():
    conn = get_db_connection()
    
    # Статистика
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_balance = conn.execute('SELECT SUM(balance) as total FROM users').fetchone()['total']
    recent_logs = conn.execute('SELECT * FROM system_log ORDER BY created_at DESC LIMIT 10').fetchall()
    
    info = {
        'admin': ADMIN_USERNAME,
        'total_users': total_users,
        'total_balance': total_balance,
        'server_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'recent_logs': []
    }
    
    for log in recent_logs:
        info['recent_logs'].append({
            'message': log['message'],
            'time': log['created_at']
        })
    
    conn.close()
    return jsonify(info)

@app.route('/admin/users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT username, balance, created_at FROM users ORDER BY balance DESC').fetchall()
    
    result = []
    for user in users:
        result.append({
            'username': user['username'],
            'balance': user['balance'],
            'created_at': user['created_at'],
            'is_admin': user['username'] == ADMIN_USERNAME
        })
    
    conn.close()
    return jsonify(result)

@app.route('/admin/reset/<username>', methods=['POST'])
def reset_user_balance(username):
    conn = get_db_connection()
    
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if user:
        old_balance = user['balance']
        conn.execute('UPDATE users SET balance = 1000 WHERE username = ?', (username,))
        
        # Логируем сброс
        conn.execute('INSERT INTO system_log (message) VALUES (?)', 
                    (f'Админ {ADMIN_USERNAME}: сброс баланса {username} с {old_balance} до 1000',))
        
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Баланс {username} сброшен до 1000"})
    
    conn.close()
    return jsonify({"status": "error", "message": "Пользователь не найден"})

@app.route('/')
def index():
    return f"""
    <html>
    <head>
        <title>Turbo Happiness Casino Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: white; }}
            .container {{ background: #2d2d2d; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
            h1 {{ color: #ffd700; text-align: center; }}
            .admin-badge {{ background: #ff6b00; color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.8em; }}
            .endpoint {{ background: #3d3d3d; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #007bff; }}
            .admin-endpoint {{ border-left-color: #ff6b00; }}
            .server-info {{ background: #4CAF50; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎰 Turbo Happiness Casino Server</h1>
            
            <div class="server-info">
                <h3>🌐 Информация о сервере</h3>
                <p><strong>Адрес:</strong> http://192.168.0.177:5000</p>
                <p><strong>Администратор:</strong> <span class="admin-badge">{ADMIN_USERNAME}</span></p>
                <p><strong>Статус:</strong> 🟢 Активен</p>
            </div>
            
            <h3>📡 Основные endpoints:</h3>
            <div class="endpoint"><b>GET /users/get?name=USERNAME</b> - получить баланс</div>
            <div class="endpoint"><b>GET /users/pay?name=USERNAME&money=AMOUNT</b> - списать средства</div>
            <div class="endpoint"><b>GET /users/give?name=USERNAME&money=AMOUNT</b> - начислить средства</div>
            <div class="endpoint"><b>GET /users/top</b> - топ игроков</div>
            <div class="endpoint"><b>GET /get/time</b> - серверное время</div>
            
            <h3>👑 Админские endpoints:</h3>
            <div class="endpoint admin-endpoint"><b>GET /admin/info</b> - информация системы</div>
            <div class="endpoint admin-endpoint"><b>GET /admin/users</b> - все пользователи</div>
            <div class="endpoint admin-endpoint"><b>POST /admin/reset/USERNAME</b> - сброс баланса</div>
        </div>
    </body>
    </html>
    """

def get_local_ip():
    return "192.168.0.177"  # Ваш фиксированный IP

if __name__ == '__main__':
    init_database()
    local_ip = get_local_ip()
    
    print("\n" + "="*60)
    print("🎰 TURBO HAPPINESS CASINO SERVER")
    print("="*60)
    print(f"👑 Администратор: {ADMIN_USERNAME}")
    print(f"🌐 Локальный URL: http://localhost:5000")
    print(f"🌐 Сетевой URL:   http://{local_ip}:5000")
    print(f"📁 База данных:   casino.db")
    print("="*60)
    print("📊 Доступные endpoints:")
    print("   • GET /users/get?name=USERNAME")
    print("   • GET /users/pay?name=USERNAME&money=AMOUNT") 
    print("   • GET /users/give?name=USERNAME&money=AMOUNT")
    print("   • GET /users/top")
    print("   • GET /get/time")
    print("   • GET /admin/info")
    print("   • GET /admin/users")
    print("="*60)
    print("🚀 Сервер запущен!")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
