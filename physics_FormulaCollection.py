import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from matplotlib.widgets import Button

# ---------- 한글 폰트 설정 ----------
for name in ["Malgun Gothic", "AppleGothic", "NanumGothic"]:
    if name in {f.name for f in font_manager.fontManager.ttflist}:
        plt.rcParams["font.family"] = name
        break

plt.rcParams["toolbar"] = "None"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.default"] = "regular"
plt.rcParams["keymap.back"] = []  # ← → 키는 공식 넘기기에 사용
plt.rcParams["keymap.forward"] = []

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
HEADER_COLOR = "#7f7f7f"
READOUT_COLOR = "#1F4E79"
COLOR_A = "tab:red"
COLOR_B = "tab:blue"
COLOR_C = "tab:green"
BOX_FC = "#f7f7f7"
BOX_EC = "#bbbbbb"

GRAV = 10.0  # 중력 가속도 (m/s²), 수능 문제와 같이 10으로 계산


def g(x):
    """숫자를 보기 좋게: 4.0 → 4,  1.50 → 1.5,  0.667 → 0.67"""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def sci(x):
    """큰 수·작은 수를 a×10^b 꼴로 (mathtext)"""
    if x == 0:
        return "0"
    e = int(np.floor(np.log10(abs(x))))
    return rf"${x / 10**e:.2f}\times10^{{{e}}}$"


# ---------- 그래프 공통 도우미 ----------
def finish(ax, xlabel, ylabel, title, legend="best"):
    ax.set_xlabel(xlabel, fontsize=fs(13))
    ax.set_ylabel(ylabel, fontsize=fs(13))
    ax.set_title(title, fontsize=fs(15))
    ax.tick_params(labelsize=fs(11))
    ax.grid(True, alpha=0.3)
    if legend:
        ax.legend(loc=legend, fontsize=fs(11.5))


def mark(ax, x, y, color=COLOR_A):
    ax.plot(
        x,
        y,
        "o",
        color=color,
        markersize=ms(10),
        markeredgecolor="black",
        zorder=8,
    )


def bar_label(ax, x, y, s, color="black"):
    ax.text(
        x,
        y,
        s,
        ha="center",
        va="bottom",
        fontsize=fs(13),
        weight="bold",
        color=color,
    )


# ======================================================================
#  공식 20개
#  각 공식: 제목, 단원, 문제, 핵심 공식 안내, 변수, 그래프 함수, 모범답안 함수
#  변수: (이름, 표시 이름, 단위, 증감 단위, 최솟값, 최댓값, 처음 값)
# ======================================================================
FORMULAS = []


def add_formula(title, area, problem, guide, variables, draw, answer, fix=None):
    FORMULAS.append(
        dict(
            title=title,
            area=area,
            problem=problem,
            guide=guide,
            vars=variables,
            draw=draw,
            answer=answer,
            fix=fix,
            state={v[0]: v[6] for v in variables},
        )
    )


# ---------- 1. 등가속도 운동: 변위 ----------
def draw_1(ax, s):
    v0, a, t = s["v0"], s["a"], s["t"]
    tt = np.linspace(0, 10, 300)
    ax.plot(
        tt,
        v0 * tt + 0.5 * a * tt**2,
        color=COLOR_B,
        linewidth=lw(3),
        label=r"$s=v_0t+\frac{1}{2}at^2$",
    )
    st, vt = v0 * t + 0.5 * a * t * t, v0 + a * t
    tl = np.array([max(0, t - 2), min(10, t + 2)])
    ax.plot(
        tl,
        st + vt * (tl - t),
        "--",
        color=COLOR_A,
        linewidth=lw(2.2),
        label=f"접선의 기울기 = 속도 {g(vt)} m/s",
    )
    ax.axvline(t, color="gray", linestyle=":", linewidth=lw(1.2))
    ax.axhline(0, color="gray", linewidth=lw(0.8))
    mark(ax, t, st)
    ax.set_xlim(0, 10)
    finish(ax, "시간 t (s)", "변위 s (m)", "변위-시간 그래프", "upper left")
    return f"t = {g(t)} s     변위 s = {g(st)} m     속도 v = {g(vt)} m/s"


def answer_1(s):
    v0, a, t = s["v0"], s["a"], s["t"]
    st, vt = v0 * t + 0.5 * a * t * t, v0 + a * t
    return (
        "① 변위  s = v0·t + ½·a·t²\n"
        f"      = {g(v0)}×{g(t)} + ½×({g(a)})×{g(t)}²\n"
        f"      = {g(st)} m\n"
        "② 속도  v = v0 + a·t\n"
        f"      = {g(v0)} + ({g(a)})×{g(t)} = {g(vt)} m/s\n"
        "※ s-t 그래프 접선의 기울기 = 그 순간의 속도"
    )


add_formula(
    "등가속도 직선 운동 (변위와 속도)",
    "물리Ⅰ · 역학",
    "문제) 직선 도로의 기준선을 속력 $v_0$로 통과한\n"
    "자동차가 일정한 가속도 $a$로 운동한다.\n"
    "기준선을 통과하고 $t$초가 지났을 때\n"
    "① 자동차의 변위 $s$는 몇 m인가?\n"
    "② 이때 자동차의 속도 $v$는 몇 m/s인가?\n"
    "\n"
    "(가속도가 음수이면 속도가 줄어드는 운동)",
    r"핵심 공식     $s=v_0t+\frac{1}{2}at^2$     $v=v_0+at$     "
    r"$s$-$t$ 그래프 접선의 기울기 = 속도,  $v$-$t$ 그래프 넓이 = 변위",
    [
        ("v0", r"$v_0$   처음 속력", "m/s", 1, 0, 20, 2),
        ("a", r"$a$   가속도", "m/s²", 1, -5, 5, 2),
        ("t", r"$t$   시간", "s", 1, 0, 10, 4),
    ],
    draw_1,
    answer_1,
)


# ---------- 2. 등가속도 운동: 속도-변위 관계 ----------
def draw_2(ax, s):
    v0, a, d = s["v0"], s["a"], s["s"]
    xs = np.linspace(0, 100, 400)
    vv = np.sqrt(np.clip(v0**2 + 2 * a * xs, 0, None))
    ax.plot(
        xs, vv, color=COLOR_B, linewidth=lw(3), label=r"$v=\sqrt{v_0^2+2as}$"
    )
    if a < 0 and v0**2 / (-2 * a) <= 100:
        stop = v0**2 / (-2 * a)
        ax.axvline(
            stop,
            color=COLOR_A,
            linestyle="--",
            linewidth=lw(1.8),
            label=f"정지 거리 {g(stop)} m",
        )
    v_now = np.sqrt(max(0.0, v0**2 + 2 * a * d))
    mark(ax, d, v_now)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, max(vv.max(), v0, 1) * 1.15)
    finish(ax, "이동 거리 s (m)", "속력 v (m/s)", "속력-이동 거리 그래프")
    return f"s = {g(d)} m 일 때   속력 v = {g(v_now)} m/s"


def answer_2(s):
    v0, a, d = s["v0"], s["a"], s["s"]
    v2 = v0**2 + 2 * a * d
    text = (
        "공식  v² - v0² = 2as  →  v² = v0² + 2as\n"
        f"v² = {g(v0)}² + 2×({g(a)})×{g(d)} = {g(v2)}\n"
    )
    if v2 < 0:
        stop = v0**2 / (-2 * a)
        return text + (
            "v²이 음수 → 그 거리까지 가지 못한다\n"
            f"정지 거리 = v0² ÷ (2|a|) = {g(stop)} m\n"
            "답: 물체는 이미 정지 (v = 0)"
        )
    return text + (
        f"v = √{g(v2)} = {g(np.sqrt(v2))} m/s\n"
        "※ 시간을 모를 때는 이 공식이 가장 빠르다"
    )


add_formula(
    "등가속도 운동 (속도-변위 관계식)",
    "물리Ⅰ · 역학",
    "문제) 속력 $v_0$로 달리던 물체가\n"
    "일정한 가속도 $a$로 운동하여 거리 $s$를 이동하였다.\n"
    "이때 물체의 속력 $v$는 몇 m/s인가?\n"
    "\n"
    "(가속도가 음수이면 감속 운동이며,\n"
    " 정지한 뒤에는 다시 움직이지 않는다고 한다.)",
    r"핵심 공식     $v^2-v_0^2=2as$     "
    r"(시간 $t$가 주어지지 않을 때 사용)     정지 거리 $=\frac{v_0^2}{2|a|}$",
    [
        ("v0", r"$v_0$   처음 속력", "m/s", 2, 0, 30, 10),
        ("a", r"$a$   가속도", "m/s²", 1, -5, 5, -2),
        ("s", r"$s$   이동 거리", "m", 4, 0, 100, 16),
    ],
    draw_2,
    answer_2,
)


