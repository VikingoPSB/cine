import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Cinematic Data Mining | Top 50 Años",
    page_icon="🎬",
    layout="wide",
)

# 2. CARGA Y PREPROCESAMIENTO DE DATOS
@st.cache_data
def cargar_datos():
    df = pd.read_csv("dataset_minado.csv")

    if "presupuesto_usd" not in df.columns:
        df["presupuesto_usd"] = 0.0
    if "log_presupuesto" not in df.columns:
        df["log_presupuesto"] = np.log1p(df["presupuesto_usd"])
    if "roi" not in df.columns:
        df["roi"] = np.where(
            df["presupuesto_usd"] > 0,
            (df["recaudacion_usd"] - df["presupuesto_usd"]) / df["presupuesto_usd"],
            0.0,
        )
    return df


try:
    df = cargar_datos()
except Exception as e:
    st.error("No se pudo encontrar 'dataset_minado.csv'. Asegúrate de tener el archivo en el mismo directorio.")
    st.stop()

# ENCABEZADO PRINCIPAL
st.title("🎬 Análisis de Taquilla Cine Mundial (Últimos 50 Años)")
st.caption("Proceso KDD integrado: Scraping + API REST + Clustering K-Means + Modelos Predictivos")
st.markdown("---")

# ==============================================================================
# INICIALIZACIÓN DE SESSION STATE
# ==============================================================================
OPCIONES_DECADAS = sorted(df["decada"].dropna().unique().tolist())
OPCIONES_CLUSTERS = sorted(df["cluster"].unique())

MIN_RANKING = int(df["posicion_ranking"].min()) if "posicion_ranking" in df.columns else 1
MAX_RANKING = int(df["posicion_ranking"].max()) if "posicion_ranking" in df.columns else 20

if "filtro_busqueda" not in st.session_state:
    st.session_state.filtro_busqueda = ""
if "filtro_anio_exacto" not in st.session_state:
    st.session_state.filtro_anio_exacto = ""
if "filtro_ranking" not in st.session_state:
    st.session_state.filtro_ranking = (MIN_RANKING, MAX_RANKING)

# Estado de checkboxes
for dec in OPCIONES_DECADAS:
    key_dec = f"chk_dec_{dec}"
    if key_dec not in st.session_state:
        st.session_state[key_dec] = True

for cls in OPCIONES_CLUSTERS:
    key_cls = f"chk_cls_{cls}"
    if key_cls not in st.session_state:
        st.session_state[key_cls] = True


def reiniciar_filtros():
    st.session_state.filtro_busqueda = ""
    st.session_state.filtro_anio_exacto = ""
    st.session_state.filtro_ranking = (MIN_RANKING, MAX_RANKING)
    
    for dec in OPCIONES_DECADAS:
        st.session_state[f"chk_dec_{dec}"] = True
        
    for cls in OPCIONES_CLUSTERS:
        st.session_state[f"chk_cls_{cls}"] = True


# ==============================================================================
# CONTROLES DE LA BARRA LATERAL (SIDEBAR)
# ==============================================================================
st.sidebar.header("🔍 Filtros Interactivos")

if st.sidebar.button("🧹 Limpiar todos los filtros", use_container_width=True):
    reiniciar_filtros()
    st.rerun()

st.sidebar.markdown("---")

st.sidebar.text_input(
    "🔎 Buscar por Título:",
    key="filtro_busqueda",
    placeholder="Ej: Avatar, Star Wars...",
)

# DÉCADAS EN CHECKBOXES
decadas_seleccionadas = []
with st.sidebar.expander("🗓️ Selección de Décadas", expanded=True):
    for dec in OPCIONES_DECADAS:
        if st.checkbox(str(dec), key=f"chk_dec_{dec}"):
            decadas_seleccionadas.append(dec)

st.sidebar.text_input(
    "📆 Año Específico (Opcional):",
    key="filtro_anio_exacto",
    placeholder="Ej: 1997",
)

st.sidebar.slider(
    "🏆 Posición en Ranking Anual (Box Office):",
    min_value=MIN_RANKING,
    max_value=MAX_RANKING,
    key="filtro_ranking",
    help="Filtra las películas según su puesto en el Top Anual (ej: Top 1 al 5)",
)

# CLUSTERS EN CHECKBOXES
clusters_seleccionados = []
with st.sidebar.expander("🎯 Cluster (K-Means)", expanded=True):
    for cls in OPCIONES_CLUSTERS:
        if st.checkbox(f"Cluster {cls}", key=f"chk_cls_{cls}"):
            clusters_seleccionados.append(cls)

