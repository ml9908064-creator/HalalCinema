from flask import Flask, render_template_string, request, redirect, session

app = Flask(__name__)
app.secret_key = 'halal_cinema_super_secret_key'

ADMIN_PASSWORD = "admin"

# قاعدة البيانات (تأتي افتراضياً مع أعمال مجهزة لتوضيح الفكرة)
MOVIES = [
    {
        "id": "1",
        "title": "انمي Kimetsu no Yaiba الموسم الاول",
        "type": "مسلسل",
        "category": "أنمي",
        "year": "2026",
        "quality": "1080p BluRay",
        "country": "اليابان",
        "poster": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500&q=80",
        "description": "قصة تانجيرو وأخته نيزوكو ورحلتهما في القضاء على الشياطين.",
        "episodes": [
            {"ep_number": "1", "embed_url": "https://earnvids.xyz/v/eaervqlc2jo9"},
            {"ep_number": "2", "embed_url": "https://dood.so/e/0k1234567890"}
        ]
    },
    {
        "id": "2",
        "title": "فيلم The Last House 2026 مترجم",
        "type": "فيلم",
        "category": "رعب",
        "year": "2026",
        "quality": "1080p BluRay",
        "country": "أجنبي",
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&q=80",
        "description": "قصة مشوقة تدور في إطار من الغموض والإثارة داخل بيت قديم.",
        "episodes": [
            {"ep_number": "1", "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ"}
        ]
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
        .logo-text { font-size: 1.8rem; font-weight: 900; color: #10b981; }
        .nav-menu { display: flex; list-style: none; gap: 20px; align-items: center; }
        .nav-link { color: #e5e7eb; text-decoration: none; font-weight: 700; font-size: 0.95rem; }
        .nav-link:hover { color: #10b981; }
        .admin-btn { background: #10b981; color: #000; font-weight: 800; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; }

        .filter-section {
            background: #12141c;
            border: 1px solid #1f2430;
            border-radius: 12px;
            padding: 15px;
            margin: 25px auto;
            max-width: 1300px;
            width: 92%;
            display: flex;
            gap: 12px;
            align-items: center;
        }
        .filter-select { background: #1a1d28; color: #d1d5db; border: 1px solid #2d3446; padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; }

        .main-container { max-width: 1300px; width: 92%; margin: 0 auto; }

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

        /* Episodes Bar */
        .episodes-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 15px; background: #1a1d28; padding: 12px; border-radius: 8px; }
        .ep-btn { background: #2d3446; color: #fff; border: none; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-weight: 700; }
        .ep-btn.active, .ep-btn:hover { background: #10b981; color: #000; }

        .grid-header { border-right: 4px solid #10b981; padding-right: 12px; margin-bottom: 20px; }
        .movies-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 18px; }

        .movie-card {
            background: #12141c;
            border-radius: 10px;
            overflow: hidden;
            cursor: pointer;
            border: 1px solid #1f2430;
            transition: transform 0.25s ease;
        }
        .movie-card:hover { transform: translateY(-6px); border-color: #10b981; }
        .poster-wrapper { position: relative; width: 100%; height: 270px; }
        .poster-wrapper img { width: 100%; height: 100%; object-fit: cover; }
        .badge-quality { position: absolute; top: 12px; left: -32px; background: #10b981; color: #000; font-weight: 800; font-size: 0.7rem; padding: 3px 30px; transform: rotate(-45deg); }
        .card-overlay { position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, #0b0c10, transparent); padding: 15px 10px; text-align: center; }
        .movie-name { font-size: 0.9rem; font-weight: 700; }
    </style>
</head>
<body>

    <header>
        <a href="/" style="text-decoration:none;"><span class="logo-text">HALAL CINEMA</span></a>
        <ul class="nav-menu">
            <li><a href="/" class="nav-link">الرئيسية</a></li>
            <li><a href="/?type=فيلم" class="nav-link">الأفلام</a></li>
            <li><a href="/?type=مسلسل" class="nav-link">المسلسلات</a></li>
        </ul>
        <a href="/admin" class="admin-btn"><i class="fa-solid fa-lock"></i> لوحة التحكم</a>
    </header>

    <div class="main-container" style="margin-top: 25px;">

        <!-- Video Player Block -->
        <div class="player-box" id="playerWindow">
            <div class="iframe-container">
                <iframe id="videoIframe" src="" allowfullscreen></iframe>
            </div>
            <div class="player-info">
                <h2 id="videoTitle"></h2>
                <p id="videoDesc" style="color: #9ca3af; font-size: 0.9rem;"></p>
                
                <div id="episodesSection" style="display:none; margin-top: 15px;">
                    <h4 style="color:#10b981;">اختر الحلقة:</h4>
                    <div class="episodes-bar" id="episodesList"></div>
                </div>
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
                        <span style="font-size:0.75rem; color:#10b981; font-weight:bold;"><i class="fa-solid fa-play"></i> مشاهدة الآن</span>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

    </div>

    <script>
        let currentMovie = null;

        function playMovie(movie) {
            currentMovie = movie;
            document.getElementById('playerWindow').style.display = 'block';
            document.getElementById('videoTitle').innerText = movie.title;
            document.getElementById('videoDesc').innerText = movie.description;

            const epSection = document.getElementById('episodesSection');
            const epList = document.getElementById('episodesList');
            epList.innerHTML = '';

            if (movie.episodes && movie.episodes.length > 0) {
                // التشغيل التلقائي للحلقة الأولى
                changeEpisode(movie.episodes[0].embed_url, movie.episodes[0].ep_number);

                if (movie.type === 'مسلسل') {
                    epSection.style.display = 'block';
                    movie.episodes.forEach(ep => {
                        const btn = document.createElement('button');
                        btn.className = 'ep-btn';
                        btn.innerText = 'الحلقة ' + ep.ep_number;
                        btn.onclick = () => changeEpisode(ep.embed_url, ep.ep_number);
                        epList.appendChild(btn);
                    });
                } else {
                    epSection.style.display = 'none';
                }
            }
            window.scrollTo({ top: 100, behavior: 'smooth' });
        }

        function changeEpisode(url, epNum) {
            document.getElementById('videoIframe').src = url;
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
        body { background: #0b0c10; color: #fff; font-family: 'Cairo', sans-serif; padding: 30px 15px; }
        .admin-card { max-width: 800px; margin: 0 auto; background: #12141c; padding: 25px; border-radius: 12px; border: 1px solid #10b981; }
        h2, h3 { color: #10b981; text-align: center; margin-bottom: 20px; }
        input, select, textarea { width: 100%; padding: 10px; margin-bottom: 10px; background: #1a1d28; border: 1px solid #2d3446; color: #fff; border-radius: 6px; box-sizing: border-box; }
        .row { display: flex; gap: 10px; }
        button { width: 100%; padding: 10px; background: #10b981; border: none; font-weight: 800; border-radius: 6px; cursor: pointer; color: #000; margin-top: 5px; }
        .btn-danger { background: #ef4444; color: #fff; }
        .table-item { background: #1a1d28; padding: 12px; border-radius: 6px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .back-link { display: block; text-align: center; margin-top: 15px; color: #9ca3af; text-decoration: none; }
    </style>
</head>
<body>

    <div class="admin-card">
        <h2>لوحة التحكم والمحتوى 🎬</h2>

        {% if not logged_in %}
        <form method="POST" action="/admin/login">
            <input type="password" name="password" placeholder="أدخل كلمة المرور" required>
            <button type="submit">دخول</button>
        </form>
        {% else %}

        <!-- Add New Work Form -->
        <h3>إضافة عمل جديد (فيلم / مسلسل)</h3>
        <form method="POST" action="/admin/add">
            <input type="text" name="title" placeholder="عنوان العمل (مثال: مسلسل Kimetsu no Yaiba الموسم الأول)" required>
            <div class="row">
                <select name="type">
                    <option value="مسلسل">مسلسل</option>
                    <option value="فيلم">فيلم</option>
                </select>
                <select name="category">
                    <option value="أنمي">أنمي</option>
                    <option value="رعب">رعب</option>
                    <option value="أكشن">أكشن</option>
                    <option value="دراما">دراما</option>
                </select>
            </div>
            <div class="row">
                <input type="text" name="quality" placeholder="الجودة" value="1080p BluRay">
                <input type="text" name="year" placeholder="السنة" value="2026">
            </div>
            <input type="text" name="poster" placeholder="رابط صورة البوستر (URL)" required>
            <input type="text" name="embed_url" placeholder="رابط Embed للحلقة الأولى أو الفيلم" required>
            <textarea name="description" placeholder="نبذة عن العمل" rows="2"></textarea>
            <button type="submit">إنشاء العمل</button>
        </form>

        <hr style="border-color: #2d3446; margin: 30px 0;">

        <!-- Manage Works & Add Episodes -->
        <h3>إدارة الأعمال وإضافة الحلقات</h3>
        {% for movie in movies %}
        <div class="table-item">
            <div>
                <strong>{{ movie.title }}</strong> ({{ movie.type }})
                <br><small style="color: #10b981;">عدد الحلقات المتاحة: {{ movie.episodes | length }}</small>
            </div>
            <div style="display: flex; gap: 8px;">
                <form method="POST" action="/admin/delete/{{ movie.id }}">
                    <button type="submit" class="btn-danger" onclick="return confirm('هل تريد حذف العمل بالكامل؟')">حذف</button>
                </form>
            </div>
        </div>

        {% if movie.type == 'مسلسل' %}
        <div style="background: #12141c; padding: 10px; border-right: 2px solid #10b981; margin-bottom: 20px;">
            <form method="POST" action="/admin/add_episode/{{ movie.id }}">
                <div class="row">
                    <input type="number" name="ep_number" placeholder="رقم الحلقة (مثال: 2)" required style="width: 30%;">
                    <input type="text" name="embed_url" placeholder="رابط Embed الحلقة الجديدة" required>
                </div>
                <button type="submit" style="background: #3b82f6; color: #fff;">+ إضافة هذه الحلقة للمسلسل</button>
            </form>
        </div>
        {% endif %}

        {% endfor %}

        <a href="/admin/logout" class="back-link">تسجيل الخروج</a>
        {% endif %}
        <a href="/" class="back-link">العودة للواجهة الرئيسية</a>
    </div>

</body>
</html>
"""

@app.route('/')
def home():
    m_type = request.args.get('type')
    filtered = MOVIES
    if m_type: filtered = [m for m in filtered if m['type'] == m_type]
    return render_template_string(HTML_TEMPLATE, movies=filtered)

@app.route('/admin')
def admin():
    return render_template_string(ADMIN_TEMPLATE, logged_in=session.get('logged_in'), movies=MOVIES)

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
            "poster": request.form.get('poster'),
            "description": request.form.get('description'),
            "episodes": [
                {"ep_number": "1", "embed_url": "https://earnvids.xyz/v/eaervqlc2jo9"}
            ]
        }
        MOVIES.insert(0, new_item)
    return redirect('/admin')

@app.route('/admin/add_episode/<movie_id>', methods=['POST'])
def add_episode(movie_id):
    if session.get('logged_in'):
        for movie in MOVIES:
            if movie['id'] == movie_id:
                ep_num = request.form.get('ep_number')
                embed_url = request.form.get('embed_url')
                movie['episodes'].append({"ep_number": ep_num, "embed_url": embed_url})
                break
    return redirect('/admin')

@app.route('/admin/delete/<movie_id>', methods=['POST'])
def delete_movie(movie_id):
    global MOVIES
    if session.get('logged_in'):
        MOVIES = [m for m in MOVIES if m['id'] != movie_id]
    return redirect('/admin')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run()
