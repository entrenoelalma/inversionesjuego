import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="Panel de Inversiones — Banda de Brothers",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Estilos ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stApp { background-color: #0f1117; color: #e8e8e8; }
    [data-testid="stSidebar"] { background-color: #1a1d27; border-right: 1px solid #2d3148; }
    .metric-card {
        background: linear-gradient(135deg, #1e2235 0%, #252840 100%);
        border: 1px solid #3a3f5c;
        border-radius: 12px;
        padding: 18px 20px;
        margin: 6px 0;
    }
    .metric-card h4 { color: #8891b4; font-size: 12px; margin: 0 0 6px 0; text-transform: uppercase; letter-spacing: 1px; }
    .metric-card .value { color: #e8e8e8; font-size: 26px; font-weight: 700; margin: 0; }
    .metric-card .delta { font-size: 13px; margin-top: 4px; }
    .positive { color: #4ade80; }
    .negative { color: #f87171; }
    .neutral { color: #94a3b8; }
    .section-title {
        color: #c9d1f5;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 16px 0 8px 0;
        border-bottom: 1px solid #2d3148;
        padding-bottom: 6px;
    }
    .alert-box {
        background: linear-gradient(135deg, #1e2d1e, #1a2a1a);
        border: 1px solid #3d6b3d;
        border-left: 4px solid #4ade80;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0;
        font-size: 14px;
        color: #b8f0b8;
    }
    .alert-box-warn {
        background: linear-gradient(135deg, #2d2614, #261f0a);
        border: 1px solid #7a6020;
        border-left: 4px solid #fbbf24;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0;
        font-size: 14px;
        color: #fde68a;
    }
    .note-box {
        background: #1a1d27;
        border: 1px solid #2d3148;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        color: #8891b4;
        font-style: italic;
        margin: 4px 0;
    }
    div[data-testid="stMetricValue"] { color: #e8e8e8; }
    .stSlider > div > div { background: #2d3148; }
    h1, h2, h3 { color: #c9d1f5 !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_excel("dataset.xlsx", sheet_name="Data_Flat", header=0)
    cols = df.iloc[0].tolist()
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = cols
    df["Año"] = pd.to_numeric(df["Año"], errors="coerce")
    for c in df.columns:
        if c not in ["Año", "ARG_Nota_Economia", "ARG_Nota_Agro", "ARG_Tipo_Cambio_Ref"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Año"])
    df["Año"] = df["Año"].astype(int)
    return df.sort_values("Año").reset_index(drop=True)


df = load_data()

ACTIVOS = {
    "🥇 Oro (USD/oz)": "Oro_USD_oz",
    "🛢️ Petróleo WTI (USD/barril)": "Petroleo_WTI_USD_barril",
    "🌾 Tierra ARG (USD/ha)": "ARG_Tierra_Ha_USD",
    "🏙️ Inmueble CABA (USD/m²)": "ARG_Inmueble_Venta_m2_USD",
    "🌱 Soja ARG (USD/qq)": "ARG_Soja_USD_qq",
    "🌽 Maíz ARG (USD/qq)": "ARG_Maiz_USD_qq",
    "🌾 Trigo ARG (USD/qq)": "ARG_Trigo_USD_qq",
    "🐄 Novillo ARG (USD/kg)": "ARG_Novillo_USD_kg_vivo",
    "🌽 Tierra Iowa USA (USD/ha)": "USA_Iowa_USD_ha",
    "🗽 Inmueble Manhattan (USD/m²)": "NYC_Venta_m2_USD",
    "🌱 Soja USA (USD/ton)": "USA_Soja_USD_ton",
    "🌽 Maíz USA (USD/ton)": "USA_Maiz_USD_ton",
}

RATIOS = {
    "Ha campo / m² depto BN": "ARG_Ratio_Ha_m2_BN",
    "Ha campo / meses alquiler": "ARG_Ratio_Ha_meses_alq",
    "Ha campo / qq soja": "ARG_Ratio_Ha_qq_soja",
    "Ha campo / qq maíz": "ARG_Ratio_Ha_qq_maiz",
    "Ha campo / qq trigo": "ARG_Ratio_Ha_qq_trigo",
    "Ha campo / kg novillo": "ARG_Ratio_Ha_kg_novillo",
}

COLORES = [
    "#6366f1", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6",
    "#06b6d4", "#f97316", "#ec4899", "#14b8a6", "#a855f7"
]

# ─── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Panel de Control")
    st.markdown('<div class="section-title">Período de análisis</div>', unsafe_allow_html=True)
    min_y, max_y = int(df["Año"].min()), int(df["Año"].max())
    año_rango = st.slider("", min_y, max_y, (1990, max_y), label_visibility="collapsed")

    st.markdown('<div class="section-title">Capital disponible (USD)</div>', unsafe_allow_html=True)
    capital = st.slider("", 1_000_000, 10_000_000, 3_000_000, 250_000,
                        format="$%d", label_visibility="collapsed")
    st.caption(f"Capital: **${capital:,.0f}**")

    st.markdown('<div class="section-title">Vista del gráfico</div>', unsafe_allow_html=True)
    modo_viz = st.radio("", ["Valores absolutos (USD)", "Índice base 100", "Retorno acumulado %"],
                        label_visibility="collapsed")

    st.markdown('<div class="section-title">Activos a comparar</div>', unsafe_allow_html=True)
    seleccion = []
    for nombre in ACTIVOS:
        default = nombre in ["🥇 Oro (USD/oz)", "🌾 Tierra ARG (USD/ha)", "🏙️ Inmueble CABA (USD/m²)", "🌽 Tierra Iowa USA (USD/ha)"]
        if st.checkbox(nombre, value=default, key=f"chk_{nombre}"):
            seleccion.append(nombre)

    st.markdown("---")
    st.markdown("**🛡️ Perfil:** Inversor conservador")
    st.markdown("**💰 Foco:** Preservación de capital en USD")
    st.caption("Todos los valores en USD nominales")

# ─── Filtrar datos ─────────────────────────────────────────────────────────
df_f = df[(df["Año"] >= año_rango[0]) & (df["Año"] <= año_rango[1])].copy()

# ─── Header ────────────────────────────────────────────────────────────────
st.markdown("# 📈 Panel de Inversiones — Banda de Brothers")
st.markdown(f"**Período:** {año_rango[0]}–{año_rango[1]}  ·  **Capital:** ${capital:,.0f}  ·  **Perfil:** Conservador")
st.markdown("---")

# ─── Métricas resumen ──────────────────────────────────────────────────────
if seleccion:
    st.markdown("### 📌 Métricas Clave del Período Seleccionado")
    cols_met = st.columns(min(len(seleccion), 4))
    for i, nombre in enumerate(seleccion[:8]):
        col_key = ACTIVOS[nombre]
        serie = df_f[["Año", col_key]].dropna()
        if len(serie) >= 2:
            v_ini = serie.iloc[0][col_key]
            v_fin = serie.iloc[-1][col_key]
            ret_total = ((v_fin / v_ini) - 1) * 100 if v_ini > 0 else 0
            n_años = serie.iloc[-1]["Año"] - serie.iloc[0]["Año"]
            cagr = ((v_fin / v_ini) ** (1 / n_años) - 1) * 100 if n_años > 0 and v_ini > 0 else 0
            capital_final = capital * (v_fin / v_ini) if v_ini > 0 else capital
            delta_class = "positive" if ret_total > 0 else "negative"
            with cols_met[i % 4]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{nombre}</h4>
                    <div class="value">${v_fin:,.0f}</div>
                    <div class="delta {delta_class}">▲ {ret_total:.1f}% total · CAGR {cagr:.1f}%/año</div>
                    <div class="delta neutral">Capital → ${capital_final:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# ─── Gráfico principal ─────────────────────────────────────────────────────
st.markdown("### 📊 Evolución Histórica")

tab1, tab2, tab3 = st.tabs(["📈 Serie de Precios", "⚖️ Ratios de Valor ARG", "🧮 Simulador de Portafolio"])

with tab1:
    if not seleccion:
        st.info("Seleccioná al menos un activo en el panel lateral.")
    else:
        fig = go.Figure()
        for i, nombre in enumerate(seleccion):
            col_key = ACTIVOS[nombre]
            serie = df_f[["Año", col_key]].dropna()
            if len(serie) < 2:
                continue
            color = COLORES[i % len(COLORES)]
            y_vals = serie[col_key].values

            if modo_viz == "Índice base 100":
                y_plot = (y_vals / y_vals[0]) * 100
                ytitle = "Índice (base 100)"
            elif modo_viz == "Retorno acumulado %":
                y_plot = ((y_vals / y_vals[0]) - 1) * 100
                ytitle = "Retorno acumulado (%)"
            else:
                y_plot = y_vals
                ytitle = "Precio (USD)"

            fig.add_trace(go.Scatter(
                x=serie["Año"], y=y_plot,
                name=nombre,
                line=dict(color=color, width=2.5),
                mode="lines+markers",
                marker=dict(size=4),
                hovertemplate=f"<b>{nombre}</b><br>Año: %{{x}}<br>Valor: %{{y:,.1f}}<extra></extra>"
            ))

        # Eventos históricos ARG relevantes
        eventos = {
            2001: ("Crisis 2001", "#f87171"),
            2018: ("Crisis peso 2018", "#fbbf24"),
            2020: ("Pandemia", "#818cf8"),
        }
        for año_ev, (label, color_ev) in eventos.items():
            if año_rango[0] <= año_ev <= año_rango[1]:
                fig.add_vline(x=año_ev, line_dash="dot", line_color=color_ev, opacity=0.5,
                              annotation_text=label, annotation_font_color=color_ev,
                              annotation_font_size=10)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f1117",
            plot_bgcolor="#131625",
            legend=dict(bgcolor="#1a1d27", bordercolor="#2d3148", borderwidth=1, font_color="#c9d1f5"),
            xaxis=dict(title="Año", gridcolor="#1e2235", tickfont_color="#8891b4"),
            yaxis=dict(title=ytitle, gridcolor="#1e2235", tickfont_color="#8891b4"),
            hovermode="x unified",
            height=480,
            margin=dict(l=10, r=10, t=30, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabla de retornos
        st.markdown("#### 📋 Tabla de Retornos por Activo")
        rows = []
        for nombre in seleccion:
            col_key = ACTIVOS[nombre]
            serie = df_f[["Año", col_key]].dropna()
            if len(serie) < 2:
                continue
            v_ini = serie.iloc[0][col_key]
            v_fin = serie.iloc[-1][col_key]
            n_años = serie.iloc[-1]["Año"] - serie.iloc[0]["Año"]
            ret_total = ((v_fin / v_ini) - 1) * 100 if v_ini > 0 else 0
            cagr = ((v_fin / v_ini) ** (1 / n_años) - 1) * 100 if n_años > 0 and v_ini > 0 else 0
            max_v = serie[col_key].max()
            min_v = serie[col_key].min()
            capital_f = capital * (v_fin / v_ini) if v_ini > 0 else capital
            rows.append({
                "Activo": nombre,
                f"Valor {año_rango[0]}": f"${v_ini:,.0f}",
                f"Valor {año_rango[1]}": f"${v_fin:,.0f}",
                "Retorno Total": f"{ret_total:+.1f}%",
                "CAGR anual": f"{cagr:+.1f}%",
                "Máximo hist.": f"${max_v:,.0f}",
                "Mínimo hist.": f"${min_v:,.0f}",
                f"Capital ${capital/1e6:.1f}M → ": f"${capital_f:,.0f}",
            })
        if rows:
            df_tabla = pd.DataFrame(rows)
            st.dataframe(df_tabla.set_index("Activo"), use_container_width=True,
                         column_config={col: st.column_config.TextColumn(col) for col in df_tabla.columns})

with tab2:
    st.markdown("#### ⚖️ Ratios de Valor Relativos — Argentina")
    st.markdown("""
    <div class="note-box">
    Estos ratios muestran cuántas unidades de un activo equivalen a una hectárea de campo en Argentina.
    Valores altos = campo <em>caro</em> en relación al otro activo. Valores bajos = campo <em>barato</em> (posible compra).
    </div>
    """, unsafe_allow_html=True)

    ratios_sel = st.multiselect(
        "Seleccioná ratios a visualizar:",
        list(RATIOS.keys()),
        default=["Ha campo / m² depto BN", "Ha campo / qq soja", "Ha campo / meses alquiler"]
    )

    if ratios_sel:
        fig2 = make_subplots(
            rows=len(ratios_sel), cols=1,
            subplot_titles=ratios_sel,
            shared_xaxes=True,
            vertical_spacing=0.06
        )
        for i, ratio_name in enumerate(ratios_sel):
            col_key = RATIOS[ratio_name]
            serie = df_f[["Año", col_key]].dropna()
            if len(serie) < 2:
                continue
            color = COLORES[i % len(COLORES)]
            media = serie[col_key].mean()
            fig2.add_trace(go.Scatter(
                x=serie["Año"], y=serie[col_key],
                name=ratio_name, line=dict(color=color, width=2),
                hovertemplate=f"<b>{ratio_name}</b><br>Año: %{{x}}<br>Ratio: %{{y:,.1f}}<extra></extra>"
            ), row=i+1, col=1)
            fig2.add_hline(y=media, line_dash="dash", line_color="#94a3b8", opacity=0.4,
                           annotation_text=f"Media: {media:.1f}", annotation_font_size=10,
                           row=i+1, col=1)

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f1117",
            plot_bgcolor="#131625",
            height=280 * len(ratios_sel),
            showlegend=False,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        for i in range(1, len(ratios_sel)+1):
            fig2.update_xaxes(gridcolor="#1e2235", row=i, col=1)
            fig2.update_yaxes(gridcolor="#1e2235", row=i, col=1)
        st.plotly_chart(fig2, use_container_width=True)

        # Señales de valor actual
        st.markdown("#### 🚦 Señales de Valor Actual")
        ultimo = df_f[df_f["Año"] == df_f["Año"].max()].iloc[0] if len(df_f) > 0 else None
        if ultimo is not None:
            for ratio_name in ratios_sel:
                col_key = RATIOS[ratio_name]
                serie = df_f[["Año", col_key]].dropna()
                if len(serie) < 5:
                    continue
                media = serie[col_key].mean()
                std = serie[col_key].std()
                val_actual = pd.to_numeric(df[df["Año"] == df["Año"].max()][col_key].values[0], errors="coerce")
                if pd.isna(val_actual):
                    continue
                z = (val_actual - media) / std if std > 0 else 0
                if z < -0.5:
                    icon, clase, msg = "🟢", "alert-box", f"Campo <strong>barato</strong> en términos históricos (z={z:.1f}σ). Potencial oportunidad de compra."
                elif z > 0.5:
                    icon, clase, msg = "🔴", "alert-box-warn", f"Campo <strong>caro</strong> en términos históricos (z={z:.1f}σ). Momento de cautela."
                else:
                    icon, clase, msg = "🟡", "note-box", f"Campo en zona <strong>neutral</strong> (z={z:.1f}σ). Sin señal clara."
                st.markdown(f'<div class="{clase}">{icon} <b>{ratio_name}</b>: {msg}</div>', unsafe_allow_html=True)

with tab3:
    st.markdown("#### 🧮 Simulador de Portafolio Conservador")
    st.markdown("""
    <div class="note-box">
    Distribuí tu capital entre los activos disponibles y visualizá cómo habría evolucionado históricamente.
    Pensado para inversores conservadores con capital de USD 1–10M.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Distribuí el portafolio (%):**")
    col_p1, col_p2, col_p3 = st.columns(3)
    pesos = {}
    activos_sim = [
        ("🥇 Oro", "Oro_USD_oz"),
        ("🌾 Tierra ARG", "ARG_Tierra_Ha_USD"),
        ("🏙️ CABA m²", "ARG_Inmueble_Venta_m2_USD"),
        ("🌽 Iowa USA", "USA_Iowa_USD_ha"),
        ("🗽 Manhattan", "NYC_Venta_m2_USD"),
        ("🌱 Soja ARG", "ARG_Soja_USD_qq"),
    ]
    for i, (nombre, col_key) in enumerate(activos_sim):
        defaults = [30, 25, 15, 15, 10, 5]
        col_obj = [col_p1, col_p2, col_p3][i % 3]
        with col_obj:
            pesos[col_key] = st.number_input(nombre, 0, 100, defaults[i], 5, key=f"peso_{col_key}")

    total_pesos = sum(pesos.values())
    if total_pesos != 100:
        st.warning(f"⚠️ Los pesos suman {total_pesos}%. Deben sumar exactamente 100%.")
    else:
        # Calcular evolución del portafolio
        años_sim = df_f["Año"].values
        portafolio_vals = []
        for año in años_sim:
            row = df_f[df_f["Año"] == año].iloc[0]
            val_total = 0
            valid = True
            for col_key, peso in pesos.items():
                if peso == 0:
                    continue
                v = pd.to_numeric(row.get(col_key, np.nan), errors="coerce")
                if pd.isna(v):
                    valid = False
                    break
                val_total += peso / 100
            portafolio_vals.append(1.0 if valid else np.nan)

        # Calcular retorno real de portafolio
        retornos_por_activo = {}
        base_año = df_f.dropna(subset=[col_key for col_key, _ in [(c, None) for c in pesos]])
        año_inicio = df_f["Año"].min()

        port_series = pd.Series(index=df_f["Año"], dtype=float)
        for año in df_f["Año"]:
            row_ini = df_f[df_f["Año"] == año_inicio].iloc[0] if año_inicio in df_f["Año"].values else None
            row_cur = df_f[df_f["Año"] == año].iloc[0]
            total = 0
            all_ok = True
            for col_key, peso in pesos.items():
                if peso == 0:
                    continue
                v0 = pd.to_numeric(df_f[df_f["Año"] == año_inicio][col_key].values[0], errors="coerce") if año_inicio in df_f["Año"].values else np.nan
                v1 = pd.to_numeric(row_cur[col_key], errors="coerce")
                if pd.isna(v0) or pd.isna(v1) or v0 == 0:
                    all_ok = False
                    break
                total += (peso / 100) * (v1 / v0)
            port_series[año] = total if all_ok else np.nan

        port_series = port_series.dropna()
        capital_evol = port_series * capital

        fig3 = go.Figure()
        # Portafolio total
        fig3.add_trace(go.Scatter(
            x=port_series.index, y=capital_evol.values,
            name="Portafolio combinado",
            line=dict(color="#6366f1", width=3),
            fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
            hovertemplate="Año: %{x}<br>Capital: $%{y:,.0f}<extra></extra>"
        ))
        # Línea de capital inicial
        fig3.add_hline(y=capital, line_dash="dash", line_color="#94a3b8",
                       annotation_text=f"Capital inicial: ${capital:,.0f}",
                       annotation_font_color="#94a3b8", opacity=0.5)

        # Cada activo por separado
        for col_key, peso in pesos.items():
            if peso == 0:
                continue
            nombre_a = next((n for n, c in activos_sim if c == col_key), col_key)
            serie_a = df_f[["Año", col_key]].dropna()
            if len(serie_a) < 2:
                continue
            v0 = serie_a.iloc[0][col_key]
            evol = capital * (peso / 100) * (serie_a[col_key] / v0)
            fig3.add_trace(go.Scatter(
                x=serie_a["Año"], y=evol,
                name=f"{nombre_a} ({peso}%)",
                line=dict(width=1.5, dash="dot"),
                hovertemplate=f"{nombre_a}: $%{{y:,.0f}}<extra></extra>"
            ))

        fig3.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f1117",
            plot_bgcolor="#131625",
            yaxis_title="Capital (USD)",
            xaxis_title="Año",
            hovermode="x unified",
            legend=dict(bgcolor="#1a1d27", bordercolor="#2d3148", borderwidth=1),
            height=450,
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig3, use_container_width=True)

        if len(port_series) >= 2:
            v_ini_p = capital
            v_fin_p = capital_evol.iloc[-1]
            n_años_p = port_series.index[-1] - port_series.index[0]
            ret_p = ((v_fin_p / v_ini_p) - 1) * 100
            cagr_p = ((v_fin_p / v_ini_p) ** (1 / n_años_p) - 1) * 100 if n_años_p > 0 else 0
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h4>Capital Final</h4><div class="value">${v_fin_p:,.0f}</div></div>', unsafe_allow_html=True)
            with c2:
                cls = "positive" if ret_p > 0 else "negative"
                st.markdown(f'<div class="metric-card"><h4>Retorno Total</h4><div class="value {cls}">{ret_p:+.1f}%</div></div>', unsafe_allow_html=True)
            with c3:
                cls = "positive" if cagr_p > 0 else "negative"
                st.markdown(f'<div class="metric-card"><h4>CAGR Anual</h4><div class="value {cls}">{cagr_p:+.1f}%/año</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ─── Notas históricas ──────────────────────────────────────────────────────
with st.expander("📜 Notas históricas del período"):
    notas = df_f[["Año", "ARG_Nota_Economia", "ARG_Nota_Agro", "ARG_Tipo_Cambio_Ref"]].dropna(
        subset=["ARG_Nota_Economia"]
    )
    if len(notas) > 0:
        for _, row in notas.iterrows():
            st.markdown(f"""
            **{int(row['Año'])}** — {row['ARG_Nota_Economia']}  
            &nbsp;&nbsp;&nbsp;🌾 _{row['ARG_Nota_Agro'] if pd.notna(row['ARG_Nota_Agro']) else ''}_
            &nbsp;&nbsp;💱 _{row['ARG_Tipo_Cambio_Ref'] if pd.notna(row['ARG_Tipo_Cambio_Ref']) else ''}_
            """)
    else:
        st.info("No hay notas para el período seleccionado.")

st.caption("Fuente: Dataset Maestro Unificado — Banda de Brothers · Todos los valores en USD nominales · No constituye asesoramiento financiero.")
