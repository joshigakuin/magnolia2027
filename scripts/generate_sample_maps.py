"""Generate clearly labelled, fictional Magnolia demo maps and route slides."""
from pathlib import Path
import math
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = ROOT / "images"
IMAGE_DIR.mkdir(exist_ok=True)
WIDTH, HEIGHT = 1000, 680
BG = "#f7f5ed"
INK = "#26352b"
GRID = "#d9ded2"
BLUE = "#2479d8"
GREEN = "#36865d"
RED = "#d64141"

font_paths = [
    Path("C:/Windows/Fonts/meiryo.ttc"),
    Path("C:/Windows/Fonts/YuGothM.ttc"),
    Path("C:/Windows/Fonts/msgothic.ttc"),
]
font_path = next((p for p in font_paths if p.exists()), None)
def font(size):
    return ImageFont.truetype(str(font_path), size) if font_path else ImageFont.load_default()

hub_points = {
    "A_stairs": (340, 335), "B_stairs": (510, 335),
    "C_hub": (690, 335), "G_hub": (255, 335),
}
place_points = {
    "mainGate": (115, 320), "building1f": (470, 180), "building2f": (470, 215),
    "room301": (160, 150), "eastEntrance": (100, 220), "northEntrance": (470, 130),
    "southEntrance": (760, 335), "gymEntrance": (150, 510), "courtyard": (870, 510),
}
dest_points = {
    "east": (185, 165), "north": (470, 150), "south": (800, 195),
    "gym": (155, 510), "gym-small": (380, 510), "hall": (610, 510),
    "roof": (870, 510), "chemAB": (455, 185), "physicsAB": (500, 185), "magnolia-hall": (610, 510),
    "toilet": (675, 365),
    "class3a": (165, 175), "artclub": (450, 195), "tea": (790, 200),
    "science": (455, 185), "photo": (180, 210), "cafe": (800, 240),
    "music": (610, 510), "book": (490, 215),
}
labels = {
    "east":"東館", "north":"北館", "south":"南館", "gym":"大体育館",
    "gym-small":"小体育館", "hall":"講堂", "roof":"屋上庭園",
    "chemAB":"化学AB", "physicsAB":"物理AB", "magnolia-hall":"マグノリアホール", "toilet":"トイレ",
    "A_stairs":"ハブA", "B_stairs":"ハブB", "C_hub":"ハブC", "G_hub":"ハブG",
    "room301":"東館301", "building1f":"北館1F", "building2f":"北館2F",
    "mainGate":"正門", "eastEntrance":"東館入口", "northEntrance":"北館入口",
    "southEntrance":"南館入口", "gymEntrance":"体育館入口", "courtyard":"校庭QR",
}

def floor_background(level=1, campus=False):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    for x in range(30, WIDTH, 40):
        draw.line((x, 100, x, HEIGHT - 45), fill=GRID, width=1)
    for y in range(105, HEIGHT - 40, 40):
        draw.line((30, y, WIDTH - 30, y), fill=GRID, width=1)
    draw.rounded_rectangle((35, 95, 965, 570), radius=28, fill="#fffdf8", outline="#89978b", width=4)
    # Same schematic geometry across floors keeps every demo waypoint aligned.
    blocks = [
        ((65, 125, 295, 285), "東館", "教室・展示"),
        ((340, 115, 625, 285), "北館", f"{level}階 · 化学AB / 物理AB"),
        ((675, 115, 935, 285), "南館", f"{level}階 · 展示 / 体験"),
        ((65, 420, 250, 545), "大体育館", "運動・試合"),
        ((300, 420, 480, 545), "小体育館", "運動・試合"),
        ((535, 420, 720, 545), "講堂", "公演"),
        ((785, 420, 940, 545), "屋上庭園", "屋外"),
    ]
    for rect, title, subtitle in blocks:
        draw.rounded_rectangle(rect, radius=16, fill="#e8efe5", outline="#6f8c73", width=3)
        x1, y1, x2, y2 = rect
        draw.text((x1 + 10, y1 + 20), title, fill=INK, font=font(23))
        draw.text((x1 + 10, y1 + 60), subtitle, fill="#526458", font=font(15))
    draw.line((255, 335, 755, 335), fill="#9caa9d", width=18)
    draw.line((255, 335, 755, 335), fill="#fffdf8", width=5)
    for hub, (x, y) in hub_points.items():
        draw.ellipse((x - 13, y - 13, x + 13, y + 13), fill="#58725c", outline="white", width=3)
        draw.text((x - 25, y + 20), labels[hub], fill="#334b39", font=font(15))
    title = "マグノリア祭・校内図（動作確認用の仮図）"
    draw.text((38, 28), title, fill=INK, font=font(24))
    draw.text((38, 608), f"仮想レイアウト · {level}階サンプル · 実在の校舎・通路を表していません", fill="#8a3e35", font=font(17))
    return image

# Three distinct floor-plan PNGs for responsive overlays and route-page testing.
for level in (1, 2, 3):
    floor_background(level).save(IMAGE_DIR / f"floor-{level}.png", optimize=True)

# A separate East-wing map is used by the exhibition list.
base = floor_background(1)
base.save(IMAGE_DIR / "campus-east.png", optimize=True)

