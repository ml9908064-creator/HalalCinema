from flask import Flask, render_template_string

app = Flask(__name__)

# قاعدة بيانات الأفلام
MOVIES = [
    {
        "id": "1",
        "title": "رحلة العجائب",
        "category": "وثائقي",
        "rating": "9.2",
        "quality": "4K Ultra HD",
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&q=80",
        "description": "وثائقي رائع يأخذك في رحلة حول أسرار الطبيعة وعجائب الخلق في أقصى بقاع الأرض.",
        "servers": [
            {"name": "سيرفر رئيسي", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"},
            {"name": "سيرفر احتياطي", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"}
        ]
    },
    {
        "id": "2",
        "title": "أسرار الفضاء والكون",
        "category": "علمي",
        "rating": "8.8",
        "quality": "1080p",
        "poster": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&q=80",
        "description": "استكشاف لأعماق المجرات والنجوم وكيف يعمل هذا الكون الفسيح بانتظام ودقة متناهية.",
        "servers": [
            {"name": "سيرفر HD", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"}
        ]
    },
    {
        "id": "3",
        "title": "تاريخ الحضارات الإسلامية",
        "category": "تاريخي",
        "rating": "9.5",
        "quality": "1080p",
        "poster": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=500&q=80",
        "description": "نظرة شمولية على العصر الذهبي وتأثير العلماء والعلماء المسلمين في إثراء العلوم والتكنولوجيا.",
        "servers": [
            {"name": "سيرفر سريع", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"}
        ]
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
        body {
            background-color: #0d0b18;
            color: #ffffff;
            min-height: 100vh;
            padding-bottom: 40px;
        }
        header {
            background: rgba(20, 16, 36, 0.95);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding: 15px 5%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        .logo { font-size: 1.8rem; font-weight: 800; color: #22c55e; text-decoration: none; display: flex; align-items: center; gap: 8px; }
        
        .main-container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        
        /* Ad Banner */
        .ad-banner {
            background: rgba(255, 255, 255, 0.02);
            border: 1px dashed rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            color: #818cf8;
            font-size: 0.85rem;
            margin-bottom: 25px;
        }

        /* Movie Player View */
        .player-section { display: none; background: #141024; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.08); overflow: hidden; margin-bottom: 40px; }
        .video-box { position: relative; padding-bottom: 56.25%; height: 0; background: #000; }
        .video-box iframe { position: absolute; top:0; left:0; width:100%; height:100%; border:0; }
        
        .player-details { padding: 20px; }
        .movie-title { font-size: 1.8rem; font-weight: 700; color: #4ade80; margin-bottom: 8px; }
        .meta-tags { display: flex; gap: 10px; margin-bottom: 15px; }
        .tag { background: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; }
        
        .server-selector { display: flex; gap: 10px; margin: 15px 0; }
        .server-btn { background: #221c38; color: #fff; border: 1px solid rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .server-btn.active { background: #22c55e; border-color: #22c55e; }

        /* Grid Catalog */
        .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .section-title { font-size: 1.4rem; font-weight: 700; border-right: 4px solid #22c55e; padding-right: 10px; }
        
        .movies-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 20px;
        }
        
        .movie-card {
            background: #141024;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
            cursor: pointer;
            transition: transform 0.3s, border-color 0.3s;
        }
        .movie-card:hover { transform: translateY(-5px); border-color: #22c55e; }
        .poster-box { position: relative; height: 300px; width: 100%; }
        .poster-box img { width: 100%; height: 100%; object-fit: cover; }
        .badge-rating { position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: #facc15; padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 0.8rem; }
        
        .card-info { padding: 12px; }
        .card-title { font-size: 1.1rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .card-meta { display: flex; justify-content: space-between; color: #a1a1aa; font-size: 0.8rem; margin-top: 5px; }
    </style>
</head>
<body>

    <header>
        <a href="/" class="logo"><i class="fa-solid fa-film"></i> HalalCinema</a>
    </header>

    <div class="main-container">
        
        <div class="ad-banner">📢 مساحة إعلانية علوية</div>

        <!-- قسم المشغل (يظهر عند اختيار فيلم) -->
        <div class="player-section" id="playerSection">
            <div class="video-box">
                <iframe id="videoPlayer" src="" allowfullscreen></iframe>
            </div>
            <div class="player-details">
                <div class="movie-title" id="playerTitle"></div>
                <div class="meta-tags">
                    <span class="tag" id="playerRating"></span>
                    <span class="tag" id="playerQuality"></span>
                    <span class="tag" id="playerCategory"></span>
                </div>
                <p id="playerDesc" style="color: #cbd5e1; line-height: 1.6;"></p>
                <div class="server-selector" id="serverContainer"></div>
            </div>
        </div>

        <!-- دليل الأفلام -->
        <div class="section-header">
            <div class="section-title">الأفلام والوثائقيات المتاحة</div>
        </div>

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

        <div class="ad-banner" style="margin-top: 30px;">📢 مساحة إعلانية سفلية</div>

    </div>

    <script>
        function playMovie(movie) {
            document.getElementById('playerSection').style.display = 'block';
            document.getElementById('playerTitle').innerText = movie.title;
            document.getElementById('playerRating').innerText = '⭐ ' + movie.rating;
            document.getElementById('playerQuality').innerText = movie.quality;
            document.getElementById('playerCategory').innerText = movie.category;
            document.getElementById('playerDesc').innerText = movie.description;
            
            // تعيين السيرفر الأول
            document.getElementById('videoPlayer').src = movie.servers[0].url;
            
            // إنشاء أزرار السيرفرات
            const serverContainer = document.getElementById('serverContainer');
            serverContainer.innerHTML = '';
            movie.servers.forEach((server, index) => {
                const btn = document.createElement('button');
                btn.className = `server-btn ${index === 0 ? 'active' : ''}`;
                btn.innerText = server.name;
                btn.onclick = () => {
                    document.getElementById('videoPlayer').src = server.url;
                    document.querySelectorAll('.server-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                };
                serverContainer.appendChild(btn);
            });

            window.scrollTo({ top: 100, behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, movies=MOVIES)

if __name__ == '__main__':
    app.run()
