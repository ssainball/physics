import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.widgets import Button

# ---------- 한글 폰트 설정 ----------
for name in ["Malgun Gothic", "AppleGothic", "NanumGothic"]:
    if name in {f.name for f in font_manager.fontManager.ttflist}:
        plt.rcParams["font.family"] = name
        break

plt.rcParams["toolbar"] = "None"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.default"] = "regular"

# ---------- 화면 크기: 1920 x 1080 (19.2 x 10.8 인치, dpi 100) 기준 ----------
DESIGN_W_IN, DESIGN_H_IN = 19.2, 10.8
K = {"k": 1.0}  # 창 크기에 따른 글자·선 배율 (1920x1080 이면 1.0)


def fs(size):  # 글자 크기
    return size * K["k"]


def lw(width):  # 선 굵기
    return width * 1.3 * K["k"]


def ms(size):  # 점(마커) 크기
    return size * 1.3 * K["k"]


SIGN_COLOR = "#B7950B"
BTN_COLOR = "#B7950B"
PROBLEM_COLOR = "#E67E22"
COLOR_A = "tab:red"
COLOR_B = "tab:blue"
BOX_FC = "#f7f7f7"
BOX_EC = "#bbbbbb"

# ---------- 문제 (2013학년도 수능 물리Ⅰ 3번 변형) ----------
TITLE = "두 자동차 A, B의 등가속도 운동"

# A가 P를 지나는 속력은 NA·v (원래 수능 문제는 NA = 4, 이 변형 문제는 NA = 3)
NA = 3

PROBLEM = (
    "문제) 직선 도로에서 자동차 A, B가 나란히\n"
    "각각 $3v$, $v$의 속력으로 기준선 P를 통과한 후,\n"
    "각각 등가속도 운동하여 기준선 Q에 동시에 도달하였다.\n"
    "(A는 Q에서 정지, P와 Q 사이의 거리는 $L$)\n"
    "P를 통과하여 Q에 도달할 때까지 옳은 것만을\n"
    "<보기>에서 있는 대로 고른 것은?\n"
    "ㄱ. B의 속력은 증가한다.\n"
    "ㄴ. 가속도의 크기는 A가 B의 2배이다.\n"
    "ㄷ. A와 B 사이의 거리는\n"
    "     최대 $L/3$까지 증가한다.\n"
    "① ㄱ   ② ㄴ   ③ ㄱ,ㄷ   ④ ㄴ,ㄷ   ⑤ ㄱ,ㄴ,ㄷ"
)

GUIDE = (
    r"핵심 공식     $L=\frac{v_0+v}{2}\,T$ (평균 속력 × 시간 = 거리)     "
    r"$a=\frac{v-v_0}{T}$ (속력 변화 ÷ 시간)     간격 최대 ⇔ 두 속력이 같아지는 순간"
)

VARS = ["v", "L", "p"]
# 변수: (표시 이름, 단위, 증감 단위, 최솟값, 최댓값)
# 처음 값 v = 4 m/s, L = 24 m 는 T, 가속도, 최대 거리가 모두 정수로 떨어지는 값이다.
# (v: 4, 8, 12 ... / L: 24, 48, 72 ... / 시각: 0, 25, 50, 75, 100 %)
RANGES = {
    "v": ("$v$   기준 속력", "m/s", 4.0, 4.0, 20.0),
    "L": ("$L$   P-Q 거리", "m", 24.0, 24.0, 240.0),
    "p": ("$t/T$  지금 시각", "%", 25.0, 0.0, 100.0),
}

state = {"v": 4.0, "L": 24.0, "p": 50.0}
anim = {"timer": None, "playing": False}
hover = {"on": False}


def g(x):
    """숫자를 보기 좋게: 4.0 → 4,  1.50 → 1.5,  0.667 → 0.67"""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


# ---------- 물리 계산 ----------
def physics():
    v, L, p = state["v"], state["L"], state["p"]
    T = 2 * L / (NA * v)  # A: L = (NA·v + 0)/2 · T
    t = T * p / 100
    return v, L, T, t


def pos_A(v, T, t):
    return NA * v * t - NA * v * t * t / (2 * T)


def pos_B(v, T, t):
    return v * t + (NA - 2) * v * t * t / (2 * T)


def speed_A(v, T, t):
    return NA * v * (1 - t / T)


def speed_B(v, T, t):
    return v + (NA - 2) * v * t / T