# ---------- 3. 뉴턴 운동 제2법칙 (실로 연결된 두 물체) ----------
def draw_3(ax, s):
    mA, mB = s["mA"], s["mB"]
    mbs = np.linspace(0, 10, 300)
    ax.plot(
        mbs,
        mbs * GRAV / (mA + mbs),
        color=COLOR_B,
        linewidth=lw(3),
        label=rf"$a=\frac{{m_B\,g}}{{m_A+m_B}}$   ($m_A$ = {g(mA)} kg)",
    )
    ax.axhline(
        GRAV,
        color="gray",
        linestyle="--",
        linewidth=lw(1.5),
        label="g = 10 m/s² (넘을 수 없다)",
    )
    a = mB * GRAV / (mA + mB)
    mark(ax, mB, a)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    finish(ax, "B의 질량 $m_B$ (kg)", "가속도 a (m/s²)", "B의 질량과 가속도", "lower right")
    return f"가속도 a = {g(a)} m/s²     실의 장력 T = {g(mA * a)} N"


def answer_3(s):
    mA, mB = s["mA"], s["mB"]
    a = mB * GRAV / (mA + mB)
    T = mA * a
    return (
        "① 전체에 뉴턴 제2법칙: (B의 무게) = (전체 질량)×a\n"
        f"   {g(mB)}×10 = ({g(mA)}+{g(mB)})×a  →  a = {g(a)} m/s²\n"
        "② A만 보면: 장력 T = mA × a\n"
        f"   T = {g(mA)}×{g(a)} = {g(T)} N\n"
        f"③ 검산(B): {g(mB * GRAV)} - {g(T)} = {g(mB)}×{g(a)} = {g(mB * a)} N ○"
    )


add_formula(
    "뉴턴 운동 제2법칙 (연결된 물체)",
    "물리Ⅰ · 역학",
    "문제) 마찰이 없는 수평면 위의 물체 A(질량 $m_A$)가\n"
    "도르래에 걸친 실로 물체 B(질량 $m_B$)와\n"
    "연결되어 있다. B는 연직 아래로 매달려 있다.\n"
    "물체를 가만히 놓았을 때\n"
    "① 물체의 가속도의 크기 $a$는?\n"
    "② 실이 A를 당기는 힘(장력) $T$의 크기는?\n"
    "(중력 가속도 g = 10 m/s², 실의 질량 무시)",
    r"핵심 공식     $F=ma$     전체: $m_Bg=(m_A+m_B)a$     "
    r"부분(A): $T=m_Aa$     → 전체로 $a$, 부분으로 $T$",
    [
        ("mA", r"$m_A$   A의 질량", "kg", 1, 1, 10, 3),
        ("mB", r"$m_B$   B의 질량", "kg", 1, 1, 10, 2),
    ],
    draw_3,
    answer_3,
)


# ---------- 4. 충격량 ----------
def draw_4(ax, s):
    m, v, dt = s["m"], s["v"], s["dt"]
    F = m * v / dt
    tt = np.linspace(0, dt, 200)
    ax.fill_between(
        [0, dt], 0, F, color=COLOR_A, alpha=0.2, label="평균 힘 × Δt = 충격량 (넓이)"
    )
    ax.plot(
        tt,
        2 * F * np.sin(np.pi * tt / dt) ** 2,
        color=COLOR_B,
        linewidth=lw(3),
        label="실제 힘 (넓이 같음)",
    )
    ax.plot([0, dt], [F, F], color=COLOR_A, linewidth=lw(2.5), label=f"평균 힘 {g(F)} N")
    ax.set_xlim(0, 0.55)
    ax.set_ylim(0, max(2.3 * F, 2.3 * m * v / 0.1))
    finish(ax, "시간 t (s)", "힘 F (N)", "힘-시간 그래프 (넓이 = 충격량)", "upper right")
    return f"충격량 I = {g(m * v)} N·s     평균 힘 F = {g(F)} N"


def answer_4(s):
    m, v, dt = s["m"], s["v"], s["dt"]
    I = m * v
    return (
        "① 충격량 = 운동량의 변화량\n"
        f"   I = Δp = m×v - 0 = {g(m)}×{g(v)} = {g(I)} N·s\n"
        "② 평균 힘 = 충격량 ÷ 시간\n"
        f"   F = {g(I)} ÷ {g(dt)} = {g(I / dt)} N\n"
        "※ 충격량이 같아도 Δt가 길면 힘이 작다\n"
        "   (에어백, 글러브, 무릎 굽히기)"
    )


add_formula(
    "충격량과 운동량",
    "물리Ⅰ · 역학",
    "문제) 질량 $m$인 공이 속력 $v$로 날아와\n"
    "벽에 수직으로 부딪친 후 정지하였다.\n"
    "벽과 접촉한 시간은 $\\Delta t$이다.\n"
    "① 공이 받은 충격량의 크기는?\n"
    "② 공이 벽으로부터 받은 평균 힘의 크기는?\n"
    "\n"
    "(Δt를 늘리면 힘이 어떻게 변하는지 관찰하자)",
    r"핵심 공식     $I=F\Delta t=\Delta p=mv-mv_0$     "
    r"$F$-$t$ 그래프의 넓이 = 충격량     같은 충격량 → $\Delta t$↑ 이면 $F$↓",
    [
        ("m", r"$m$   공의 질량", "kg", 0.1, 0.1, 2, 0.5),
        ("v", r"$v$   충돌 전 속력", "m/s", 2, 2, 40, 20),
        ("dt", r"$\Delta t$   충돌 시간", "s", 0.02, 0.02, 0.5, 0.1),
    ],
    draw_4,
    answer_4,
)


# ---------- 5. 운동량 보존 (한 덩어리가 되는 충돌) ----------
def draw_5(ax, s):
    m1, v1, m2 = s["m1"], s["v1"], s["m2"]
    v_ = m1 * v1 / (m1 + m2)
    tt = np.linspace(0, 2, 401)
    pA = np.where(tt < 1, m1 * v1, m1 * v_)
    pB = np.where(tt < 1, 0, m2 * v_)
    ax.plot(tt, pA, color=COLOR_A, linewidth=lw(3), label="A의 운동량")
    ax.plot(tt, pB, color=COLOR_B, linewidth=lw(3), label="B의 운동량")
    ax.plot(
        tt,
        pA + pB,
        "--",
        color="black",
        linewidth=lw(2.5),
        label=f"전체 운동량 {g(m1 * v1)} kg·m/s (일정)",
    )
    ax.axvline(1, color="gray", linestyle=":", linewidth=lw(1.5))
    ax.text(1.01, m1 * v1 * 1.2, " 충돌", fontsize=fs(13), color="gray")
    ax.set_xlim(0, 2)
    ax.set_ylim(-0.05 * m1 * v1, m1 * v1 * 1.35)
    finish(ax, "시간 t (s)", "운동량 p (kg·m/s)", "충돌 전후의 운동량", "center left")
    return f"충돌 후 속력 v' = {g(v_)} m/s"


def answer_5(s):
    m1, v1, m2 = s["m1"], s["v1"], s["m2"]
    v_ = m1 * v1 / (m1 + m2)
    e0 = 0.5 * m1 * v1**2
    e1 = 0.5 * (m1 + m2) * v_**2
    return (
        "① 운동량 보존: m1·v1 + 0 = (m1+m2)·v'\n"
        f"   {g(m1)}×{g(v1)} = ({g(m1)}+{g(m2)})×v'  →  v' = {g(v_)} m/s\n"
        f"② 충돌 전 운동 에너지 = ½×{g(m1)}×{g(v1)}² = {g(e0)} J\n"
        f"   충돌 후 운동 에너지 = ½×{g(m1 + m2)}×{g(v_)}² = {g(e1)} J\n"
        f"   손실 = {g(e0 - e1)} J (열·소리로 전환)\n"
        "※ 운동량은 보존, 운동 에너지는 감소"
    )


add_formula(
    "운동량 보존 법칙 (충돌)",
    "물리Ⅰ · 역학",
    "문제) 마찰이 없는 수평면에서 질량 $m_1$인 물체 A가\n"
    "속력 $v_1$로 운동하여 정지해 있는\n"
    "질량 $m_2$인 물체 B와 충돌한 후,\n"
    "두 물체는 한 덩어리가 되어 운동하였다.\n"
    "① 충돌 후 한 덩어리의 속력 $v'$은?\n"
    "② 충돌 과정에서 손실된 운동 에너지는?",
    r"핵심 공식     $m_1v_1+m_2v_2=m_1v_1'+m_2v_2'$     "
    r"외력이 없으면 전체 운동량은 일정     $E_k=\frac{1}{2}mv^2$",
    [
        ("m1", r"$m_1$   A의 질량", "kg", 1, 1, 10, 2),
        ("v1", r"$v_1$   A의 속력", "m/s", 1, 1, 20, 6),
        ("m2", r"$m_2$   B의 질량", "kg", 1, 1, 10, 1),
    ],
    draw_5,
    answer_5,
)


