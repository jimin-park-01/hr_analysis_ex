import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from matplotlib import font_manager
import os

st.set_page_config(page_title="업무만족도 대시보드", layout="wide")

# 0) Seaborn 테마 먼저 설정 (폰트 지정 없이)
sns.set_theme(style="whitegrid")

# 1) 한글 폰트 경로 지정 (윈도우 맑은고딕)
FONT_PATH = r"C:\Windows\Fonts\malgun.ttf"
if not os.path.exists(FONT_PATH):
    st.error(f"폰트 파일을 찾을 수 없습니다: {FONT_PATH}")
else:
    # 폰트 추가 및 캐시 재빌드
    font_manager.fontManager.addfont(FONT_PATH)
    try:
        # 최신 Matplotlib(>=3.7권장) 캐시 재로드
        font_manager._load_fontmanager(try_read_cache=False)
    except Exception:
        # 구버전 호환
        try:
            font_manager._rebuild()
        except Exception:
            pass

    fam = font_manager.FontProperties(fname=FONT_PATH).get_name() or "Malgun Gothic"

    # 2) matplotlib에 'family'와 'sans-serif'를 함께 지정 (Seaborn이 덮어쓴 경우까지 방지)
    mpl.rcParams.update({
        "font.family": fam,
        "font.sans-serif": [fam, "Malgun Gothic", "NanumGothic", "Noto Sans KR"],
        "axes.unicode_minus": False,
    })

# (선택) 적용 폰트 확인
st.caption(f"🖋 Matplotlib 적용 폰트: **{mpl.rcParams['font.family']}** / sans-serif: **{mpl.rcParams['font.sans-serif']}**")


# ----------------------------
# 2) CSV 인코딩 자동 복원 로더 (utf-8-sig ↔ cp949)
# ----------------------------
@st.cache_data
def load_df(path="HR Data.csv"):
    # 1차: UTF-8-SIG
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        pass
    # 2차: CP949(윈도우)
    try:
        return pd.read_csv(path, encoding="cp949")
    except Exception:
        pass
    # 3차: UTF-8 일반
    try:
        return pd.read_csv(path, encoding="utf-8")
    except Exception as e:
        st.error(f"CSV 읽기 실패: {e}")
        return pd.DataFrame()

df = load_df()

# 한글이 실제로 보이는지 바로 확인(인코딩/폰트 둘 다 점검)
st.write("한글 테스트: 부서 / 업무만족도 / 야근정도 ✅")

# +++ 여긴 기존 KPI/그래프 코드 그대로 두세요 +++


# ===== KPI =====
st.title("업무만족도 분석 대시보드")
n = len(df)
k1,k2,k3,k4 = st.columns(4)
k1.metric("전체 직원 수", f"{n:,}명")
if "업무만족도" in df.columns:
    k2.metric("평균 업무만족도", f"{df['업무만족도'].mean():.2f}")
if "업무환경만족도" in df.columns:
    k3.metric("평균 업무환경만족도", f"{df['업무환경만족도'].mean():.2f}")
if "월급여" in df.columns:
    k4.metric("평균 월급여", f"{df['월급여'].mean():,.0f}원")

# ===== 그래프 1: 부서별 업무 만족도 =====
if "부서" in df.columns and "업무만족도" in df.columns:
    st.subheader("부서별 업무 만족도")
    fig1, ax1 = plt.subplots(figsize=(7,4))
    dept = df.groupby("부서")["업무만족도"].mean().sort_values(ascending=False)
    sns.barplot(x=dept.index, y=dept.values, ax=ax1)
    ax1.set_ylabel("평균 업무만족도")
    ax1.bar_label(ax1.containers[0], fmt="%.2f")
    plt.xticks(rotation=20)
    st.pyplot(fig1)

# ===== 그래프 2: 업무환경만족도 vs 업무만족도 =====
if "업무환경만족도" in df.columns and "업무만족도" in df.columns:
    st.subheader("업무환경만족도와 업무만족도의 관계")
    fig2, ax2 = plt.subplots(figsize=(6,4))
    sns.scatterplot(data=df, x="업무환경만족도", y="업무만족도", alpha=0.6, ax=ax2)
    sns.regplot(data=df, x="업무환경만족도", y="업무만족도", scatter=False, ax=ax2, color="red")
    st.pyplot(fig2)

# ===== 그래프 3: 야근정도별 업무만족도 =====
if "야근정도" in df.columns and "업무만족도" in df.columns:
    st.subheader("야근정도별 업무만족도")
    fig3, ax3 = plt.subplots(figsize=(6,4))
    ot = df.groupby("야근정도")["업무만족도"].mean()
    sns.barplot(x=ot.index, y=ot.values, ax=ax3)
    ax3.set_ylabel("평균 업무만족도")
    ax3.bar_label(ax3.containers[0], fmt="%.2f")
    st.pyplot(fig3)
