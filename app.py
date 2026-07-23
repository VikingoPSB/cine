import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Taquilla Cine (1986-2026)", layout="wide")

@st.cache_data
def load_data():
    # Cargar dataset procesado
    return pd.read_csv("dataset_minado.csv")

try:
    df = load_data()
    
    st.title("🎬 Dashboard Interactivo: Análisis de Taquilla (1986 - 2026)")
    st.markdown("Visualización interactiva de minería de datos sobre el éxito comercial y la respuesta de la audiencia.")

    # --- FILTRO 1: Selección de Rango de Años / Década ---
    st.sidebar.header("Filtros de Búsqueda")
    decada_sel = st.sidebar.multiselect(
        "Seleccionar Década(s):",
        options=df['decada'].dropna().unique(),
        default=df['decada'].dropna().unique()
    )
    
    df_filtered = df[df['decada'].isin(decada_sel)]

    # --- METRICAS CLAVE ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Películas Analizadas", len(df_filtered))
    col2.metric("Recaudación Promedio (USD)", f"${df_filtered['recaudacion_usd'].mean():,.0f}")
    col3.metric("Calificación Promedio", f"{df_filtered['promedio_votos'].mean():.2f} / 10")

    st.markdown("---")

    # --- GRÁFICO 1: Scatter Plot (Relación Votos vs Recaudación por Cluster) ---
    st.subplot = st.subheader("1. Relación entre Conteo de Votos y Recaudación (por Cluster)")
    fig1 = px.scatter(
        df_filtered,
        x="conteo_votos",
        y="recaudacion_usd",
        color="cluster",
        hover_name="titulo_final",
        log_x=True,
        log_y=True,
        title="Escala Logarítmica: Votos vs. Recaudación USD"
    )
    st.plotly_chart(fig1, use_container_width=True)

    col_g2, col_g3 = st.columns(2)

    # --- GRÁFICO 2: Histogram / Boxplot por Década ---
    with col_g2:
        st.subheader("2. Distribución de Recaudación por Década")
        fig2 = px.box(
            df_filtered,
            x="decada",
            y="recaudacion_usd",
            color="decada",
            log_y=True,
            title="Evolución de Ingresos Brutos en los Últimos 40 Años"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- GRÁFICO 3: Gráfico de Dispersión Promedio Votos vs Popularidad ---
    with col_g3:
        st.subheader("3. Calificación de Audiencia vs. Popularidad")
        fig3 = px.scatter(
            df_filtered,
            x="promedio_votos",
            y="popularidad",
            size="recaudacion_usd",
            color="cluster",
            hover_name="titulo_final",
            title="Relación Nota/Popularidad (Tamaño = Recaudación)"
        )
        st.plotly_chart(fig3, use_container_width=True)

except Exception as e:
    st.error(f"Asegúrate de tener el archivo 'dataset_minado.csv' en la misma carpeta del script app.py. Error: {e}")