# ---------- 6. 역학적 에너지 보존 (자유 낙하) ----------
def fix_6(s):
    s["h"] = min(s["h"], s["h0"])


def draw_6(ax, s):
    m, h0, h = s["m"], s["h0"], s["h"]
    hs = np.linspace(0, h0, 200)
    ax.plot(hs, m * GRAV * hs, color=COLOR_B, linewidth=lw(3), label="퍼텐셜 에너지 $E_p=mgh$")
    ax.plot(
        hs,
        m * GRAV * (h0 - hs),
        color=COLOR_A,
        linewidth=lw(3),
        label="운동 에너지 $E_k$",
    )
    ax.axhline(
        m * GRAV * h0,
        color="black",
        linestyle="--",
        linewidth=lw(2.2),
        label=f"역학적 에너지 {g(m * GRAV * h0)} J (일정)",
    )
    ax.axvline(h, color="gray", linestyle=":", linewidth=lw(1.5))
    mark(ax, h, m * GRAV * h, COLOR_B)
    mark(ax, h, m * GRAV * (h0 - h), COLOR_A)
    ax.set_xlim(0, h0)
    ax.set_ylim(0, m * GRAV * h0 * 1.3)
    finish(ax, "높이 h (m)", "에너지 (J)", "높이에 따른 에너지", "upper center")
    return (
        f"h = {g(h)} m     Ep = {g(m * GRAV * h)} J     "
        f"Ek = {g(m * GRAV * (h0 - h))} J     v = {g(np.sqrt(2 * GRAV * (h0 - h)))} m/s"
    )


def answer_6(s):
    m, h0, h = s["m"], s["h0"], s["h"]
    E = m * GRAV * h0
    Ep = m * GRAV * h
    Ek = E - Ep
    return (
        f"① 처음 역학적 에너지 = mgh0 = {g(m)}×10×{g(h0)} = {g(E)} J\n"
        f"② 높이 {g(h)} m의 Ep = {g(m)}×10×{g(h)} = {g(Ep)} J\n"
        f"③ Ek = E - Ep = {g(E)} - {g(Ep)} = {g(Ek)} J\n"
        f"④ ½mv² = {g(Ek)}  →  v = √(2g(h0-h)) = {g(np.sqrt(2 * GRAV * (h0 - h)))} m/s\n"
        "※ 속력은 질량과 관계없다"
    )


add_formula(
    "역학적 에너지 보존 (자유 낙하)",
    "물리Ⅰ · 역학",
    "문제) 질량 $m$인 공을 높이 $h_0$에서\n"
    "가만히 놓았다. 공이 높이 $h$를 지날 때\n"
    "① 공의 중력 퍼텐셜 에너지는?\n"
    "② 공의 운동 에너지는?\n"
    "③ 공의 속력은?\n"
    "(중력 가속도 g = 10 m/s², 공기 저항 무시,\n"
    " 지면을 퍼텐셜 에너지의 기준으로 한다.)",
    r"핵심 공식     $E_p=mgh$     $E_k=\frac{1}{2}mv^2$     "
    r"$E_p+E_k$ = 일정     $v=\sqrt{2g(h_0-h)}$",
    [
        ("m", r"$m$   공의 질량", "kg", 1, 1, 10, 2),
        ("h0", r"$h_0$   처음 높이", "m", 5, 5, 50, 20),
        ("h", r"$h$   지금 높이", "m", 1, 0, 50, 15),
    ],
    draw_6,
    answer_6,
    fix_6,
)


# ---------- 7. 탄성 퍼텐셜 에너지 ----------
def draw_7(ax, s):
    k, x, m = s["k"], s["x"], s["m"]
    xs = np.linspace(0, 0.5, 200)
    ax.plot(xs, k * xs, color=COLOR_B, linewidth=lw(3), label=f"탄성력 F = kx  (k = {g(k)} N/m)")
    xf = np.linspace(0, x, 100)
    ax.fill_between(
        xf, 0, k * xf, color=COLOR_A, alpha=0.3, label=r"넓이 = $\frac{1}{2}kx^2$ = 탄성 퍼텐셜 에너지"
    )
    mark(ax, x, k * x)
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, k * 0.55)
    finish(ax, "압축된 길이 x (m)", "탄성력 F (N)", "탄성력-변형 길이 그래프", "upper left")
    Ep = 0.5 * k * x * x
    return f"탄성 퍼텐셜 에너지 = {g(Ep)} J     발사 속력 v = {g(np.sqrt(2 * Ep / m))} m/s"


def answer_7(s):
    k, x, m = s["k"], s["x"], s["m"]
    Ep = 0.5 * k * x * x
    return (
        f"① Ep = ½kx² = ½×{g(k)}×{g(x)}² = {g(Ep)} J\n"
        "② 에너지 보존: ½kx² = ½mv²\n"
        f"   ½×{g(m)}×v² = {g(Ep)}  →  v = {g(np.sqrt(2 * Ep / m))} m/s\n"
        "※ x가 2배 → 에너지 4배 → 속력 2배"
    )


add_formula(
    "탄성 퍼텐셜 에너지 (용수철)",
    "물리Ⅰ · 역학",
    "문제) 용수철 상수가 $k$인 용수철을 $x$만큼\n"
    "압축시킨 후, 질량 $m$인 물체를 붙여 놓았다.\n"
    "용수철이 원래 길이가 되는 순간\n"
    "① 용수철에 저장되었던 탄성 퍼텐셜 에너지는?\n"
    "② 물체의 속력은?\n"
    "\n"
    "(모든 마찰과 용수철의 질량은 무시한다.)",
    r"핵심 공식     $F=kx$     $E_p=\frac{1}{2}kx^2$ ($F$-$x$ 그래프의 넓이)     "
    r"$\frac{1}{2}kx^2=\frac{1}{2}mv^2$",
    [
        ("k", r"$k$   용수철 상수", "N/m", 50, 50, 1000, 200),
        ("x", r"$x$   압축 길이", "m", 0.05, 0.05, 0.5, 0.2),
        ("m", r"$m$   물체 질량", "kg", 0.5, 0.5, 5, 2),
    ],
    draw_7,
    answer_7,
)


# ---------- 8. 열기관의 열효율 ----------
def fix_8(s):
    s["Q2"] = min(s["Q2"], s["Q1"])


def draw_8(ax, s):
    Q1, Q2 = s["Q1"], s["Q2"]
    W = Q1 - Q2
    ax.bar(0, Q1, width=0.55, color=COLOR_A, label="고열원에서 흡수한 열 $Q_1$")
    ax.bar(1, Q2, width=0.55, color=COLOR_B, label="저열원으로 방출한 열 $Q_2$")
    ax.bar(1, W, width=0.55, bottom=Q2, color=COLOR_C, label="외부에 한 일 W")
    bar_label(ax, 0, Q1, f"{g(Q1)} J", COLOR_A)
    bar_label(ax, 1, Q1, f"W {g(W)} J + Q2 {g(Q2)} J", "black")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["흡수한 열", "방출한 열 + 한 일"])
    ax.set_xlim(-0.6, 1.9)
    ax.set_ylim(0, 1200)
    finish(ax, "", "에너지 (J)", "열기관의 에너지 흐름  ($Q_1=W+Q_2$)", "upper right")
    return f"한 일 W = {g(W)} J     열효율 e = {g(W / Q1 * 100)} %"


def answer_8(s):
    Q1, Q2 = s["Q1"], s["Q2"]
    W = Q1 - Q2
    return (
        "① 에너지 보존: Q1 = W + Q2\n"
        f"   W = {g(Q1)} - {g(Q2)} = {g(W)} J\n"
        "② 열효율 e = W ÷ Q1 = 1 - Q2 ÷ Q1\n"
        f"   e = {g(W)} ÷ {g(Q1)} = {g(W / Q1)} ({g(W / Q1 * 100)} %)\n"
        "※ Q2 = 0인 열기관(효율 100 %)은 만들 수 없다\n"
        "   (열역학 제2법칙)"
    )


add_formula(
    "열기관의 열효율",
    "물리Ⅰ · 열역학",
    "문제) 어떤 열기관이 한 번 순환하는 동안\n"
    "고열원에서 열 $Q_1$을 흡수하고\n"
    "저열원으로 열 $Q_2$를 방출한다.\n"
    "① 열기관이 외부에 한 일 $W$는?\n"
    "② 열기관의 열효율 $e$는?",
    r"핵심 공식     $Q_1=W+Q_2$     $e=\frac{W}{Q_1}=1-\frac{Q_2}{Q_1}$     "
    r"열역학 제2법칙: $e<1$",
    [
        ("Q1", r"$Q_1$   흡수한 열", "J", 50, 100, 1000, 400),
        ("Q2", r"$Q_2$   방출한 열", "J", 50, 0, 1000, 300),
    ],
    draw_8,
    answer_8,
    fix_8,
)