# ==============================================================================
# LÓGICA DE FILTRADO DINÁMICO
# ==============================================================================
df_filtrado = df.copy()

if st.session_state.filtro_busqueda.strip() != "":
    df_filtrado = df_filtrado[
        df_filtrado["titulo_final"].str.contains(
            st.session_state.filtro_busqueda, case=False, na=False
        )
    ]

if decadas_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado["decada"].isin(decadas_seleccionadas)]
else:
    df_filtrado = df_filtrado.iloc[0:0]

if st.session_state.filtro_anio_exacto.strip() != "":
    try:
        anio_int = int(st.session_state.filtro_anio_exacto.strip())
        df_filtrado = df_filtrado[df_filtrado["anio"] == anio_int]
    except ValueError:
        st.sidebar.warning("⚠️ Escribe un año numérico válido (ej: 1999).")

r_min, r_max = st.session_state.filtro_ranking
if "posicion_ranking" in df_filtrado.columns:
    df_filtrado = df_filtrado[
        (df_filtrado["posicion_ranking"] >= r_min)
        & (df_filtrado["posicion_ranking"] <= r_max)
    ]

if clusters_seleccionados:
    df_filtrado = df_filtrado[df_filtrado["cluster"].isin(clusters_seleccionados)]
else:
    df_filtrado = df_filtrado.iloc[0:0]

if df_filtrado.empty:
    st.warning("⚠️ No se encontraron películas que coincidan con la combinación de filtros seleccionada.")

# ==============================================================================
# DASHBOARD
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visión General y EDA",
    "🎯 Clustering (K-Means)",
    "🤖 Modelos Machine Learning",
    "💡 Hallazgos e Insights",
])

with tab1:
    st.subheader("Métricas Generales del Conjunto Filtrado")

    col1, col2, col3, col4, col5 = st.columns(5)
    total_pelis = len(df_filtrado)

    pres_prom = f"${df_filtrado['presupuesto_usd'].mean():,.0f} USD" if total_pelis > 0 else "$0 USD"
    rec_prom = f"${df_filtrado['recaudacion_usd'].mean():,.0f} USD" if total_pelis > 0 else "$0 USD"
    roi_prom = f"{df_filtrado['roi'].mean():.2f}x" if total_pelis > 0 else "0x"
    voto_prom = f"{df_filtrado['promedio_votos'].mean():.1f} / 10" if total_pelis > 0 else "0"

    col1.metric("Películas", total_pelis)
    col2.metric("Presupuesto Prom.", pres_prom)
    col3.metric("Recaudación Prom.", rec_prom)
    col4.metric("ROI Promedio", roi_prom)
    col5.metric("Prom. Votos", voto_prom)

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
                template="plotly_white",
            )
            fig_hist.update_traces(marker_line_color="#0f172a", marker_line_width=1, opacity=0.85)
            st.plotly_chart(fig_hist, use_container_width=True)

        with c2:
            st.markdown("### Top Películas Más Taquilleras del Filtro")
            top10 = df_filtrado.sort_values(by="recaudacion_usd", ascending=False).head(10)
            fig_bar = px.bar(
                top10,
                x="recaudacion_usd",
                y="titulo_final",
                orientation="h",
                color="posicion_ranking",
                color_continuous_scale="Viridis",
                title="Top Recaudación en USD",
                labels={
                    "recaudacion_usd": "USD",
                    "titulo_final": "Película",
                    "posicion_ranking": "Puesto Ranking",
                },
                template="plotly_white",
            )
            fig_bar.update_traces(marker_line_color="#1e293b", marker_line_width=1.5, opacity=0.9)
            fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### 📋 Listado Detallado de Películas")
        cols_mostrar = [
            "titulo_final",
            "anio",
            "posicion_ranking",
            "presupuesto_usd",
            "recaudacion_usd",
            "roi",
            "popularidad",
            "promedio_votos",
            "cluster",
        ]
        cols_existentes = [c for c in cols_mostrar if c in df_filtrado.columns]

        df_tabla_ordenada = df_filtrado[cols_existentes].sort_values(by="recaudacion_usd", ascending=False)

        st.dataframe(
            df_tabla_ordenada,
            use_container_width=True,
            column_config={
                "titulo_final": st.column_config.TextColumn("Película", width="medium"),
                "anio": st.column_config.NumberColumn("Año", format="%d", width="small"),
                "posicion_ranking": st.column_config.NumberColumn("🏆 Puesto Ranking", format="#%d", width="small"),
                "presupuesto_usd": st.column_config.NumberColumn("💸 Presupuesto USD", format="$%d", width="medium"),
                "recaudacion_usd": st.column_config.NumberColumn("💵 Recaudación USD", format="$%d", width="medium"),
                "roi": st.column_config.NumberColumn("📈 ROI", format="%.2fx", width="small"),
                "popularidad": st.column_config.NumberColumn("Popularidad TMDB", format="%.1f", width="small"),
                "promedio_votos": st.column_config.NumberColumn("Promedio Votos", format="%.1f", width="small"),
                "cluster": st.column_config.TextColumn("Cluster", width="small"),
            },
        )

