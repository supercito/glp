# app.py
import streamlit as st
from math import floor

st.set_page_config(page_title="Calculadora GLP - Completa", layout="wide")

# ------------------------
# Parámetros fijos / constantes
# ------------------------
TANK1_CAP_M3 = 49170     # Tanque grande (m3)
TANK2_CAP_M3 = 30694     # Tanque chico (m3)
DENSITY_KG_PER_M3 = 0.54 # Conversión m3 -> kg (usar misma conv. que veníamos usando)
TRUCK_KG = 24000         # Camión de reabastecimiento (kg)
C2_SPEED_FIXED = 52      # Velocidad fija C2 (env/min)

# Consumos (g/env)
FORMATS_C3 = {
    "Ambiental": 87.6,
    "Desinfectante": 69.5,
    "Selton": 93.6,
}
FORMATS_C2 = {
    "Jirafa": 100.7,
    "360g": 69.5,
}

# ------------------------
# Helpers
# ------------------------
def m3_to_kg(m3):
    return m3 * DENSITY_KG_PER_M3

def kg_to_m3(kg):
    # evita división por cero
    if DENSITY_KG_PER_M3 == 0:
        return 0
    return kg / DENSITY_KG_PER_M3

def format_num(n):
    """Formato legible con separador de miles."""
    try:
        return f"{n:,.2f}"
    except:
        return str(n)

# Zeppelín horizontal (HTML) — robusto y responsivo
def zeppelin_html(label, pct, current_m3, capacity_m3):
    # pct ya en 0..100
    pct = max(0, min(100, float(pct)))
    pct_str = f"{pct:.1f}%"
    current_kg = m3_to_kg(current_m3)
    cap_kg = m3_to_kg(capacity_m3)
    color = "#10b981" if pct > min_percent else "#ef4444"  # verde > min, rojo <= min

    html = f"""
    <div style="text-align:center; font-family: Inter, sans-serif; margin-bottom:12px;">
      <div style="display:inline-block; position:relative; width:420px; height:120px;">
        <!-- cuerpo -->
        <div style="
            width:100%;
            height:72px;
            background: linear-gradient(90deg,#f1f5f9,#e6eefc);
            border-radius:40px;
            border:1px solid #cbd5e1;
            position:absolute;
            top:24px;
            overflow:hidden;">
            <div style="
                position:absolute;
                left:0;
                top:0;
                bottom:0;
                width:{pct}%;
                background: linear-gradient(90deg,{color},#06b6d4);
                transition: width 0.6s ease;">
            </div>
        </div>
        <!-- extremos -->
        <div style="position:absolute; left:-34px; top:34px; width:68px; height:34px;
                    background: #f1f5f9; border-radius:50%; border:1px solid #cbd5e1;"></div>
        <div style="position:absolute; right:-34px; top:34px; width:68px; height:34px;
                    background: #f1f5f9; border-radius:50%; border:1px solid #cbd5e1;"></div>
      </div>

      <div style="margin-top:8px; font-weight:700; font-size:15px;">{label} — {pct_str}</div>
      <div style="font-size:13px; color:#374151;">
        {format_num(current_m3)} m³ — {format_num(current_kg)} kg  /  Capacidad: {format_num(capacity_m3)} m³ ({format_num(cap_kg)} kg)
      </div>
    </div>
    """
    return html

# ------------------------
# Interfaz: Zeppelins arriba
# ------------------------
st.title("🔋 Calculadora de Disponibilidad de GLP — Completa")

st.caption("Incluye: líneas C3/C2, formatos, velocidades, conversión m³→kg, tiempo restante y lógica de recarga con camión (24.000 kg).")

st.divider()

