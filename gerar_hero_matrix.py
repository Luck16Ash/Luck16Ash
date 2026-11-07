"""Gera o banner do topo: chuva Matrix (verde sobre preto) com apenas o nome.
Tudo local, sem serviço externo. Loop perfeito.
Requer: pip install pillow
Rode:  python gerar_hero_matrix.py   ->  matrix-hero.gif
"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NOME = "LUCA SIMÕES D'AGOSTINO"
SAIDA = "matrix-hero.gif"

W, H, CELL = 1200, 240, 20
COLS, ROWS = W // CELL, H // CELL
TRAIL = 10
L = ROWS + TRAIL            # ciclo de cada coluna
N = 2 * L                   # nº de quadros (loop perfeito)
MS = 90                     # ms por quadro

POOL = "アイウエオカキクケコサ"   # 11 glifos; N/4 = 11 => troca de glifo também fecha o loop

# Ajuste os caminhos das fontes se rodar em outro sistema operacional
CJK_CANDIDATAS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/msgothic.ttc", "C:/Windows/Fonts/YuGothR.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
]
BOLD_CANDIDATAS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "C:/Windows/Fonts/consolab.ttf", "/System/Library/Fonts/Menlo.ttc",
]
def acha(lista):
    for p in lista:
        if os.path.exists(p):
            return p
    raise SystemExit("Fonte não encontrada. Edite as listas de caminhos no topo do script.")

F_RAIN = ImageFont.truetype(acha(CJK_CANDIDATAS), 17)
F_NOME = ImageFont.truetype(acha(BOLD_CANDIDATAS), 58)
TRACK = 6

random.seed(16)  # mesma chuva a cada execução
cols = []
for c in range(COLS):
    ativa = random.random() < 0.78
    cols.append(dict(
        ativa=ativa,
        fase=random.randrange(L),
        vel=random.choice([1, 2, 2, 3]),          # meio-células por quadro
        off=[random.randrange(len(POOL)) for _ in range(ROWS)],
    ))

def cor(d):
    if d == 0:
        return (190, 255, 205)                    # cabeça da gota
    k = 1 - d / TRAIL
    return (0, int(35 + 220 * k * k), int(10 + 45 * k * k))

def chuva(t):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    dr = ImageDraw.Draw(img)
    for c, col in enumerate(cols):
        if not col["ativa"]:
            continue
        head = (col["fase"] + (col["vel"] * t) // 2) % L
        for r in range(ROWS):
            d = (head - r) % L
            if d >= TRAIL:
                continue
            ch = POOL[(col["off"][r] + t // 4) % len(POOL)]
            x = c * CELL + (CELL - F_RAIN.getlength(ch)) / 2
            dr.text((x, r * CELL + 1), ch, font=F_RAIN, fill=cor(d))
    return img

def largura(s):
    return sum(F_NOME.getlength(ch) + TRACK for ch in s) - TRACK

# ---- camada fixa: faixa escura + brilho + nome ----
tw = largura(NOME)
assert tw < W - 120, "nome largo demais"
x0 = (W - tw) / 2
bb = F_NOME.getbbox("H")
y0 = (H - (bb[3] - bb[1])) / 2 - bb[1]

mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
x = x0
for ch in NOME:
    md.text((x, y0), ch, font=F_NOME, fill=255)
    x += F_NOME.getlength(ch) + TRACK

banda = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(banda)
bd.rounded_rectangle([x0 - 44, 62, x0 + tw + 44, H - 62], radius=8,
                     fill=(0, 0, 0, 215), outline=(0, 51, 0, 255), width=2)
brilho = Image.new("RGBA", (W, H), (0, 150, 40, 0))
brilho.putalpha(mask.filter(ImageFilter.GaussianBlur(9)).point(lambda v: min(255, int(v * 1.1))))
texto = Image.new("RGBA", (W, H), (0, 255, 65, 0))
texto.putalpha(mask)
topo = Image.alpha_composite(Image.alpha_composite(banda, brilho), texto)
bordas = ImageDraw.Draw(topo)
bordas.rectangle([0, 0, W, 2], fill=(0, 51, 0, 255))
bordas.rectangle([0, H - 3, W, H], fill=(0, 51, 0, 255))

frames = []
for t in range(N):
    base = chuva(t).convert("RGBA")
    frames.append(Image.alpha_composite(base, topo).convert("RGB"))

ref = frames[N // 3].quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
frames = [f.quantize(palette=ref, dither=Image.Dither.NONE) for f in frames]
frames[0].save(SAIDA, save_all=True, append_images=frames[1:], duration=MS,
               loop=0, optimize=True, disposal=1)
print(N, "quadros ->", SAIDA, round(os.path.getsize(SAIDA) / 1024), "KB")