with tab2:
    st.subheader("Agrupamiento por Similitud (K-Means)")
    if not df_filtrado.empty:
        eje_x_opcion = st.radio(
            "Seleccionar eje X para visualizar los clusters:",
            options=["Conteo de Votos (log_votos)", "Presupuesto en USD (log_presupuesto)"],
            horizontal=True,
        )

        eje_x = "log_votos" if "Votos" in eje_x_opcion else "log_presupuesto"
        titulo_eje_x = "Log(Conteo de Votos)" if eje_x == "log_votos" else "Log(Presupuesto USD)"

        fig_scatter = px.scatter(
            df_filtrado,
            x=eje_x,
            y="log_recaudacion",
            color="cluster",
            size="popularidad",
            hover_name="titulo_final",
            hover_data=["anio", "posicion_ranking", "presupuesto_usd", "recaudacion_usd", "roi"],
            title=f"Clusters: {titulo_eje_x} vs. Log(Recaudación USD)",
            template="plotly_white",
        )
        fig_scatter.update_traces(marker=dict(line=dict(width=1, color="DarkSlateGrey")))
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("🤖 Resultados y Visualización de Modelos de Machine Learning")

    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown("#### Regresión: Predicción de Recaudación")
            st.caption("Modelo: **Random Forest Regressor** ($R^2 = 0.6840$)")

            if not df_filtrado.empty:
                fig_reg = px.scatter(
                    df_filtrado,
                    x="log_presupuesto",
                    y="log_recaudacion",
                    color="decada",
                    trendline="ols",
                    hover_name="titulo_final",
                    title="Regresión: Log(Presupuesto) vs. Log(Recaudación)",
                    labels={
                        "log_presupuesto": "Log(Presupuesto USD)",
                        "log_recaudacion": "Log(Recaudación USD)",
                        "decada": "Década",
                    },
                    template="plotly_white",
                )
                st.plotly_chart(fig_reg, use_container_width=True)

                st.info("💡 **Variables determinantes:** Presupuesto en USD, Conteo de Votos y Popularidad en TMDB.")

    with col_b:
        with st.container(border=True):
            st.markdown("#### Clasificación: Distribución de 'Blockbusters'")
            st.caption("Modelo: **Random Forest Classifier** (Accuracy: **87.57%**)")

            if not df_filtrado.empty and "es_blockbuster" in df_filtrado.columns:
                df_block = df_filtrado.copy()
                df_block["tipo_pelicula"] = df_block["es_blockbuster"].map(
                    {1: "Blockbuster (Top 25%)", 0: "Estándar / Regular"}
                )

                fig_class = px.histogram(
                    df_block,
                    x="tipo_pelicula",
                    color="tipo_pelicula",
                    color_discrete_map={
                        "Blockbuster (Top 25%)": "#0284c7",
                        "Estándar / Regular": "#94a3b8",
                    },
                    title="Distribución de Películas Clasificadas",
                    labels={"tipo_pelicula": "Categoría Predicha", "count": "Cantidad"},
                    template="plotly_white",
                )
                fig_class.update_layout(showlegend=False)
                st.plotly_chart(fig_class, use_container_width=True)

                st.success("🎯 **Evaluación:** El modelo clasifica correctamente el Top 25% de recaudación integrando popularidad y presupuesto.")

with tab4:
    st.subheader("Conclusiones y Hallazgos Principales")

    with st.container(border=True):
        st.markdown(
            """
            * **Impacto Digital Moderno y Financiero:** Se observa una correlación directa entre el presupuesto asignado y la recaudación obtenida, potenciada por la popularidad en TMDB en la era digital (2010+).
            
            * **Efecto de Clusters:**
                * **Cluster 0 (Clásicos y Éxitos Moderados):** Películas con presupuestos acotados, excelente votación y retorno comercial sostenido.
                * **Cluster 1 (Blockbusters Masivos):** Producciones de presupuesto elevado y recaudación masiva, dominado por franquicias y sagas globales.
                * **Cluster 2 (Rendimiento Medio):** Producciones con niveles intermedios de inversión e impacto de taquilla acotado.
            """
        )