# ---------- 화면 생성 ----------
fig = plt.figure(figsize=(DESIGN_W_IN, DESIGN_H_IN), dpi=100)

scalable_texts = []  # (글자 객체, 기준 크기)
scalable_labels = []  # (버튼 라벨, 기준 크기)


def add_text(x, y, s, size, **kw):
    t = fig.text(x, y, s, fontsize=fs(size), **kw)
    scalable_texts.append((t, size))
    return t


def add_box(x, y, w, h, **kw):
    opts = dict(fc=BOX_FC, ec=BOX_EC, lw=1.5, zorder=0)
    opts.update(kw)
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0,rounding_size=0.006",
        transform=fig.transFigure,
        **opts,
    )
    fig.add_artist(box)
    return box


def style_button(btn, size, color):
    btn.label.set_fontsize(fs(size))
    btn.label.set_color(color)
    scalable_labels.append((btn.label, size))


# ----- 영역 배경 상자 -----
add_box(0.015, 0.600, 0.400, 0.315)  # 문제
add_box(0.015, 0.330, 0.400, 0.262)  # 변수 조절
add_box(0.015, 0.072, 0.400, 0.250)  # 모범답안
add_box(0.015, 0.012, 0.970, 0.052)  # 핵심 공식 안내
ANSWER_AREA = (
    0.015,
    0.415,
    0.072,
    0.322,
)  # 마우스를 올리는 영역 (x0, x1, y0, y1)

# ----- 1. 제목 -----
add_text(0.5, 0.988, TITLE, 40, ha="center", va="top", weight="bold")

# ----- 2. 문제 -----
add_text(
    0.028,
    0.905,
    PROBLEM,
    16.2,
    color=PROBLEM_COLOR,
    weight="bold",
    va="top",
    linespacing=1.2,
)

# ----- 7. 핵심 공식 안내 -----
add_text(0.5, 0.038, GUIDE, 17, ha="center", va="center")

# ----- 5. 그래프 (오른쪽) -----
ax_road = fig.add_axes([0.440, 0.665, 0.545, 0.200])  # 도로 그림
ax_vt = fig.add_axes([0.440, 0.395, 0.545, 0.205])  # 속력-시간 그래프
ax_gap = fig.add_axes([0.440, 0.135, 0.545, 0.190])  # 거리 그래프

# ----- 6. 모범답안 (마우스를 올리면 보임) -----
add_text(
    0.028,
    0.314,
    "※ 모범답안: 이 상자 안에 마우스를 올려 보세요\n"
    "    (판정은 여기에, 상세 풀이는 오른쪽 화면에 나타납니다)",
    12,
    color="gray",
    va="top",
)
result_text = add_text(
    0.028, 0.268, "", 15, va="top", alpha=0, linespacing=1.25
)

# 상세 풀이 패널: 마우스를 올렸을 때만 오른쪽 그래프 위에 나타난다
detail_box = add_box(
    0.435, 0.100, 0.550, 0.800, fc="white", ec=PROBLEM_COLOR, lw=3, zorder=20
)
detail_box.set_visible(False)
DETAIL_TOP = 0.885  # 첫 줄 위치
DETAIL_STEP = 0.0258  # 줄 간격 (화면 높이 비율, 글꼴과 상관없이 고정)
DETAIL_MAX_LINES = 30
detail_lines = []
for _i in range(DETAIL_MAX_LINES):
    _t = add_text(
        0.450, DETAIL_TOP - _i * DETAIL_STEP, "", 16, va="top", zorder=21
    )
    _t.set_visible(False)
    detail_lines.append(_t)

rows = []
buttons = []