# ---------- 9. 특수 상대성 이론: 시간 팽창, 길이 수축 ----------
def draw_9(ax, s):
    b, t0, L0 = s["b"], s["t0"], s["L0"]
    bs = np.linspace(0, 0.99, 400)
    ax.plot(bs, 1 / np.sqrt(1 - bs**2), color=COLOR_A, linewidth=lw(3), label=r"$\gamma=1/\sqrt{1-(v/c)^2}$  (시간 배율)")
    ax.plot(bs, np.sqrt(1 - bs**2), color=COLOR_B, linewidth=lw(3), label=r"$1/\gamma$  (길이 배율)")
    gam = 1 / np.sqrt(1 - b * b)
    mark(ax, b, gam, COLOR_A)
    mark(ax, b, 1 / gam, COLOR_B)
    ax.axvline(b, color="gray", linestyle=":", linewidth=lw(1.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 4)
    finish(ax, "우주선의 속력 v / c", "배율", "속력에 따른 시간 팽창·길이 수축", "upper left")
    return (
        f"γ = {g(gam)}     지구에서 잰 시간 = {g(gam * t0)} 년     "
        f"우주선에서 잰 거리 = {g(L0 / gam)} 광년"
    )


def answer_9(s):
    b, t0, L0 = s["b"], s["t0"], s["L0"]
    gam = 1 / np.sqrt(1 - b * b)
    return (
        f"γ = 1/√(1 - {g(b)}²) = {g(gam)}\n"
        "① 시간 팽창: 움직이는 쪽 시간이 느리게 간다\n"
        f"   지구에서 측정 = γ×t0 = {g(gam)}×{g(t0)} = {g(gam * t0)} 년\n"
        "② 길이 수축: 운동 방향의 길이가 짧아진다\n"
        f"   우주선에서 측정 = L0÷γ = {g(L0)}÷{g(gam)} = {g(L0 / gam)} 광년\n"
        "※ 고유 시간·고유 길이가 기준"
    )


add_formula(
    "특수 상대성 이론 (시간 팽창·길이 수축)",
    "물리Ⅰ · 시공간",
    "문제) 우주선이 지구에 대해 일정한 속력 $v$로\n"
    "지구에서 별까지 운동한다.\n"
    "지구와 별 사이의 거리는 지구에서 $L_0$이고,\n"
    "우주선 안의 시계로 $t_0$의 시간이 흘렀다.\n"
    "① 이 시간을 지구에서 측정하면 몇 년인가?\n"
    "② 우주선에서 측정한 지구-별 거리는?\n"
    "(c: 빛의 속력)",
    r"핵심 공식     $\gamma=\frac{1}{\sqrt{1-(v/c)^2}}$     "
    r"시간 팽창 $t=\gamma t_0$     길이 수축 $L=\frac{L_0}{\gamma}$",
    [
        ("b", r"$v/c$   우주선 속력", "c", 0.05, 0, 0.95, 0.6),
        ("t0", r"$t_0$   고유 시간", "년", 1, 1, 10, 4),
        ("L0", r"$L_0$   고유 길이", "광년", 1, 1, 20, 10),
    ],
    draw_9,
    answer_9,
)


# ---------- 10. 쿨롱 법칙 ----------
COULOMB_K = 9e9


def draw_10(ax, s):
    q1, q2, r = s["q1"], s["q2"], s["r"]
    rs = np.linspace(0.1, 1.0, 300)
    qq = q1 * q2 * 1e-12
    same = qq > 0
    color = COLOR_A if same else COLOR_B
    ax.plot(
        rs,
        COULOMB_K * abs(qq) / rs**2,
        color=color,
        linewidth=lw(3),
        label=r"$F=k\frac{q_1q_2}{r^2}$" + ("  (척력)" if same else "  (인력)" if qq < 0 else ""),
    )
    F = COULOMB_K * abs(qq) / r**2
    mark(ax, r, F, color)
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, max(COULOMB_K * abs(qq) / 0.01 * 0.3, 0.1))
    finish(ax, "두 전하 사이의 거리 r (m)", "전기력의 크기 F (N)", "거리에 따른 전기력", "upper right")
    kind = "척력 (서로 민다)" if same else "인력 (서로 당긴다)" if qq < 0 else "힘 없음"
    return f"F = {g(F)} N     {kind}"


def answer_10(s):
    q1, q2, r = s["q1"], s["q2"], s["r"]
    qq = q1 * q2 * 1e-12
    F = COULOMB_K * abs(qq) / r**2
    kind = "같은 부호 → 척력" if qq > 0 else "다른 부호 → 인력" if qq < 0 else "전하가 0 → 힘 없음"
    return (
        "F = k × |q1·q2| ÷ r²     (k = 9×10^9 N·m²/C²)\n"
        f"  = 9×10^9 × |{g(q1)}×{g(q2)}|×10^-12 ÷ {g(r)}²\n"
        f"  = {g(F)} N   ({kind})\n"
        "※ 거리가 2배 → 힘은 1/4배\n"
        "※ 전하량이 2배 → 힘은 2배"
    )


add_formula(
    "쿨롱 법칙 (전기력)",
    "물리Ⅰ · 전자기",
    "문제) 점전하 $q_1$과 $q_2$가 거리 $r$만큼\n"
    "떨어져 고정되어 있다.\n"
    "① 두 전하 사이에 작용하는 전기력의 크기는?\n"
    "② 이 힘은 인력인가, 척력인가?\n"
    "\n"
    "(쿨롱 상수 k = 9$\\times10^{9}$ N·m²/C², 1 μC = $10^{-6}$ C)",
    r"핵심 공식     $F=k\frac{q_1q_2}{r^2}$     "
    r"같은 부호 → 척력, 다른 부호 → 인력     $F\propto\frac{1}{r^2}$",
    [
        ("q1", r"$q_1$   전하량 1", "μC", 1, -5, 5, 2),
        ("q2", r"$q_2$   전하량 2", "μC", 1, -5, 5, 3),
        ("r", r"$r$   거리", "m", 0.1, 0.1, 1.0, 0.3),
    ],
    draw_10,
    answer_10,
)


# ---------- 11. 옴의 법칙과 전기 저항 ----------
def draw_11(ax, s):
    V, L, A = s["V"], s["L"], s["A"]
    R = L / A  # 비저항 1.0×10^-6 Ω·m, A는 mm² 단위
    Vs = np.linspace(0, 12, 100)
    ax.plot(Vs, Vs / R, color=COLOR_B, linewidth=lw(3), label=f"R = {g(R)} Ω  (기울기 = 1/R)")
    ax.plot(Vs, Vs / 2, color="gray", linestyle="--", linewidth=lw(1.5), label="비교: R = 2 Ω")
    mark(ax, V, V / R)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 20)
    finish(ax, "전압 V (V)", "전류 I (A)", "전류-전압 그래프", "upper left")
    return f"저항 R = {g(R)} Ω     전류 I = {g(V / R)} A     소비 전력 P = {g(V * V / R)} W"


def answer_11(s):
    V, L, A = s["V"], s["L"], s["A"]
    R = L / A
    return (
        "① R = ρ×L÷A = 1.0×10^-6 × {L} ÷ ({A}×10^-6)\n".format(L=g(L), A=g(A))
        + f"     = {g(R)} Ω\n"
        f"② I = V ÷ R = {g(V)} ÷ {g(R)} = {g(V / R)} A\n"
        "※ 길이 2배 → 저항 2배,  굵기 2배 → 저항 1/2배\n"
        "※ I-V 그래프의 기울기가 클수록 저항이 작다"
    )


add_formula(
    "옴의 법칙과 전기 저항",
    "물리Ⅰ · 전자기",
    "문제) 길이 $L$, 단면적 $A$인 니크롬선에\n"
    "전압 $V$를 걸었다.\n"
    "① 니크롬선의 저항 $R$은?\n"
    "② 니크롬선에 흐르는 전류 $I$는?\n"
    "\n"
    "(니크롬선의 비저항 ρ = 1.0$\\times10^{-6}$ Ω·m,\n"
    " 1 mm² = $10^{-6}$ m²)",
    r"핵심 공식     $V=IR$     $R=\rho\frac{L}{A}$     "
    r"$I$-$V$ 그래프의 기울기 $=\frac{1}{R}$",
    [
        ("V", r"$V$   전압", "V", 1, 0, 12, 6),
        ("L", r"$L$   도선 길이", "m", 1, 1, 10, 4),
        ("A", r"$A$   단면적", "mm²", 0.5, 0.5, 5, 2),
    ],
    draw_11,
    answer_11,
)


