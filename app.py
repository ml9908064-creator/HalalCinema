import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template_string, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "halal-cinema-secret-key-2026")

# Database Connection
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is missing.")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    if not DATABASE_URL:
        return
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                year INTEGER,
                rating VARCHAR(20),
                poster_url TEXT,
                embed_urls TEXT,
                download_url TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize Database on Start
try:
    init_db()
except Exception as e:
    print(f"Database init skipped or failed: {e}")

# Modern Shahid4u / Netflix Style HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>حلال سينما | Halal Cinema</title>
    <!-- Google Fonts & FontAwesome Icons -->
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --bg-main: #0b0c10;
            --bg-card: #1f2833;
            --primary: #00e676;
            --primary-hover: #00c853;
            --accent: #1f2833;
            --text-main: #ffffff;
            --text-muted: #c5c6c7;
            --card-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            --gradient-overlay: linear-gradient(180deg, rgba(11,12,16,0) 0%, rgba(11,12,16,0.95) 100%);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Cairo', sans-serif;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        /* Navbar Style */
        .navbar {
            background: rgba(11, 12, 16, 0.95);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding: 15px 5%;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .brand-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            color: #fff;
            font-size: 1.6rem;
            font-weight: 900;
            letter-spacing: 1px;
        }

        .brand-logo i {
            color: var(--primary);
            font-size: 1.8rem;
        }

        .nav-links {
            display: flex;
            gap: 20px;
            align-items: center;
        }

        .nav-link {
            color: var(--text-muted);
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s ease;
        }

        .nav-link:hover, .nav-link.active {
            color: var(--primary);
        }

        .admin-btn {
            background: var(--primary);
            color: #000;
            padding: 8px 18px;
            border-radius: 20px;
            font-weight: 700;
            text-decoration: none;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .admin-btn:hover {
            background: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3);
        }

        /* Hero Banner */
        .hero {
            position: relative;
            padding: 60px 5% 40px;
            background: radial-gradient(circle at top right, rgba(0, 230, 118, 0.08), transparent 50%);
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .hero h1 {
            font-size: 2.8rem;
            font-weight: 900;
            margin-bottom: 15px;
            background: linear-gradient(90deg, #ffffff, var(--primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            color: var(--text-muted);
            font-size: 1.1rem;
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.6;
        }

        /* Main Content Grid */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 5%;
            width: 100%;
            flex: 1;
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 25px;
            border-right: 4px solid var(--primary);
            padding-right: 12px;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
        }

        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 25px;
        }

        /* Media Card Component (Netflix/Shahid Style) */
        .media-card {
            background: var(--bg-card);
            border-radius: 12px;
            overflow: hidden;
            position: relative;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: var(--card-shadow);
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
        }

        .media-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 12px 30px rgba(0, 230, 118, 0.2);
        }

        .poster-wrapper {
            position: relative;
            width: 100%;
            padding-top: 145%; /* 2:3 Aspect Ratio */
            overflow: hidden;
            background: #15161d;
        }

        .poster-img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }

        .media-card:hover .poster-img {
            transform: scale(1.08);
        }

        .badge-type {
            position: absolute;
            top: 12px;
            right: 12px;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(5px);
            color: var(--primary);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            border: 1px solid rgba(0, 230, 118, 0.3);
            z-index: 2;
        }

        .badge-rating {
            position: absolute;
            top: 12px;
            left: 12px;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(5px);
            color: #ffd700;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 4px;
            z-index: 2;
        }

        .card-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            top: 0;
            background: var(--gradient-overlay);
            display: flex;
            align-items: flex-end;
            padding: 15px;
            opacity: 0.9;
        }

        .card-info {
            width: 100%;
            z-index: 2;
        }

        .card-title {
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 6px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .card-meta {
            font-size: 0.8rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .play-btn {
            background: var(--primary);
            color: #000;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
            transition: transform 0.2s ease;
        }

        .media-card:hover .play-btn {
            transform: scale(1.1);
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
        }

        .empty-state i {
            font-size: 4rem;
            color: #333;
            margin-bottom: 15px;
        }

        /* Details Modal / View Page Style */
        .details-container {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 30px;
            margin-top: 20px;
            box-shadow: var(--card-shadow);
        }

        .embed-responsive {
            position: relative;
            padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
            height: 0;
            overflow: hidden;
            border-radius: 12px;
            background: #000;
            margin: 20px 0;
        }

        .embed-responsive iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 700;
            text-decoration: none;
            cursor: pointer;
            border: none;
            transition: all 0.3s ease;
        }

        .btn-primary {
            background: var(--primary);
            color: #000;
        }

        .btn-primary:hover {
            background: var(--primary-hover);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        /* Footer */
        footer {
            background: #07070a;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding: 25px 5%;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: auto;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .hero h1 { font-size: 2rem; }
            .content-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; }
            .card-title { font-size: 0.88rem; }
        }
    </style>
</head>
<body>

    <!-- Header / Navbar -->
    <nav class="navbar">
        <a href="/" class="brand-logo">
            <i class="fa-solid fa-film"></i>
            <span>حلال<span style="color: var(--primary);">سينما</span></span>
        </a>
        <div class="nav-links">
            <a href="/" class="nav-link active">الرئيسية</a>
            <a href="/admin" class="admin-btn">
                <i class="fa-solid fa-lock"></i>
                <span>لوحة التحكم</span>
            </a>
        </div>
    </nav>

    {% block content %}
    <!-- Main Home Page -->
    <section class="hero">
        <h1>سينما آمنة ونظيفة للجميع</h1>
        <p>نقدم لكم مشاهدة معالجة ومفلترة للأفلام والمسلسلات لتناسب القيم والأخلاق، بجودة عالية وبدون إعلانات مزعجة.</p>
    </section>

    <main class="container">
        <div class="section-header">
            <h2 class="section-title">أحدث العروض المتاحة</h2>
        </div>

        {% if items %}
        <div class="content-grid">
            {% for item in items %}
            <a href="/watch/{{ item.id }}" class="media-card">
                <div class="poster-wrapper">
                    <img src="{{ item.poster_url if item.poster_url else 'https://via.placeholder.com/300x450/1f2833/ffffff?text=No+Poster' }}" alt="{{ item.title }}" class="poster-img" loading="lazy">
                    <span class="badge-type">{{ item.type }}</span>
                    {% if item.rating %}
                    <span class="badge-rating"><i class="fa-solid fa-star"></i> {{ item.rating }}</span>
                    {% endif %}
                    <div class="card-overlay">
                        <div class="card-info">
                            <h3 class="card-title">{{ item.title }}</h3>
                            <div class="card-meta">
                                <span>{{ item.year if item.year else '' }}</span>
                                <div class="play-btn">
                                    <i class="fa-solid fa-play"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </a>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            <i class="fa-solid fa-clapperboard"></i>
            <h3>لا توجد عروض متاحة حالياً</h3>
            <p>قم بزيارة لوحة التحكم لإضافة أول فيلم أو مسلسل لمكتبتك.</p>
        </div>
        {% endif %}
    </main>
    {% endblock %}

    <footer>
        <p>جميع الحقوق محفوظة منصة حلال سينما &copy; 2026</p>
    </footer>

</body>
</html>
'''

ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم | حلال سينما</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background-color: #0b0c10;
            color: #fff;
            font-family: 'Cairo', sans-serif;
            padding: 30px 5%;
        }
        .admin-card {
            background: #1f2833;
            border-radius: 12px;
            padding: 25px;
            max-width: 800px;
            margin: 0 auto 30px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
        h2 { margin-bottom: 20px; color: #00e676; text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #333;
            background: #0b0c10;
            color: #fff;
            box-sizing: border-box;
        }
        .btn-submit {
            background: #00e676;
            color: #000;
            font-weight: 700;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            font-size: 1rem;
        }
        .btn-submit:hover { background: #00c853; }
        .item-list { max-width: 800px; margin: 0 auto; }
        .item-row {
            background: #1f2833;
            padding: 15px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .btn-delete {
            background: #ff5252;
            color: #fff;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
        }
    </style>
</head>
<body>

    <div class="admin-card">
        <h2><i class="fa-solid fa-circle-plus"></i> إضافة فيلم أو مسلسل جديد</h2>
        <form method="POST" action="/admin/add">
            <div class="form-group">
                <label>العنوان:</label>
                <input type="text" name="title" required placeholder="مثال: انمي Kimetsu no Yaiba">
            </div>
            <div style="display: flex; gap: 15px;">
                <div class="form-group" style="flex: 1;">
                    <label>النوع:</label>
                    <select name="type">
                        <option value="فيلم">فيلم</option>
                        <option value="مسلسل">مسلسل</option>
                    </select>
                </div>
                <div class="form-group" style="flex: 1;">
                    <label>السنة:</label>
                    <input type="number" name="year" value="2026">
                </div>
                <div class="form-group" style="flex: 1;">
                    <label>التقييم:</label>
                    <input type="text" name="rating" placeholder="8.5/10">
                </div>
            </div>
            <div class="form-group">
                <label>رابط بوستر الصورة (Poster URL):</label>
                <input type="url" name="poster_url" required placeholder="https://...">
            </div>
            <div class="form-group">
                <label>رابط سيرفر المشاهدة (Embed URL):</label>
                <input type="url" name="embed_urls" placeholder="https://...">
            </div>
            <div class="form-group">
                <label>رابط التحميل المباشر (Download URL):</label>
                <input type="url" name="download_url" placeholder="https://...">
            </div>
            <div class="form-group">
                <label>الوصف:</label>
                <textarea name="description" rows="3"></textarea>
            </div>
            <button type="submit" class="btn-submit">حفظ وإضافة إلى المكتبة</button>
        </form>
    </div>

    <div class="item-list">
        <h3 style="margin-bottom: 15px; color: #c5c6c7;">المحتوى المضاف حالياً:</h3>
        {% for item in items %}
        <div class="item-row">
            <div>
                <strong>{{ item.title }}</strong> ({{ item.type }})
            </div>
            <a href="/admin/delete/{{ item.id }}" class="btn-delete" onclick="return confirm('هل أنت تأكد من الحذف؟')">حذف</a>
        </div>
        {% endfor %}
    </div>

</body>
</html>
'''

WATCH_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مشاهدة {{ item.title }} | حلال سينما</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background-color: #0b0c10;
            color: #fff;
            font-family: 'Cairo', sans-serif;
            padding: 20px 5%;
        }
        .watch-container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .video-box {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            background: #000;
            border-radius: 12px;
            overflow: hidden;
            margin: 20px 0;
            box-shadow: 0 8px 24px rgba(0,0,0,0.8);
        }
        .video-box iframe {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            border: 0;
        }
        .info-box {
            background: #1f2833;
            padding: 25px;
            border-radius: 12px;
            margin-top: 20px;
        }
        .btn-download {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: #00e676;
            color: #000;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 700;
            margin-top: 15px;
        }
        .btn-back {
            color: #c5c6c7;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>

    <div class="watch-container">
        <a href="/" class="btn-back"><i class="fa-solid fa-arrow-right"></i> العودة للرئيسية</a>
        <h1>{{ item.title }}</h1>
        
        {% if item.embed_urls %}
        <div class="video-box">
            <iframe src="{{ item.embed_urls }}" allowfullscreen></iframe>
        </div>
        {% endif %}

        <div class="info-box">
            <h3>تفاصيل العمل:</h3>
            <p style="margin-top: 10px; color: #c5c6c7;">{{ item.description if item.description else 'لا يوجد وصف متاح.' }}</p>

            {% if item.download_url %}
            <br>
            <a href="{{ item.download_url }}" target="_blank" class="btn-download">
                <i class="fa-solid fa-download"></i> تحميل مباشر
            </a>
            {% endif %}
        </div>
    </div>

</body>
</html>
'''

# Flask Routes
@app.route('/')
def home():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM content ORDER BY id DESC;")
        items = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        items = []
        print(f"Error fetching content: {e}")
    return render_template_string(HTML_TEMPLATE, items=items)

@app.route('/watch/<int:item_id>')
def watch(item_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM content WHERE id = %s;", (item_id,))
        item = cur.fetchone()
        cur.close()
        conn.close()
        if item:
            return render_template_string(WATCH_TEMPLATE, item=item)
    except Exception as e:
        print(f"Error fetching watch item: {e}")
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM content ORDER BY id DESC;")
        items = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        items = []
    return render_template_string(ADMIN_TEMPLATE, items=items)

@app.route('/admin/add', methods=['POST'])
def add_content():
    title = request.form.get('title')
    content_type = request.form.get('type')
    year = request.form.get('year')
    rating = request.form.get('rating')
    poster_url = request.form.get('poster_url')
    embed_urls = request.form.get('embed_urls')
    download_url = request.form.get('download_url')
    description = request.form.get('description')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO content (title, type, year, rating, poster_url, embed_urls, download_url, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        ''', (title, content_type, year, rating, poster_url, embed_urls, download_url, description))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error adding content: {e}")

    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:item_id>')
def delete_content(item_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM content WHERE id = %s;", (item_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error deleting content: {e}")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
