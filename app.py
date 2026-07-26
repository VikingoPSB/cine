import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(page_title="Dashboard Taquilla Cine (1976-2026)", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("dataset_minado.csv")
    if 'anio' in df.columns:
        df['anio'] = pd.to_numeric(df['anio'], errors='coerce').dropna().astype(int)
    return df

try:
    df = load_data()

    st.title("🎬 Dashboard Interactivo: Análisis de Taquilla (1976 - 2026)")
    st.markdown("Visualización interactiva de minería de datos sobre el éxito comercial y la respuesta de la audiencia.")

    # --------------------------------------------------------------------------
    # LISTAS GLOBALES
    # --------------------------------------------------------------------------
    todas_decadas = sorted(df['decada'].dropna().unique()) if 'decada' in df.columns else []
    todos_anios = sorted(df['anio'].unique().tolist(), reverse=True) if 'anio' in df.columns else []
    min_year_global = min(todos_anios) if todos_anios else 1976
    max_year_global = max(todos_anios) if todos_anios else 2026

    # --------------------------------------------------------------------------
    # INICIALIZACIÓN DE SESSION STATE
    # --------------------------------------------------------------------------
    if 'decada_sel' not in st.session_state:
        st.session_state.decada_sel = todas_decadas
    if 'rango_anios' not in st.session_state:
        st.session_state.rango_anios = (min_year_global, max_year_global)
    if 'anio_exacto' not in st.session_state:
        st.session_state.anio_exacto = "Todos los años"
    if 'busqueda_titulo' not in st.session_state:
        st.session_state.busqueda_titulo = ""

    # --------------------------------------------------------------------------
    # FUNCIONES DE CALLBACK PARA RESETEO Y REFRESCO
    # --------------------------------------------------------------------------
    def reset_filtros():
        st.session_state.decada_sel = todas_decadas
        st.session_state.rango_anios = (min_year_global, max_year_global)
        st.session_state.anio_exacto = "Todos los años"
        st.session_state.busqueda_titulo = ""

    def al_cambiar_anio_exacto():
        if st.session_state.anio_exacto != "Todos los años":
            anio = int(st.session_state.anio_exacto)
            st.session_state.rango_anios = (anio, anio)
            decada_del_anio = df[df['anio'] == anio]['decada'].dropna().unique().tolist()
            if decada_del_anio:
                st.session_state.decada_sel = decada_del_anio

    # --------------------------------------------------------------------------
    # BARRA LATERAL CON FILTROS DINÁMICOS
    # --------------------------------------------------------------------------
    st.sidebar.header("🔍 Búsqueda y Filtros Reactivos")

    # Botón de reseteo
    st.sidebar.button("🧹 Limpiar Filtros", on_click=reset_filtros, use_container_width=True)
    st.sidebar.markdown("---")

    # FILTRO 0: Búsqueda incremental por Título de Película
    st.sidebar.subheader("🔎 Búsqueda por Nombre")
    st.sidebar.text_input(
        "Escribe el nombre de una película:",
        key="busqueda_titulo",
        placeholder="Ej: Matrix, Avatar, Batman...",
        help="Filtra las películas en tiempo real a medida que escribes."
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Filtros de Fecha")

    # FILTRO 1: Selección de Décadas
    st.sidebar.multiselect(
        "1. Filtrar por Década(s):",
        options=todas_decadas,
        key='decada_sel'
    )

    # Filtrar el dataframe por década para alimentar el desplegable
    if st.session_state.decada_sel:
        df_decada_temp = df[df['decada'].isin(st.session_state.decada_sel)]
    else:
        df_decada_temp = df.copy()

    anios_permitidos = sorted(df_decada_temp['anio'].unique().tolist(), reverse=True)
    opciones_desplegable = ["Todos los años"] + [str(a) for a in anios_permitidos]

    if str(st.session_state.anio_exacto) not in opciones_desplegable:
        st.session_state.anio_exacto = "Todos los años"

    # FILTRO 2: Año Exacto
    st.sidebar.selectbox(
        "2. Filtrar por Año Exacto:",
        options=opciones_desplegable,
        key='anio_exacto',
        on_change=al_cambiar_anio_exacto
    )

    # Ajustar límites del slider
    min_year_din = int(df_decada_temp['anio'].min()) if len(df_decada_temp) > 0 else min_year_global
    max_year_din = int(df_decada_temp['anio'].max()) if len(df_decada_temp) > 0 else max_year_global

    rango_actual = st.session_state.rango_anios
    nuevo_min = max(rango_actual[0], min_year_din)
    nuevo_max = min(rango_actual[1], max_year_din)
    if nuevo_min > nuevo_max:
        nuevo_min, nuevo_max = min_year_din, max_year_din
    st.session_state.rango_anios = (nuevo_min, nuevo_max)

    # FILTRO 3: Slider de Rango
    st.sidebar.slider(
        "3. Rango de Años:",
        min_value=min_year_din,
        max_value=max_year_din,
        key='rango_anios',
        step=1
    )

    # --------------------------------------------------------------------------
    # APLICACIÓN DE TODOS LOS FILTROS
    # --------------------------------------------------------------------------
    # 1. Filtro de Rango y Décadas
    df_filtered = df_decada_temp[
        (df_decada_temp['anio'] >= st.session_state.rango_anios[0]) &
        (df_decada_temp['anio'] <= st.session_state.rango_anios[1])
    ]

    # 2. Filtro Incremental por Texto (Búsqueda parcial en 'titulo_final')
    texto_busqueda = st.session_state.busqueda_titulo.strip()
    if texto_busqueda:
        df_filtered = df_filtered[
            df_filtered['titulo_final'].astype(str).str.contains(texto_busqueda, case=False, na=False)
        ]

    st.sidebar.info(f"Mostrando **{len(df_filtered)}** películas con los criterios activos.")

    # --------------------------------------------------------------------------
    # MÉTRICAS CLAVE
    # --------------------------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Películas en el Período", f"{len(df_filtered):,}")
    col2.metric("Recaudación Promedio (USD)", f"${df_filtered['recaudacion_usd'].mean():,.0f}" if len(df_filtered) > 0 else "$0")
    col3.metric("Calificación Promedio", f"{df_filtered['promedio_votos'].mean():.2f} / 10" if len(df_filtered) > 0 else "0 / 10")

    st.markdown("---")

    if len(df_filtered) == 0:
        st.warning(f"⚠️ No se encontraron películas que coincidan con '{texto_busqueda}' y los filtros de fecha. Haz clic en 'Limpiar / Resetear Filtros'.")
    else:
        # ----------------------------------------------------------------------
        # RANKING TOP PELÍCULAS
        # ----------------------------------------------------------------------
        st.subheader("🏆 Ranking Top de Películas Más Taquilleras")

        col_rank_num, _ = st.columns([1, 3])
        with col_rank_num:
            top_n = st.selectbox("Mostrar Top:", options=[5, 10, 15, 20], index=1)

        df_ranking = df_filtered.sort_values(by='recaudacion_usd', ascending=False).head(top_n).copy()

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

        df_ranking_display = df_ranking[['Puesto', 'titulo_final', 'anio', 'recaudacion_usd', 'promedio_votos', 'conteo_votos', 'cluster']].copy()
        df_ranking_display.columns = ['Posición', 'Título', 'Año', 'Recaudación Mundial (USD)', 'Nota Promedio', 'Total Votos', 'Cluster']
        df_ranking_display['Recaudación Mundial (USD)'] = df_ranking_display['Recaudación Mundial (USD)'].map('${:,.0f}'.format)

        st.dataframe(df_ranking_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # ----------------------------------------------------------------------
        # GRÁFICOS INTERACTIVOS
        # ----------------------------------------------------------------------
        st.subheader("📊 Visualización de Patrones e Interacciones")

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