import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'halal_cinema_secret_key_123')

# الاتصال بقاعدة بيانات Supabase
def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL variable is not set in Vercel")
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return conn

# إنشاء الجداول تلقائياً إذا لم تكن موجودة
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS shows (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                description TEXT,
                poster_url TEXT
            );
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id SERIAL PRIMARY KEY,
                show_id INTEGER REFERENCES shows(id) ON DELETE CASCADE,
                episode_number INTEGER NOT NULL,
                embed_code TEXT NOT NULL
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Database Init Error:", e)

# تهيئة قاعدة البيانات عند بدء التشغيل
init_db()

@app.route('/')
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shows ORDER BY id DESC")
    shows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', shows=shows)

@app.route('/show/<int:show_id>')
def show_detail(show_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shows WHERE id = %s", (show_id,))
    show = cur.fetchone()
    
    cur.execute("SELECT * FROM episodes WHERE show_id = %s ORDER BY episode_number ASC", (show_id,))
    episodes = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('show.html', show=show, episodes=episodes)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':  # كلمة مرور لوحة التحكم
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "كلمة المرور خاطئة!"
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shows ORDER BY id DESC")
    shows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin_dashboard.html', shows=shows)

@app.route('/admin/add_show', methods=['POST'])
def add_show():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    
    title = request.form.get('title')
    show_type = request.form.get('type')
    description = request.form.get('description')
    poster_url = request.form.get('poster_url')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO shows (title, type, description, poster_url) VALUES (%s, %s, %s, %s)",
        (title, show_type, description, poster_url)
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_episode', methods=['POST'])
def add_episode():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    
    show_id = request.form.get('show_id')
    episode_number = request.form.get('episode_number')
    embed_code = request.form.get('embed_code')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO episodes (show_id, episode_number, embed_code) VALUES (%s, %s, %s)",
        (show_id, episode_number, embed_code)
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