# ---------- 12. 저항의 연결과 소비 전력 ----------
def draw_12(ax, s):
    R1, R2, V = s["R1"], s["R2"], s["V"]
    I = V / (R1 + R2)
    sP = [I * I * R1, I * I * R2]
    pP = [V * V / R1, V * V / R2]
    xs = [0, 1, 3, 4]
    vals = sP + pP
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    ax.bar(xs, vals, width=0.7, color=colors)
    for x, val in zip(xs, vals):
        bar_label(ax, x, val, f"{g(val)} W")
    ax.set_xticks(xs)
    ax.set_xticklabels(["직렬 R1", "직렬 R2", "병렬 R1", "병렬 R2"])
    ax.bar([], [], color=COLOR_A, label=f"R1 = {g(R1)} Ω")
    ax.bar([], [], color=COLOR_B, label=f"R2 = {g(R2)} Ω")
    ax.set_xlim(-0.7, 4.7)
    ax.set_ylim(0, max(vals) * 1.25)
    finish(ax, "", "소비 전력 P (W)", "직렬 연결 vs 병렬 연결의 소비 전력", "upper left")
    return f"직렬 전체 {g(sum(sP))} W     병렬 전체 {g(sum(pP))} W"


def answer_12(s):
    R1, R2, V = s["R1"], s["R2"], s["V"]
    I = V / (R1 + R2)
    return (
        "[직렬] 전류가 같다 → P = I²R (저항 큰 쪽이 더 소비)\n"
        f"  I = {g(V)}÷({g(R1)}+{g(R2)}) = {g(I)} A\n"
        f"  P1 = {g(I * I * R1)} W,  P2 = {g(I * I * R2)} W\n"
        "[병렬] 전압이 같다 → P = V²/R (저항 작은 쪽이 더 소비)\n"
        f"  P1 = {g(V)}²÷{g(R1)} = {g(V * V / R1)} W,  P2 = {g(V * V / R2)} W\n"
        f"합성 저항: 직렬 {g(R1 + R2)} Ω,  병렬 {g(R1 * R2 / (R1 + R2))} Ω"
    )


add_formula(
    "저항의 연결과 소비 전력",
    "물리Ⅰ · 전자기",
    "문제) 저항값이 $R_1$, $R_2$인 두 저항을\n"
    "(가) 직렬로, (나) 병렬로 연결하여\n"
    "각각 전압 $V$인 전원에 연결하였다.\n"
    "(가), (나)에서 각 저항이 소비하는 전력은?\n"
    "\n"
    "직렬일 때와 병렬일 때\n"
    "어느 저항이 더 밝게(많이) 소비하는지 비교하자.",
    r"핵심 공식     $P=VI=I^2R=\frac{V^2}{R}$     "
    r"직렬 $R=R_1+R_2$     병렬 $\frac{1}{R}=\frac{1}{R_1}+\frac{1}{R_2}$",
    [
        ("R1", r"$R_1$   저항 1", "Ω", 1, 1, 20, 2),
        ("R2", r"$R_2$   저항 2", "Ω", 1, 1, 20, 4),
        ("V", r"$V$   전원 전압", "V", 1, 1, 24, 12),
    ],
    draw_12,
    answer_12,
)


# ---------- 13. 직선 전류에 의한 자기장 ----------
def draw_13(ax, s):
    I, r = s["I"], s["r"]
    rs = np.linspace(1, 20, 300)
    ax.plot(rs, 20 * I / rs, color=COLOR_B, linewidth=lw(3), label=r"$B=k\frac{I}{r}$" + f"  (I = {g(I)} A)")
    B = 20 * I / r  # μT  (k = 2×10^-7, r는 cm)
    mark(ax, r, B)
    ax.set_xlim(0, 20.5)
    ax.set_ylim(0, 20 * I * 1.05)
    finish(ax, "도선으로부터의 거리 r (cm)", "자기장 세기 B (μT)", "거리에 따른 자기장 세기", "upper right")
    return f"B = {g(B)} μT  ( = {sci(B * 1e-6)} T )"


def answer_13(s):
    I, r = s["I"], s["r"]
    B = 2e-7 * I / (r / 100)
    return (
        "B = k × I ÷ r     (k = 2×10^-7 T·m/A)\n"
        f"  = 2×10^-7 × {g(I)} ÷ {g(r / 100)}\n"
        f"  = {g(B * 1e6)} μT\n"
        "※ 방향: 오른손 엄지 = 전류, 감아쥔 네 손가락 = 자기장\n"
        "※ 전류 2배 → B 2배,  거리 2배 → B 1/2배"
    )


add_formula(
    "직선 전류에 의한 자기장",
    "물리Ⅰ · 전자기",
    "문제) 무한히 긴 직선 도선에 세기 $I$인\n"
    "전류가 흐르고 있다.\n"
    "도선으로부터 거리 $r$만큼 떨어진 점 P에서\n"
    "전류에 의한 자기장의 세기는?\n"
    "\n"
    "(k = 2$\\times10^{-7}$ T·m/A, 1 μT = $10^{-6}$ T)",
    r"핵심 공식     $B=k\frac{I}{r}$     "
    r"방향: 오른손 법칙 (엄지 = 전류, 네 손가락 = 자기장)     $B\propto I$, $B\propto\frac{1}{r}$",
    [
        ("I", r"$I$   전류 세기", "A", 1, 1, 10, 2),
        ("r", r"$r$   거리", "cm", 1, 1, 20, 4),
    ],
    draw_13,
    answer_13,
)


# ---------- 14. 전자기 유도 (움직이는 도체 막대) ----------
EMF_R = 2.0  # 회로 저항 (Ω)


def draw_14(ax, s):
    B, L, v = s["B"], s["L"], s["v"]
    vs = np.linspace(0, 20, 100)
    ax.plot(vs, B * L * vs, color=COLOR_B, linewidth=lw(3), label=rf"$\varepsilon=BLv$   (B = {g(B)} T, L = {g(L)} m)")
    mark(ax, v, B * L * v)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, max(B * L * 20 * 1.1, 0.1))
    finish(ax, "막대의 속력 v (m/s)", "유도 기전력 ε (V)", "속력에 따른 유도 기전력", "upper left")
    e = B * L * v
    return f"ε = {g(e)} V     전류 I = {g(e / EMF_R)} A     막대가 받는 자기력 = {g(B * e / EMF_R * L)} N"


def answer_14(s):
    B, L, v = s["B"], s["L"], s["v"]
    e = B * L * v
    I = e / EMF_R
    return (
        "① 1초마다 늘어나는 면적 = L×v → 자속 변화율 = BLv\n"
        f"   ε = {g(B)}×{g(L)}×{g(v)} = {g(e)} V\n"
        f"② I = ε÷R = {g(e)}÷{g(EMF_R)} = {g(I)} A\n"
        f"③ 막대가 받는 힘 F = BIL = {g(B * I * L)} N\n"
        "   (렌츠 법칙: 운동을 방해하는 방향)"
    )


add_formula(
    "전자기 유도 (패러데이 법칙)",
    "물리Ⅰ · 전자기",
    "문제) 세기 $B$인 균일한 자기장 속에서\n"
    "ㄷ자 모양 레일 위에 길이 $L$인 도체 막대를 놓고\n"
    "속력 $v$로 일정하게 움직인다.\n"
    "① 회로에 유도되는 기전력 ε은?\n"
    "② 회로에 흐르는 전류는? (회로 저항 R = 2 Ω)\n"
    "③ 막대가 자기장에서 받는 힘의 크기는?",
    r"핵심 공식     $\varepsilon=-N\frac{\Delta\Phi}{\Delta t}$     "
    r"움직이는 막대 $\varepsilon=BLv$     렌츠 법칙: 자속 변화를 방해",
    [
        ("B", r"$B$   자기장 세기", "T", 0.1, 0.1, 2, 0.5),
        ("L", r"$L$   막대 길이", "m", 0.1, 0.1, 1, 0.4),
        ("v", r"$v$   막대 속력", "m/s", 1, 1, 20, 5),
    ],
    draw_14,
    answer_14,
)


# ---------- 15. 파동의 속력 ----------
def draw_15(ax, s):
    f, lam, t = s["f"], s["lam"], s["t"]
    v = f * lam
    xs = np.linspace(0, 8, 800)
    ax.plot(xs, np.sin(2 * np.pi * xs / lam), color="gray", linestyle="--", linewidth=lw(1.5), label="t = 0 일 때")
    ax.plot(
        xs,
        np.sin(2 * np.pi * (xs / lam - f * t)),
        color=COLOR_B,
        linewidth=lw(3),
        label=f"t = {g(t)} s 일 때",
    )
    xc = lam / 4 + v * t  # 처음 마루가 이동한 위치
    if xc <= 8:
        mark(ax, lam / 4, 1, "white")
        mark(ax, xc, 1)
        ax.annotate(
            "",
            xy=(xc, 1.25),
            xytext=(lam / 4, 1.25),
            arrowprops=dict(arrowstyle="-|>", color=COLOR_A, lw=lw(2.5), mutation_scale=fs(18)),
        )
        ax.text((xc + lam / 4) / 2, 1.33, f"마루 이동 {g(v * t)} m", ha="center", fontsize=fs(12.5), color=COLOR_A)
    ax.set_xlim(0, 8)
    ax.set_ylim(-1.6, 1.7)
    finish(ax, "위치 x (m)", "변위 y (cm)", "파동의 모양 (오른쪽으로 진행)", "lower right")
    return f"파동의 속력 v = {g(v)} m/s     주기 T = {g(1 / f)} s"


