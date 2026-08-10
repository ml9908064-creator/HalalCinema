from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HalalCinema - سينما العائلة</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body {
            background-color: #0f0c1b;
            color: #ffffff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        header { width: 100%; max-width: 900px; padding: 15px 0; text-align: center; margin-bottom: 20px; }
        header h1 { color: #22c55e; font-size: 2.2rem; font-weight: 800; }
        .main-container { width: 100%; max-width: 900px; background: rgba(26, 21, 43, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        
        .ad-banner {
            width: 100%;
            background: rgba(255, 255, 255, 0.03);
            border: 1px dashed rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            color: #a1a1aa;
            font-size: 0.85rem;
            margin: 15px 0;
        }

        .video-player-box {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: 16px;
            background: #000;
            box-shadow: 0 8px 25px rgba(0,0,0,0.7);
        }
        .video-player-box iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0;
        }

        .server-selector { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
        .server-btn {
            background: #272042;
            color: #fff;
            border: 1px solid rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: 0.3s;
        }
        .server-btn.active, .server-btn:hover { background: #22c55e; border-color: #22c55e; }

        .movie-info { margin-top: 25px; line-height: 1.7; }
        .movie-title { font-size: 1.5rem; font-weight: 700; color: #4ade80; margin-bottom: 10px; }
        .movie-desc { color: #d4d4d8; font-size: 0.95rem; }
        .tags { display: flex; gap: 10px; margin-top: 10px; }
        .tag { background: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 4px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; }
    </style>
</head>
<body>

    <header>
        <h1>🍿 HalalCinema</h1>
        <p style="color: #a1a1aa; font-size: 0.9rem;">سينما العائلة - مشاهدة آمنة ونقية</p>
    </header>

    <div class="main-container">
        
        <div class="ad-banner">
            📢 مساحة إعلانية
        </div>

        <div class="video-player-box">
            <iframe id="moviePlayer" src="https://www.youtube.com/embed/dQw4w9WgXcQ" allowfullscreen></iframe>
        </div>

        <div class="server-selector">
            <button class="server-btn active" onclick="changeServer('https://www.youtube.com/embed/dQw4w9WgXcQ', this)">سيرفر 1</button>
            <button class="server-btn" onclick="changeServer('https://www.youtube.com/embed/dQw4w9WgXcQ', this)">سيرفر 2</button>
        </div>

        <div class="movie-info">
            <div class="movie-title">فيلم تجريبي</div>
            <div class="tags">
                <span class="tag">⭐ 9.0/10</span>
                <span class="tag">HD 1080p</span>
                <span class="tag">عائلي / وثائقي</span>
            </div>
            <p class="movie-desc" style="margin-top: 12px;">
                مرحباً بك في HalalCinema. هذا العرض التجريبي يعرض كيفية عمل المشغّل وتغيير السيرفرات بمرونة عالية.
            </p>
        </div>

        <div class="ad-banner">
            📢 مساحة إعلانية
        </div>

    </div>

    <script>
        function changeServer(embedUrl, btn) {
            document.getElementById('moviePlayer').src = embedUrl;
            document.querySelectorAll('.server-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run()
