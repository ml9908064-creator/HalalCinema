from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'halal_cinema_admin_secret_key'  # مفتاح جلسة الأدمن

# كلمة مرور لوحة التحكم (يمكنك تغييرها هنا)
ADMIN_PASSWORD = "admin"

# قاعدة بيانات متغيرة بداخل الأقسام
MOVIES = [
    {
        "id": "1",
        "title": "رحلة العجائب",
        "category": "وثائقي",
        "rating": "9.2",
        "quality": "4K",
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&q=80",
        "description": "وثائقي رائع يأخذك في رحلة حول أسرار الطبيعة وعجائب الخلق في أقصى بقاع الأرض.",
        "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ"
    },
    {
        "id": "2",
        "title": "أسرار الفضاء والكون",
        "category": "علمي",
        "rating": "8.8",
        "quality": "1080p",
        "poster": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&q=80",
        "description": "استكشاف لأعماق المجرات والنجوم وكيف يعمل هذا الكون الفسيح بانتظام ودقة متناهية.",
        "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ"
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HalalCinema - سينما العائلة</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background-color: #0d0b18; color: #ffffff; min-height: 100vh; padding-bottom: 40px; }
        header {
            background: rgba(20, 16, 36, 0.95);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding: 15px 5%;
            display: flex; justify-content: space-between; align-items: center;
            position: sticky; top: 0; z-index: 100; backdrop-filter: blur(10px);
        }
        .logo { font-size: 1.8rem; font-weight: 800; color: #22c55e; text-decoration: none; }
        .admin-link { color: #a1a1aa; text-decoration: none; font-size: 0.9rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 8px; }
        .admin-link:hover { background: rgba(255,255,255,0.05); color: #fff; }

        .main-container { max-width: 1200px; margin: 25px auto; padding: 0 20px; }

        /* الأقسام/الفئات */
        .categories-bar { display: flex; gap: 10px; margin-bottom: 25px; overflow-x: auto; padding-bottom: 5px; }
        .cat-btn { background: #141024; color: #d4d4d8; border: 1px solid rgba(255,255,255,0.08); padding: 8px 18px; border-radius: 20px; text-decoration: none; font-weight: 600; font-size: 0.9rem; transition: 0.3s; white-space: nowrap; }
        .cat-btn.active, .cat-btn:hover { background: #22c55e; color: #000; border-color: #22c55e; }

        /* المشغل */
        .player-section { display: none; background: #141024; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.08); overflow: hidden; margin-bottom: 35px; }
        .video-box { position: relative; padding-bottom: 56.25%; height: 0; background: #000; }
        .video-box iframe { position: absolute; top:0; left:0; width:100%; height:100%; border:0; }
        .player-details { padding: 20px; }
        .movie-title { font-size: 1.6rem; font-weight: 700; color: #4ade80; margin-bottom: 8px; }

        /* الشبكة */
        .movies-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 20px; }
        .movie-card { background: #141024; border-radius: 14px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05); cursor: pointer; transition: 0.3s; }
        .movie-card:hover { transform: translateY(-5px); border-color: #22c55e; }
        .poster-box { position: relative; height: 280px; width: 100%; }
        .poster-box img { width: 100%; height: 100%; object-fit: cover; }
        .badge-rating { position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: #facc15; padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 0.8rem; }
        .card-info { padding: 12px; }
        .card-title { font-size: 1.05rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .card-meta { display: flex; justify-content: space-between; color: #a1a1aa; font-size: 0.85rem; margin-top: 5px; }
    </style>
</head>
<body>

    <header>
        <a href="/" class="logo">🍿 HalalCinema</a>
        <a href="/admin" class="admin-link"><i class="fa-solid fa-lock"></i> لوحة التحكم</a>
    </header>

    <div class="main-container">
        
        <!-- الأقسام -->
        <div class="categories-bar">
            <a href="/" class="cat-btn {% if not selected_cat %}active{% endif %}">الكل</a>
            <a href="/?cat=وثائقي" class="cat-btn {% if selected_cat == 'وثائقي' %}active{% endif %}">وثائقي</a>
            <a href="/?cat=علمي" class="cat-btn {% if selected_cat == 'علمي' %}active{% endif %}">علمي</a>
            <a href="/?cat=تاريخي" class="cat-btn {% if selected_cat == 'تاريخي' %}active{% endif %}">تاريخي</a>
            <a href="/?cat=أطفال" class="cat-btn {% if selected_cat == 'أطفال' %}active{% endif %}">أطفال وعائلة</a>
        </div>

        <!-- المشغل -->
        <div class="player-section" id="playerSection">
            <div class="video-box">
                <iframe id="videoPlayer" src="" allowfullscreen></iframe>
            </div>
            <div class="player-details">
                <div class="movie-title" id="playerTitle"></div>
                <p id="playerDesc" style="color: #cbd5e1; margin-top: 8px;"></p>
            </div>
        </div>

        <!-- عرض الأفلام -->
        <div class="movies-grid">
            {% for movie in movies %}
            <div class="movie-card" onclick='playMovie({{ movie | tojson }})'>
                <div class="poster-box">
                    <span class="badge-rating">⭐ {{ movie.rating }}</span>
                    <img src="{{ movie.poster }}" alt="{{ movie.title }}">
                </div>
                <div class="card-info">
                    <div class="card-title">{{ movie.title }}</div>
                    <div class="card-meta">
                        <span>{{ movie.category }}</span>
                        <span>{{ movie.quality }}</span>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

    </div>

    <script>
        function playMovie(movie) {
            document.getElementById('playerSection').style.display = 'block';
            document.getElementById('playerTitle').innerText = movie.title;
            document.getElementById('playerDesc').innerText = movie.description;
            document.getElementById('videoPlayer').src = movie.embed_url;
            window.scrollTo({ top: 120, behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم - HalalCinema</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@600;700&display=swap" rel="stylesheet">
    <style>
        body { background: #0d0b18; color: #fff; font-family: 'Cairo', sans-serif; padding: 40px 20px; }
        .admin-box { max-width: 600px; margin: 0 auto; background: #141024; padding: 30px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); }
        h2 { color: #22c55e; margin-bottom: 20px; text-align: center; }
        input, select, textarea { width: 100%; padding: 12px; margin-bottom: 15px; background: #221c38; border: 1px solid rgba(255,255,255,0.1); color: #fff; border-radius: 8px; }
        button { width: 100%; padding: 12px; background: #22c55e; border: none; font-weight: 700; border-radius: 8px; cursor: pointer; color: #000; }
        .back-btn { display: block; text-align: center; margin-top: 15px; color: #a1a1aa; text-decoration: none; }
    </style>
</head>
<body>
    <div class="admin-box">
        <h2>إضافة فيلم جديد 🎬</h2>
        {% if error %}<p style="color: #ef4444; margin-bottom: 10px;">{{ error }}</p>{% endif %}
        
        {% if not logged_in %}
        <form method="POST" action="/admin/login">
            <input type="password" name="password" placeholder="أدخل كلمة المرور" required>
            <button type="submit">دخول</button>
        </form>
        {% else %}
        <form method="POST" action="/admin/add">
            <input type="text" name="title" placeholder="اسم الفيلم" required>
            <select name="category">
                <option value="وثائقي">وثائقي</option>
                <option value="علمي">علمي</option>
                <option value="تاريخي">تاريخي</option>
                <option value="أطفال">أطفال وعائلة</option>
            </select>
            <input type="text" name="embed_url" placeholder="رابط Embed (مثل: https://streamtape.com/e/...)" required>
            <input type="text" name="poster" placeholder="رابط صورة الغلاف (URL)" required>
            <input type="text" name="rating" placeholder="التقييم (مثال: 8.5)" value="8.5">
            <input type="text" name="quality" placeholder="الجودة (مثال: 1080p)" value="1080p">
            <textarea name="description" placeholder="وصف وقصة الفيلم" rows="3"></textarea>
            <button type="submit">إضافة الفيلم فوراً</button>
        </form>
        <a href="/admin/logout" class="back-btn">تسجيل الخروج</a>
        {% endif %}
        <a href="/" class="back-btn">العودة للموقع الرئيسي</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    selected_cat = request.args.get('cat')
    if selected_cat:
        filtered_movies = [m for m in MOVIES if m['category'] == selected_cat]
    else:
        filtered_movies = MOVIES
    return render_template_string(HTML_TEMPLATE, movies=filtered_movies, selected_cat=selected_cat)

@app.route('/admin')
def admin():
    return render_template_string(ADMIN_TEMPLATE, logged_in=session.get('logged_in'))

@app.route('/admin/login', methods=['POST'])
def admin_login():
    if request.form.get('password') == ADMIN_PASSWORD:
        session['logged_in'] = True
    return redirect('/admin')

@app.route('/admin/add', methods=['POST'])
def admin_add():
    if session.get('logged_in'):
        new_movie = {
            "id": str(len(MOVIES) + 1),
            "title": request.form.get('title'),
            "category": request.form.get('category'),
            "embed_url": request.form.get('embed_url'),
            "poster": request.form.get('poster'),
            "rating": request.form.get('rating'),
            "quality": request.form.get('quality'),
            "description": request.form.get('description')
        }
        MOVIES.insert(0, new_movie)
    return redirect('/')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run()
