import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(page_title="Dashboard Taquilla Cine (1986-2026)", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("dataset_minado.csv")
    # Asegurar que el año sea numérico entero
    if 'anio' in df.columns:
        df['anio'] = pd.to_numeric(df['anio'], errors='coerce')
    return df

try:
    df = load_data()
    
    st.title("🎬 Dashboard Interactivo: Análisis de Taquilla (1986 - 2026)")
    st.markdown("Visualización interactiva de minería de datos sobre el éxito comercial y la respuesta de la audiencia.")

    # --------------------------------------------------------------------------
    # FILTROS EN LA BARRA LATERAL
    # --------------------------------------------------------------------------
    st.sidebar.header("🔍 Filtros de Búsqueda")

    # Obtener el rango de años dinámicamente según el dataset
    min_year = int(df['anio'].min()) if 'anio' in df.columns else 1986
    max_year = int(df['anio'].max()) if 'anio' in df.columns else 2026

    # FILTRO 1: Rango de Años (Slider)
    rango_anios = st.sidebar.slider(
        "Seleccionar Rango de Años:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )

    # FILTRO 2: Selección de Décadas (Multiselect complementario)
    decada_sel = st.sidebar.multiselect(
        "Filtrar por Década(s):",
        options=df['decada'].dropna().unique(),
        default=df['decada'].dropna().unique()
    )

    # Aplicación combinada de filtros
    df_filtered = df[
        (df['anio'] >= rango_anios[0]) & 
        (df['anio'] <= rango_anios[1]) & 
        (df['decada'].isin(decada_sel))
    ]

    # Indicador visual del rango seleccionado
    st.sidebar.info(f"Mostrando datos desde **{rango_anios[0]}** hasta **{rango_anios[1]}** ({len(df_filtered)} registros)")

    # --------------------------------------------------------------------------
    # MÉTRICAS CLAVE
    # --------------------------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Películas en el Período", f"{len(df_filtered):,}")
    col2.metric("Recaudación Promedio (USD)", f"${df_filtered['recaudacion_usd'].mean():,.0f}" if len(df_filtered) > 0 else "$0")
    col3.metric("Calificación Promedio", f"{df_filtered['promedio_votos'].mean():.2f} / 10" if len(df_filtered) > 0 else "0 / 10")

    st.markdown("---")

    if len(df_filtered) == 0:
        st.warning("⚠️ No hay datos para el rango de años y décadas seleccionado. Intenta ampliar el filtro.")
    else:
        # ----------------------------------------------------------------------
        # GRÁFICO 1: Scatter Plot (Relación Votos vs Recaudación por Cluster)
        # ----------------------------------------------------------------------
        st.subheader(f"1. Relación Votos vs. Recaudación USD ({rango_anios[0]} - {rango_anios[1]})")
        fig1 = px.scatter(
            df_filtered,
            x="conteo_votos",
            y="recaudacion_usd",
            color="cluster",
            hover_name="titulo_final",
            hover_data=["anio", "promedio_votos"],
            log_x=True,
            log_y=True,
            title="Escala Logarítmica: Votos vs. Recaudación USD"
        )
        st.plotly_chart(fig1, use_container_width=True)

        col_g2, col_g3 = st.columns(2)

        # ----------------------------------------------------------------------
        # GRÁFICO 2: Evolución Anual de Recaudación / Boxplot
        # ----------------------------------------------------------------------
        with col_g2:
            st.subheader("2. Evolución de Ingresos por Década")
            fig2 = px.box(
                df_filtered,
                x="decada",
                y="recaudacion_usd",
                color="decada",
                log_y=True,
                title="Distribución de Recaudación en Período Seleccionado"
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ----------------------------------------------------------------------
        # GRÁFICO 3: Calificación vs. Popularidad
        # ----------------------------------------------------------------------
        with col_g3:
            st.subheader("3. Calificación de Audiencia vs. Popularidad")
            fig3 = px.scatter(
                df_filtered,
                x="promedio_votos",
                y="popularidad",
                size="recaudacion_usd",
                color="cluster",
                hover_name="titulo_final",
                title="Relación Nota vs. Popularidad (Tamaño = Recaudación USD)"
            )
            st.plotly_chart(fig3, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar los datos o el dashboard. Verifica que 'dataset_minado.csv' esté en el repositorio. Detalle: {e}")
