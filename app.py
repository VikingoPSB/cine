import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(page_title="Dashboard Taquilla Cine (1986-2026)", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("dataset_minado.csv")
    if 'anio' in df.columns:
        df['anio'] = pd.to_numeric(df['anio'], errors='coerce').dropna().astype(int)
    return df

try:
    df = load_data()
    
    st.title("🎬 Dashboard Interactivo: Análisis de Taquilla (1986 - 2026)")
    st.markdown("Visualización interactiva de minería de datos sobre el éxito comercial y la respuesta de la audiencia.")

    # --------------------------------------------------------------------------
    # FILTROS EN CASCADA EN LA BARRA LATERAL
    # --------------------------------------------------------------------------
    st.sidebar.header("🔍 Filtros Dinámicos")

    # FILTRO 1 (Padre): Selección de Década(s)
    todas_decadas = sorted(df['decada'].dropna().unique())
    decada_sel = st.sidebar.multiselect(
        "1. Filtrar por Década(s):",
        options=todas_decadas,
        default=todas_decadas
    )

    # Filtrar dataset preliminar según las décadas elegidas para refrescar el rango de años
    if decada_sel:
        df_decada_filtrada = df[df['decada'].isin(decada_sel)]
    else:
        df_decada_filtrada = df.copy()

    # Obtener el rango de años dinámico ajustado
    min_year_dinamico = int(df_decada_filtrada['anio'].min()) if len(df_decada_filtrada) > 0 else 1986
    max_year_dinamico = int(df_decada_filtrada['anio'].max()) if len(df_decada_filtrada) > 0 else 2026

    # FILTRO 2 (Hijo): Slider de Años que responde al Filtro 1
    rango_anios = st.sidebar.slider(
        "2. Rango de Años (Refrescado por Década):",
        min_value=min_year_dinamico,
        max_value=max_year_dinamico,
        value=(min_year_dinamico, max_year_dinamico),
        step=1
    )

    # Dataset filtrado definitivo
    df_filtered = df_decada_filtrada[
        (df_decada_filtrada['anio'] >= rango_anios[0]) & 
        (df_decada_filtrada['anio'] <= rango_anios[1])
    ]

    st.sidebar.info(f"Mostrando **{len(df_filtered)}** películas entre **{rango_anios[0]}** y **{rango_anios[1]}**.")

    # --------------------------------------------------------------------------
    # MÉTRICAS CLAVE
    # --------------------------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Películas en el Período", f"{len(df_filtered):,}")
    col2.metric("Recaudación Promedio (USD)", f"${df_filtered['recaudacion_usd'].mean():,.0f}" if len(df_filtered) > 0 else "$0")
    col3.metric("Calificación Promedio", f"{df_filtered['promedio_votos'].mean():.2f} / 10" if len(df_filtered) > 0 else "0 / 10")

    st.markdown("---")

    if len(df_filtered) == 0:
        st.warning("⚠️ No se encontraron registros con la combinación de filtros seleccionada.")
    else:
        # ----------------------------------------------------------------------
        # REQUISITO ADICIONAL: RANKING TOP PELÍCULAS MÁS TAQUILLERAS
        # ----------------------------------------------------------------------
        st.subheader("🏆 Ranking Top de Películas Más Taquilleras")
        
        col_rank_num, _ = st.columns([1, 3])
        with col_rank_num:
            top_n = st.selectbox("Mostrar Top:", options=[5, 10, 15, 20], index=1)

        # Preparación de la tabla de ranking
        df_ranking = df_filtered.sort_values(by='recaudacion_usd', ascending=False).head(top_n).copy()
        
        # Asignar medallas para los primeros puestos
        posiciones = []
        for i in range(1, len(df_ranking) + 1):
            if i == 1:
                posiciones.append("🥇 1°")
            elif i == 2:
                posiciones.append("🥈 2°")
            elif i == 3:
                posiciones.append("🥉 3°")
            else:
                posiciones.append(f"{i}°")
        
        df_ranking.insert(0, "Puesto", posiciones)
        
        # Formatear la tabla de presentación
        df_ranking_display = df_ranking[['Puesto', 'titulo_final', 'anio', 'recaudacion_usd', 'promedio_votos', 'conteo_votos', 'cluster']].copy()
        df_ranking_display.columns = ['Posición', 'Título', 'Año', 'Recaudación Mundial (USD)', 'Nota Promedio', 'Total Votos', 'Cluster']
        
        # Formatear número monetario
        df_ranking_display['Recaudación Mundial (USD)'] = df_ranking_display['Recaudación Mundial (USD)'].map('${:,.0f}'.format)
        
        st.dataframe(df_ranking_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # ----------------------------------------------------------------------
        # GRÁFICOS INTERACTIVOS
        # ----------------------------------------------------------------------
        st.subheader("📊 Visualización de Patrones e Interacciones")
        
        # Gráfico 1: Scatter Plot
        fig1 = px.scatter(
            df_filtered,
            x="conteo_votos",
            y="recaudacion_usd",
            color="cluster",
            hover_name="titulo_final",
            hover_data=["anio", "promedio_votos"],
            log_x=True,
            log_y=True,
            title="1. Votos vs. Recaudación USD (Escala Logarítmica)"
        )
        st.plotly_chart(fig1, use_container_width=True)

        col_g2, col_g3 = st.columns(2)

        # Gráfico 2: Distribución
        with col_g2:
            fig2 = px.box(
                df_filtered,
                x="decada",
                y="recaudacion_usd",
                color="decada",
                log_y=True,
                title="2. Distribución de Recaudación por Década"
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Gráfico 3: Calificación vs Popularidad
        with col_g3:
            fig3 = px.scatter(
                df_filtered,
                x="promedio_votos",
                y="popularidad",
                size="recaudacion_usd",
                color="cluster",
                hover_name="titulo_final",
                title="3. Nota Audiencia vs. Popularidad (Tamaño = Recaudación)"
            )
            st.plotly_chart(fig3, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar el Dashboard. Detalle: {e}")