def answer_15(s):
    f, lam, t = s["f"], s["lam"], s["t"]
    v = f * lam
    return (
        f"① v = f×λ = {g(f)}×{g(lam)} = {g(v)} m/s\n"
        f"② T = 1÷f = 1÷{g(f)} = {g(1 / f)} s\n"
        f"③ {g(t)}초 동안 마루의 이동 거리 = v×t = {g(v * t)} m\n"
        "※ 한 주기 동안 파동은 한 파장만큼 진행\n"
        "※ 매질은 제자리에서 진동만 한다"
    )


add_formula(
    "파동의 진행 속력",
    "물리Ⅰ · 파동",
    "문제) 진동수 $f$, 파장 $\\lambda$인 파동이\n"
    "+x 방향으로 진행하고 있다.\n"
    "① 파동의 진행 속력 $v$는?\n"
    "② 파동의 주기 $T$는?\n"
    "③ 시간 $t$ 동안 마루는 얼마나 이동하는가?",
    r"핵심 공식     $v=f\lambda=\frac{\lambda}{T}$     $T=\frac{1}{f}$     "
    r"한 주기 동안 한 파장 진행",
    [
        ("f", r"$f$   진동수", "Hz", 0.5, 0.5, 5, 2),
        ("lam", r"$\lambda$   파장", "m", 0.5, 0.5, 4, 2),
        ("t", r"$t$   시간", "s", 0.05, 0, 1, 0.25),
    ],
    draw_15,
    answer_15,
)


# ---------- 16. 빛의 굴절과 전반사 ----------
def draw_16(ax, s):
    n1, n2, th1 = s["n1"], s["n2"], s["th1"]
    r1 = np.radians(th1)
    sin2 = n1 * np.sin(r1) / n2
    ax.fill_between([-1.8, 1.8], 0, 1.3, color=COLOR_B, alpha=0.06 + 0.25 * (n1 - 1))
    ax.fill_between([-1.8, 1.8], -1.3, 0, color=COLOR_B, alpha=0.06 + 0.25 * (n2 - 1))
    ax.text(-1.7, 1.15, f"매질 1  (n1 = {g(n1)})", fontsize=fs(13), va="top")
    ax.text(-1.7, -1.15, f"매질 2  (n2 = {g(n2)})", fontsize=fs(13), va="bottom")
    ax.axhline(0, color="black", linewidth=lw(1.5))
    ax.plot([0, 0], [-1.2, 1.2], color="gray", linestyle="--", linewidth=lw(1.2))
    ax.annotate(
        "",
        xy=(0, 0),
        xytext=(-np.sin(r1), np.cos(r1)),
        arrowprops=dict(arrowstyle="-|>", color=COLOR_A, lw=lw(3), mutation_scale=fs(20)),
    )
    tir = sin2 > 1
    ax.annotate(
        "",
        xy=(np.sin(r1), np.cos(r1)),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="-|>", color=COLOR_A, lw=lw(3 if tir else 1.5), alpha=1 if tir else 0.35, mutation_scale=fs(20)),
    )
    if tir:
        ax.text(0.5, 0.35, "전반사!", fontsize=fs(20), color=COLOR_A, weight="bold")
    else:
        r2 = np.arcsin(sin2)
        ax.annotate(
            "",
            xy=(np.sin(r2), -np.cos(r2)),
            xytext=(0, 0),
            arrowprops=dict(arrowstyle="-|>", color=COLOR_C, lw=lw(3), mutation_scale=fs(20)),
        )
        ax.text(0.5 * np.sin(r2) + 0.08, -0.5 * np.cos(r2), f"θ2 = {np.degrees(r2):.1f}°", fontsize=fs(14), color=COLOR_C, weight="bold", va="center")
    ax.text(-0.5 * np.sin(r1) + 0.08, 0.5 * np.cos(r1), f"θ1 = {g(th1)}°", fontsize=fs(14), color=COLOR_A, weight="bold", va="center")
    if n1 > n2:
        rc = np.arcsin(n2 / n1)
        ax.plot([-np.sin(rc), 0], [np.cos(rc), 0], color="purple", linestyle=":", linewidth=lw(2))
        ax.text(-np.sin(rc) - 0.05, np.cos(rc), f"임계각 {np.degrees(rc):.1f}°", fontsize=fs(12), color="purple", ha="right")
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("빛의 경로 (빨강: 입사·반사, 초록: 굴절)", fontsize=fs(15))
    if tir:
        return "굴절 광선 없음 → 전반사"
    return f"굴절각 θ2 = {np.degrees(np.arcsin(sin2)):.1f}°"


def answer_16(s):
    n1, n2, th1 = s["n1"], s["n2"], s["th1"]
    sin2 = n1 * np.sin(np.radians(th1)) / n2
    text = (
        "① n1·sinθ1 = n2·sinθ2\n"
        f"   sinθ2 = {g(n1)}×sin{g(th1)}° ÷ {g(n2)} = {sin2:.3f}\n"
    )
    if sin2 > 1:
        text += "   sinθ2 > 1 → 굴절 불가 → 전반사\n"
    else:
        text += f"   θ2 = {np.degrees(np.arcsin(sin2)):.1f}°\n"
    if n1 > n2:
        text += f"② 임계각: sinθc = n2÷n1 = {g(n2 / n1)} → θc = {np.degrees(np.arcsin(n2 / n1)):.1f}°\n"
        text += "   θ1 > θc 이면 전반사 (광섬유의 원리)"
    else:
        text += "② n1 ≤ n2 → 전반사는 일어나지 않는다\n"
        text += "   (전반사: 굴절률 큰 쪽 → 작은 쪽일 때만)"
    return text


add_formula(
    "빛의 굴절과 전반사 (스넬 법칙)",
    "물리Ⅰ · 파동",
    "문제) 굴절률 $n_1$인 매질 1에서 굴절률 $n_2$인\n"
    "매질 2로 빛이 입사각 $\\theta_1$로 입사한다.\n"
    "① 굴절각 $\\theta_2$는?\n"
    "② 전반사가 일어날 수 있는가?\n"
    "   일어난다면 임계각은?\n"
    "\n"
    "(입사각을 늘려 가며 전반사를 관찰하자)",
    r"핵심 공식     $n_1\sin\theta_1=n_2\sin\theta_2$     "
    r"임계각 $\sin\theta_c=\frac{n_2}{n_1}$  ($n_1>n_2$)     $\theta_1>\theta_c$ → 전반사",
    [
        ("n1", r"$n_1$   매질 1 굴절률", "", 0.1, 1.0, 2.0, 1.5),
        ("n2", r"$n_2$   매질 2 굴절률", "", 0.1, 1.0, 2.0, 1.0),
        ("th1", r"$\theta_1$   입사각", "°", 5, 0, 85, 30),
    ],
    draw_16,
    answer_16,
)


# ---------- 17. 광전 효과 ----------
H_EV = 0.414  # 플랑크 상수 4.14×10^-15 eV·s × 10^14 Hz


def draw_17(ax, s):
    f, W = s["f"], s["W"]
    f0 = W / H_EV
    fs_ = np.linspace(0, 15, 300)
    ax.plot(fs_, H_EV * fs_ - W, color="gray", linestyle="--", linewidth=lw(1.5), label=f"연장선 (y절편 = -W = -{g(W)} eV)")
    fa = fs_[fs_ >= f0]
    ax.plot(fa, H_EV * fa - W, color=COLOR_B, linewidth=lw(3), label=r"$E_k=hf-W$  (기울기 = h)")
    ax.axvline(f0, color="purple", linestyle=":", linewidth=lw(2), label=f"문턱 진동수 {g(f0)}" + r"$\times10^{14}$ Hz")
    Ek = H_EV * f - W
    mark(ax, f, max(Ek, 0))
    ax.axhline(0, color="black", linewidth=lw(1))
    ax.set_xlim(0, 15)
    ax.set_ylim(-5.5, 6.5)
    finish(ax, r"빛의 진동수 f ($\times10^{14}$ Hz)", "광전자의 최대 운동 에너지 (eV)", "광전 효과 그래프", "upper left")
    if Ek <= 0:
        return "문턱 진동수보다 작다 → 광전자 방출 없음"
    return f"광자 에너지 hf = {g(H_EV * f)} eV     최대 운동 에너지 = {g(Ek)} eV"


