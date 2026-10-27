import threading, time, socket, requests, webview
from flask import Flask, render_template_string, request
from youtubesearchpython import VideosSearch

app = Flask(__name__)
ANILIST_URL = "https://graphql.anilist.co"

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>RAXTES ULTIMATE</title>
<style>
:root{--bg:#08080c;--card:#181821;--card2:#23232f;--pink:#ff2e63;--pink2:#ff4b7a;--gray:#8f8fa3;--green:#00ff88}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}body{margin:0;background:var(--bg);color:#fff;font-family:system-ui,Arial;overflow-x:hidden;padding-bottom:70px}
a{color:inherit;text-decoration:none}
.header{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:#000;position:sticky;top:0;z-index:50;border-bottom:1px solid #1a1a22}
.logo{color:var(--pink);font-weight:900;font-size:22px;letter-spacing:1px}.logo span{color:#fff}
.search-box{display:flex;flex:1;margin:0 10px;background:var(--card2);border-radius:25px;padding:9px 14px;align-items:center;border:1px solid #2a2a35}
.search-box input{flex:1;background:transparent;border:0;color:#fff;outline:none;font-size:13px}
.nav{display:flex;gap:8px;overflow-x:auto;padding:12px 14px;scrollbar-width:none}
.nav::-webkit-scrollbar{display:none}
.nav-item{padding:8px 16px;background:var(--card);border-radius:20px;font-size:12px;cursor:pointer;white-space:nowrap;border:1px solid #222;transition:.2s}
.nav-item.active{background:var(--pink);border-color:var(--pink);font-weight:700}
.banner{position:relative;height:300px;margin:10px 12px;border-radius:18px;overflow:hidden;background:#111}
.banner img{width:100%;height:100%;object-fit:cover;opacity:0.6}
.banner-overlay{position:absolute;inset:0;background:linear-gradient(0deg,#000 5%,transparent 60%);display:flex;align-items:flex-end;padding:18px}
.badge{display:inline-block;padding:3px 8px;border-radius:5px;font-size:10px;font-weight:700;margin-right:6px}
.badge-pink{background:var(--pink)}.badge-green{background:var(--green);color:#000}.badge-dark{background:rgba(255,255,255,0.15)}
.section{padding:14px 12px}.section-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.section-head h2{font-size:15px;margin:0}.section-head span{font-size:11px;color:var(--gray)}
.hscroll{display:flex;gap:10px;overflow-x:auto;scrollbar-width:none;padding-bottom:4px}
.hscroll::-webkit-scrollbar{display:none}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
@media(min-width:600px){.grid{grid-template-columns:repeat(5,1fr)}}
.card{background:var(--card);border-radius:12px;overflow:hidden;cursor:pointer;border:1px solid #1f1f28;transition:.2s;position:relative}
.card:hover{border-color:var(--pink);transform:translateY(-2px)}
.card img{width:100%;height:160px;object-fit:cover;background:#111}
.card-info{padding:7px 8px}.card-info p{font-size:11px;margin:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600}
.card-info span{font-size:10px;color:var(--gray)}
.card .play-icon{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(255,46,99,0.9);width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;opacity:0;transition:.2s}
.card:hover .play-icon{opacity:1}
.ad-box{background:linear-gradient(135deg,#1a1a2e,#16213e);border:1px dashed #3a3a4a;padding:12px;text-align:center;border-radius:12px;margin:12px;font-size:12px;color:var(--gray)}
.ad-box b{color:#ffaa00}
.detail-hero{position:relative;height:380px}.detail-hero img{width:100%;height:100%;object-fit:cover}
.detail-hero::after{content:'';position:absolute;inset:0;background:linear-gradient(0deg,var(--bg) 10%,transparent 70%)}
.detail-content{margin-top:-60px;position:relative;z-index:2;padding:16px;display:flex;gap:14px}
.detail-poster{width:120px;height:175px;border-radius:12px;object-fit:cover;border:2px solid #222;flex-shrink:0}
.play-btn{width:100%;background:var(--pink);color:#fff;padding:14px;border-radius:28px;border:0;font-weight:900;font-size:14px;margin:8px 0;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px}
.btn-row{display:flex;gap:8px}.btn-small{flex:1;background:var(--card2);color:#fff;border:1px solid #2a2a35;padding:10px;border-radius:20px;font-size:12px;cursor:pointer}
.player-wrap{margin:12px;border-radius:14px;overflow:hidden;background:#000;border:1px solid #222}
.player-wrap iframe{width:100%;height:220px;border:0}
.bottom{position:fixed;bottom:0;left:0;right:0;background:rgba(0,0,0,0.96);backdrop-filter:blur(10px);display:flex;justify-content:space-around;padding:8px 0 10px;border-top:1px solid #1a1a22;z-index:100}
.bottom div{text-align:center;font-size:9px;color:var(--gray);cursor:pointer;line-height:1.2;padding:4px 12px;border-radius:10px}
.bottom div.active{color:var(--pink)}.bottom div i{font-size:18px;display:block;margin-bottom:2px;font-style:normal}
.toast{position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#222;color:#fff;padding:10px 18px;border-radius:20px;font-size:12px;z-index:200;display:none}
</style>
</head>
<body>

<div class="header">
<div class="logo">RAX<span>TES</span></div>
<form class="search-box" method="GET" action="/"><input name="q" value="{{q}}" placeholder="Search movies, anime, series..."><button type="submit" style="background:transparent;border:0;color:var(--pink);cursor:pointer">🔍</button></form>
<div style="font-size:10px;color:var(--gray)">ULTIMATE</div>
</div>

<div class="nav">
<div class="nav-item {{'active' if tab=='home' else ''}}" onclick="location.href='/?tab=home'">🏠 Home</div>
<div class="nav-item {{'active' if tab=='anime' else ''}}" onclick="location.href='/?tab=anime'">🔥 Anime</div>
<div class="nav-item {{'active' if tab=='movies' else ''}}" onclick="location.href='/?tab=movies&q=2024 movie'">🎬 Movies</div>
<div class="nav-item" onclick="location.href='/?tab=anime&q=Action'">⚔️ Action</div>
<div class="nav-item" onclick="location.href='/?tab=anime&q=Isekai'">🌍 Isekai</div>
<div class="nav-item" onclick="location.href='/?tab=anime&q=Romance'">❤️ Romance</div>
<div class="nav-item" onclick="location.href='/?tab=movies&q=Comedy'">😂 Comedy</div>
</div>

{% if detail %}
<div class="detail-hero"><img src="{{detail.banner or detail.cover}}"></div>
<div class="detail-content">
<img class="detail-poster" src="{{detail.cover}}">
<div style="flex:1"><h2 style="margin:0 0 6px 0;font-size:18px">{{detail.title}}</h2>
<div><span class="badge badge-pink">HD</span><span class="badge badge-green">FREE</span><span class="badge badge-dark">{{detail.year}} • {{detail.status}}</span></div>
<p style="font-size:11px;color:var(--gray);line-height:1.4;margin:8px 0">{{detail.desc}}</p>
</div>
</div>

<div style="padding:0 14px">
<button class="play-btn" onclick="document.getElementById('player').style.display='block'; window.scrollTo(0,0)">▶ PLAY NOW - FREE</button>
<div class="btn-row">
<button class="btn-small" onclick="addFav('{{detail.title}}'); showToast('Added to Favorites ❤️')">❤️ Favorite</button>
<button class="btn-small" onclick="showToast('Downloading... ⬇️ Saved to Downloads')">⬇ Download</button>
<button class="btn-small" onclick="showToast('Link copied! 🔗')">🔗 Share</button>
</div>

<div id="player" class="player-wrap" style="display:none;margin-top:14px">
<iframe src="https://www.youtube.com/embed/{{detail.yt or ''}}?autoplay=1" allow="autoplay; fullscreen" allowfullscreen></iframe>
<div style="padding:10px;font-size:11px;color:var(--gray);text-align:center">Playing trailer - Full movie search: {{detail.title}} free on YouTube</div>
</div>

<div class="ad-box">💰 Support RAXTES: MTN MoMo <b>07XXXXXXXX</b> - Donate 5k UGX keeps app alive! | <a href="https://mubiruabdurahuman33-coder.github.io/Raxtes/" style="color:var(--pink)">Get Latest Version</a></div>
</div>

{% else %}

{% if tab=='home' and not q %}
<div class="banner">
<img src="https://s4.anilist.co/file/anilistcdn/media/anime/banner/21-wdArKO4w1BT.jpg">
<div class="banner-overlay"><div><span class="badge badge-pink">TRENDING #1 WORLDWIDE</span><h1 style="margin:8px 0 4px 0">RAXTES ULTIMATE</h1><p style="margin:0;font-size:12px;color:#ccc">MovieBox clone • 10,000+ Movies & Anime • Free • No ads Pro 15k UGX</p><button class="play-btn" style="width:auto;padding:10px 22px;margin-top:10px" onclick="location.href='/?tab=anime'">▶ WATCH NOW</button></div></div>
</div>
{% endif %}

<div class="ad-box">🔥 RAXTES ULTIMATE - Remove Ads + 4K - <b style="color:#ffaa00">MTN MoMo: 07XXXXXXXX</b> | Pro 15,000 UGX | WhatsApp: 07XXXXXXXX</div>

<div class="section">
<div class="section-head"><h2>{{ '🔍 Search: '+q if q else '🔥 Trending Now' }}</h2><span>View all ></span></div>
<div class="grid">
{% for a in animes %}
<div class="card" onclick="location.href='/anime/{{a.id}}?tab={{tab}}&q={{q}}'">
<div style="position:relative"><img src="{{a.cover}}" loading="lazy"><div class="play-icon">▶</div></div>
<div class="card-info"><p>{{a.title}}</p><span>{{a.format}} • {{a.year}}</span></div>
</div>
{% endfor %}
</div>
</div>

<div class="section">
<div class="section-head"><h2>🎬 Recommended For You</h2></div>
<div class="hscroll">
{% for a in animes[:12] %}
<div class="card" style="flex:0 0 120px" onclick="location.href='/anime/{{a.id}}'"><img src="{{a.cover}}" style="height:170px"><div class="card-info"><p>{{a.title}}</p><span>HD • {{a.format}}</span></div></div>
{% endfor %}
</div>
</div>

{% endif %}

<div class="ad-box" style="margin-bottom:20px">📢 Monetize: 1. MoMo Donations 2. AdSense on website 3. Pro Version 15k UGX<br><small>Legal APIs: AniList + YouTube Free Movies - No piracy = No ban</small></div>

<div class="bottom">
<div class="{{'active' if tab=='home' else ''}}" onclick="location.href='/?tab=home'"><i>🏠</i>Home</div>
<div class="{{'active' if tab=='anime' else ''}}" onclick="location.href='/?tab=anime'"><i>🔥</i>Anime</div>
<div class="{{'active' if tab=='movies' else ''}}" onclick="location.href='/?tab=movies&q=latest movie'"><i>🎬</i>Movies</div>
<div onclick="showToast('Downloads - Coming Soon ⬇️')"><i>⬇</i>Download</div>
<div onclick="showFav()"><i>❤️</i>My List</div>
</div>

<div id="toast" class="toast"></div>

<script>
function showToast(msg){let t=document.getElementById('toast');t.innerText=msg;t.style.display='block';setTimeout(()=>t.style.display='none',2500)}
function addFav(title){let f=JSON.parse(localStorage.getItem('raxtes_fav')||'[]');if(!f.includes(title)){f.push(title);localStorage.setItem('raxtes_fav',JSON.stringify(f))}}
function showFav(){let f=JSON.parse(localStorage.getItem('raxtes_fav')||'[]');if(f.length==0)showToast('No favorites yet - Add some ❤️');else showToast('Favorites: '+f.join(', ').slice(0,60)+'...')}
let hist=localStorage.getItem('raxtes_hist');if(!hist) localStorage.setItem('raxtes_hist','[]');
</script>

</body>
</html>
"""

def fetch_anime(q=""):
    query = 'query ($search: String) { Page(perPage: 36) { media(search: $search, type: ANIME, sort: POPULARITY_DESC) { id title { romaji } coverImage { large } bannerImage format seasonYear } } }'
    try:
        r = requests.post(ANILIST_URL, json={"query": query, "variables": {"search": q if q else None}}, timeout=12)
        data = r.json()["data"]["Page"]["media"]
        out=[]
        for m in data:
            out.append({"id": m["id"], "title": m["title"]["romaji"], "cover": m["coverImage"]["large"], "banner": m["bannerImage"], "format": m["format"] or "TV", "year": m["seasonYear"] or "2024"})
        return out
    except:
        return []

def fetch_detail(aid):
    query = 'query ($id: Int) { Media(id: $id) { title { romaji } description coverImage { extraLarge } bannerImage status seasonYear trailer { id site } } }'
    try:
        r = requests.post(ANILIST_URL, json={"query": query, "variables": {"id": int(aid)}}, timeout=12)
        m = r.json()["data"]["Media"]
        yt = ""
        if m.get("trailer") and m["trailer"]["site"]=="youtube":
            yt=m["trailer"]["id"]
        return {"title": m["title"]["romaji"], "desc": (m["description"] or "Watch on RAXTES ULTIMATE - Free streaming.")[0:350].replace("<br>"," "), "cover": m["coverImage"]["extraLarge"], "banner": m["bannerImage"], "status": m["status"] or "FINISHED", "year": m["seasonYear"] or "2024", "yt": yt}
    except:
        return None

def fetch_movies(q):
    try:
        s = VideosSearch(f"{q} full movie free HD 2024", limit=36)
        res = s.result()['result']
        out=[]
        for v in res:
            thumb = v['thumbnails'][0]['url'] if v.get('thumbnails') else ""
            out.append({"id": v['id'], "title": v['title'][:60], "cover": thumb, "banner": thumb, "format": "MOVIE", "year": v.get('duration',"HD")})
        return out
    except:
        return []

@app.route("/")
def home():
    q=request.args.get("q","").strip()
    tab=request.args.get("tab","home")
    if tab=="movies":
        animes=fetch_movies(q if q else "latest movie 2024")
    else:
        animes=fetch_anime(q)
    return render_template_string(BASE_HTML, animes=animes, detail=None, q=q, tab=tab)

@app.route("/anime/<aid>")
def detail_page(aid):
    q=request.args.get("q","")
    tab=request.args.get("tab","anime")
    d=fetch_detail(aid)
    if not d:
        return home()
    return render_template_string(BASE_HTML, animes=[], detail=d, q=q, tab=tab)

def find_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1",0))
        return s.getsockname()[1]

def start_server(p):
    app.run(host="127.0.0.1", port=p, debug=False, use_reloader=False, threaded=True)

if __name__ == "__main__":
    port=find_port()
    threading.Thread(target=start_server, args=(port,), daemon=True).start()
    url=f"http://127.0.0.1:{port}"
    for _ in range(120):
        try:
            requests.get(url, timeout=0.3)
            break
        except:
            time.sleep(0.12)
    webview.create_window("RAXTES ULTIMATE - MovieBox Clone", url, width=420, height=850, min_size=(360,600))
    webview.start()