# ---------- 1) 도로 그림 ----------
def draw_road(v, L, T, t):
    ax = ax_road
    ax.clear()
    cw = 0.075 * L  # 자동차 길이
    yA, yB = 1.0, 0.0

    xA, xB = pos_A(v, T, t), pos_B(v, T, t)
    sA, sB = speed_A(v, T, t), speed_B(v, T, t)

    # 도로, 가운데 차선, 기준선 P·Q
    ax.add_patch(
        Rectangle((-0.12 * L, -0.55), 1.34 * L, 2.1, color="#e6e6e6", zorder=0)
    )
    ax.plot(
        [-0.12 * L, 1.22 * L],
        [0.5, 0.5],
        color="white",
        linestyle="--",
        linewidth=lw(2),
        zorder=1,
    )
    for x, name in ((0, "기준선 P"), (L, "기준선 Q")):
        ax.plot(
            [x, x],
            [-0.55, 1.55],
            color="black",
            linestyle="--",
            linewidth=lw(1.5),
            zorder=2,
        )
        ax.text(
            x,
            1.62,
            name,
            ha="center",
            va="bottom",
            fontsize=fs(13),
            weight="bold",
        )

    # 같은 시간 간격(T/10)마다의 위치 → 점 사이 간격이 속력을 보여 준다
    for k in range(11):
        tk = T * k / 10
        ax.plot(
            pos_A(v, T, tk),
            yA,
            "o",
            color=COLOR_A,
            markersize=ms(4.5),
            alpha=0.45,
            zorder=3,
        )
        ax.plot(
            pos_B(v, T, tk),
            yB,
            "o",
            color=COLOR_B,
            markersize=ms(4.5),
            alpha=0.45,
            zorder=3,
        )

    # 자동차 + 속력 화살표 (화살표 길이 = 속력)
    for x, y, s, c, name, ty in (
        (xA, yA, sA, COLOR_A, "A", yA + 0.42),
        (xB, yB, sB, COLOR_B, "B", yB - 0.42),
    ):
        ax.add_patch(
            Rectangle((x - cw / 2, y - 0.22), cw, 0.44, color=c, zorder=5)
        )
        ax.text(
            x,
            y,
            name,
            color="white",
            ha="center",
            va="center",
            fontsize=fs(14),
            weight="bold",
            zorder=6,
        )
        arrow_len = s / (NA * v) * 0.12 * L
        if arrow_len > 0.004 * L:
            ax.annotate(
                "",
                xy=(x + cw / 2 + arrow_len, y),
                xytext=(x + cw / 2, y),
                arrowprops=dict(
                    arrowstyle="-|>", color=c, lw=lw(3), mutation_scale=fs(18)
                ),
                zorder=6,
            )
        ax.text(
            x,
            ty,
            f"{g(s)} m/s" if s > 0.05 else "정지",
            ha="center",
            va="center",
            fontsize=fs(12),
            color=c,
            weight="bold",
            zorder=6,
        )

    # A와 B 사이의 거리
    gap = xA - xB
    ax.plot(
        [xA, xA],
        [yA - 0.22, 0.5],
        color="tab:green",
        linestyle=":",
        linewidth=lw(1.5),
        zorder=4,
    )
    ax.plot(
        [xB, xB],
        [yB + 0.22, 0.5],
        color="tab:green",
        linestyle=":",
        linewidth=lw(1.5),
        zorder=4,
    )
    if gap > 0.002 * L:
        ax.annotate(
            "",
            xy=(xA, 0.5),
            xytext=(xB, 0.5),
            arrowprops=dict(
                arrowstyle="<->",
                color="tab:green",
                lw=lw(2.5),
                mutation_scale=fs(14),
            ),
            zorder=6,
        )
    ax.text(
        (xA + xB) / 2,
        0.5,
        f"간격 {g(gap)} m",
        ha="center",
        va="center",
        fontsize=fs(13),
        color="tab:green",
        weight="bold",
        zorder=7,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"),
    )

    # P-Q 거리 L
    ax.annotate(
        "",
        xy=(L, -0.8),
        xytext=(0, -0.8),
        arrowprops=dict(
            arrowstyle="<->", color="black", lw=lw(1.5), mutation_scale=fs(14)
        ),
    )
    ax.text(
        L / 2,
        -0.8,
        f"$L$ = {g(L)} m",
        ha="center",
        va="center",
        fontsize=fs(13),
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"),
    )

    ax.set_xlim(-0.12 * L, 1.22 * L)
    ax.set_ylim(-1.0, 2.0)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title(
        "도로를 위에서 본 모습  (점 = 같은 시간 간격마다의 위치)",
        fontsize=fs(14),
    )


