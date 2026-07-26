import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Cinematic Data Mining | Top 50 Años",
    page_icon="🎬",
    layout="wide"
)

# ==============================================================================
# ESTILO CSS PERSONALIZADO (FONDO LIMPIO + CINTA DE CINE EN ESQUINA)
# ==============================================================================
estilo_cine_css = """
<style>
/* Fondo oscuro elegante y limpio */
.stApp {
    background-color: #0f172a;
    color: #f8fafc;
}

/* Imagen decorativa de cinta de cine en la esquina superior derecha */
.stApp::before {
    content: "";
    position: fixed;
    top: 15px;
    right: 25px;
    width: 150px;
    height: 150px;
    background-image: url("https://cdn-icons-png.flaticon.com/512/3172/3172554.png");
    background-size: contain;
    background-repeat: no-repeat;
    opacity: 0.30;
    z-index: 999;
    pointer-events: none;
}

/* Barra lateral estilizada */
section[data-testid="stSidebar"] {
    background-color: #1e293b !important;
    border-right: 1px solid #334155;
}

/* Métrica con tono azul brillante */
div[data-testid="stMetricValue"] {
    color: #38bdf8 !important;
}

/* Colores de contraste para títulos */
h1, h2, h3 {
    color: #f8fafc !important;
}
</style>
"""
st.markdown(estilo_cine_css, unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data
def cargar_datos():
    df = pd.read_csv("dataset_minado.csv")
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error("No se pudo encontrar 'dataset_minado.csv'. Asegurate de tener el archivo en el mismo directorio.")
    st.stop()

# ENCABEZADO PRINCIPAL CON LOGO Y TÍTULO
col_head1, col_head2 = st.columns([0.88, 0.12])
with col_head1:
    st.title("🎬 Análisis de Taquilla Cine Mundial (Últimos 50 Años)")
    st.markdown("Proceso KDD integrado: Scraping + API REST + Clustering K-Means + Modelos Predictivos")
with col_head2:
    st.image("https://cdn-icons-png.flaticon.com/512/3172/3172554.png", width=90)

# ==============================================================================
# INICIALIZACIÓN DE SESSION STATE (Estado de los Filtros)
# ==============================================================================
OPCIONES_DECADAS = ['1977-1985', '1986-1995', '1996-2005', '2006-2015', '2016-2026']
OPCIONES_CLUSTERS = sorted(df['cluster'].unique())

MIN_RANKING = int(df['posicion_ranking'].min()) if 'posicion_ranking' in df.columns else 1
MAX_RANKING = int(df['posicion_ranking'].max()) if 'posicion_ranking' in df.columns else 20

if 'filtro_busqueda' not in st.session_state:
    st.session_state.filtro_busqueda = ""
if 'filtro_decadas' not in st.session_state:
    st.session_state.filtro_decadas = OPCIONES_DECADAS.copy()
if 'filtro_anio_exacto' not in st.session_state:
    st.session_state.filtro_anio_exacto = ""
if 'filtro_ranking' not in st.session_state:
    st.session_state.filtro_ranking = (MIN_RANKING, MAX_RANKING)
if 'filtro_clusters' not in st.session_state:
    st.session_state.filtro_clusters = OPCIONES_CLUSTERS.copy()

# Función de reinicio de filtros
def reiniciar_filtros():
    st.session_state.filtro_busqueda = ""
    st.session_state.filtro_decadas = OPCIONES_DECADAS.copy()
    st.session_state.filtro_anio_exacto = ""
    st.session_state.filtro_ranking = (MIN_RANKING, MAX_RANKING)
    st.session_state.filtro_clusters = OPCIONES_CLUSTERS.copy()

# ==============================================================================
# CONTROLES DE LA BARRA LATERAL (SIDEBAR)
# ==============================================================================
st.sidebar.header("🔍 Filtros Interactivos")

# 1. Botón de Limpiar Filtros
st.sidebar.button("🧹 Limpiar todos los filtros", on_click=reiniciar_filtros, use_container_width=True)
st.sidebar.markdown("---")

# 2. Textbox para buscar película(s) por título
st.sidebar.text_input(
    "🔎 Buscar por Título:",
    key="filtro_busqueda",
    placeholder="Ej: Avatar, Star Wars..."
)

# 3. Botonera Múltiple de Décadas
st.sidebar.multiselect(
    "🗓️ Selección de Décadas:",
    options=OPCIONES_DECADAS,
    key="filtro_decadas"
)

# 4. Textbox para Año Exacto
st.sidebar.text_input(
    "📆 Año Específico (Opcional):",
    key="filtro_anio_exacto",
    placeholder="Ej: 1997"
)

# 5. Slider de Ranking de Taquilla (Box Office Mojo)
st.sidebar.slider(
    "🏆 Posición en Ranking Anual (Box Office):",
    min_value=MIN_RANKING,
    max_value=MAX_RANKING,
    key="filtro_ranking",
    help="Filtra las películas según su puesto en el Top Anual (ej: Top 1 al 5)"
)

# 6. Filtro Clusters K-Means
st.sidebar.multiselect(
    "🎯 Cluster (K-Means):",
    options=OPCIONES_CLUSTERS,
    key="filtro_clusters"
)

# ==============================================================================
# LÓGICA DE FILTRADO DINÁMICO REFRESCADO
# ==============================================================================
df_filtrado = df.copy()

# A) Filtrar por búsqueda de texto
if st.session_state.filtro_busqueda.strip() != "":
    df_filtrado = df_filtrado[
        df_filtrado['titulo_final'].str.contains(st.session_state.filtro_busqueda, case=False, na=False)
    ]

# B) Filtrar por décadas
if st.session_state.filtro_decadas:
    df_filtrado = df_filtrado[df_filtrado['decada'].isin(st.session_state.filtro_decadas)]
else:
    df_filtrado = df_filtrado.iloc[0:0]

# C) Filtrar por año exacto
if st.session_state.filtro_anio_exacto.strip() != "":
    try:
        anio_int = int(st.session_state.filtro_anio_exacto.strip())
        df_filtrado = df_filtrado[df_filtrado['anio'] == anio_int]
    except ValueError:
        st.sidebar.warning("⚠️ Escribí un año numérico válido (ej: 1999).")

# D) Filtrar por rango de ranking
r_min, r_max = st.session_state.filtro_ranking
if 'posicion_ranking' in df_filtrado.columns:
    df_filtrado = df_filtrado[
        (df_filtrado['posicion_ranking'] >= r_min) & 
        (df_filtrado['posicion_ranking'] <= r_max)
    ]

# E) Filtrar por clusters
if st.session_state.filtro_clusters:
    df_filtrado = df_filtrado[df_filtrado['cluster'].isin(st.session_state.filtro_clusters)]
else:
    df_filtrado = df_filtrado.iloc[0:0]

# Mensaje de advertencia si no hay coincidencias
if df_filtrado.empty:
    st.warning("⚠️ No se encontraron películas que coincidan con la combinación de filtros seleccionada.")

# ==============================================================================
# DASHBOARD (PESTAÑAS REFRESCADAS)
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visión General y EDA", 
    "🎯 Clustering (K-Means)", 
    "🤖 Modelos Machine Learning", 
    "💡 Hallazgos e Insights"
])