# Inputs principales (columna izquierda)
with st.sidebar:
    st.header("Ajustes y entradas")
    # porcentajes (default 85)
    tank1_pct = st.number_input("Tanque Grande (%)", min_value=0, max_value=100, value=85, step=1)
    tank2_pct = st.number_input("Tanque Chico (%)", min_value=0, max_value=100, value=85, step=1)
    min_percent = st.number_input("% Mínimo requerido (reservas)", min_value=0, max_value=100, value=5, step=1)

    # línea y formatos
    line = st.selectbox("Línea activa", options=["C3", "C2", "C3 y C2"])
    format_c3 = None
    format_c2 = None
    if line in ("C3", "C3 y C2"):
        format_c3 = st.selectbox("Formato C3", options=list(FORMATS_C3.keys()), index=0)
    if line in ("C2", "C3 y C2"):
        format_c2 = st.selectbox("Formato C2", options=list(FORMATS_C2.keys()), index=0)

    # velocidades: C2 fijo, C3 editable
    speed_c3 = st.number_input("Velocidad C3 (env/min)", min_value=1, max_value=5000, value=195, step=1)
    st.markdown(f"- Velocidad C2 fija: **{C2_SPEED_FIXED} env/min**")

    st.markdown("---")
    st.write("Parámetros fijos (si necesitás cambiar, editá el código):")
    st.write(f"- Tanque Grande: {TANK1_CAP_M3:,} m³")
    st.write(f"- Tanque Chico: {TANK2_CAP_M3:,} m³")
    st.write(f"- Densidad usada: {DENSITY_KG_PER_M3} kg/m³")
    st.write(f"- Camión: {TRUCK_KG:,} kg")

st.divider()

# Calc: convertir % a m3 actuales
tank1_current_m3 = (tank1_pct / 100.0) * TANK1_CAP_M3
tank2_current_m3 = (tank2_pct / 100.0) * TANK2_CAP_M3

# Mostrar zepelines en la parte superior (dos columnas)
col_z1, col_z2 = st.columns(2)
with col_z1:
    st.markdown(zeppelin_html("Tanque Grande", tank1_pct, tank1_current_m3, TANK1_CAP_M3), unsafe_allow_html=True)
with col_z2:
    st.markdown(zeppelin_html("Tanque Chico", tank2_pct, tank2_current_m3, TANK2_CAP_M3), unsafe_allow_html=True)

st.divider()

# ------------------------
# CÁLCULOS
# ------------------------

# disponibles en kg
tank1_current_kg = m3_to_kg(tank1_current_m3)
tank2_current_kg = m3_to_kg(tank2_current_m3)
total_available_kg = tank1_current_kg + tank2_current_kg

# mínimo requerido (kg) — aplicamos sobre la suma de capacidades como pediste originalmente
min_required_kg = ((TANK1_CAP_M3 + TANK2_CAP_M3) * (min_percent / 100.0)) * DENSITY_KG_PER_M3

usable_glp_kg = total_available_kg - min_required_kg
if usable_glp_kg < 0:
    usable_glp_kg = 0.0

# consumo por minuto en kg/min según selección
consumption_kg_per_min = 0.0
consumption_details = []

if line == "C3" and format_c3:
    g_per_env = FORMATS_C3[format_c3]
    consumption_kg_per_min = (g_per_env * speed_c3) / 1000.0
    consumption_details.append(f"C3 ({format_c3}): {g_per_env} g/env × {speed_c3} env/min → {consumption_kg_per_min:.4f} kg/min")
elif line == "C2" and format_c2:
    g_per_env = FORMATS_C2[format_c2]
    consumption_kg_per_min = (g_per_env * C2_SPEED_FIXED) / 1000.0
    consumption_details.append(f"C2 ({format_c2}): {g_per_env} g/env × {C2_SPEED_FIXED} env/min → {consumption_kg_per_min:.4f} kg/min")
elif line == "C3 y C2" and format_c3 and format_c2:
    g_c3 = FORMATS_C3[format_c3]
    g_c2 = FORMATS_C2[format_c2]
    c3_kg_min = (g_c3 * speed_c3) / 1000.0
    c2_kg_min = (g_c2 * C2_SPEED_FIXED) / 1000.0
    consumption_kg_per_min = c3_kg_min + c2_kg_min
    consumption_details.append(f"C3 ({format_c3}): {g_c3} g/env × {speed_c3} env/min → {c3_kg_min:.4f} kg/min")
    consumption_details.append(f"C2 ({format_c2}): {g_c2} g/env × {C2_SPEED_FIXED} env/min → {c2_kg_min:.4f} kg/min")