# ---------- 2) 속력-시간 그래프 ----------
def draw_vt(v, L, T, t):
    ax = ax_vt
    ax.clear()
    tt = np.linspace(0, T, 200)
    vA = NA * v * (1 - tt / T)
    vB = v + (NA - 2) * v * tt / T

    ax.fill_between(tt, 0, vA, color=COLOR_A, alpha=0.25)
    ax.fill_between(tt, 0, vB, color=COLOR_B, alpha=0.25)
    ax.plot(
        tt,
        vA,
        color=COLOR_A,
        linewidth=lw(3),
        label=f"A: {g(NA * v)} → 0 m/s  (감속)",
    )
    ax.plot(
        tt,
        vB,
        color=COLOR_B,
        linewidth=lw(3),
        label=f"B: {g(v)} → {g((NA - 1) * v)} m/s  (가속)",
    )
    ax.plot(
        T / 2,
        NA * v / 2,
        "*",
        color="gold",
        markeredgecolor="black",
        markersize=ms(17),
        label="두 속력이 같아지는 순간 ($t=T/2$)",
    )

    ax.axvline(t, color="gray", linestyle="--", linewidth=lw(1.2))
    sA, sB = speed_A(v, T, t), speed_B(v, T, t)
    ax.plot(t, sA, "o", color=COLOR_A, markersize=ms(10))
    ax.plot(t, sB, "o", color=COLOR_B, markersize=ms(10))
    ax.annotate(
        g(sA),
        (t, sA),
        xytext=(9, 6),
        textcoords="offset points",
        color=COLOR_A,
        weight="bold",
        fontsize=fs(13),
    )
    ax.annotate(
        g(sB),
        (t, sB),
        xytext=(9, -17),
        textcoords="offset points",
        color=COLOR_B,
        weight="bold",
        fontsize=fs(13),
    )

    ax.axhline(0, color="gray", linewidth=lw(0.8))
    ax.set_xlim(0, T * 1.05)
    ax.set_ylim(-0.3 * v, 1.5 * NA * v)
    ax.set_ylabel("속력 (m/s)", fontsize=fs(12))
    ax.set_title(
        "속력-시간 그래프  (색칠한 넓이 = 간 거리 $L$, A·B가 같다)",
        fontsize=fs(14),
    )
    ax.tick_params(labelsize=fs(11))
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper center", fontsize=fs(10.5))


# ---------- 3) A와 B 사이의 거리 그래프 ----------
def draw_gap(v, L, T, t):
    ax = ax_gap
    ax.clear()
    tt = np.linspace(0, T, 200)
    gap = (NA - 1) * v * tt * (1 - tt / T)
    gmax = (NA - 1) * L / (2 * NA)
    gap_now = pos_A(v, T, t) - pos_B(v, T, t)

    ax.plot(
        tt, gap, color="tab:green", linewidth=lw(3), label="A와 B 사이의 거리"
    )
    ax.axhline(
        gmax,
        color="tab:red",
        linestyle=":",
        linewidth=lw(1.5),
        label=f"최대 $L/3$ = {g(gmax)} m",
    )
    ax.plot(
        T / 2,
        gmax,
        "*",
        color="gold",
        markeredgecolor="black",
        markersize=ms(17),
    )
    ax.axvline(t, color="gray", linestyle="--", linewidth=lw(1.2))
    ax.plot(t, gap_now, "o", color="tab:green", markersize=ms(10))
    ax.text(
        0.02,
        0.92,
        f"$t$ = {g(t)} s   거리 = {g(gap_now)} m",
        transform=ax.transAxes,
        va="top",
        fontsize=fs(12.5),
    )
    ax.set_xlim(0, T * 1.05)
    ax.set_ylim(-0.1 * gmax, gmax * 1.45)
    ax.set_xlabel("시간 $t$ (s)", fontsize=fs(12))
    ax.set_ylabel("거리 (m)", fontsize=fs(12))
    ax.tick_params(labelsize=fs(11))
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=fs(11))


# ---------- 모범답안 ----------
def answer_summary(v, L, T):
    """왼쪽 상자: 보기별 판정 요약"""
    vB = (NA - 1) * v
    aA = NA * v / T
    aB = (NA - 2) * v / T
    gmax = (NA - 1) * L / (2 * NA)
    return (
        "정답 ③ ㄱ, ㄷ\n"
        f"ㄱ ○  B의 속력 증가 ({g(v)} → {g(vB)} m/s)\n"
        f"ㄴ ×  A는 B의 {g(aA / aB)}배 ({g(aA)} ÷ {g(aB)})\n"
        f"ㄷ ○  최대 거리 L/3 = {g(gmax)} m\n"
        "→ 자세한 풀이는 오른쪽 화면"
    )


