import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import requests
import io 

st.set_page_config(
    page_title="StudyApp Visualization",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("StudyApp Visualization")
st.markdown("Toto je vizualizácia pre StudyApp.")

response = requests.get("http://localhost:5000/export_csv")
if response.status_code != 200:
    st.error("Nepodarilo sa načítať CSV z API.")
    st.stop()

csv_data = response.content.decode("utf-8")
df = pd.read_csv(io.StringIO(csv_data))

with st.expander('Ukážka prvých 5 riadkov datasetu'):
    st.dataframe(df.head())


topic_opt = df['topic'].unique()
selected_topic = st.sidebar.multiselect(
    'Vyber predmetu:',
    options=topic_opt,
    default=list(topic_opt),
    key='topic_filter'
)


min_time = int(df['study_time'].min())
max_time = int(df['study_time'].max())
study_time_range = st.sidebar.slider(
    "Vyber rozsahu študijného času:",
    min_value=min_time,
    max_value=max_time,
    value=(min_time, max_time),
    key='study_time_filter'
)

df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Handle bad/missing values

# Drop rows with invalid dates (optional but safer)
df = df.dropna(subset=['date'])

# Get consistent datetime objects
min_date = df['date'].min().to_pydatetime()
max_date = df['date'].max().to_pydatetime()
date_range = st.sidebar.slider(
    "Vyber rozsahu dátumu:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD",
    key='date_filter'
)



# Aplikovanie filtrov
df_filtered = df[
    df['topic'].isin(selected_topic) &
     df['study_time'].between(*study_time_range) &
    df['date'].between(*date_range)
]

st.markdown(f"Počet vyfiltrovaných záznamov: **{len(df_filtered)}**")

# Vizualizácie v stĺpcoch
col1, col2 = st.columns(2)


df['day_name'] = df['date'].dt.day_name()
df_filtered['day_name'] = df_filtered['date'].dt.day_name()

with col1:
    st.subheader("Topic tela vs. Study time (podľa dňa)")
    fig_scatter, ax_scatter = plt.subplots()
    sns.scatterplot(data=df_filtered, x='topic', y='study_time', hue='day_name', ax=ax_scatter)
    ax_scatter.set_xlabel("Topic")
    ax_scatter.set_ylabel("Study time")
    ax_scatter.legend(title="Deň v týždni", bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig_scatter)


with col2:
    st.subheader("Bar plot")
    avg_time_topic = df_filtered.groupby('topic')['study_time'].mean().dropna()
    fig_bar, ax_bar = plt.subplots()
    avg_time_topic.plot(kind='bar', ax=ax_bar)
    ax_bar.set_xlabel("Topic")
    ax_bar.set_ylabel("Study Time")
    ax_bar.tick_params(axis='x', rotation=0)
    st.pyplot(fig_bar)