def answer_17(s):
    f, W = s["f"], s["W"]
    hf = H_EV * f
    text = f"① 광자 1개의 에너지 E = hf = {g(hf)} eV\n"
    if hf <= W:
        text += (
            f"② hf({g(hf)}) ≤ W({g(W)}) → 광전자가 나오지 않는다\n"
            "   (빛의 세기를 아무리 세게 해도 마찬가지)\n"
        )
    else:
        text += f"② Ek = hf - W = {g(hf)} - {g(W)} = {g(hf - W)} eV\n"
    text += (
        f"③ 문턱 진동수 f0 = W÷h = {g(W / H_EV)}×10^14 Hz\n"
        "※ 빛의 세기 → 광전자 수, 진동수 → 운동 에너지"
    )
    return text


add_formula(
    "광전 효과",
    "물리Ⅰ · 빛과 물질",
    "문제) 일함수가 $W$인 금속판에 진동수 $f$인\n"
    "단색광을 비추었다.\n"
    "① 광자 1개의 에너지는 몇 eV인가?\n"
    "② 방출되는 광전자의 최대 운동 에너지는?\n"
    "③ 이 금속의 문턱 진동수는?\n"
    "\n"
    "(플랑크 상수 h = 4.14$\\times10^{-15}$ eV·s)",
    r"핵심 공식     $E=hf$     $E_k=hf-W$     문턱 진동수 $f_0=\frac{W}{h}$     "
    r"빛의 세기와 광전자 에너지는 무관",
    [
        ("f", r"$f$   진동수", r"$\times10^{14}$ Hz", 0.5, 1, 15, 10),
        ("W", r"$W$   일함수", "eV", 0.5, 1, 5, 2.5),
    ],
    draw_17,
    answer_17,
)


# ---------- 18. 보어의 수소 원자 모형 ----------
def fix_18(s):
    if s["nl"] >= s["nu"]:
        s["nl"] = s["nu"] - 1


def wavelength_color(nm):
    if nm < 380:
        return "purple"
    if nm > 750:
        return "darkred"
    for edge, c in ((450, "violet"), (495, "blue"), (570, "green"), (590, "gold"), (620, "orange")):
        if nm < edge:
            return c
    return "red"


def draw_18(ax, s):
    nu, nl = int(s["nu"]), int(s["nl"])
    for n in range(1, 7):
        E = -13.6 / n**2
        on = n in (nu, nl)
        ax.plot([0, 1], [E, E], color="black" if on else "gray", linewidth=lw(3 if on else 1.5))
        # 위쪽 준위는 촘촘하므로 n = 5, 6 이름표는 오른쪽에 조금 벌려서 쓴다
        x, ha, y = {5: (1.02, "left", -0.75), 6: (1.02, "left", -0.05)}.get(n, (-0.02, "right", E))
        ax.text(x, y, f"n={n}  {E:.2f} eV", ha=ha, va="center", fontsize=fs(12), weight="bold" if on else "normal")
    dE = 13.6 * (1 / nl**2 - 1 / nu**2)
    lam = 1240 / dE
    c = wavelength_color(lam)
    ax.annotate(
        "",
        xy=(0.55, -13.6 / nl**2),
        xytext=(0.55, -13.6 / nu**2),
        arrowprops=dict(arrowstyle="-|>", color=c, lw=lw(4), mutation_scale=fs(24)),
    )
    ax.text(0.6, (-13.6 / nl**2 - 13.6 / nu**2) / 2, f"빛 방출\nΔE = {g(dE)} eV\nλ = {lam:.0f} nm", color=c, fontsize=fs(14), weight="bold", va="center")
    ax.set_xlim(-0.45, 1.45)
    ax.set_ylim(-14.5, 0.8)
    ax.set_xticks([])
    ax.tick_params(labelsize=fs(11))
    ax.set_ylabel("에너지 (eV)", fontsize=fs(13))
    ax.set_title("수소 원자의 에너지 준위", fontsize=fs(15))
    series = {1: "라이먼 계열 (자외선)", 2: "발머 계열 (가시광선)", 3: "파셴 계열 (적외선)"}.get(nl, "적외선 영역")
    return f"n = {nu} → {nl}     ΔE = {g(dE)} eV     λ = {lam:.0f} nm     {series}"


def answer_18(s):
    nu, nl = int(s["nu"]), int(s["nl"])
    Eu, El = -13.6 / nu**2, -13.6 / nl**2
    dE = Eu - El
    return (
        f"① En = -13.6/n² → E{nu} = {g(Eu)} eV,  E{nl} = {g(El)} eV\n"
        f"② ΔE = E{nu} - E{nl} = {g(dE)} eV  (광자 1개의 에너지)\n"
        f"③ λ = hc/ΔE = 1240 ÷ {g(dE)} = {1240 / dE:.0f} nm\n"
        "※ 에너지 차이가 클수록 파장이 짧다\n"
        "※ n=1로 전이 → 자외선, n=2로 전이 → 가시광선"
    )


add_formula(
    "보어의 수소 원자 모형 (선 스펙트럼)",
    "물리Ⅰ · 빛과 물질",
    "문제) 수소 원자의 전자가 양자수 $n$인 궤도에서\n"
    "양자수 $n'$인 궤도로 전이하며 빛을 방출한다.\n"
    "① 방출되는 광자 1개의 에너지는?\n"
    "② 방출되는 빛의 파장은?\n"
    "③ 이 빛은 어떤 영역의 빛인가?\n"
    "\n"
    "(수소 에너지 준위 $E_n$ = -13.6/$n^2$ eV, hc = 1240 eV·nm)",
    r"핵심 공식     $E_n=-\frac{13.6}{n^2}$ eV     "
    r"$\Delta E=|E_n-E_{n'}|=hf=\frac{hc}{\lambda}$     $\lambda$(nm) $=\frac{1240}{\Delta E(eV)}$",
    [
        ("nu", r"$n$   처음 궤도", "", 1, 2, 6, 3),
        ("nl", r"$n'$   나중 궤도", "", 1, 1, 5, 2),
    ],
    draw_18,
    answer_18,
    fix_18,
)


# ---------- 19. 수평으로 던진 물체 ----------
def draw_19(ax, s):
    v0, h = s["v0"], s["h"]
    T = np.sqrt(2 * h / GRAV)
    tt = np.linspace(0, T, 200)
    ax.plot(v0 * tt, h - 0.5 * GRAV * tt**2, color=COLOR_B, linewidth=lw(3), label="포물선 경로")
    tk = np.arange(0, T + 1e-9, 0.5)
    ax.plot(v0 * tk, h - 0.5 * GRAV * tk**2, "o", color=COLOR_A, markersize=ms(7), label="0.5초 간격 위치")
    ax.plot(np.zeros_like(tk), h - 0.5 * GRAV * tk**2, "o", color="gray", markersize=ms(5), alpha=0.6, label="자유 낙하 물체 (비교)")
    R = v0 * T
    mark(ax, R, 0)
    ax.axhline(0, color="saddlebrown", linewidth=lw(3))
    ax.text(R, 3, f"수평 거리 {g(R)} m", ha="center", fontsize=fs(13), color=COLOR_A, weight="bold")
    ax.set_xlim(-3, 125)
    ax.set_ylim(-2, 88)
    finish(ax, "수평 거리 x (m)", "높이 y (m)", "수평으로 던진 물체의 경로", "upper right")
    return f"떨어지는 시간 = {g(T)} s     수평 거리 = {g(R)} m     지면 도달 속력 = {g(np.hypot(v0, GRAV * T))} m/s"


def answer_19(s):
    v0, h = s["v0"], s["h"]
    T = np.sqrt(2 * h / GRAV)
    return (
        "연직: 자유 낙하 (등가속도),  수평: 등속 운동\n"
        f"① h = ½gt² → {g(h)} = 5t² → t = {g(T)} s\n"
        f"② 수평 거리 = v0×t = {g(v0)}×{g(T)} = {g(v0 * T)} m\n"
        f"③ 연직 속력 = g×t = {g(GRAV * T)} m/s\n"
        f"   속력 = √({g(v0)}² + {g(GRAV * T)}²) = {g(np.hypot(v0, GRAV * T))} m/s\n"
        "※ 떨어지는 시간은 v0와 관계없다"
    )


add_formula(
    "수평으로 던진 물체 (포물선 운동)",
    "물리Ⅱ · 역학",
    "문제) 높이 $h$인 곳에서 물체를 수평 방향으로\n"
    "속력 $v_0$로 던졌다.\n"
    "① 물체가 지면에 닿을 때까지 걸리는 시간은?\n"
    "② 물체가 날아간 수평 거리는?\n"
    "③ 지면에 닿는 순간의 속력은?\n"
    "\n"
    "(중력 가속도 g = 10 m/s², 공기 저항 무시)",
    r"핵심 공식     수평: $x=v_0t$     연직: $y=\frac{1}{2}gt^2$     "
    r"$t=\sqrt{\frac{2h}{g}}$     $v=\sqrt{v_0^2+(gt)^2}$",
    [
        ("v0", r"$v_0$   던진 속력", "m/s", 2, 0, 30, 10),
        ("h", r"$h$   높이", "m", 5, 5, 80, 45),
    ],
    draw_19,
    answer_19,
)