def detail_solution(v, L, T):
    """오른쪽 패널: 풀이 과정 (지금 화면의 숫자로 계산)"""
    vA0 = NA * v
    avg = vA0 / 2
    vB = (NA - 1) * v
    aA = vA0 / T
    aB = (vB - v) / T
    t_star = (vA0 - v) / (aA + aB)  # 두 속력이 같아지는 시각 (= T/2)
    xA = vA0 * t_star - 0.5 * aA * t_star**2
    xB = v * t_star + 0.5 * aB * t_star**2
    gmax = xA - xB
    return (
        f"모범답안 · 상세 풀이    (지금 화면의 값  v = {g(v)} m/s,  L = {g(L)} m)\n"
        "\n"
        "[1단계] 주어진 것 정리\n"
        f"   A : P에서 {g(vA0)} m/s  →  Q에서 0 (정지)\n"
        f"   B : P에서 {g(v)} m/s  →  Q에서의 속력 v_B 는 모른다\n"
        f"   두 차는 같은 시간 T 동안 같은 거리 L = {g(L)} m 를 이동\n"
        "\n"
        "[2단계] 걸린 시간 T  (A의 평균 속력 이용)\n"
        f"   평균 속력 = (처음 + 나중) ÷ 2 = ({g(vA0)} + 0) ÷ 2 = {g(avg)} m/s\n"
        f"   거리 = 평균 속력 × 시간  →  {g(L)} = {g(avg)} × T  →  T = {g(T)} s\n"
        "\n"
        "[3단계] B의 나중 속력 v_B  →  ㄱ 판단\n"
        f"   B도 L, T가 같으므로 평균 속력 = L ÷ T = {g(L)} ÷ {g(T)} = {g(L / T)} m/s\n"
        f"   ({g(v)} + v_B) ÷ 2 = {g(L / T)}  →  v_B = {g(vB)} m/s\n"
        f"   {g(v)} → {g(vB)} m/s 로 커졌으므로 B의 속력은 증가  →  ㄱ  ○\n"
        "\n"
        "[4단계] 가속도의 크기  →  ㄴ 판단     (a = 속력 변화 ÷ 시간)\n"
        f"   A : |0 - {g(vA0)}| ÷ {g(T)} = {g(aA)} m/s²\n"
        f"   B : ({g(vB)} - {g(v)}) ÷ {g(T)} = {g(aB)} m/s²\n"
        f"   A ÷ B = {g(aA)} ÷ {g(aB)} = {g(aA / aB)} 배  →  2배가 아니다  →  ㄴ  ×\n"
        "\n"
        "[5단계] 두 차 사이의 최대 거리  →  ㄷ 판단\n"
        "   거리가 가장 클 때 = 두 속력이 같아지는 순간\n"
        f"   {g(vA0)} - {g(aA)}t = {g(v)} + {g(aB)}t  →  t = {g(t_star)} s  ( = T ÷ 2 )\n"
        f"   A의 위치 = {g(vA0)}×{g(t_star)} - 1/2×{g(aA)}×{g(t_star)}² = {g(xA)} m\n"
        f"   B의 위치 = {g(v)}×{g(t_star)} + 1/2×{g(aB)}×{g(t_star)}² = {g(xB)} m\n"
        f"   최대 거리 = {g(xA)} - {g(xB)} = {g(gmax)} m = L ÷ 3 = {g(L)} ÷ 3  →  ㄷ  ○\n"
        "\n"
        "[정답]   ㄱ ○,  ㄴ ×,  ㄷ ○     →     ③ ㄱ, ㄷ"
    )


def apply_hover():
    on = hover["on"]
    result_text.set_alpha(1 if on else 0)
    detail_box.set_visible(on)
    for t_ in detail_lines:
        t_.set_visible(on)
    for ax_ in (ax_road, ax_vt, ax_gap):
        ax_.set_visible(not on)


# ---------- 화면 갱신 ----------
def redraw():
    v, L, T, t = physics()

    for row, key in zip(rows, VARS):
        label, unit, *_ = RANGES[key]
        row["label"].set_text(label)
        if key == "p":
            row["value"].set_text(f"{state[key]:.0f} % · {g(t)} s")
        else:
            row["value"].set_text(f"{g(state[key])} {unit}")

    result_text.set_text(answer_summary(v, L, T))
    lines = detail_solution(v, L, T).split("\n")
    for i, t_ in enumerate(detail_lines):
        t_.set_text(lines[i] if i < len(lines) else "")
    apply_hover()

    draw_road(v, L, T, t)
    draw_vt(v, L, T, t)
    draw_gap(v, L, T, t)
    fig.canvas.draw_idle()