with tab1:
    st.subheader("Métricas Generales del Conjunto Filtrado")
    
    col1, col2, col3, col4 = st.columns(4)
    total_pelis = len(df_filtrado)
    rec_prom = f"${df_filtrado['recaudacion_usd'].mean():,.0f} USD" if total_pelis > 0 else "$0 USD"
    pop_prom = f"{df_filtrado['popularidad'].mean():.1f}" if total_pelis > 0 else "0"
    voto_prom = f"{df_filtrado['promedio_votos'].mean():.1f} / 10" if total_pelis > 0 else "0"

    col1.metric("Películas Encontradas", total_pelis)
    col2.metric("Recaudación Promedio", rec_prom)
    col3.metric("Popularidad TMDB", pop_prom)
    col4.metric("Promedio Votos", voto_prom)

    st.markdown("---")
    
    if not df_filtrado.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### Distribución de Recaudación Mundial (Escala Log)")
            fig_hist = px.histogram(
                df_filtrado, 
                x="log_recaudacion", 
                color="decada", 
                marginal="rug",
                title="Distribución de Recaudación según Filtros",
                template="plotly_dark"
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with c2:
            st.markdown("### Top Películas MÁS Taquilleras del Filtro")
            top10 = df_filtrado.sort_values(by="recaudacion_usd", ascending=False).head(10)
            fig_bar = px.bar(
                top10, 
                x="recaudacion_usd", 
                y="titulo_final", 
                orientation='h', 
                color="posicion_ranking",
                color_continuous_scale="Viridis_r",
                title="Top Recaudación en USD (Color por Puesto de Ranking)", 
                labels={"recaudacion_usd": "USD", "titulo_final": "Película", "posicion_ranking": "Puesto Ranking"},
                template="plotly_dark"
            )
            fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)

        # Tabla interactiva formateada
        st.markdown("### 📋 Listado Detallado de Películas (Con Ranking Anual)")
        cols_mostrar = ['posicion_ranking', 'titulo_final', 'anio', 'recaudacion_usd', 'popularidad', 'promedio_votos', 'cluster']
        cols_existentes = [c for c in cols_mostrar if c in df_filtrado.columns]
        
        st.dataframe(
            df_filtrado[cols_existentes].sort_values(by=['anio', 'posicion_ranking'], ascending=[False, True]),
            use_container_width=True,
            column_config={
                "posicion_ranking": st.column_config.NumberColumn("🏆 Ranking", format="#%d"),
                "recaudacion_usd": st.column_config.NumberColumn("💵 Recaudación USD", format="$%d"),
                "titulo_final": "Película",
                "anio": "Año"
            }
        )