# ---------- 20. 질량-에너지 등가 (핵반응) ----------
U_MEV = 931.5  # 1 u 에 해당하는 에너지 (MeV)


def draw_20(ax, s):
    dm, N = s["dm"], s["N"]
    dms = np.linspace(0, 30, 100)
    ax.plot(dms, dms * U_MEV / 1000, color=COLOR_B, linewidth=lw(3), label=r"$E=\Delta mc^2$  (1 u → 931.5 MeV)")
    E = dm * U_MEV / 1000
    mark(ax, dm, E)
    ax.axvline(18.9, color="gray", linestyle=":", linewidth=lw(1.5), label="중수소+삼중수소 핵융합 (0.0189 u)")
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 30)
    finish(ax, r"질량 결손 Δm ($\times10^{-3}$ u)", "방출 에너지 E (MeV)", "질량 결손과 방출 에너지", "upper left")
    return f"반응 1회 E = {g(E)} MeV     반응 {g(N)}몰 전체 = {sci(E * 1.602e-13 * N * 6.02e23)} J"


def answer_20(s):
    dm, N = s["dm"], s["N"]
    E = dm * U_MEV / 1000
    EJ = E * 1.602e-13
    return (
        "① 질량 결손 = (반응 전 질량) - (반응 후 질량)\n"
        f"② E = Δm×c² = {dm / 1000:.3f} u × 931.5 MeV/u = {g(E)} MeV\n"
        f"   = {sci(EJ)} J  (1 MeV = 1.6×10^-13 J)\n"
        f"③ {g(N)}몰 반응: {sci(EJ)} × {g(N)} × 6.02×10^23 = {sci(EJ * N * 6.02e23)} J\n"
        "※ 핵분열·핵융합 모두 질량이 줄어든 만큼 에너지 방출"
    )


add_formula(
    "질량-에너지 등가 (핵반응)",
    "물리Ⅰ · 빛과 물질",
    "문제) 핵반응 과정에서 반응 전후 질량의 차이\n"
    "(질량 결손)가 $\\Delta m$이다.\n"
    "① 핵반응 1회에서 방출되는 에너지는 몇 MeV인가?\n"
    "② 이 반응이 $N$몰 일어날 때 방출되는\n"
    "   전체 에너지는 몇 J인가?\n"
    "\n"
    "(1 u ↔ 931.5 MeV, 1 MeV = 1.6$\\times10^{-13}$ J,\n"
    " 아보가드로수 6.02$\\times10^{23}$)",
    r"핵심 공식     $E=\Delta mc^2$     "
    r"질량 결손 = (반응 전 질량 합) - (반응 후 질량 합)     1 u ↔ 931.5 MeV",
    [
        ("dm", r"$\Delta m$   질량 결손", r"$\times10^{-3}$ u", 1, 1, 30, 19),
        ("N", r"$N$   반응한 양", "몰", 1, 1, 10, 1),
    ],
    draw_20,
    answer_20,
)


# ======================================================================
#  화면 구성
# ======================================================================
current = {"i": 0}
hover = {"on": False}

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
add_box(0.015, 0.925, 0.970, 0.067)  # 1. 제목
add_box(0.015, 0.615, 0.400, 0.302)  # 2. 문제
add_box(0.015, 0.345, 0.400, 0.262)  # 3. 변수 조절
add_box(0.425, 0.072, 0.560, 0.845)  # 4. 그래프 시각화
add_box(0.015, 0.072, 0.400, 0.265)  # 5. 모범답안
add_box(0.015, 0.012, 0.970, 0.052)  # 6. 핵심 공식 안내
ANSWER_AREA = (0.015, 0.415, 0.072, 0.337)  # 마우스를 올리는 영역 (x0, x1, y0, y1)

# ----- 상자 머리말 -----
problem_header = add_text(0.025, 0.905, "", 12, color=HEADER_COLOR, va="top", weight="bold")
add_text(0.025, 0.597, "변수 조절   (- / + 버튼으로 값을 바꿔 보세요)", 12, color=HEADER_COLOR, va="top", weight="bold")
add_text(0.435, 0.905, "그래프 시각화", 12, color=HEADER_COLOR, va="top", weight="bold")
add_text(0.025, 0.327, "모범답안   (이 상자에 마우스를 올리면 보입니다)", 12, color=HEADER_COLOR, va="top", weight="bold")

# ----- 1. 제목 -----
title_text = add_text(0.5, 0.9585, "", 30, ha="center", va="center", weight="bold")

# ----- 2. 문제 -----
problem_text = add_text(
    0.028, 0.875, "", 16, color=PROBLEM_COLOR, weight="bold", va="top", linespacing=1.3
)

# ----- 4. 그래프 -----
readout_text = add_text(0.705, 0.880, "", 16, ha="center", va="top", color=READOUT_COLOR, weight="bold")
ax = fig.add_axes([0.485, 0.130, 0.485, 0.690])

# ----- 5. 모범답안 (마우스를 올리면 보임) -----
hint_text = add_text(
    0.215, 0.205, "?  모범답안 보기\n(마우스를 올려 보세요)", 20, color="#c0c0c0", ha="center", va="center", weight="bold"
)
answer_text = add_text(0.028, 0.290, "", 14.5, va="top", alpha=0, linespacing=1.35)

# ----- 6. 핵심 공식 안내 -----
guide_text = add_text(0.5, 0.038, "", 17, ha="center", va="center")

rows = []
buttons = []


def apply_hover():
    on = hover["on"]
    answer_text.set_alpha(1 if on else 0)
    hint_text.set_alpha(0 if on else 1)


# ---------- 화면 갱신 ----------
def redraw():
    F = FORMULAS[current["i"]]
    s = F["state"]

    title_text.set_text(f"수능 물리 핵심 공식  {current['i'] + 1} / {len(FORMULAS)}   ·   {F['title']}")
    problem_header.set_text(f"문제   [{F['area']}]")
    problem_text.set_text(F["problem"])
    guide_text.set_text(F["guide"])

    for i, row in enumerate(rows):
        used = i < len(F["vars"])
        for btn in row["buttons"]:
            btn.ax.set_visible(used)
            btn.set_active(used)
        if used:
            key, label, unit, *_ = F["vars"][i]
            row["label"].set_text(label)
            row["value"].set_text(f"{g(s[key])} {unit}".strip())
        else:
            row["label"].set_text("")
            row["value"].set_text("")

    answer_text.set_text(F["answer"](s))
    apply_hover()

    ax.clear()
    ax.set_aspect("auto")  # 굴절 그림(16번)의 1:1 비율이 다른 그래프에 남지 않게
    readout_text.set_text(F["draw"](ax, s) or "")
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
    def on_click(event):
        F = FORMULAS[current["i"]]
        if row_index >= len(F["vars"]):
            return
        key, _, _, step, lo, hi, _ = F["vars"][row_index]
        s = F["state"]
        s[key] = round(min(hi, max(lo, s[key] + direction * step)), 10)
        if F["fix"]:
            F["fix"](s)
        redraw()

    return on_click


# ---------- 이전 / 다음 공식 ----------
def change_formula(direction):
    current["i"] = (current["i"] + direction) % len(FORMULAS)
    hover["on"] = False
    redraw()


btn_prev = Button(fig.add_axes([0.022, 0.935, 0.095, 0.047]), "◀ 이전 공식")
btn_next = Button(fig.add_axes([0.883, 0.935, 0.095, 0.047]), "다음 공식 ▶")
btn_prev.on_clicked(lambda e: change_formula(-1))
btn_next.on_clicked(lambda e: change_formula(+1))
for btn in (btn_prev, btn_next):
    style_button(btn, 14, BTN_COLOR)
buttons += [btn_prev, btn_next]

# ----- 3. 변수 조절 (최대 3개) -----
y = 0.505
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
    rows.append({"label": label, "value": value, "buttons": (btn_minus, btn_plus)})
    y -= 0.068


# ---------- 마우스를 모범답안 상자에 올리면 답안 표시 ----------
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


def on_key(event):
    if event.key in ("right", "pagedown"):
        change_formula(+1)
    elif event.key in ("left", "pageup"):
        change_formula(-1)


fig.canvas.mpl_connect("motion_notify_event", show_answer_on_hover)
fig.canvas.mpl_connect("figure_leave_event", hide_answer)
fig.canvas.mpl_connect("resize_event", on_resize)
fig.canvas.mpl_connect("key_press_event", on_key)


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
if __name__ == "__main__":
    redraw()
    fig.canvas.toolbar_visible = False
    maximize_window()  # 전체 화면은 키보드 f 키로도 전환할 수 있다
    plt.show()