# ---------- 창 크기가 바뀌면 글자·선 크기도 함께 조절 ----------
def on_resize(event):
    w_in, h_in = fig.get_size_inches()
    k = max(0.3, min(w_in / DESIGN_W_IN, h_in / DESIGN_H_IN))
    if abs(k - K["k"]) < 0.01:
        return
    K["k"] = k
    for t_, size in scalable_texts:
        t_.set_fontsize(fs(size))
    for lab, size in scalable_labels:
        lab.set_fontsize(fs(size))
    redraw()


# ---------- +/- 버튼 ----------
def make_click(row_index, direction):
    key = VARS[row_index]
    _, _, step, lo, hi = RANGES[key]

    def on_click(event):
        state[key] = round(min(hi, max(lo, state[key] + direction * step)), 10)
        redraw()

    return on_click


# ---------- 재생 버튼 (시각을 0 → 100%로 자동으로 움직임) ----------
def stop_play():
    if anim["timer"] is not None:
        anim["timer"].stop()
    anim["playing"] = False
    btn_play.label.set_text("재생")


def tick():
    state["p"] = min(100.0, state["p"] + 1.0)
    redraw()
    if state["p"] >= 100.0:
        stop_play()


def toggle_play(event):
    if anim["playing"]:
        stop_play()
        fig.canvas.draw_idle()
        return
    if state["p"] >= 100.0:
        state["p"] = 0.0
    anim["playing"] = True
    btn_play.label.set_text("정지")
    anim["timer"] = fig.canvas.new_timer(interval=40)
    anim["timer"].add_callback(tick)
    anim["timer"].start()


# ----- 3. 문제변경 자리에 재생 버튼 -----
btn_play = Button(fig.add_axes([0.03, 0.540, 0.370, 0.040]), "재생")
btn_play.on_clicked(toggle_play)
style_button(btn_play, 15, BTN_COLOR)
buttons.append(btn_play)

# ----- 4. 변수 조절 -----
y = 0.472
for i in range(3):
    label = add_text(0.03, y + 0.0225, "", 15, weight="bold", va="center")

    btn_minus = Button(fig.add_axes([0.205, y, 0.055, 0.045]), "-")
    btn_plus = Button(fig.add_axes([0.345, y, 0.055, 0.045]), "+")
    btn_minus.on_clicked(make_click(i, -1))
    btn_plus.on_clicked(make_click(i, +1))
    for btn in (btn_minus, btn_plus):
        style_button(btn, 30, SIGN_COLOR)

    buttons += [btn_minus, btn_plus]

    value = add_text(0.3025, y + 0.0225, "", 15, ha="center", va="center")
    rows.append({"label": label, "value": value})
    y -= 0.062


# ---------- 마우스를 모범답안 상자에 올리면 답안과 상세 풀이 표시 ----------
def show_answer_on_hover(event):
    inside = False
    if event.x is not None and event.y is not None:
        fx = event.x / fig.bbox.width
        fy = event.y / fig.bbox.height
        x0, x1, y0, y1 = ANSWER_AREA
        inside = x0 <= fx <= x1 and y0 <= fy <= y1
    if inside != hover["on"]:
        hover["on"] = inside
        apply_hover()
        fig.canvas.draw_idle()


def hide_answer(event):
    if hover["on"]:
        hover["on"] = False
        apply_hover()
        fig.canvas.draw_idle()


fig.canvas.mpl_connect("motion_notify_event", show_answer_on_hover)
fig.canvas.mpl_connect("figure_leave_event", hide_answer)
fig.canvas.mpl_connect("resize_event", on_resize)
fig.canvas.mpl_connect("close_event", lambda e: stop_play())


# ---------- 창을 화면에 꽉 차게 (최대화) ----------
def maximize_window():
    mgr = plt.get_current_fig_manager()
    try:  # TkAgg (Windows)
        mgr.window.state("zoomed")
        return
    except Exception:
        pass
    try:  # TkAgg (Linux)
        mgr.window.attributes("-zoomed", True)
        return
    except Exception:
        pass
    try:  # Qt
        mgr.window.showMaximized()
        return
    except Exception:
        pass
    try:  # 그 밖의 백엔드: 전체 화면
        mgr.full_screen_toggle()
    except Exception:
        pass


# ---------- 최초 실행 ----------
redraw()
fig.canvas.toolbar_visible = False
maximize_window()  # 전체 화면은 키보드 f 키로도 전환할 수 있다
plt.show()
