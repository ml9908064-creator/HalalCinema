import sqlite3
from flask import Flask, render_template_string, request, redirect, session, g

app = Flask(__name__)

# --- إعدادات الأمان وقاعدة البيانات ---
app.secret_key = 'halal_cinema_ultra_secure_key_2026_x89f'
ADMIN_PASSWORD = "Halal#CinemaSecured2026!"
DATABASE = 'halal_cinema.db'

# --- إدارة الاتصال بقاعدة البيانات ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- إنشاء جداول قاعدة البيانات للفظ الدائم ---
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                year TEXT,
                poster TEXT NOT NULL,
                description TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER,
                ep_number INTEGER NOT NULL,
                servers TEXT NOT NULL,
                FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
            )
        ''')
        db.commit()

init_db()

# --- القوالب وتصميم الواجهات ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HalalCinema - حلال سينما</title>
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

        .welcome-hero {
            background: linear-gradient(135deg, #12141c 0%, #1a2332 100%);
            border: 1px solid #10b981;
            border-radius: 12px;
            padding: 25px;
            margin: 20px auto;
            text-align: center;
            box-shadow: 0 4px 20px rgba(16, 185, 129, 0.1);
        }
        .welcome-hero h1 { color: #10b981; font-size: 1.8rem; margin-bottom: 10px; font-weight: 900; }
        .welcome-hero p { color: #d1d5db; font-size: 1rem; max-width: 800px; margin: 0 auto; line-height: 1.7; }
        .badge-halal { background: #10b981; color: #000; padding: 3px 10px; border-radius: 20px; font-weight: bold; font-size: 0.8rem; display: inline-block; margin-bottom: 8px; }

        .main-container { max-width: 1200px; width: 92%; margin: 10px auto; }

        .player-box {
            display: none;
            background: #12141c;
            border-radius: 12px;
            border: 2px solid #10b981;
            overflow: hidden;
            margin-bottom: 30px;
        }
        .iframe-container { position: relative; padding-bottom: 56.25%; height: 0; background: #000; }
        .iframe-container iframe { position: absolute; top:0; left:0; width:100%; height:100%; border:0; }
        .player-info { padding: 20px; }
        .player-info h2 { color: #10b981; font-weight: 800; margin-bottom: 8px; font-size: 1.4rem; }

        .servers-bar { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0; background: #111827; padding: 10px; border-radius: 8px; border: 1px solid #1f2430; }
        .server-btn { background: #374151; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-weight: 700; font-size: 0.85rem; }
        .server-btn:hover, .server-btn.active { background: #f59e0b; color: #000; }

        .episodes-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; background: #1a1d28; padding: 15px; border-radius: 8px; }
        .ep-btn { background: #2d3446; color: #fff; border: 1px solid #10b981; padding: 8px 18px; border-radius: 6px; cursor: pointer; font-weight: 700; font-size: 0.9rem; }
        .ep-btn:hover, .ep-btn.active { background: #10b981; color: #000; }

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

    <div class="main-container">

        <!-- القسم الترحيبي والتعريفي بمفهوم الموقع -->
        <div class="welcome-hero">
            <span class="badge-halal"><i class="fa-solid fa-shield-halal"></i> سينما آمنة ونظيفة</span>
            <h1>مرحباً بكم في منصة حلال سينما</h1>
            <p>
                نحن نمكنكم من مشاهدة ممتعة ومحتوى عائلي آمن. جميع الأفلام والمسلسلات المتاحة تم مراجعتها وتعديلها وتقطيع المشاهد واللقطات التي لا تتناسب مع قيمنا وثقافتنا الإسلامية وعاداتنا العربية، لنقدم لكم الفن بأسلوب نقي وراقي.
            </p>
        </div>

        <!-- مشغل الفيديو -->
        <div class="player-box" id="playerWindow">
            <div class="iframe-container">
                <iframe id="videoIframe" src="" allowfullscreen></iframe>
            </div>
            <div class="player-info">
                <h2 id="videoTitle"></h2>
                
                <div id="serversSection" style="margin-top: 10px;">
                    <span style="color:#f59e0b; font-weight:bold; font-size:0.9rem;"><i class="fa-solid fa-server"></i> اختر السيرفر:</span>
                    <div class="servers-bar" id="serversList"></div>
                </div>

                <p id="videoDesc" style="color: #9ca3af; font-size: 0.9rem; margin-top:10px;"></p>
                
                <div id="episodesSection" style="display:none; margin-top: 15px;">
                    <h4 style="color:#10b981; margin-bottom:10px;">قائمة الحلقات:</h4>
                    <div class="episodes-bar" id="episodesList"></div>
                </div>
            </div>
        </div>

        <div class="grid-header">
            <h3>قائمة العروض والمسلسلات المتاحة</h3>
        </div>

        <div class="movies-grid">
            {% for movie in movies %}
            <div class="movie-card" onclick='playMovie({{ movie | tojson }})'>
                <div class="poster-wrapper">
                    <img src="{{ movie.poster }}" alt="{{ movie.title }}">
                    <div class="card-overlay">
                        <div class="movie-name">{{ movie.title }}</div>
                        <span style="font-size:0.75rem; color:#10b981; font-weight:bold;"><i class="fa-solid fa-play"></i> مشاهدة العرض</span>
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

            const epSection = document.getElementById('episodesSection');
            const epList = document.getElementById('episodesList');
            epList.innerHTML = '';

            if (movie.episodes && movie.episodes.length > 0) {
                loadEpisodeServers(movie.episodes[0]);

                if (movie.type === 'مسلسل') {
                    epSection.style.display = 'block';
                    movie.episodes.forEach((ep, index) => {
                        const btn = document.createElement('button');
                        btn.className = 'ep-btn' + (index === 0 ? ' active' : '');
                        btn.innerText = 'الحلقة ' + ep.ep_number;
                        btn.onclick = function() {
                            document.querySelectorAll('.ep-btn').forEach(b => b.classList.remove('active'));
                            btn.classList.add('active');
                            loadEpisodeServers(ep);
                        };
                        epList.appendChild(btn);
                    });
                } else {
                    epSection.style.display = 'none';
                }
            }
            window.scrollTo({ top: 100, behavior: 'smooth' });
        }

        function loadEpisodeServers(ep) {
            const serversList = document.getElementById('serversList');
            serversList.innerHTML = '';
            let servers = ep.servers || [];

            if (servers.length > 0) {
                document.getElementById('videoIframe').src = servers[0];

                servers.forEach((url, i) => {
                    const sBtn = document.createElement('button');
                    sBtn.className = 'server-btn' + (i === 0 ? ' active' : '');
                    sBtn.innerText = 'سيرفر ' + (i + 1);
                    sBtn.onclick = function() {
                        document.querySelectorAll('.server-btn').forEach(sb => sb.classList.remove('active'));
                        sBtn.classList.add('active');
                        document.getElementById('videoIframe').src = url;
                    };
                    serversList.appendChild(sBtn);
                });
            }
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
    <title>لوحة التحكم المحمية - حلال سينما</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@600;700;800&display=swap" rel="stylesheet">
    <style>
        body { background: #0b0c10; color: #fff; font-family: 'Cairo', sans-serif; padding: 30px 15px; }
        .admin-card { max-width: 850px; margin: 0 auto; background: #12141c; padding: 25px; border-radius: 12px; border: 1px solid #10b981; }
        h2, h3 { color: #10b981; text-align: center; margin-bottom: 20px; }
        input, select, textarea { width: 100%; padding: 10px; margin-bottom: 10px; background: #1a1d28; border: 1px solid #2d3446; color: #fff; border-radius: 6px; box-sizing: border-box; }
        .row { display: flex; gap: 10px; }
        button { padding: 10px; background: #10b981; border: none; font-weight: 800; border-radius: 6px; cursor: pointer; color: #000; margin-top: 5px; }
        .btn-danger { background: #ef4444; color: #fff; }
        .btn-warning { background: #f59e0b; color: #000; }
        .btn-add-ep { background: #3b82f6; color: #fff; width: 100%; }
        .work-box { background: #1a1d28; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-right: 4px solid #10b981; }
        .ep-item { background: #12141c; padding: 8px 12px; border-radius: 6px; margin-top: 6px; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
        .edit-form { background: #111827; padding: 12px; border-radius: 8px; margin-top: 10px; display: none; border: 1px dashed #f59e0b; }
        .back-link { display: block; text-align: center; margin-top: 15px; color: #9ca3af; text-decoration: none; }
        .hint { color: #f59e0b; font-size: 0.75rem; margin-bottom: 8px; display: block; }
        .security-badge { background: #10b98122; border: 1px solid #10b981; color: #10b981; padding: 8px; border-radius: 6px; text-align: center; font-size: 0.85rem; margin-bottom: 20px; }
    </style>
</head>
<body>

    <div class="admin-card">
        <h2>لوحة التحكم المحمية - حلال سينما 🔒</h2>

        {% if not logged_in %}
        <form method="POST" action="/admin/login">
            <input type="password" name="password" placeholder="أدخل كلمة المرور المشفرة" required>
            <button type="submit" style="width:100%;">دخول أمن</button>
        </form>
        {% else %}

        <div class="security-badge">
            <i class="fa-solid fa-database"></i> قاعدة البيانات نشطة ومحمية. لن تتأثر بياناتك بتحديثات الكود!
        </div>

        <!-- إضافة مسلسل جديد -->
        <h3>إضافة مسلسل أو فيلم جديد</h3>
        <form method="POST" action="/admin/add">
            <input type="text" name="title" placeholder="عنوان المسلسل" required>
            <div class="row">
                <select name="type">
                    <option value="مسلسل">مسلسل</option>
                    <option value="فيلم">فيلم</option>
                </select>
                <input type="text" name="year" placeholder="السنة" value="2026">
            </div>
            <input type="text" name="poster" placeholder="رابط صورة البوستر (URL)" required>
            
            <span class="hint">💡 افصل بين سيرفرات الحلقة الأولى بفاصلة ( , )</span>
            <input type="text" name="embed_urls" placeholder="روابط Embed للحلقة الأولى" required>
            
            <textarea name="description" placeholder="وصف المسلسل" rows="2"></textarea>
            <button type="submit" style="width:100%;">إنشاء السلسلة وحفظها دائماً</button>
        </form>

        <hr style="border-color: #2d3446; margin: 30px 0;">

        <!-- التحكم بالسلسلة والحلقات -->
        <h3>إدارة العروض المتاحة في قاعدة البيانات</h3>
        {% for movie in movies %}
        <div class="work-box">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4>{{ movie.title }} <span style="font-size:0.8rem; color:#10b981;">({{ movie.type }})</span></h4>
                <div style="display:flex; gap:6px;">
                    <button type="button" class="btn-warning" onclick="toggleEdit('edit-{{ movie.id }}')">تعديل</button>
                    <form method="POST" action="/admin/delete/{{ movie.id }}" style="margin:0;">
                        <button type="submit" class="btn-danger" onclick="return confirm('حذف هذا العمل نهائياً؟')">حذف</button>
                    </form>
                </div>
            </div>

            <!-- نموذج تعديل -->
            <div id="edit-{{ movie.id }}" class="edit-form">
                <strong style="color:#f59e0b; font-size:0.85rem;">تعديل البيانات:</strong>
                <form method="POST" action="/admin/edit/{{ movie.id }}" style="margin-top:8px;">
                    <input type="text" name="title" value="{{ movie.title }}" required>
                    <div class="row">
                        <input type="text" name="year" value="{{ movie.year }}">
                        <input type="text" name="poster" value="{{ movie.poster }}" required>
                    </div>
                    <textarea name="description" rows="2">{{ movie.description }}</textarea>
                    <button type="submit" style="background:#f59e0b; color:#000; width:100%;">تحديث</button>
                </form>
            </div>

            <!-- الحلقات -->
            <div style="margin-top: 15px;">
                <strong style="font-size: 0.85rem; color: #9ca3af;">الحلقات المحفوظة:</strong>
                {% for ep in movie.episodes %}
                <div class="ep-item">
                    <span>
                        <strong>الحلقة {{ ep.ep_number }}</strong> — 
                        <small style="color: #f59e0b;">سيرفرات: {{ ep.servers | length }}</small>
                    </span>
                    <form method="POST" action="/admin/delete_ep/{{ ep.id }}" style="margin:0;">
                        <button type="submit" style="background:#ef4444; color:#fff; padding:3px 8px; font-size:0.75rem;">حذف</button>
                    </form>
                </div>
                {% endfor %}
            </div>

            {% if movie.type == 'مسلسل' %}
            <div style="margin-top: 15px; background: #12141c; padding: 10px; border-radius: 6px;">
                <strong style="color: #10b981; font-size: 0.85rem;">+ إضافة حلقة جديدة:</strong>
                <form method="POST" action="/admin/add_episode/{{ movie.id }}" style="margin-top: 8px;">
                    <div class="row">
                        <input type="number" name="ep_number" placeholder="رقم الحلقة" required style="width: 25%;">
                        <input type="text" name="embed_urls" placeholder="روابط السيرفرات (مفصولة بفاصلة ,)" required>
                    </div>
                    <button type="submit" class="btn-add-ep">إضافة ورسخ في قاعدة البيانات</button>
                </form>
            </div>
            {% endif %}

        </div>
        {% endfor %}

        <a href="/admin/logout" class="back-link">تسجيل الخروج الأمن</a>
        {% endif %}
        <a href="/" class="back-link">العودة للواجهة الرئيسية</a>
    </div>

    <script>
        function toggleEdit(id) {
            const form = document.getElementById(id);
            form.style.display = form.style.display === 'block' ? 'none' : 'block';
        }
    </script>

</body>
</html>
"""

# --- دالة جلب كل الأفلام والحلقات من قاعدة البيانات ---
def fetch_all_movies(movie_type=None):
    db = get_db()
    cursor = db.cursor()
    if movie_type:
        cursor.execute("SELECT * FROM movies WHERE type = ? ORDER BY id DESC", (movie_type,))
    else:
        cursor.execute("SELECT * FROM movies ORDER BY id DESC")
    
    movies_rows = cursor.fetchall()
    result = []
    
    for row in movies_rows:
        m = dict(row)
        cursor.execute("SELECT * FROM episodes WHERE movie_id = ? ORDER BY ep_number ASC", (m['id'],))
        ep_rows = cursor.fetchall()
        episodes = []
        for ep in ep_rows:
            episodes.append({
                "id": ep['id'],
                "ep_number": ep['ep_number'],
                "servers": [s.strip() for s in ep['servers'].split(',') if s.strip()]
            })
        m['episodes'] = episodes
        result.append(m)
    return result

# --- مسارات Flask ---
@app.route('/')
def home():
    m_type = request.args.get('type')
    movies = fetch_all_movies(m_type)
    return render_template_string(HTML_TEMPLATE, movies=movies)

@app.route('/admin')
def admin():
    movies = fetch_all_movies() if session.get('logged_in') else []
    return render_template_string(ADMIN_TEMPLATE, logged_in=session.get('logged_in'), movies=movies)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    if request.form.get('password') == ADMIN_PASSWORD:
        session['logged_in'] = True
    return redirect('/admin')

@app.route('/admin/add', methods=['POST'])
def admin_add():
    if session.get('logged_in'):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO movies (title, type, year, poster, description) VALUES (?, ?, ?, ?, ?)",
            (request.form.get('title'), request.form.get('type'), request.form.get('year'), request.form.get('poster'), request.form.get('description'))
        )
        movie_id = cursor.lastrowid
        urls = request.form.get('embed_urls')
        cursor.execute(
            "INSERT INTO episodes (movie_id, ep_number, servers) VALUES (?, ?, ?)",
            (movie_id, 1, urls)
        )
        db.commit()
    return redirect('/admin')

@app.route('/admin/edit/<int:movie_id>', methods=['POST'])
def edit_movie(movie_id):
    if session.get('logged_in'):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE movies SET title = ?, year = ?, poster = ?, description = ? WHERE id = ?",
            (request.form.get('title'), request.form.get('year'), request.form.get('poster'), request.form.get('description'), movie_id)
        )
        db.commit()
    return redirect('/admin')

@app.route('/admin/add_episode/<int:movie_id>', methods=['POST'])
def add_episode(movie_id):
    if session.get('logged_in'):
        db = get_db()
        cursor = db.cursor()
        ep_num = request.form.get('ep_number')
        urls = request.form.get('embed_urls')
        
        cursor.execute("DELETE FROM episodes WHERE movie_id = ? AND ep_number = ?", (movie_id, ep_num))
        cursor.execute("INSERT INTO episodes (movie_id, ep_number, servers) VALUES (?, ?, ?)", (movie_id, ep_num, urls))
        db.commit()
    return redirect('/admin')

@app.route('/admin/delete_ep/<int:ep_id>', methods=['POST'])
def delete_ep(ep_id):
    if session.get('logged_in'):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM episodes WHERE id = ?", (ep_id,))
        db.commit()
    return redirect('/admin')

@app.route('/admin/delete/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if session.get('logged_in'):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        cursor.execute("DELETE FROM episodes WHERE movie_id = ?", (movie_id,))
        db.commit()
    return redirect('/admin')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run()
