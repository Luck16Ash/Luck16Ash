"""Gera o banner do topo: chuva Matrix de 0 e 1 (verde sobre preto) com apenas o nome.
Tudo local, sem serviço externo. Loop perfeito.
Requer: pip install pillow
Rode:  python gerar_hero_matrix.py   ->  matrix-hero.gif
"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NOME = "LUCA D'AGOSTINO"
SAIDA = "matrix-hero.gif"

W, H, CELL = 1200, 240, 20
COLS, ROWS = W // CELL, H // CELL
TRAIL = 9
L = ROWS + TRAIL            # ciclo de cada coluna
N = 2 * L                   # nº de quadros (loop perfeito)
PASSOS = N // 2             # o dígito troca a cada 2 quadros e fecha o ciclo no fim
MS = 90                     # ms por quadro

# Ajuste os caminhos se rodar em outro sistema operacional
FONTES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "C:/Windows/Fonts/consolab.ttf", "/System/Library/Fonts/Menlo.ttc",
]
def acha(lista):
    for p in lista:
        if os.path.exists(p):
            return p
    raise SystemExit("Fonte não encontrada. Edite a lista FONTES no topo do script.")

F_RAIN = ImageFont.truetype(acha(FONTES), 18)
F_NOME = ImageFont.truetype(acha(FONTES), 60)
TRACK = 5

random.seed(16)  # mesma chuva a cada execução
cols = []
for c in range(COLS):
    cols.append(dict(
        ativa=random.random() < 0.6,
        fase=random.randrange(L),
        vel=random.choice([1, 2, 2, 3]),          # meio-células por quadro
        bits=[[random.choice("01") for _ in range(PASSOS)] for _ in range(ROWS)],
    ))

def cor(d):
    if d == 0:
        return (200, 255, 210)                    # cabeça da gota
    k = 1 - d / TRAIL
    return (int(20 * k), int(40 + 190 * k * k), int(20 + 60 * k * k))

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
            ch = col["bits"][r][(t // 2) % PASSOS]
            x = c * CELL + (CELL - F_RAIN.getlength(ch)) / 2
            dr.text((x, r * CELL + 1), ch, font=F_RAIN, fill=cor(d))
    return img

def largura(s):
    return sum(F_NOME.getlength(ch) + TRACK for ch in s) - TRACK

# ---- camada fixa: faixa escura suave + brilho + nome ----
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
ImageDraw.Draw(banda).rounded_rectangle([x0 - 46, 64, x0 + tw + 46, H - 64], radius=10,
                                        fill=(0, 0, 0, 185))
brilho = Image.new("RGBA", (W, H), (0, 150, 40, 0))
brilho.putalpha(mask.filter(ImageFilter.GaussianBlur(9)).point(lambda v: min(255, int(v * 1.1))))
texto = Image.new("RGBA", (W, H), (0, 255, 65, 0))
texto.putalpha(mask)
topo = Image.alpha_composite(Image.alpha_composite(banda, brilho), texto)

frames = []
for t in range(N):
    base = chuva(t).convert("RGBA")
    frames.append(Image.alpha_composite(base, topo).convert("RGB"))

ref = frames[N // 3].quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
frames = [f.quantize(palette=ref, dither=Image.Dither.NONE) for f in frames]
frames[0].save(SAIDA, save_all=True, append_images=frames[1:], duration=MS,
               loop=0, optimize=True, disposal=1)
print(N, "quadros ->", SAIDA, round(os.path.getsize(SAIDA) / 1024), "KB")
