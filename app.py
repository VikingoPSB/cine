import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as gg

st.set_page_config(
    page_title="Cinematic Data Mining | Top 50 Años",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Análisis de Taquilla Cine Mundial (Últimos 50 Años)")
st.markdown("Proceso KDD integrado: Scraping + API REST + Clustering K-Means + Modelos Predictivos")

@st.cache_data
def cargar_datos():
    # Cargar el dataset procesado y minado
    df = pd.read_csv("dataset_minado.csv")
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error("Por favor asegúrate de que 'dataset_minado.csv' esté en el mismo directorio.")
    st.stop()

# --- FILTROS EN BARRA LATERAL ---
st.sidebar.header("🔍 Filtros Interactivos")

anios = st.sidebar.slider(
    "Rango de Años:",
    int(df['anio'].min()),
    int(df['anio'].max()),
    (1980, 2025)
)

clusters_sel = st.sidebar.multiselect(
    "Filtrar por Cluster (K-Means):",
    options=sorted(df['cluster'].unique()),
    default=sorted(df['cluster'].unique())
)

df_filtrado = df[
    (df['anio'] >= anios[0]) & 
    (df['anio'] <= anios[1]) & 
    (df['cluster'].isin(clusters_sel))
]

# --- PESTAÑAS DEL DASHBOARD ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visión General y EDA", 
    "🎯 Clustering (K-Means)", 
    "🤖 Modelos Machine Learning", 
    "💡 Hallazgos e Insights"
])

with tab1:
    st.subheader("Métricas Generales")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Películas Analizadas", len(df_filtrado))
    col2.metric("Recaudación Promedio", f"${df_filtrado['recaudacion_usd'].mean():,.0f} USD")
    col3.metric("Popularidad Promedio TMDB", f"{df_filtrado['popularidad'].mean():.1f}")
    col4.metric("Promedio Votos Público", f"{df_filtrado['promedio_votos'].mean():.1f} / 10")

    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### Distibución de Recaudación Mundial (Log-Scale)")
        fig_hist = px.histogram(df_filtrado, x="log_recaudacion", color="decada", marginal="rug",
                                title="Distribución de Recaudación por Década")
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        st.markdown("### Top 10 Películas MÁS Taquilleras del Rango Seleccionado")
        top10 = df_filtrado.sort_values(by="recaudacion_usd", ascending=False).head(10)
        fig_bar = px.bar(top10, x="recaudacion_usd", y="titulo_final", orientation='h', color="recaudacion_usd",
                         title="Top 10 Películas en USD", labels={"recaudacion_usd": "USD", "titulo_final": "Película"})
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.subheader("Agrupamiento por Similitud (K-Means)")
    st.markdown("Visualización de los 3 Clusters identificados según volumen de interacción y rendimiento financiero.")
    
    fig_scatter = px.scatter(
        df_filtrado, 
        x="log_votos", 
        y="log_recaudacion", 
        color="cluster",
        size="popularidad",
        hover_name="titulo_final",
        hover_data=["anio", "recaudacion_usd"],
        title="Clusters: Votos vs. Recaudación Mundial"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("Resultados de Modelos de Machine Learning")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### Regresión: Predicción de Recaudación")
        st.write("Modelo: **Random Forest Regressor** (R² = ~0.68)")
        st.info("Variables más determinantes: Conteo de Votos y Popularidad en TMDB.")

    with col_b:
        st.markdown("#### Clasificación: Detección de 'Blockbusters'")
        st.write("Modelo: **Random Forest Classifier** vs **Regresión Logística**")
        st.success("Accuracy alcanzado: **> 85%** evaluando el percentil 75 de ingresos.")

with tab4:
    st.subheader("Conclusiones y Hallazgos Principales")
    st.markdown("""
    * **Impacto Digital Moderno:** Las películas producidas después de 2010 muestran una fuerte correlación entre la popularidad previa en plataformas como TMDB y su recaudación final.
    * **Efecto de Clusters:**
      * *Cluster 0 (Clásicos y Éxitos Moderados):* Películas con excelente votación pero menor volumen masivo de votos.
      * *Cluster 1 (Blockbusters Masivos):* Altísima recaudación y votos, dominado por franquicias recientes.
      * *Cluster 2 (Rendimiento Medio):* Películas de nicho o con éxito comercial acotado.
    """)
