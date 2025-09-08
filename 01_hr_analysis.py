import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from matplotlib import font_manager
import os, re

st.set_page_config(page_title="업무만족도 대시보드", layout="wide")
sns.set(style="whitegrid")  # 폰트 지정은 rcParams로만

# =============== (A) 폰트 로더: '있는 폰트'만 적용 + 번들폰트 지원 =================
def set_korean_font():
    # 1) 레포에 같이 넣은 폰트 우선 (권장: ./fonts/NotoSansKR-Regular.otf)
    for p in ["./fonts/NotoSansKR-Regular.otf", "./fonts/NanumGothic.ttf"]:
        if os.path.exists(p):
            font_manager.fontManager.addfont(p)
            fam = font_manager.FontProperties(fname=p).get_name()
            mpl.rcParams["font.family"] = fam
            mpl.rcParams["axes.unicode_minus"] = False
            return "bundled:" + fam

    # 2) 시스템에 설치된 폰트 중 한국어 지원 후보만 선택
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for fam in ["Malgun Gothic", "AppleGothic", "NanumGothic", "Noto Sans KR", "Noto Sans CJK KR"]:
        if fam in installed:
            mpl.rcParams["font.family"] = fam
            mpl.rcParams["axes.unicode_minus"] = False
            return "system:" + fam

    # 3) 못 찾으면, 폰트는 건드리지 않고 마이너스만 보호 (여긴 한글이 □로 나올 수 있음)
    mpl.rcParams["axes.unicode_minus"] = False
    return "fallback:none"

FONT_PICKED = set_korean_font()

# =============== (B) 인코딩 오토검출 로더: '한글비율'로 가장 좋은 것을 선택 =========
HANGUL_RE = re.compile(r"[가-힣]")
def hangul_ratio(df, sample_cols=5, sample_rows=100):
    if df is None or df.empty: return 0.0
    cols = df.columns[:sample_cols]
    txt = " ".join(str(x) for x in df[cols].head(sample_rows).values.flatten())
    if not txt: return 0.0
    total = len(txt)
    if total == 0: return 0.0
    hits = len(HANGUL_RE.findall(txt))
    return hits / total

@st.cache_data
def smart_read_csv(path="HR Data.csv"):
    tried = []
    best_df, best_enc, best_score = None, None, -1
    for enc in ("utf-8-sig", "cp949", "utf-8"):
        try:
            df = pd.read_csv(path, encoding=enc)
            score = hangul_ratio(df)
            tried.append((enc, score, "ok"))
            if score > best_score:
                best_df, best_enc, best_score = df, enc, score
        except Exception as e:
            tried.append((enc, 0.0, f"error:{type(e).__name__}"))
    return best_df if best_df is not None else pd.DataFrame(), best_enc, best_score, tried

df, ENC_PICKED, ENC_SCORE, ENC_TRIED = smart_read_csv("HR Data.csv")

# =============== (C) 디버그 표기 (무조건 화면에 표시) ==============================
st.caption(f"🔤 선택된 인코딩: **{ENC_PICKED or 'detect-failed'}** (한글비율 {ENC_SCORE:.3f}) · 폰트: **{FONT_PICKED}**")
with st.expander("인코딩 시도 결과 열기"):
    st.write(pd.DataFrame(ENC_TRIED, columns=["encoding","hangul_ratio","status"]))

# =============== 안전 가드: 인코딩 실패/모지바케 탐지 =============================
if df.empty:
    st.error("CSV를 읽지 못했습니다. UTF-8(또는 UTF-8-SIG)로 저장해서 다시 올려보세요.")
    st.stop()

# 모지바케(깨진문자) 흔적이 많으면 즉시 경고
sample_text = " ".join(str(x) for x in df.head(50).values.flatten())
if ("�" in sample_text) or ("ì" in sample_text and " 가" not in sample_text):  # 흔한 깨짐 패턴
    st.warning("텍스트가 이미 깨져 보입니다. 원본 CSV 인코딩이 맞는지 확인해 주세요. (엑셀 → 'CSV UTF-8' 권장)")

# ============================ KPI ==============================
st.title("업무만족도 분석 대시보드")
n = len(df)
k1,k2,k3,k4 = st.columns(4)
k1.metric("전체 직원 수", f"{n:,}명")
if "업무만족도" in df.columns:
    k2.metric("평균 업무만족도", f"{pd.to_numeric(df['업무만족도'], errors='coerce').mean():.2f}")
if "업무환경만족도" in df.columns:
    k3.metric("평균 업무환경만족도", f"{pd.to_numeric(df['업무환경만족도'], errors='coerce').mean():.2f}")
if "월급여" in df.columns:
    s = pd.to_numeric(df["월급여"].astype(str).str.replace(r"[^\d\.\-]", "", regex=True), errors="coerce")
    if s.notna().any():
        k4.metric("평균 월급여", f"{s.mean():,.0f}원")

# ============================ 그래프 1 =========================
if "부서" in df.columns and "업무만족도" in df.columns:
    st.subheader("부서별 업무 만족도")
    show = df.copy()
    show["업무만족도"] = pd.to_numeric(show["업무만족도"], errors="coerce")
    show = show.dropna(subset=["업무만족도"])
    if not show.empty:
        fig1, ax1 = plt.subplots(figsize=(7,4))
        dept = show.groupby("부서")["업무만족도"].mean().sort_values(ascending=False)
        sns.barplot(x=dept.index, y=dept.values, ax=ax1)
        ax1.set_ylabel("평균 업무만족도")
        if ax1.containers:
            try: ax1.bar_label(ax1.containers[0], fmt="%.2f")
            except: pass
        plt.xticks(rotation=20)
        st.pyplot(fig1)

# ============================ 그래프 2 =========================
if "업무환경만족도" in df.columns and "업무만족도" in df.columns:
    st.subheader("업무환경만족도와 업무만족도의 관계")
    x = pd.to_numeric(df["업무환경만족도"], errors="coerce")
    y = pd.to_numeric(df["업무만족도"], errors="coerce")
    plot_df = pd.DataFrame({"업무환경만족도": x, "업무만족도": y}).dropna()
    if not plot_df.empty:
        fig2, ax2 = plt.subplots(figsize=(6,4))
        sns.scatterplot(data=plot_df, x="업무환경만족도", y="업무만족도", alpha=0.6, ax=ax2)
        sns.regplot(data=plot_df, x="업무환경만족도", y="업무만족도", scatter=False, ax=ax2, color="red")
        st.pyplot(fig2)

# ============================ 그래프 3 =========================
if "야근정도" in df.columns and "업무만족도" in df.columns:
    st.subheader("야근정도별 업무만족도")
    show = df.copy()
    show["업무만족도"] = pd.to_numeric(show["업무만족도"], errors="coerce")
    show = show.dropna(subset=["업무만족도"])
    if not show.empty:
        fig3, ax3 = plt.subplots(figsize=(6,4))
        ot = show.groupby("야근정도")["업무만족도"].mean()
        sns.barplot(x=ot.index, y=ot.values, ax=ax3)
        ax3.set_ylabel("평균 업무만족도")
        if ax3.containers:
            try: ax3.bar_label(ax3.containers[0], fmt="%.2f")
            except: pass
        st.pyplot(fig3)