with tab2:
    st.subheader("Agrupamiento por Similitud (K-Means)")
    if not df_filtrado.empty:
        fig_scatter = px.scatter(
            df_filtrado, 
            x="log_votos", 
            y="log_recaudacion", 
            color="cluster",
            size="popularidad",
            hover_name="titulo_final",
            hover_data=["anio", "posicion_ranking", "recaudacion_usd"],
            title="Clusters: Votos vs. Recaudación Mundial (Datos Filtrados)",
            template="plotly_dark"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("Resultados de Modelos de Machine Learning")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Regresión: Predicción de Recaudación")
        st.write("Modelo: **Random Forest Regressor** ($R^2 = 0.6840$)")
        st.info("Variables más determinantes: Conteo de Votos y Popularidad en TMDB.")
    with col_b:
        st.markdown("#### Clasificación: Detección de 'Blockbusters'")
        st.write("Modelo: **Random Forest Classifier** vs **Regresión Logística**")
        st.success("Accuracy alcanzado: **87.57%** evaluando el Top 25% de recaudación.")

with tab4:
    st.subheader("Conclusiones y Hallazgos Principales")
    st.markdown("""
    * **Impacto Digital Moderno:** Las películas producidas después de 2010 muestran una fuerte correlación entre la popularidad previa en TMDB y la recaudación.
    * **Efecto de Clusters:**
      * *Cluster 0 (Clásicos y Éxitos Moderados):* Películas con excelente votación pero menor volumen masivo de votos.
      * *Cluster 1 (Blockbusters Masivos):* Altísima recaudación y votos, dominado por franquicias recientes.
      * *Cluster 2 (Rendimiento Medio):* Películas de nicho o éxito comercial acotado.
    """)
