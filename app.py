import streamlit as st

st.set_page_config(page_title="GLP Simplificado", layout="centered")

# ---------------------------------------
# Parámetros fijos
# ---------------------------------------
T1_CAP = 49170      # m3 tanque grande
T2_CAP = 30694      # m3 tanque chico
DENSIDAD = 0.54     # kg/m3
CAMION_KG = 24000   # kg
C2_SPEED = 52       # env/min fijo

CONSUMOS_C3 = {"Ambiental": 87.6, "Desinfectante": 69.5, "Selton": 93.6}
CONSUMOS_C2 = {"Jirafa": 100.7, "360g": 69.5}

# ---------------------------------------
# Encabezado
# ---------------------------------------
st.title("🔋 GLP - Vista Simplificada")

st.markdown("Esta versión muestra solo: tanques, capacidad de trabajo y si el camión puede cargar GLP.")

# ---------------------------------------
# Entradas
# ---------------------------------------
col_p1, col_p2 = st.columns(2)

with col_p1:
    p1 = st.number_input("Tanque grande (%)", 0, 100, 85)
with col_p2:
    p2 = st.number_input("Tanque chico (%)", 0, 100, 85)

minimo = st.number_input("Mínimo (%)", 0, 100, 5)

linea = st.selectbox("Línea activa", ["C3", "C2", "C3 y C2"])

formato_c3 = None
formato_c2 = None
if linea in ("C3", "C3 y C2"):
    formato_c3 = st.selectbox("Formato C3", list(CONSUMOS_C3.keys()))
if linea in ("C2", "C3 y C2"):
    formato_c2 = st.selectbox("Formato C2", list(CONSUMOS_C2.keys()))

speed_c3 = st.number_input("Velocidad C3 (env/min)", 1, 2000, 195)

# ---------------------------------------
# Cálculos tanques
# ---------------------------------------
def porcentaje_a_kg(cap_m3, pct):
    return cap_m3 * (pct / 100) * DENSIDAD

t1_kg = porcentaje_a_kg(T1_CAP, p1)
t2_kg = porcentaje_a_kg(T2_CAP, p2)
total_kg = t1_kg + t2_kg

min_kg = porcentaje_a_kg(T1_CAP + T2_CAP, minimo)
usable_kg = max(0, total_kg - min_kg)

# Consumos
consumo_total = 0

if linea == "C3":
    c = CONSUMOS_C3[formato_c3]
    consumo_total = (c * speed_c3) / 1000
elif linea == "C2":
    c = CONSUMOS_C2[formato_c2]
    consumo_total = (c * C2_SPEED) / 1000
else:
    c3 = (CONSUMOS_C3[formato_c3] * speed_c3) / 1000
    c2 = (CONSUMOS_C2[formato_c2] * C2_SPEED) / 1000
    consumo_total = c3 + c2

tiempo_min = usable_kg / consumo_total if consumo_total > 0 else 0
h = int(tiempo_min // 60)
m = int(tiempo_min % 60)

# Espacio disponible
cap_total_kg = (T1_CAP + T2_CAP) * DENSIDAD
espacio_disp = cap_total_kg - total_kg

puede_cargar = CAMION_KG <= espacio_disp

# ---------------------------------------
# UI visual tanques horizontales
# ---------------------------------------
st.markdown("---")
st.subheader("🛢️ Tanques (Vista Horizontal)")

def tanque_horizontal(pct, color):
    return f"""
    <div style="width:350px; height:40px; border-radius:20px; background:#e5e7eb; border:1px solid #cbd5e1; overflow:hidden;">
        <div style="width:{pct}%; height:100%; background:{color}; transition:width 0.6s;"></div>
    </div>
    """

def color_pct(pct):
    return "#ef4444" if pct <= minimo else "#10b981"

col_t1, col_t2 = st.columns(2)

with col_t1:
    st.markdown("**Tanque Grande**")
    st.markdown(tanque_horizontal(p1, color_pct(p1)), unsafe_allow_html=True)
    st.write(f"{p1}% — {t1_kg:,.1f} kg")

with col_t2:
    st.markdown("**Tanque Chico**")
    st.markdown(tanque_horizontal(p2, color_pct(p2)), unsafe_allow_html=True)
    st.write(f"{p2}% — {t2_kg:,.1f} kg")

# ---------------------------------------
# Resultados finales simples
# ---------------------------------------
st.markdown("---")
st.subheader("📌 Información de Trabajo")

st.write(f"**GLP utilizable:** {usable_kg:,.1f} kg")

if tiempo_min > 0:
    st.success(f"Capacidad de trabajo: **{h} h {m} min**")
else:
    st.error("Sin capacidad de trabajo (no hay GLP por encima del mínimo).")

st.markdown("---")
st.subheader("🚚 Carga del camión")

st.write(f"**Espacio disponible:** {espacio_disp:,.1f} kg")
st.write(f"**Requiere cargar:** {CAMION_KG:,} kg")

if puede_cargar:
    st.success("✔️ El camión **puede** descargar completamente.")
else:
    st.error("❌ El camión **NO puede** descargar completo.")