# Gather the explicit route image names plus generated destinations in the shared-hub table.
html = (ROOT / "index.html").read_text(encoding="utf-8")
route_names = set(re.findall(r"images/([A-Za-z0-9_.-]+\.png)", html))
hubs = ("A_stairs", "B_stairs", "C_hub", "G_hub")
extra_destinations = ("gym-small", "hall", "magnolia-hall", "chemAB", "physicsAB", "toilet")
short_hub_routes = {
    "A_stairs": {"gym"},
    "B_stairs": {"north", "chemAB", "physicsAB"},
    "C_hub": {"south", "roof"},
    "G_hub": {"gym", "gym-small"},
}
for hub in hubs:
    for dest in extra_destinations:
        route_names.add(f"{hub}_to_{dest}_01.png")
        if dest not in short_hub_routes.get(hub, set()):
            route_names.add(f"{hub}_to_{dest}_02.png")
for hub, destinations in short_hub_routes.items():
    for dest in destinations:
        route_names.discard(f"{hub}_to_{dest}_02.png")

# Draw arrows as corridor-following right-angle paths. Page two starts at page one's
# arrow point; the final page always ends at a red destination pin.
def draw_arrow(draw, points, color=GREEN, width=9):
    draw.line(points, fill=color, width=width, joint="curve")
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 22
    left = (x2 - size * math.cos(angle - .55), y2 - size * math.sin(angle - .55))
    right = (x2 - size * math.cos(angle + .55), y2 - size * math.sin(angle + .55))
    draw.polygon([(x2, y2), left, right], fill=color)

def marker(draw, point, color, label, pin=False):
    x, y = point
    if pin:
        draw.ellipse((x - 15, y - 15, x + 15, y + 15), fill=color, outline="white", width=4)
        draw.polygon([(x - 10, y + 8), (x + 10, y + 8), (x, y + 39)], fill=color)
    else:
        draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=color, outline="white", width=5)
    # Keep route labels in the map header, away from building labels and paths.
    if color == BLUE:
        box = (500, 34, 720, 62)
    elif color == GREEN:
        box = (500, 68, 720, 94)
    else:
        box = (735, 34, 970, 62)
    draw.rounded_rectangle(box, radius=8, fill="white", outline=color, width=2)
    draw.text((box[0] + 11, box[1] + 6), label, fill=INK, font=font(14))

def save_route(filename):
    stem = filename[:-4]
    # Route pages stay on the same schematic floor; the floor note is separate.
    level = 1
    image = floor_background(level)
    draw = ImageDraw.Draw(image)
    if "_to_" in stem and stem.split("_to_", 1)[0] in hub_points:
        source, rest = stem.split("_to_", 1)
        destination, page = rest.rsplit("_", 1)
        start = hub_points[source]
        end = dest_points.get(destination, dest_points["north"])
        waypoint = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        page_count = 2 if f"{source}_to_{destination}_02.png" in route_names else 1
        if page == "01" and page_count == 1:
            marker(draw, start, BLUE, "現在地・前ページから")
            draw_arrow(draw, [start, (end[0], start[1]), end], RED)
            if destination == "toilet":
                marker(draw, (end[0] - 22, end[1]), BLUE, "男子トイレ", pin=True)
                marker(draw, (end[0] + 22, end[1]), RED, "女子トイレ", pin=True)
            else:
                marker(draw, end, RED, f"目的地：{labels.get(destination, destination)}", pin=True)
            step = "目的地までのルート · 到着地点をピンで表示"
        elif page == "01":
            marker(draw, start, BLUE, "現在地・前ページから")
            draw_arrow(draw, [start, (waypoint[0], start[1]), waypoint])
            marker(draw, waypoint, GREEN, "次の地点")
            step = "次ページは矢印の地点から続きます"
        else:
            marker(draw, waypoint, BLUE, "前ページの地点")
            draw_arrow(draw, [waypoint, (end[0], waypoint[1]), end], RED)
            if destination == "toilet":
                marker(draw, (end[0] - 22, end[1]), BLUE, "男子トイレ", pin=True)
                marker(draw, (end[0] + 22, end[1]), RED, "女子トイレ", pin=True)
            else:
                marker(draw, end, RED, f"目的地：{labels.get(destination, destination)}", pin=True)
            step = "到着地点をピンで表示しています"
    else:
        source, destination = stem.split("_to_", 1)
        start = place_points.get(source, (120, 335))
        end = hub_points.get(destination, hub_points["A_stairs"])
        marker(draw, start, BLUE, f"現在地：{labels.get(source, source)}")
        draw_arrow(draw, [start, (end[0], start[1]), end])
        marker(draw, end, GREEN, f"次の地点：{labels.get(destination, destination)}")
        step = "次のページはこのハブから続きます"
    draw.rounded_rectangle((40, 570, 960, 598), radius=10, fill="#fffdf8", outline="#d5a48a", width=2)
    draw.text((55, 575), step, fill="#72513c", font=font(15))
    image.save(IMAGE_DIR / filename, optimize=True)

for name in sorted(route_names):
    if name in ("campus-other.png", "campus-east.png", "floor-1.png", "floor-2.png", "floor-3.png"):
        continue
    if "_to_" in name:
        save_route(name)

print(f"Generated 3 floor maps, campus-east.png, and {sum(1 for p in IMAGE_DIR.glob('*_to_*.png'))} fictional route images.")