# tiempo restante
minutes_available = usable_glp_kg / consumption_kg_per_min if consumption_kg_per_min > 0 and usable_glp_kg > 0 else 0.0
hours = int(minutes_available // 60)
minutes = int(minutes_available % 60)
minutes_available_rounded = round(minutes_available, 2)

# capacidad total en kg y necesidad para llenar al 100%
capacity_total_kg = (TANK1_CAP_M3 + TANK2_CAP_M3) * DENSITY_KG_PER_M3
capacity_needed_to_full_kg = max(0.0, capacity_total_kg - total_available_kg)
truck_can_fill = TRUCK_KG >= capacity_needed_to_full_kg

# si no alcanza, distribución proporcional para ver niveles después del camión
if TRUCK_KG >= capacity_needed_to_full_kg:
    # llega a 100%
    tank1_after_truck_kg = TANK1_CAP_M3 * DENSITY_KG_PER_M3
    tank2_after_truck_kg = TANK2_CAP_M3 * DENSITY_KG_PER_M3
else:
    need1 = TANK1_CAP_M3 * DENSITY_KG_PER_M3 - tank1_current_kg
    need2 = TANK2_CAP_M3 * DENSITY_KG_PER_M3 - tank2_current_kg
    total_need = max(0.0, need1 + need2)
    if total_need <= 0:
        tank1_after_truck_kg = tank1_current_kg
        tank2_after_truck_kg = tank2_current_kg
    else:
        add1 = TRUCK_KG * (need1 / total_need) if total_need > 0 else 0
        add2 = TRUCK_KG * (need2 / total_need) if total_need > 0 else 0
        tank1_after_truck_kg = min(TANK1_CAP_M3 * DENSITY_KG_PER_M3, tank1_current_kg + add1)
        tank2_after_truck_kg = min(TANK2_CAP_M3 * DENSITY_KG_PER_M3, tank2_current_kg + add2)

tank1_after_truck_pct = (tank1_after_truck_kg / (TANK1_CAP_M3 * DENSITY_KG_PER_M3)) * 100.0
tank2_after_truck_pct = (tank2_after_truck_kg / (TANK2_CAP_M3 * DENSITY_KG_PER_M3)) * 100.0

# ------------------------
# UI: resultados
# ------------------------
st.header("Resultados")

left, right = st.columns(2)

with left:
    st.subheader("Disponibilidad (kg)")
    st.write(f"- Total disponible ahora: **{format_num(total_available_kg)} kg**")
    st.write(f"- Mínimo requerido ({min_percent}%): **{format_num(min_required_kg)} kg**")
    st.write(f"- GLP utilizable por encima del mínimo: **{format_num(usable_glp_kg)} kg**")

with right:
    st.subheader("Consumo")
    if consumption_details:
        for d in consumption_details:
            st.write(f"- {d}")
    else:
        st.write("- No hay consumo configurado (falta seleccionar formato/línea).")
    st.write(f"- Consumo total: **{consumption_kg_per_min:.4f} kg/min**")
    if minutes_available > 0:
        st.success(f"Tiempo estimado de operación restante: **{hours} h {minutes} min** ({minutes_available_rounded} minutos).")
    else:
        if usable_glp_kg == 0:
            st.error("No hay GLP utilizable por encima del mínimo configurado.")
        else:
            st.info("Consumo no configurado o cero.")

st.divider()

st.subheader("Reabastecimiento con camión")

st.write(f"- Capacidad total sistema (kg): **{format_num(capacity_total_kg)} kg**")
st.write(f"- Cantidad necesaria para llenar tanques al 100%: **{format_num(capacity_needed_to_full_kg)} kg**")
st.write(f"- Camión disponible: **{TRUCK_KG:,} kg**")

if truck_can_fill:
    st.success("El camión alcanza para **llenar completamente** los tanques al 100%.")
else:
    st.info("El camión **no alcanza** para llenar completamente los tanques. Se repartirá proporcionalmente la carga disponible.")

st.write(f"- Nivel estimado Tanque Grande después del camión: **{tank1_after_truck_pct:.1f}%**")
st.write(f"- Nivel estimado Tanque Chico después del camión: **{tank2_after_truck_pct:.1f}%**")

st.divider()

# Visual alert por tanque cerca o por debajo del mínimo
st.subheader("Alertas")

if tank1_pct <= min_percent:
    st.error("⚠️ Tanque Grande está en o por debajo del mínimo configurado.")
if tank2_pct <= min_percent:
    st.error("⚠️ Tanque Chico está en o por debajo del mínimo configurado.")

st.markdown("---")
st.caption("Hecho según tu pedido: tanques zepelín horizontales arriba, cálculos m³→kg con densidad, selección de líneas/formato, velocidad C2 fija 52 env/min, velocidad C3 editable, cálculo de tiempo y verificación de si el camión de 24.000 kg alcanza.")
