import streamlit as st

st.set_page_config(page_title="Disponibilidad GLP", layout="centered")

# ----------------------------------------------
# FUNCIONES
# ----------------------------------------------

def tanque_zeppelin(label, nivel, capacidad):
    # evita división por cero y limita entre 0-100
    porcentaje = 0
    if capacidad > 0:
        porcentaje = max(0, min(100, (float(nivel) / float(capacidad)) * 100))
    porcentaje_str = f"{porcentaje:.1f}"

    tanque_html = f"""
    <div style="text-align:center; margin-bottom:10px; font-family: sans-serif;">
      <div style="display:inline-block; position:relative; width:320px; height:100px;">
        <!-- cuerpo zepelín -->
        <div style="
            width:100%;
            height:60px;
            background: linear-gradient(90deg,#e6eefc,#cfe8ff);
            border-radius:40px;
            border:1px solid #9aa6b2;
            position:absolute;
            top:20px;
            overflow:hidden;">
            <!-- relleno -->
            <div style="
                position:absolute;
                left:0;
                top:0;
                bottom:0;
                width:{porcentaje}%;
                background: linear-gradient(90deg,#10b981,#06b6d4);
                transition: width 0.6s ease;">
            </div>
        </div>

        <!-- extremos tipo tanque -->
        <div style="position:absolute; left:-25px; top:30px; width:50px; height:20px;
                    background:#e6eefc; border-radius:50%; border:1px solid #9aa6b2;
                    transform:translateY(-50%);"></div>

        <div style="position:absolute; right:-25px; top:30px; width:50px; height:20px;
                    background:#e6eefc; border-radius:50%; border:1px solid #9aa6b2;
                    transform:translateY(-50%);"></div>

      </div>

      <div style="margin-top:6px; font-weight:700;">{label}</div>
      <div style="font-size:13px; color:#374151;">Nivel: {porcentaje_str}% — {nivel:,} / {capacidad:,}</div>
    </div>
    """
    st.markdown(tanque_html, unsafe_allow_html=True)


def calcular_glp(capacidad_m3, porcentaje):
    """Convierte porcentaje a m3 reales."""
    return (porcentaje / 100) * capacidad_m3


def puede_cargar_camion(espacio_disponible_m3):
    """Convierte el GLP del camión (24000 kg ≈ 46.15 m3) y revisa si entra."""
    camion_m3 = 46.15
    return espacio_disponible_m3 >= camion_m3, camion_m3


# ----------------------------------------------
# INTERFAZ
# ----------------------------------------------

st.title("🛢️ Disponibilidad de GLP — Planta")

st.write("App simplificada para ver **capacidad disponible**, **capacidad de trabajo** y si **entra o no** el camión de GLP.")

st.divider()

# ----------------------------------------------
# ENTRADAS
# ----------------------------------------------

st.subheader("Cargar datos de tanques")

TANQUE_GRANDE = 49170
TANQUE_CHICO = 30694

c1, c2 = st.columns(2)

with c1:
    porc_grande = st.number_input("Tanque Grande (%)", 0, 100, 85)

with c2:
    porc_chico = st.number_input("Tanque Chico (%)", 0, 100, 85)

st.subheader("Nivel visual de tanques")

# Mostrar los zepelines arriba
tanque_zeppelin("Tanque Grande", calcular_glp(TANQUE_GRANDE, porc_grande), TANQUE_GRANDE)
tanque_zeppelin("Tanque Chico", calcular_glp(TANQUE_CHICO, porc_chico), TANQUE_CHICO)

st.divider()

# ----------------------------------------------
# CÁLCULOS
# ----------------------------------------------

nivel_g = calcular_glp(TANQUE_GRANDE, porc_grande)
nivel_c = calcular_glp(TANQUE_CHICO, porc_chico)

total = nivel_g + nivel_c
capacidad_total = TANQUE_GRANDE + TANQUE_CHICO
espacio_disponible = capacidad_total - total

puede_cargar, camion_m3 = puede_cargar_camion(espacio_disponible)

# ----------------------------------------------
# RESULTADOS
# ----------------------------------------------

st.subheader("Resultados del sistema")

st.write(f"🔵 **Capacidad total actual:** {total:,.2f} m³")
st.write(f"⚪ **Espacio disponible:** {espacio_disponible:,.2f} m³")
st.write(f"🚚 El camión aporta: {camion_m3:.2f} m³ (equivalente a 24.000 kg)")

if puede_cargar:
    st.success("✅ El camión **SÍ** puede descargar GLP.")
else:
    st.error("❌ El camión **NO** puede descargar GLP — falta espacio.")

st.divider()

st.caption("Versión inicial simplificada — lista para ampliar con consumos, líneas, velocidades y cálculo de horas de trabajo.")

