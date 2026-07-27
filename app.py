/* BOTONES DE SELECCIÓN DE CLUSTERS (Pills) EN SIDEBAR */

/* 1. Estado Desactivado / Inactivo */
section[data-testid="stSidebar"] [data-testid="stPillsItem"] button {
    background-color: #334155 !important; /* Gris oscuro neutro */
    color: #cbd5e1 !important;            /* Texto gris claro */
    border: 1px solid #475569 !important;
    border-radius: 20px !important;        /* Bordes redondeados tipo píldora */
    font-weight: 500 !important;
    transition: all 0.2s ease-in-out !important;
}

/* Hover en estado desactivado */
section[data-testid="stSidebar"] [data-testid="stPillsItem"] button:hover {
    background-color: #475569 !important;
    color: #ffffff !important;
    border-color: #94a3b8 !important;
}

/* 2. Estado Activado / Seleccionado */
section[data-testid="stSidebar"] [data-testid="stPillsItem"] button[aria-selected="true"] {
    background-color: #0284c7 !important; /* Azul celeste vibrante */
    color: #ffffff !important;            /* Texto blanco puro */
    border: 1px solid #38bdf8 !important; /* Borde azul claro resplandeciente */
    font-weight: 700 !important;
    box-shadow: 0 0 8px rgba(56, 189, 248, 0.4) !important; /* Resplandor suave */
}

/* Hover en estado activado */
section[data-testid="stSidebar"] [data-testid="stPillsItem"] button[aria-selected="true"]:hover {
    background-color: #0369a1 !important;
    border-color: #7dd3fc !important;
}
