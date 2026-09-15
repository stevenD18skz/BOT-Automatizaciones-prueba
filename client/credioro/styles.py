import streamlit as st


def inject_styles():
    """Inyecta los estilos CSS globales de la aplicación."""
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    st.markdown("""
<style>
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > [data-testid="stMain"] {
    background: #F4F7FA !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    color: #1A2B3C !important;
}
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2EAF0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
h1, h2, h3, h4 {
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.02em;
}
h1 { color: #1A2B3C !important; font-weight: 700 !important; font-size: 1.65rem !important; }
h2 { color: #1A2B3C !important; font-weight: 700 !important; font-size: 1.2rem !important;
     border-bottom: none !important; margin-top: 0 !important; }
h3 { color: #1A2B3C !important; font-weight: 600 !important; }
[data-testid="stSidebar"] h2 { border-bottom: none !important; }
.stTextInput > label,
.stSelectbox > label,
.stCheckbox > label,
.stRadio > label {
    color: #2D3F50 !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}

/* Estilo moderno para desplegables (stSelectbox / BaseWeb) */
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: #FFFFFF !important;
    border: 1.5px solid #D0DCE8 !important;
    border-radius: 10px !important;
    color: #1A2B3C !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    box-shadow: 0 2px 5px rgba(26, 43, 60, 0.04) !important;
    transition: all 0.2s ease-in-out !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover {
    border-color: #19BCE0 !important;
    box-shadow: 0 3px 10px rgba(25, 188, 224, 0.12) !important;
    background: #FAFDFF !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {
    border-color: #19BCE0 !important;
    box-shadow: 0 0 0 3px rgba(25, 188, 224, 0.18) !important;
    background: #FFFFFF !important;
}

/* Flechas e íconos de los desplegables */
div[data-testid="stSelectbox"] svg {
    fill: #19BCE0 !important;
    transition: transform 0.2s ease-in-out !important;
}

/* Opciones desplegadas flotantes (Popover / Listbox) */
div[data-baseweb="popover"] {
    border-radius: 12px !important;
    box-shadow: 0 10px 30px rgba(26, 43, 60, 0.18) !important;
    border: 1px solid #E2EAF0 !important;
    overflow: hidden !important;
}

div[data-baseweb="popover"] ul {
    background: #FFFFFF !important;
    padding: 6px !important;
}

div[data-baseweb="popover"] ul li {
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #1A2B3C !important;
    transition: background 0.15s ease, color 0.15s ease !important;
}

div[data-baseweb="popover"] ul li:hover,
div[data-baseweb="popover"] ul li[aria-selected="true"] {
    background: #EBF9FD !important;
    color: #0FA8CC !important;
    font-weight: 600 !important;
}

/* Estilo para campos de texto (stTextInput) */
div[data-testid="stTextInput"] div[data-baseweb="input"] {
    background: #FFFFFF !important;
    border: 1.5px solid #D0DCE8 !important;
    border-radius: 10px !important;
    color: #1A2B3C !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    box-shadow: 0 2px 5px rgba(26, 43, 60, 0.04) !important;
    transition: all 0.2s ease-in-out !important;
}

div[data-testid="stTextInput"] div[data-baseweb="input"]:hover {
    border-color: #19BCE0 !important;
    box-shadow: 0 3px 10px rgba(25, 188, 224, 0.12) !important;
}

div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    border-color: #19BCE0 !important;
    box-shadow: 0 0 0 3px rgba(25, 188, 224, 0.18) !important;
}

.stTextInput > div > div > input::placeholder { color: #A0B4C4 !important; }

/* Estilo para st.expander */
div[data-testid="stExpander"] {
    background: #F8FAFC !important;
    border: 1.5px solid #E2EAF0 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(26, 43, 60, 0.03) !important;
    overflow: hidden !important;
    margin-top: 10px !important;
    margin-bottom: 14px !important;
}

div[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    color: #2D3F50 !important;
    padding: 10px 14px !important;
    background: #F8FAFC !important;
}

div[data-testid="stExpander"] summary:hover {
    color: #19BCE0 !important;
    background: #F0FAFD !important;
}
div.stButton > button {
    background: #19BCE0 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border-radius: 50px !important;
    padding: 0.5rem 1.6rem !important;
    box-shadow: 0 2px 8px rgba(25,188,224,0.25) !important;
    transition: background 0.2s, box-shadow 0.2s, transform 0.15s !important;
    letter-spacing: 0.01em !important;
}
div.stButton > button:hover {
    background: #0FA8CC !important;
    box-shadow: 0 4px 14px rgba(25,188,224,0.35) !important;
    transform: translateY(-1px) !important;
}
div.stButton > button:active {
    transform: translateY(0) !important;
}
[data-testid="stSidebar"] div.stButton > button {
    background: transparent !important;
    color: #8A9CA8 !important;
    border: 1.5px dashed #D0DCE8 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    border-radius: 8px !important;
    padding: 0.35rem 1rem !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}
[data-testid="stSidebar"] div.stButton > button:hover {
    background: #FEF0F3 !important;
    color: #D63F5E !important;
    border: 1.5px solid #FCA5B7 !important;
    box-shadow: none !important;
    transform: none !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="primary"],
[data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-primary"] {
    background: #19BCE0 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border-radius: 50px !important;
    padding: 0.5rem 1.6rem !important;
    box-shadow: 0 2px 8px rgba(25,188,224,0.25) !important;
    transition: background 0.2s, box-shadow 0.2s, transform 0.15s !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover,
[data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: #0FA8CC !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(25,188,224,0.35) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 1px solid #E2EAF0 !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 12px rgba(26, 43, 60, 0.07) !important;
    padding: 1.25rem !important;
    transition: box-shadow 0.2s, border-color 0.2s !important;
    display: flow-root !important;
    overflow: hidden !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #BDD8E8 !important;
    box-shadow: 0 4px 20px rgba(26, 43, 60, 0.11) !important;
}
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}
hr { border-color: #E2EAF0 !important; margin: 1rem 0 !important; }
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] > div {
    width: 100% !important;
    box-sizing: border-box !important;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #F4F7FA; }
::-webkit-scrollbar-thumb { background: #C8D8E4; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #19BCE0; }
.sidebar-logo-wrap {
    display: flex; flex-direction: column; align-items: center;
    padding: 24px 0 20px;
    border-bottom: 3px solid #FCE700;
    margin-bottom: 20px;
}
.sidebar-app-name {
    font-size: 0.9rem; font-weight: 700; color: #1A2B3C;
    margin-top: 8px; letter-spacing: -0.01em; text-align: center;
}
.sidebar-app-sub {
    font-size: 0.72rem; color: #7A94A8; text-align: center;
    margin-top: 2px; line-height: 1.5;
}
.sidebar-section-lbl {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: #9AB0C0;
    padding: 14px 0 8px; border-bottom: 1px solid #EFF4F8;
    margin-bottom: 12px;
}
.status-dot {
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; margin-right: 6px; vertical-align: middle;
}
.module-tag {
    display: inline-flex; align-items: center; gap: 6px;
    background: #EBF9FD; color: #19BCE0;
    border: 1px solid #C2EEFA; border-radius: 20px;
    padding: 3px 12px; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 12px;
}
.module-tag-pay { background: #FFFBE6; color: #B89B00; border-color: #FCEEA0; }
.section-header { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.section-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 30px; height: 30px; border-radius: 50%;
    background: #19BCE0; color: #fff;
    font-weight: 700; font-size: 0.9rem; flex-shrink: 0;
}
.section-title { font-size: 1.1rem; font-weight: 700; color: #1A2B3C; }
.section-subtitle { font-size: 0.82rem; color: #7A94A8; margin: 0 0 18px; line-height: 1.5; }
.result-card {
    background: linear-gradient(135deg, #F0FAFD 0%, #FFFFFF 100%);
    border: 1.5px solid #C2EEFA;
    border-radius: 12px; padding: 12px 14px; margin-top: 8px;
    box-sizing: border-box; width: 100%; overflow: hidden;
}
.result-avatar {
    display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; border-radius: 50%;
    background: #19BCE0; color: #fff;
    font-weight: 700; font-size: 0.85rem; flex-shrink: 0;
}
.result-name { font-weight: 700; font-size: 1rem; color: #1A2B3C; }
.result-sub { font-size: 0.75rem; color: #7A94A8; margin-top: 1px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }
.info-cell {
    background: #FFFFFF; border: 1px solid #E2EAF0;
    border-radius: 10px; padding: 8px 12px;
}
.info-cell-label {
    font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 0.06em; color: #9AB0C0; margin-bottom: 4px;
}
.info-cell-value { font-size: 0.88rem; font-weight: 600; color: #1A2B3C; }
.badge-ok  { display:inline-block;padding:3px 10px;border-radius:20px;background:#E7FBF5;color:#0DA87A;font-size:.75rem;font-weight:700; }
.badge-err { display:inline-block;padding:3px 10px;border-radius:20px;background:#FEF0F3;color:#D63F5E;font-size:.75rem;font-weight:700; }
.badge-warn{ display:inline-block;padding:3px 10px;border-radius:20px;background:#FFF8E1;color:#BF8E00;font-size:.75rem;font-weight:700; }
.mtcn-badge {
    font-family: 'Inter', monospace; font-weight: 700; font-size: 0.9rem;
    background: #EBF9FD; color: #0FA8CC;
    border: 1px solid #C2EEFA; border-radius: 8px;
    padding: 5px 14px; display: inline-block;
}
.cat-badge {
    font-weight: 600; font-size: 0.88rem;
    background: #F0FAFD; color: #19BCE0;
    border: 1px solid #C2EEFA; border-radius: 8px;
    padding: 5px 14px; display: inline-block;
}
.step-row { display: flex; align-items: center; gap: 10px; margin: 14px 0 10px; }
.step-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 26px; height: 26px; border-radius: 50%;
    background: #19BCE0; color: #fff; font-weight: 700; font-size: 0.82rem; flex-shrink: 0;
}
.step-num-done { background: #2DD4A6; }
.step-label { font-size: 0.95rem; font-weight: 600; color: #1A2B3C; }
.rule-row { display:flex;align-items:center;gap:8px;font-size:.82rem;color:#4A6278;margin-bottom:6px; }
.app-header-wrap {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 22px;
}
.siif-pill {
    background: #FCE700; color: #1A2B3C;
    border-radius: 20px; padding: 5px 16px;
    font-size: 0.78rem; font-weight: 700;
    letter-spacing: 0.04em; white-space: nowrap;
}
.footer-bar {
    text-align: center; color: #9AB0C0;
    font-size: 0.72rem; margin-top: 32px;
    padding-top: 16px; border-top: 1px solid #E2EAF0;
}
.cuentas-disponibles-header {
    display: flex; align-items: center; gap: 8px;
    margin: 4px 0 10px;
}
.cuentas-icon { font-size: 1.1rem; }
.cuentas-title {
    font-size: 0.88rem; font-weight: 700;
    color: #1A2B3C; letter-spacing: -0.01em;
}
.valor-giro-card {
    background: linear-gradient(135deg, #FFFBE6 0%, #FFFFFF 100%);
    border: 1.5px solid #FCEEA0;
    border-radius: 14px; padding: 16px 18px; margin: 8px 0 4px;
    box-sizing: border-box; width: 100%;
}
.valor-giro-label {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.06em; color: #B89B00; margin-bottom: 4px;
}
.valor-giro-amount {
    font-size: 1.7rem; font-weight: 800; color: #1A2B3C;
    letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 6px;
}
.valor-giro-cuenta {
    font-size: 0.82rem; font-weight: 600; color: #4A6278;
    margin-bottom: 4px;
}
.valor-giro-hint {
    font-size: 0.75rem; color: #9AB0C0; line-height: 1.4;
}
/* Estilos Simulador de Garantías CrediOro (Diseño Moderno) */
.sim-section-card {
    background: #FFFFFF !important;
    border: 1.5px solid #E2EAF0 !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 2px 10px rgba(26, 43, 60, 0.04) !important;
}
.sim-section-title {
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    color: #1A2B3C !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 12px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
}
.sim-badge-tag {
    background: #EBF9FD !important;
    color: #0FA8CC !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    padding: 3px 10px !important;
    border-radius: 12px !important;
    border: 1px solid #C2EEFA !important;
}
.sim-grid {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)) !important;
    gap: 10px !important;
}
.sim-kpi-item {
    background: #F8FAFC !important;
    border: 1px solid #E2EAF0 !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
    text-align: left !important;
}
.sim-kpi-item-highlight {
    background: linear-gradient(135deg, #F0FAFD 0%, #FFFFFF 100%) !important;
    border: 1.5px solid #C2EEFA !important;
}
.sim-kpi-label {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    color: #7A94A8 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    margin-bottom: 4px !important;
}
.sim-kpi-val {
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: #1A2B3C !important;
}
.sim-kpi-val-main {
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    color: #0FA8CC !important;
}

/* Tarjetas de Decisión del Estudio (Módulo ORC / CrediOro) */
.decision-card {
    border-radius: 14px !important;
    padding: 20px 24px !important;
    margin: 8px 0 16px !important;
    display: flex !important;
    align-items: center !important;
    gap: 18px !important;
    box-sizing: border-box !important;
    width: 100% !important;
    transition: all 0.25s ease-in-out !important;
}

.decision-card-aprobado {
    background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%) !important;
    border: 1.5px solid #A7F3D0 !important;
    border-left: 6px solid #10B981 !important;
    box-shadow: 0 4px 18px rgba(16, 185, 129, 0.08) !important;
}

.decision-card-rechazado {
    background: linear-gradient(135deg, #FEF2F2 0%, #FFFFFF 100%) !important;
    border: 1.5px solid #FECDD3 !important;
    border-left: 6px solid #EF4444 !important;
    box-shadow: 0 4px 18px rgba(239, 68, 68, 0.08) !important;
}

.decision-card-pendiente {
    background: linear-gradient(135deg, #F0FAFD 0%, #FFFFFF 100%) !important;
    border: 1.5px solid #C2EEFA !important;
    border-left: 6px solid #19BCE0 !important;
    box-shadow: 0 4px 18px rgba(25, 188, 224, 0.08) !important;
}

.decision-icon-wrapper {
    width: 52px !important;
    height: 52px !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.6rem !important;
    flex-shrink: 0 !important;
}

.decision-icon-aprobado {
    background: #D1FAE5 !important;
    color: #059669 !important;
    border: 1.5px solid #A7F3D0 !important;
}

.decision-icon-rechazado {
    background: #FEE2E2 !important;
    color: #DC2626 !important;
    border: 1.5px solid #FECDD3 !important;
}

.decision-icon-pendiente {
    background: #EBF9FD !important;
    color: #0FA8CC !important;
    border: 1.5px solid #C2EEFA !important;
}

.decision-content {
    flex: 1 !important;
}

.decision-header-row {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    margin-bottom: 4px !important;
}

.decision-title-tag {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: #7A94A8 !important;
}

.decision-badge {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    padding: 3px 10px !important;
    border-radius: 20px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

.decision-badge-aprobado {
    background: #D1FAE5 !important;
    color: #065F46 !important;
    border: 1px solid #A7F3D0 !important;
}

.decision-badge-rechazado {
    background: #FEE2E2 !important;
    color: #991B1B !important;
    border: 1px solid #FECDD3 !important;
}

.decision-badge-pendiente {
    background: #EBF9FD !important;
    color: #0FA8CC !important;
    border: 1px solid #C2EEFA !important;
}

.decision-main-text {
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
    font-family: 'Inter', sans-serif !important;
    line-height: 1.25 !important;
    margin-bottom: 4px !important;
}

.decision-text-aprobado { color: #065F46 !important; }
.decision-text-rechazado { color: #991B1B !important; }
.decision-text-pendiente { color: #1A2B3C !important; }

.decision-subtext {
    font-size: 0.84rem !important;
    color: #4A6278 !important;
    line-height: 1.45 !important;
    margin-bottom: 6px !important;
}

.decision-footer-info {
    display: flex !important;
    align-items: center !important;
    gap: 14px !important;
    font-size: 0.75rem !important;
    color: #7A94A8 !important;
    font-weight: 500 !important;
    flex-wrap: wrap !important;
}

.decision-status-pill {
    display: inline-flex !important;
    align-items: center !important;
    gap: 5px !important;
    font-weight: 600 !important;
}

.decision-status-pill-aprobado { color: #059669 !important; }
.decision-status-pill-rechazado { color: #DC2626 !important; }
.decision-status-pill-pendiente { color: #0FA8CC !important; }

/* Estilos para Flujo Lineal Continuo y Navegación */
html {
    scroll-behavior: smooth !important;
}

.linear-flow-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #FFFFFF;
    border: 1px solid #E2EAF0;
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(26, 43, 60, 0.04);
    gap: 8px;
    flex-wrap: wrap;
}

.linear-step-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #4A6278;
    text-decoration: none !important;
    padding: 6px 10px;
    border-radius: 8px;
    transition: all 0.2s ease;
}

.linear-step-item:hover {
    background: #EBF9FD;
    color: #19BCE0;
}

.linear-step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #19BCE0;
    color: #FFFFFF;
    font-size: 0.7rem;
    font-weight: 700;
}

.sidebar-nav-link {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    margin-bottom: 6px;
    background: #F8FAFC;
    border: 1px solid #E2EAF0;
    border-radius: 8px;
    color: #2D3F50 !important;
    font-size: 0.82rem;
    font-weight: 600;
    text-decoration: none !important;
    transition: all 0.2s ease;
}

.sidebar-nav-link:hover {
    background: #EBF9FD;
    border-color: #19BCE0;
    color: #0FA8CC !important;
    transform: translateX(2px);
}

/* ─────────────────────────────────────────────────────────────
   Estilos: Consulta de Insolvencia en Simulador (src/data/insolvency/)
   ───────────────────────────────────────────────────────────── */
.insolvencia-card-blocked {
    background: linear-gradient(135deg, #FFF1F2 0%, #FFE4E6 100%) !important;
    border: 1.5px solid #F43F5E !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    margin: 12px 0 16px 0 !important;
    box-shadow: 0 4px 16px rgba(244, 63, 94, 0.12) !important;
    animation: fadeIn 0.3s ease-in-out !important;
}

.insolvencia-header-row {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    margin-bottom: 12px !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
}

.insolvencia-badge-blocked {
    background: #E11D48 !important;
    color: #FFFFFF !important;
    font-size: 0.74rem !important;
    font-weight: 800 !important;
    padding: 4px 12px !important;
    border-radius: 20px !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
}

.insolvencia-badge-ok {
    background: #059669 !important;
    color: #FFFFFF !important;
    font-size: 0.74rem !important;
    font-weight: 700 !important;
    padding: 4px 12px !important;
    border-radius: 20px !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
}

.insolvencia-card-ok {
    background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%) !important;
    border: 1.5px solid #86EFAC !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin: 10px 0 14px 0 !important;
    box-shadow: 0 2px 8px rgba(34, 197, 94, 0.08) !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    animation: fadeIn 0.25s ease-in-out !important;
}

.insolvencia-title-blocked {
    color: #9F1239 !important;
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    font-family: 'Inter', sans-serif !important;
}

.insolvencia-detail-grid {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)) !important;
    gap: 10px !important;
    margin: 12px 0 !important;
    background: rgba(255, 255, 255, 0.85) !important;
    padding: 12px 14px !important;
    border-radius: 8px !important;
    border: 1px solid #FECDD3 !important;
}

.insolvencia-detail-item {
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
}

.insolvencia-detail-lbl {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    color: #9F1239 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

.insolvencia-detail-val {
    font-size: 0.92rem !important;
    font-weight: 700 !important;
    color: #1A2B3C !important;
    word-break: break-word !important;
}

.insolvencia-notice {
    font-size: 0.82rem !important;
    color: #BE123C !important;
    font-weight: 600 !important;
    line-height: 1.4 !important;
    margin-top: 8px !important;
    padding-top: 8px !important;
    border-top: 1px dashed #FDA4AF !important;
}
</style>
""", unsafe_allow_html=True)

