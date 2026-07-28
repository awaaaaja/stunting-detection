"""Download Unsplash photos for landing page."""
import requests, os

UNSPLASH_ACCESS_KEY = "bK4FMVdZsWvyL3b4Hnhmxyq7K4aw3gCocwRB91evD70"
QUERIES = [
    ("hero-baby", "indonesian baby health"),
    ("posyandu", "posyandu indonesia"),
    ("nutrition", "child nutrition mother"),
    ("doctor-child", "doctor examining child clinic"),
]
OUT = "frontend/public/images"
os.makedirs(OUT, exist_ok=True)

for name, query in QUERIES:
    path = f"{OUT}/{name}.jpg"
    if os.path.exists(path):
        print(f"SKIP {name} — already exists")
        continue
    url = f"https://api.unsplash.com/photos/random?query={query}&orientation=landscape"
    r = requests.get(url, headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"})
    if r.status_code == 200:
        img_url = r.json()["urls"]["regular"]
        img = requests.get(img_url)
        with open(path, "wb") as f:
            f.write(img.content)
        print(f"OK {name} ({len(img.content)//1024}KB)")
    else:
        print(f"FAIL {name}: {r.status_code}")