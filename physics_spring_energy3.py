# -*- coding: utf-8 -*-
"""
physics_spring_energy.py
==========================================================
물리학Ⅰ 학습 프로그램
 - 주제 : 용수철의 탄성 퍼텐셜 에너지와 운동 에너지
 - 핵심 공식 : ① F = ma   ② Ep = ½kx²   ③ E처음 = E나중

[실행 방법]
  pip install numpy matplotlib
  python physics_spring_energy.py

[조작 방법]
  - 변수조절 박스의 [-] [+] 버튼 : 질량 mP, mQ, mR, 용수철 상수 k, 중력 가속도 g 조절
  - 끊을 줄 선택 : 줄 a(P–Q 사이) 또는 줄 b(Q–R 사이)
  - [▶ 재생 / ❚❚ 정지] : 줄을 끊은 뒤의 운동을 슬로모션(0.5배속)으로 재생
  - [⟲ 처음부터] : 줄을 끊기 전 상태로 되돌림
  - 모범답안 박스 위에 마우스를 올리면 풀이가 나타남
==========================================================
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.widgets import Button, RadioButtons


# ----------------------------------------------------------
# 0. 한글 글꼴 설정 (Windows: 맑은 고딕 / Mac: AppleGothic / Linux: 나눔고딕)
# ----------------------------------------------------------
def set_korean_font():
    candidates = [
        "Malgun Gothic",
        "AppleGothic",
        "NanumGothic",
        "Noto Sans CJK KR",
        "Noto Sans KR",
        "UnDotum",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = [name, "DejaVu Sans"]
            break
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["toolbar"] = "None"  # 윈도우창 툴바 숨김
    plt.rcParams["mathtext.fontset"] = "dejavusans"


def fmt(v, nd=3):
    """사람이 읽기 좋은 숫자 표기 (불필요한 0 제거)"""
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


# ----------------------------------------------------------
# 1. 기본값 (계산이 정수로 떨어지도록 정한 값) 과 조절 범위
# ----------------------------------------------------------
DEFAULTS = {"mA": 2.0, "mB": 1.0, "mC": 1.0, "k": 100.0, "g": 10.0}

# 화면에 보이는 물체 이름 (내부 키 A, B, C → 상자 P, Q, R)
DISP = {"A": "P", "B": "Q", "C": "R"}

# (이름, 표시 라벨, 최솟값, 최댓값, 한 번에 바뀌는 양, 단위)
VARIABLES = [
    ("mA", "P의 질량  mP", 0.5, 5.0, 0.5, "kg"),
    ("mB", "Q의 질량  mQ", 0.5, 5.0, 0.5, "kg"),
    ("mC", "R의 질량  mR", 0.5, 5.0, 0.5, "kg"),
    ("k", "용수철 상수  k", 50.0, 500.0, 50.0, "N/m"),
    ("g", "중력 가속도  g", 1.0, 20.0, 0.2, "m/s²"),
]

# <보기>에 적힌 값 (문항에 고정된 진술) — 변수를 바꾸면 참/거짓이 달라짐
CLAIM_X0 = 0.4  # ㄱ. 끊기 전 늘어난 길이 40 cm
CLAIM_A = 10.0  # ㄴ. 끊은 직후 P의 가속도 크기 10 m/s²
CLAIM_KE = 4.0  # ㄷ. P의 운동 에너지 최댓값 4 J

CHOICES = {
    frozenset("ㄱ"): "① ㄱ",
    frozenset("ㄴ"): "② ㄴ",
    frozenset("ㄱㄴ"): "③ ㄱ, ㄴ",
    frozenset("ㄴㄷ"): "④ ㄴ, ㄷ",
    frozenset("ㄱㄴㄷ"): "⑤ ㄱ, ㄴ, ㄷ",
}

SLOW = 1  # 재생 배속 (진동이 빨라서 슬로모션, 기존 0.25의 2배)
FRAME_MS = 30  # 애니메이션 프레임 간격(ms)

# 색상
C_TITLE = "#1f3a68"
C_PROB = "#2b6cb0"
C_CTRL = "#2f855a"
C_GRAPH = "#6b46c1"
C_ANS = "#c05621"
C_FORM = "#b7791f"
C_EP, C_UG, C_KE, C_TOT = "#3182ce", "#38a169", "#e53e3e", "#4a5568"


# ----------------------------------------------------------
# 2. 물리 계산
# ----------------------------------------------------------
def solve(p, cut):
    mA, mB, mC, k, g = p["mA"], p["mB"], p["mC"], p["k"], p["g"]
    m_total = mA + mB + mC
    x0 = m_total * g / k  # ① 힘의 평형 : k·x0 = (mA+mB+mC)g
    if cut == "p":  # 줄 a를 끊으면 P만 남음
        M, dropped, name = mA, mB + mC, "P"
    else:  # 줄 b를 끊으면 P+Q가 함께 운동
        M, dropped, name = mA + mB, mC, "P+Q"
    x1 = M * g / k  # 새 평형점 (운동 에너지 최대 위치)
    amp = x0 - x1  # 진폭
    w = np.sqrt(k / M)  # 각진동수
    a0 = (k * x0 - M * g) / M  # ① F = ma (끊은 직후)
    E0 = 0.5 * k * x0**2  # ② 처음 탄성 퍼텐셜 에너지
    E1 = 0.5 * k * x1**2
    Ug1 = M * g * amp  # 평형점에서의 중력 퍼텐셜 에너지
    K_sys = E0 - E1 - Ug1  # ③ 역학적 에너지 보존
    K_A = K_sys * mA / M  # A만의 운동 에너지
    return dict(
        mA=mA,
        mB=mB,
        mC=mC,
        k=k,
        g=g,
        m_total=m_total,
        x0=x0,
        M=M,
        dropped=dropped,
        name=name,
        x1=x1,
        amp=amp,
        w=w,
        a0=a0,
        E0=E0,
        E1=E1,
        Ug1=Ug1,
        K_sys=K_sys,
        K_A=K_A,
        x_top=x1 - amp,
        T=2 * np.pi / w,
    )


def verdict(value, claim):
    return abs(value - claim) < 1e-6 * max(1.0, abs(claim))


# ----------------------------------------------------------
# 3. 프로그램 본체
# ----------------------------------------------------------
class SpringEnergyApp:
    def __init__(self):
        set_korean_font()
        self.p = dict(DEFAULTS)
        self.cut = "p"
        self.t = 0.0
        self.playing = False

        self.fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
        self.fig.patch.set_facecolor("#eef2f7")
        try:
            self.fig.canvas.manager.set_window_title(
                "물리Ⅰ - 용수철에 매달린 세 상자의 에너지"
            )
        except Exception:
            pass

        self._build_boxes()
        self._build_title()
        self._build_problem()
        self._build_controls()
        self._build_graphs()
        self._build_answer()
        self._build_formula()

        self.recompute()
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.anim = FuncAnimation(
            self.fig, self.on_frame, interval=FRAME_MS, cache_frame_data=False
        )

    # ---------- 박스(테두리) ----------
    def _box(self, x, y, w, h, title, color, fill="white"):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.003,rounding_size=0.008",
            transform=self.fig.transFigure,
            fc=fill,
            ec=color,
            lw=2.2,
            zorder=-5,
        )
        self.fig.add_artist(patch)

    def _build_boxes(self):
        self.BOX = {
            "title": (0.010, 0.930, 0.980, 0.060),
            "problem": (0.010, 0.515, 0.375, 0.405),
            "control": (0.010, 0.205, 0.375, 0.300),
            "formula": (0.010, 0.010, 0.375, 0.185),
            "graph": (0.395, 0.365, 0.595, 0.555),
            "answer": (0.395, 0.010, 0.595, 0.345),
        }
        self._box(*self.BOX["title"], None, C_TITLE, fill=C_TITLE)
        self._box(*self.BOX["problem"], "■ 문제", C_PROB)
        self._box(*self.BOX["control"], "■ 변수 조절", C_CTRL)
        self._box(
            *self.BOX["formula"], "■ 핵심 공식 안내", C_FORM, fill="#fffaf0"
        )
        self._box(*self.BOX["graph"], "■ 그래프 시각화", C_GRAPH)
        self._box(*self.BOX["answer"], "■ 모범답안", C_ANS, fill="#fffaf5")

    # ---------- 제목 ----------
    def _build_title(self):
        self.fig.text(
            0.5,
            0.960,
            "용수철에 매달린 세 상자  |  탄성 퍼텐셜 에너지와 운동 에너지",
            ha="center",
            va="center",
            fontsize=24,
            weight="bold",
            color="white",
        )

    # ---------- 문제 ----------
    def _build_problem(self):
        self.prob_text = self.fig.text(
            0.020,
            0.905,
            "",
            va="top",
            ha="left",
            fontsize=14,
            linespacing=1.63,
            color="#1a202c",
        )

    def cut_name(self):
        return "a" if self.cut == "p" else "b"

    def problem_string(self):
        p = self.p
        return (
            f"용수철 상수가 {fmt(p['k'])} N/m인 용수철의 위쪽 끝을 천장에 고정하고,\n"
            f"아래쪽 끝에 상자 P를 연결하였다. P 밑에는 줄 a로 상자 Q를,\n"
            f"Q 밑에는 줄 b로 상자 R을 연결한 뒤 모두 정지 상태로 두었다.\n"
            f"P, Q, R의 질량은 차례로 {fmt(p['mA'])} kg, {fmt(p['mB'])} kg, {fmt(p['mC'])} kg이다.\n"
            f"줄 {self.cut_name()}를 자르자 P는 위아래로 진동하기 시작하였다.\n"
            f"<보기>의 설명 중 옳은 것을 모두 고른 것은?\n"
            f"(단, g = {fmt(p['g'])} m/s²이고, 용수철·줄의 질량과 모든 저항은 무시한다.)\n"
            f"\n"
            f"                         < 보 기 >\n"
            f"ㄱ. 줄을 자르기 전, 용수철은 원래 길이보다 {fmt(CLAIM_X0 * 100)} cm 늘어나 있다.\n"
            f"ㄴ. 줄을 자른 순간, P의 가속도 크기는 {fmt(CLAIM_A)} m/s²이다.\n"
            f"ㄷ. 진동하는 동안 P가 갖는 운동 에너지의 최댓값은 {fmt(CLAIM_KE)} J이다.\n"
            f"①  ㄱ        ②  ㄴ        ③  ㄱ, ㄴ        ④  ㄴ, ㄷ        ⑤  ㄱ, ㄴ, ㄷ"
        )

    def _fit_problem(self, start=14.0, minimum=10.0):
        """문제 글이 문제 박스 안에 모두 들어가도록 글자 크기를 자동 조절
        (PC마다 글꼴 크기가 달라도 박스 밖으로 넘치지 않게 함)"""
        x, y, w, h = self.BOX["problem"]
        right, bottom = x + w - 0.008, y + 0.010
        renderer = self.fig.canvas.get_renderer()
        inv = self.fig.transFigure.inverted()
        size = start
        while size >= minimum:
            self.prob_text.set_fontsize(size)
            bb = inv.transform_bbox(self.prob_text.get_window_extent(renderer))
            if bb.y0 >= bottom and bb.x1 <= right:
                break
            size -= 0.5

    # ---------- 변수 조절 ----------
    def _build_controls(self):
        self.val_texts = {}
        self.buttons = []
        y = 0.475
        for key, label, vmin, vmax, step, unit in VARIABLES:
            self.fig.text(
                0.022, y, label, va="center", fontsize=14.5, color="#22543d"
            )
            self.val_texts[key] = self.fig.text(
                0.200,
                y,
                "",
                va="center",
                ha="right",
                fontsize=15,
                weight="bold",
                color="#1a202c",
            )
            self.fig.text(
                0.205, y, unit, va="center", fontsize=13, color="#4a5568"
            )
            ax_m = self.fig.add_axes([0.268, y - 0.016, 0.042, 0.032])
            ax_p = self.fig.add_axes([0.318, y - 0.016, 0.042, 0.032])
            b_m = Button(ax_m, "－", color="#fed7d7", hovercolor="#feb2b2")
            b_p = Button(ax_p, "＋", color="#c6f6d5", hovercolor="#9ae6b4")
            for b in (b_m, b_p):
                b.label.set_fontsize(16)
                b.label.set_weight("bold")
            b_m.on_clicked(self._make_step(key, -step, vmin, vmax))
            b_p.on_clicked(self._make_step(key, +step, vmin, vmax))
            self.buttons += [b_m, b_p]
            y -= 0.042

        # 자를 줄 선택
        self.fig.text(
            0.022,
            0.245,
            "자를 줄",
            va="center",
            fontsize=14.5,
            color="#22543d",
        )
        ax_r = self.fig.add_axes(
            [0.075, 0.214, 0.105, 0.062], facecolor="#f0fff4"
        )
        self.radio = RadioButtons(ax_r, ("줄 a (P–Q)", "줄 b (Q–R)"), active=0)
        for lb in self.radio.labels:
            lb.set_fontsize(13.5)
        self.radio.on_clicked(self.on_radio)

        ax_play = self.fig.add_axes([0.195, 0.222, 0.085, 0.046])
        ax_rew = self.fig.add_axes([0.288, 0.222, 0.085, 0.046])
        self.b_play = Button(
            ax_play, "▶ 재생", color="#bee3f8", hovercolor="#90cdf4"
        )
        self.b_rew = Button(
            ax_rew, "⟲ 처음부터", color="#e2e8f0", hovercolor="#cbd5e0"
        )
        for b in (self.b_play, self.b_rew):
            b.label.set_fontsize(14)
            b.label.set_weight("bold")
        self.b_play.on_clicked(self.on_play)
        self.b_rew.on_clicked(self.on_rewind)

    def _make_step(self, key, delta, vmin, vmax):
        def handler(_event):
            new = round(self.p[key] + delta, 2)
            if vmin - 1e-9 <= new <= vmax + 1e-9:
                self.p[key] = new
                self.recompute()

        return handler

    # ---------- 그래프 ----------
    def _build_graphs(self):
        # (가) 장치 그림
        self.ax_sch = self.fig.add_axes([0.425, 0.405, 0.140, 0.470])
        self.ax_sch.set_xticks([])
        self.ax_sch.set_facecolor("#fbfbfe")
        self.ax_sch.set_ylabel("천장에서부터의 위치 (m)", fontsize=12)
        self.ax_sch.set_xlim(-1, 1)
        self.ax_sch.plot([-1, 1], [0, 0], color="#2d3748", lw=5)
        (self.spring_line,) = self.ax_sch.plot([], [], color="#4a5568", lw=2)
        (self.str_p,) = self.ax_sch.plot([], [], color="#975a16", lw=2)
        (self.str_q,) = self.ax_sch.plot([], [], color="#975a16", lw=2)
        self.rects, self.rlabels = {}, {}
        colors = {"A": "#90cdf4", "B": "#fbd38d", "C": "#fbb6ce"}
        for nm in "ABC":
            r = Rectangle((0, 0), 1, 1, fc=colors[nm], ec="#1a202c", lw=1.8)
            self.ax_sch.add_patch(r)
            self.rects[nm] = r
            self.rlabels[nm] = self.ax_sch.text(
                0,
                0,
                DISP[nm],
                ha="center",
                va="center",
                fontsize=15,
                weight="bold",
                clip_on=True,
            )
        self.line_eq = self.ax_sch.axhline(0, color=C_KE, ls="--", lw=1.3)
        self.txt_eq = self.ax_sch.text(
            -0.98,
            0,
            "새 평형점",
            ha="left",
            va="bottom",
            fontsize=10,
            color=C_KE,
        )
        self.line_nat = self.ax_sch.axhline(0, color="#a0aec0", ls=":", lw=1.3)
        self.txt_nat = self.ax_sch.text(
            0.98,
            0,
            "원래 길이",
            ha="right",
            va="bottom",
            fontsize=10,
            color="#718096",
        )
        self.cut_mark = self.ax_sch.text(
            0,
            0,
            "",
            ha="left",
            va="center",
            fontsize=12,
            color="#c53030",
            weight="bold",
            clip_on=True,
        )
        self.sch_title = self.ax_sch.set_title("", fontsize=13)

        # (나) 위치에 따른 에너지 그래프
        self.ax_en = self.fig.add_axes([0.605, 0.435, 0.225, 0.450])
        self.ax_en.set_title(
            "(나) 용수철 늘어난 길이 x 에 따른 에너지", fontsize=13
        )
        self.ax_en.set_xlabel(
            "용수철이 늘어난 길이 x (m)   (음수 = 압축)", fontsize=12
        )
        self.ax_en.set_ylabel("에너지 (J)", fontsize=12)
        self.ax_en.grid(alpha=0.3)
        (self.cv_ep,) = self.ax_en.plot(
            [], [], color=C_EP, lw=2.5, label="탄성 퍼텐셜  ½kx²"
        )
        (self.cv_ug,) = self.ax_en.plot(
            [], [], color=C_UG, lw=2.5, label="중력 퍼텐셜  Mgh"
        )
        (self.cv_ke,) = self.ax_en.plot(
            [], [], color=C_KE, lw=2.5, label="운동 에너지  ½Mv²"
        )
        (self.cv_tot,) = self.ax_en.plot(
            [], [], color=C_TOT, lw=2, ls="--", label="역학적 에너지(일정)"
        )
        self.dots = [
            self.ax_en.plot([], [], "o", color=c, ms=10, mec="k")[0]
            for c in (C_EP, C_UG, C_KE)
        ]
        self.vline_now = self.ax_en.axvline(0, color="#718096", lw=1)
        self.vline_eq = self.ax_en.axvline(0, color=C_KE, ls=":", lw=1.5)
        self.ax_en.legend(
            loc="upper center", fontsize=10.5, ncol=2, framealpha=0.9
        )

        # (다) 에너지 막대
        self.ax_bar = self.fig.add_axes([0.868, 0.435, 0.112, 0.450])
        self.ax_bar.set_title("(다) 지금 이 순간의 에너지", fontsize=13)
        self.bars = self.ax_bar.bar(
            ["탄성\n퍼텐셜", "중력\n퍼텐셜", "운동\n에너지", "역학적\n에너지"],
            [0, 0, 0, 0],
            color=[C_EP, C_UG, C_KE, C_TOT],
        )
        self.ax_bar.tick_params(axis="x", labelsize=10.5)
        self.bar_txt = [
            self.ax_bar.text(i, 0, "", ha="center", va="bottom", fontsize=10.5)
            for i in range(4)
        ]

        self.info_text = self.fig.text(
            0.425, 0.372, "", fontsize=12, color="#2d3748", va="bottom"
        )

    # ---------- 모범답안 ----------
    def _build_answer(self):
        self.ax_ans = self.fig.add_axes([0.402, 0.015, 0.583, 0.328])
        self.ax_ans.axis("off")
        self.ax_ans.set_facecolor("none")
        self.ans_text = self.ax_ans.text(
            0.0,
            1.0,
            "",
            va="top",
            ha="left",
            fontsize=14.5,
            linespacing=1.55,
            color="#1a202c",
            transform=self.ax_ans.transAxes,
            visible=False,
        )
        self.ans_cover = self.ax_ans.text(
            0.5,
            0.5,
            "모범답안이 숨겨져 있습니다.\n\n"
            "먼저 직접 풀어 본 뒤, 이 상자 위에 마우스를 올려 확인하세요.",
            ha="center",
            va="center",
            fontsize=17,
            color="#c05621",
            transform=self.ax_ans.transAxes,
        )

    def answer_string(self, s):
        v1 = verdict(s["x0"], CLAIM_X0)
        v2 = verdict(s["a0"], CLAIM_A)
        v3 = verdict(s["K_A"], CLAIM_KE)
        trues = frozenset(c for c, v in zip("ㄱㄴㄷ", (v1, v2, v3)) if v)
        choice = CHOICES.get(
            trues, "해당 선택지 없음 (아래 보기별 판정을 참고)"
        )
        ox = lambda v: "참 ○" if v else "거짓 ×"
        M, nm = s["M"], s["name"]
        lines = [
            f"정답 : {choice}        [ ㄱ {ox(v1)} ,  ㄴ {ox(v2)} ,  ㄷ {ox(v3)} ]",
            "[1단계] 자르기 전 – 힘의 평형 (F = ma 에서 a = 0)",
            f"     k·x₀ = (mP+mQ+mR)·g  →  {fmt(s['k'])}·x₀ = {fmt(s['m_total'])}×{fmt(s['g'])}"
            f"  →  x₀ = {fmt(s['x0'])} m = {fmt(s['x0'] * 100)} cm   ⇒ ㄱ ({fmt(CLAIM_X0 * 100)} cm) {ox(v1)}",
            f"[2단계] 자른 순간 – 용수철 길이는 순간적으로 그대로 → 탄성력 k·x₀ = {fmt(s['k'] * s['x0'])} N 유지",
            f"     {nm} : k·x₀ − M·g = M·a  →  {fmt(s['k'] * s['x0'])} − {fmt(M * s['g'])} = {fmt(M)}·a"
            f"  →  a = {fmt(s['a0'])} m/s² (위쪽)   ⇒ ㄴ ({fmt(CLAIM_A)} m/s²) {ox(v2)}",
            "[3단계] 운동 에너지 최대 위치 = 힘의 합이 0인 새 평형점",
            f"     k·x₁ = M·g  →  x₁ = {fmt(s['x1'])} m ,  {nm}는 x₀ − x₁ = {fmt(s['amp'])} m 만큼 올라간다",
            "[4단계] 역학적 에너지 보존 (E처음 = E나중), 처음 위치를 중력 퍼텐셜 에너지 기준(0)으로",
            f"     ½k·x₀² = ½k·x₁² + M·g·(x₀ − x₁) + Ek  →  {fmt(s['E0'])} = {fmt(s['E1'])} + {fmt(s['Ug1'])} + Ek"
            f"  →  Ek = {fmt(s['K_sys'])} J",
        ]
        if self.cut == "q":
            lines.append(
                f"     P와 Q는 같은 속력이므로 P의 운동 에너지 = Ek × mP/(mP+mQ) = {fmt(s['K_A'])} J"
            )
        lines.append(
            f"     ⇒ ㄷ ({fmt(CLAIM_KE)} J) {ox(v3)}"
            f"     [빠른 검산] Ek = ½k(x₀ − x₁)² = ½×{fmt(s['k'])}×{fmt(s['amp'])}² = {fmt(0.5 * s['k'] * s['amp'] ** 2)} J"
        )
        return "\n".join(lines)

    # ---------- 핵심 공식 ----------
    def _build_formula(self):
        items = [
            (
                "①  뉴턴 운동 법칙",
                r"$F = ma$",
                "자르기 전 a = 0 (평형) / 자른 순간 가속도",
            ),
            (
                "②  탄성 퍼텐셜 에너지",
                r"$E_p = \frac{1}{2}kx^2$",
                "x : 원래 길이에서 늘어나거나 줄어든 길이",
            ),
            (
                "③  역학적 에너지 보존",
                "E처음 = E나중",
                "탄성 퍼텐셜 + 중력 퍼텐셜 + 운동 에너지 = 일정",
            ),
        ]
        y = 0.168
        for name, formula, note in items:
            self.fig.text(
                0.022,
                y,
                name,
                fontsize=14,
                weight="bold",
                color="#744210",
                va="center",
            )
            self.fig.text(
                0.148, y, formula, fontsize=17, color="#1a202c", va="center"
            )
            self.fig.text(
                0.240, y, note, fontsize=9.8, color="#4a5568", va="center"
            )
            y -= 0.046
        self.fig.text(
            0.022,
            0.030,
            "Tip : 운동 에너지 최대 = 힘의 합이 0인 평형점 (kx = Mg),  Ek최대 = ½k(진폭)²",
            fontsize=12,
            color="#c05621",
            va="center",
            weight="bold",
        )

    # ------------------------------------------------------
    # 4. 상태 갱신
    # ------------------------------------------------------
    def recompute(self):
        """변수가 바뀌면 처음 상태로 되돌리고 모든 박스를 다시 그림"""
        self.t = 0.0
        self.playing = False
        self.b_play.label.set_text("▶ 재생")
        self.s = solve(self.p, self.cut)
        s = self.s

        for key, *_ in VARIABLES:
            self.val_texts[key].set_text(fmt(self.p[key], 2))
        self.prob_text.set_text(self.problem_string())
        self._fit_problem()
        self.ans_text.set_text(self.answer_string(s))

        # 장치 그림의 축척
        S = max(s["x0"], 0.3)
        self.S = S
        self.L0 = max(1.0 * S, -s["x_top"] + 0.35 * S)
        self.blk = 0.22 * S
        self.slen = 0.25 * S
        bottom = -(self.L0 + s["x0"] + 3 * self.blk + 2 * self.slen) - 0.25 * S
        self.ax_sch.set_ylim(bottom, 0.12 * S)
        y_eq = -(self.L0 + s["x1"])
        self.line_eq.set_ydata([y_eq, y_eq])
        self.txt_eq.set_y(y_eq)
        self.line_nat.set_ydata([-self.L0, -self.L0])
        self.txt_nat.set_y(-self.L0)

        # 에너지 곡선
        if s["amp"] > 1e-9:
            xs = np.linspace(s["x_top"], s["x0"], 300)
        else:
            xs = np.linspace(s["x0"] - 0.01, s["x0"] + 0.01, 10)
        ep = 0.5 * s["k"] * xs**2
        ug = s["M"] * s["g"] * (s["x0"] - xs)
        ke = s["E0"] - ep - ug
        self.cv_ep.set_data(xs, ep)
        self.cv_ug.set_data(xs, ug)
        self.cv_ke.set_data(xs, np.clip(ke, 0, None))
        self.cv_tot.set_data(xs, np.full_like(xs, s["E0"]))
        pad = 0.05 * (xs[-1] - xs[0])
        self.ax_en.set_xlim(xs[0] - pad, xs[-1] + pad)
        self.ax_en.set_ylim(0, s["E0"] * 1.35 + 1e-9)
        self.vline_eq.set_xdata([s["x1"], s["x1"]])
        self.ax_bar.set_ylim(0, s["E0"] * 1.25 + 1e-9)

        self.draw_state()
        self.fig.canvas.draw_idle()

    def state_at(self, t):
        s = self.s
        if t <= 0:
            return s["x0"], 0.0
        x = s["x1"] + s["amp"] * np.cos(s["w"] * t)
        v = s["amp"] * s["w"] * abs(np.sin(s["w"] * t))
        return x, v

    def draw_state(self):
        s = self.s
        t = self.t
        x, v = self.state_at(t)
        S, blk, slen, L0 = self.S, self.blk, self.slen, self.L0

        # 용수철 (지그재그)
        y_end = -(L0 + x)
        n = 16
        ys = np.linspace(0, y_end, 2 * n + 3)
        xs = np.zeros_like(ys)
        xs[2:-2] = np.where(np.arange(2 * n - 1) % 2 == 0, 0.22, -0.22)
        self.spring_line.set_data(xs, ys)

        # A
        yA = y_end
        self.rects["A"].set_bounds(-0.35, yA - blk, 0.7, blk)
        # 자르기 전 Q, R 위치 (줄을 자르면 떨어진 물체는 자유 낙하)
        drop = 0.5 * s["g"] * t**2 if t > 0 else 0.0
        yB0 = yA - blk - slen
        yC0 = yB0 - blk - slen
        if self.cut == "p":
            yB = (-(L0 + s["x0"]) - blk - slen) - drop
            yC = yB - blk - slen
        else:
            yB = yB0
            yC = (-(L0 + s["x0"]) - 2 * blk - 2 * slen) - drop
        self.rects["B"].set_bounds(-0.30, yB - blk, 0.6, blk)
        self.rects["C"].set_bounds(-0.25, yC - blk, 0.5, blk)
        for nm, yy in (("A", yA), ("B", yB), ("C", yC)):
            self.rlabels[nm].set_position((0, yy - blk / 2))

        # 줄 a, b
        if t > 0 and self.cut == "p":
            self.str_p.set_data([], [])
            self.cut_mark.set_text("× 줄 a 자름")
            self.cut_mark.set_position((0.05, yA - blk - slen * 0.5))
        else:
            self.str_p.set_data([0, 0], [yA - blk, yB])
        if t > 0 and self.cut == "q":
            self.str_q.set_data([], [])
            self.cut_mark.set_text("× 줄 b 자름")
            self.cut_mark.set_position((0.05, yB - blk - slen * 0.5))
        else:
            self.str_q.set_data([0, 0], [yB - blk, yC])
        if t <= 0:
            self.cut_mark.set_text("")

        stage = "자르기 전" if t <= 0 else f"t = {t:.2f} s"
        self.sch_title.set_text(f"(가) 장치 모습  ·  {stage}")

        # 에너지
        ep = 0.5 * s["k"] * x**2
        ug = s["M"] * s["g"] * (s["x0"] - x)
        ke = max(s["E0"] - ep - ug, 0.0)
        for dot, val in zip(self.dots, (ep, ug, ke)):
            dot.set_data([x], [val])
        self.vline_now.set_xdata([x, x])
        for bar, txt, val in zip(
            self.bars, self.bar_txt, (ep, ug, ke, s["E0"])
        ):
            bar.set_height(val)
            txt.set_position((bar.get_x() + bar.get_width() / 2, val))
            txt.set_text(fmt(val, 2))

        self.info_text.set_text(
            f"현재  x = {fmt(x)} m   |   속력 v = {fmt(v)} m/s   |   움직이는 물체 : {s['name']} (M = {fmt(s['M'])} kg)"
            f"   |   주기 T = {fmt(s['T'])} s   |   재생 {fmt(SLOW)}배속   |   중력 퍼텐셜 기준 : 처음 위치"
        )

    # ------------------------------------------------------
    # 5. 이벤트 처리
    # ------------------------------------------------------
    def on_frame(self, _frame):
        if self.playing:
            self.t += FRAME_MS / 1000.0 * SLOW
            self.draw_state()
        return []

    def on_play(self, _event):
        self.playing = not self.playing
        self.b_play.label.set_text("❚❚ 정지" if self.playing else "▶ 재생")
        self.fig.canvas.draw_idle()

    def on_rewind(self, _event):
        self.t = 0.0
        self.playing = False
        self.b_play.label.set_text("▶ 재생")
        self.draw_state()
        self.fig.canvas.draw_idle()

    def on_radio(self, label):
        self.cut = "p" if label.startswith("줄 a") else "q"
        self.recompute()

    def on_hover(self, event):
        inside = event.inaxes is self.ax_ans
        if inside != self.ans_text.get_visible():
            self.ans_text.set_visible(inside)
            self.ans_cover.set_visible(not inside)
            self.fig.canvas.draw_idle()


# ----------------------------------------------------------
# 6. 실행 (창을 화면 가득 확대)
# ----------------------------------------------------------
def maximize_window():
    mng = plt.get_current_fig_manager()
    for attempt in (
        lambda: mng.window.state("zoomed"),  # TkAgg (Windows)
        lambda: mng.window.showMaximized(),  # QtAgg
        lambda: mng.window.maximize(),  # GTK
        lambda: mng.resize(1920, 1080),
    ):
        try:
            attempt()
            return
        except Exception:
            continue


def main():
    app = SpringEnergyApp()
    maximize_window()
    plt.show()
    return app


if __name__ == "__main__":
    main()
