import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="업무만족도 대시보드", layout="wide")
sns.set(style="whitegrid", font="Malgun Gothic")

# 데이터 로드
@st.cache_data
def load_df(path="HR Data.csv"):
    return pd.read_csv(path, encoding="utf-8-sig")

df = load_df()

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
