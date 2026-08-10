from flask import Flask, render_template_string, request, redirect, session

app = Flask(__name__)
app.secret_key = 'halal_cinema_super_secret_key'

ADMIN_PASSWORD = "admin"

MOVIES = [
    {
        "id": "1",
        "title": "فيلم The Last House 2026 مترجم اون لاين",
        "type": "فيلم",
        "category": "رعب",
        "year": "2026",
        "quality": "1080p BluRay",
        "country": "أجنبي",
        "rating": "8.5",
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&q=80",
        "description": "قصة مشوقة تدور في إطار من الغموض والإثارة داخل بيت قديم يحمل أسراراً غريبة.",
        "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ"
    },
    {
        "id": "2",
        "title": "مسلسل Project Hail Mary 2026 مترجم",
        "type": "مسلسل",
        "category": "خيال علمي",
        "year": "2026",
        "quality": "4K WEB-DL",
        "country": "أجنبي",
        "rating": "9.1",
        "poster": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&q=80",
        "description": "مغامرة فضائية ملحمية لإنقاذ كوكب الأرض من كارثة محققة.",
        "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ"
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HalalCinema - هلال سينما</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background-color: #0b0c10; color: #ffffff; min-height: 100vh; padding-bottom: 50px; }
        
        /* Top Navigation Header */
        header {
            background: #12141c;
            border-bottom: 2px solid #1f2430;
            padding: 12px 4%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        .logo-box { display: flex; align-items: center; gap: 10px; text-decoration: none; }
        .logo-text { font-size: 1.8rem; font-weight: 900; color: #10b981; letter-spacing: -0.5px; }
        .logo-sub { font-size: 0.75rem; color: #9ca3af; display: block; margin-top: -6px; }

        .nav-menu { display: flex; list-style: none; gap: 20px; align-items: center; }
        .nav-link { color: #e5e7eb; text-decoration: none; font-weight: 700; font-size: 0.95rem; transition: 0.2s; }
        .nav-link:hover, .nav-link.active { color: #10b981; }

        .admin-btn { background: #10b981; color: #000; font-weight: 800; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; }

        /* Filter Section (TopCinema Style) */
        .filter-section {
            background: #12141c;
            border: 1px solid #1f2430;
            border-radius: 12px;
            padding: 15px;
            margin: 25px auto;
            max-width: 1300px;
            width: 92%;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
        }
        .filter-title { font-weight: 800; color: #10b981; font-size: 1rem; margin-left: 10px; display: flex; align-items: center; gap: 6px; }
        .filter-select {
            background: #1a1d28;
            color: #d1d5db;
            border: 1px solid #2d3446;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            outline: none;
            cursor: pointer;
        }

        .main-container { max-width: 1300px; width: 92%; margin: 0 auto; }

        /* Video Player */
        .player-box {
            display: none;
            background: #12141c;
            border-radius: 12px;
            border: 1px solid #10b981;
            overflow: hidden;
            margin-bottom: 30px;
        }
        .iframe-container { position: relative; padding-bottom: 56.25%; height: 0; background: #000; }
        .iframe-container iframe { position: absolute; top:0; left:0; width:100%; height:100%; border:0; }
        .player-info { padding: 18px; }
        .player-info h2 { color: #10b981; font-weight: 800; margin-bottom: 8px; font-size: 1.4rem; }

        /* Movies Grid (TopCinema Poster Design) */
        .grid-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; border-right: 4px solid #10b981; padding-right: 12px; }
        .grid-header h3 { font-size: 1.3rem; font-weight: 800; }

        .movies-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
            gap: 18px;
        }

        .movie-card {
            background: #12141c;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
            cursor: pointer;
            border: 1px solid #1f2430;
            transition: transform 0.25s ease, border-color 0.25s ease;
        }
        .movie-card:hover { transform: translateY(-6px); border-color: #10b981; }

        .poster-wrapper { position: relative; width: 100%; height: 270px; overflow: hidden; }
        .poster-wrapper img { width: 100%; height: 100%; object-fit: cover; }
        
        /* Quality Ribbons (TopCinema Ribbons) */
        .badge-quality {
            position: absolute;
            top: 12px;
            left: -32px;
            background: #10b981;
            color: #000;
            font-weight: 800;
            font-size: 0.7rem;
            padding: 3px 30px;
            transform: rotate(-45deg);
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
            text-align: center;
            text-transform: uppercase;
        }

        .card-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, rgba(11, 12, 16, 0.95), transparent);
            padding: 20px 10px 10px 10px;
            text-align: center;
        }
        .movie-name { font-size: 0.9rem; font-weight: 700; color: #fff; line-height: 1.3; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
        .movie-btn-watch { margin-top: 6px; font-size: 0.75rem; color: #10b981; font-weight: 800; display: inline-block; }

        @media (max-width: 768px) {
            .nav-menu { display: none; }
            .movies-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
            .poster-wrapper { height: 210px; }
        }
    </style>
</head>
<body>

    <header>
        <a href="/" class="logo-box">
            <div>
                <span class="logo-text">HALAL CINEMA</span>
                <span class="logo-sub">توب سينما العائلة</span>
            </div>
        </a>
        <ul class="nav-menu">
            <li><a href="/" class="nav-link active">المضاف حديثاً</a></li>
            <li><a href="/?type=فيلم" class="nav-link">الأفلام</a></li>
            <li><a href="/?type=مسلسل" class="nav-link">المسلسلات</a></li>
            <li><a href="/?cat=أنمي" class="nav-link">الأنمي</a></li>
        </ul>
        <a href="/admin" class="admin-btn"><i class="fa-solid fa-lock"></i> لوحة التحكم</a>
    </header>

    <!-- Bar Filters -->
    <form class="filter-section" action="/" method="GET">
        <div class="filter-title"><i class="fa-solid fa-sliders"></i> الفلاتر:</div>
        
        <select name="cat" class="filter-select" onchange="this.form.submit()">
            <option value="">جميع التصنيفات</option>
            <option value="رعب">رعب</option>
            <option value="خيال علمي">خيال علمي</option>
            <option value="أكشن">أكشن</option>
            <option value="وثائقي">وثائقي</option>
        </select>

        <select name="type" class="filter-select" onchange="this.form.submit()">
            <option value="">النوع (الكل)</option>
            <option value="فيلم">أفلام</option>
            <option value="مسلسل">مسلسلات</option>
        </select>

        <select name="year" class="filter-select" onchange="this.form.submit()">
            <option value="">سنة الإصدار</option>
            <option value="2026">2026</option>
            <option value="2025">2025</option>
        </select>

        <a href="/" style="color: #9ca3af; text-decoration: none; font-size: 0.8rem; margin-right: auto;"><i class="fa-solid fa-rotate-right"></i> إعادة ضبط</a>
    </form>

    <div class="main-container">

        <!-- Player Window -->
        <div class="player-box" id="playerWindow">
            <div class="iframe-container">
                <iframe id="videoIframe" src="" allowfullscreen></iframe>
            </div>
            <div class="player-info">
                <h2 id="videoTitle"></h2>
                <p id="videoDesc" style="color: #9ca3af; font-size: 0.9rem;"></p>
            </div>
        </div>

        <div class="grid-header">
            <h3>أحدث العروض المتاحة</h3>
        </div>

        <div class="movies-grid">
            {% for movie in movies %}
            <div class="movie-card" onclick='playMovie({{ movie | tojson }})'>
                <div class="poster-wrapper">
                    <span class="badge-quality">{{ movie.quality }}</span>
                    <img src="{{ movie.poster }}" alt="{{ movie.title }}">
                    <div class="card-overlay">
                        <div class="movie-name">{{ movie.title }}</div>
                        <span class="movie-btn-watch"><i class="fa-solid fa-play"></i> مشاهدة اون لاين</span>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

    </div>

    <script>
        function playMovie(movie) {
            document.getElementById('playerWindow').style.display = 'block';
            document.getElementById('videoTitle').innerText = movie.title;
            document.getElementById('videoDesc').innerText = movie.description;
            document.getElementById('videoIframe').src = movie.embed_url;
            window.scrollTo({ top: 180, behavior: 'smooth' });
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
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@600;700;800&display=swap" rel="stylesheet">
    <style>
        body { background: #0b0c10; color: #fff; font-family: 'Cairo', sans-serif; padding: 40px 20px; }
        .admin-card { max-width: 650px; margin: 0 auto; background: #12141c; padding: 30px; border-radius: 12px; border: 1px solid #10b981; }
        h2 { color: #10b981; text-align: center; margin-bottom: 25px; }
        input, select, textarea { width: 100%; padding: 12px; margin-bottom: 12px; background: #1a1d28; border: 1px solid #2d3446; color: #fff; border-radius: 6px; box-sizing: border-box; }
        .row { display: flex; gap: 10px; }
        button { width: 100%; padding: 12px; background: #10b981; border: none; font-weight: 800; border-radius: 6px; cursor: pointer; color: #000; font-size: 1rem; margin-top: 10px; }
        .back-link { display: block; text-align: center; margin-top: 15px; color: #9ca3af; text-decoration: none; }
    </style>
</head>
<body>

    <div class="admin-card">
        <h2>لوحة التحكم لإضافة الأفلام 🎬</h2>

        {% if not logged_in %}
        <form method="POST" action="/admin/login">
            <input type="password" name="password" placeholder="أدخل كلمة المرور" required>
            <button type="submit">دخول</button>
        </form>
        {% else %}
        <form method="POST" action="/admin/add">
            <input type="text" name="title" placeholder="عنوان العمل (مثال: فيلم The Last House 2026 مترجم)" required>
            
            <div class="row">
                <select name="type">
                    <option value="فيلم">فيلم</option>
                    <option value="مسلسل">مسلسل</option>
                </select>
                <select name="category">
                    <option value="رعب">رعب</option>
                    <option value="خيال علمي">خيال علمي</option>
                    <option value="أكشن">أكشن</option>
                    <option value="وثائقي">وثائقي</option>
                    <option value="أنمي">أنمي</option>
                </select>
            </div>

            <div class="row">
                <input type="text" name="quality" placeholder="الجودة (مثال: 1080p BluRay)" value="1080p BluRay" required>
                <input type="text" name="year" placeholder="سنة الإصدار (مثال: 2026)" value="2026" required>
            </div>

            <input type="text" name="embed_url" placeholder="رابط Embed المشغل المباشر" required>
            <input type="text" name="poster" placeholder="رابط صورة البوستر (URL)" required>
            <textarea name="description" placeholder="قصة ونبذة الفيلم" rows="3"></textarea>

            <button type="submit">حفظ ونشر العمل فوراً</button>
        </form>
        <a href="/admin/logout" class="back-link">تسجيل الخروج</a>
        {% endif %}
        <a href="/" class="back-link">العودة للواجهة الرئيسية</a>
    </div>

</body>
</html>
"""

@app.route('/')
def home():
    cat = request.args.get('cat')
    m_type = request.args.get('type')
    year = request.args.get('year')
    
    filtered = MOVIES
    if cat: filtered = [m for m in filtered if m['category'] == cat]
    if m_type: filtered = [m for m in filtered if m['type'] == m_type]
    if year: filtered = [m for m in filtered if m['year'] == year]

    return render_template_string(HTML_TEMPLATE, movies=filtered)

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
        new_item = {
            "id": str(len(MOVIES) + 1),
            "title": request.form.get('title'),
            "type": request.form.get('type'),
            "category": request.form.get('category'),
            "quality": request.form.get('quality'),
            "year": request.form.get('year'),
            "embed_url": request.form.get('embed_url'),
            "poster": request.form.get('poster'),
            "description": request.form.get('description')
        }
        MOVIES.insert(0, new_item)
    return redirect('/')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run()
