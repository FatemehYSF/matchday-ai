import textwrap
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE = 1080
TOP = (20, 28, 48)        # dark navy
BOTTOM = (6, 6, 10)       # almost black
WHITE = (245, 245, 245)
GREY = (150, 150, 165)
HOME = (0, 230, 118)      # green
AWAY = (255, 77, 109)     # pink-red
HOME_X, AWAY_X = 230, SIZE - 230


def font(size: int, heavy: bool = True):
    # Avenir Next Condensed is on every Mac (index 8 = Heavy, 5 = Medium)
    try:
        return ImageFont.truetype("Avenir Next Condensed.ttc", size, index=8 if heavy else 5)
    except OSError:
        return ImageFont.load_default(size=size)


def text_at(draw, x, y, text, fnt, fill):
    """Draw text centred on the point (x, y)."""
    draw.text((x, y), text, font=fnt, fill=fill, anchor="mm")


def background():
    # Vertical gradient: TOP colour fading into BOTTOM colour
    mask = Image.linear_gradient("L").resize((SIZE, SIZE))
    img = Image.composite(Image.new("RGB", (SIZE, SIZE), BOTTOM),
                          Image.new("RGB", (SIZE, SIZE), TOP), mask)
    # Two soft coloured glows behind the team badges
    glow = Image.new("RGB", (SIZE, SIZE))
    g = ImageDraw.Draw(glow)
    g.ellipse([HOME_X - 220, 160, HOME_X + 220, 600], fill=HOME)
    g.ellipse([AWAY_X - 220, 160, AWAY_X + 220, 600], fill=AWAY)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, glow, 0.18)


def badge(draw, x, y, team, colour):
    words = team.split()
    initials = (words[0][:3] if len(words) == 1 else "".join(w[0] for w in words))[:3].upper()
    draw.ellipse([x - 100, y - 100, x + 100, y + 100], fill=BOTTOM, outline=colour, width=8)
    text_at(draw, x, y, initials, font(80), colour)
    text_at(draw, x, y + 150, team.upper(), font(48), WHITE)


def render_match_card(match, caption, out_path):
    img = background()
    draw = ImageDraw.Draw(img, "RGBA")  # RGBA lets us draw see-through shapes

    # Top: competition pill + FULL TIME
    draw.rounded_rectangle([340, 50, 740, 110], radius=30, outline=GREY, width=3)
    text_at(draw, SIZE / 2, 80, match.competition.upper(), font(32, heavy=False), GREY)
    text_at(draw, SIZE / 2, 160, "FULL TIME", font(44), HOME)

    # Middle: badges and score (the losing side's number is dimmed)
    badge(draw, HOME_X, 360, match.home_team, HOME)
    badge(draw, AWAY_X, 360, match.away_team, AWAY)
    h, a = match.home_score, match.away_score
    text_at(draw, SIZE / 2 - 90, 360, str(h), font(220), WHITE if h >= a else GREY)
    text_at(draw, SIZE / 2, 350, ":", font(160), GREY)
    text_at(draw, SIZE / 2 + 90, 360, str(a), font(220), WHITE if a >= h else GREY)

    # Goal scorers in a column under their own team (max 4 each)
    for x, team in ((HOME_X, match.home_team), (AWAY_X, match.away_team)):
        goals = [g for g in match.goals if g.team == team][:4]
        for i, g in enumerate(goals):
            text_at(draw, x, 580 + i * 40, f"{g.player}  {g.minute}'", font(30, heavy=False), GREY)

    # Bottom: AI caption on a see-through panel (emojis removed: the font can't draw them)
    draw.rounded_rectangle([60, 780, SIZE - 60, 1020], radius=32, fill=(255, 255, 255, 18))
    clean = "".join(ch for ch in caption if ord(ch) < 0x2000).strip()
    lines = textwrap.wrap(clean, width=54)[:3]
    for i, line in enumerate(lines):
        y = 900 + (i - (len(lines) - 1) / 2) * 50
        text_at(draw, SIZE / 2, y, line, font(38, heavy=False), WHITE)

    img.save(out_path)
