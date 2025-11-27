# app.py
import streamlit as st
from math import floor

st.set_page_config(page_title="Calculadora GLP", layout="centered")

# ------------------------
# Parámetros fijos
# ------------------------
TANK1_CAPACITY_M3 = 49170    # Tanque grande (m3)
TANK2_CAPACITY_M3 = 30694    # Tanque chico  (m3)
DENSITY_GLP_KG_PER_M3 = 0.54 # Conversión m3 -> kg
TRUCK_SUPPLY_KG = 24000      # Camión de reabastecimiento (kg)
C2_SPEED_FIXED = 52          # env/min fijo para C2

# Formatos y consumos (g/env)
FORMATS_C3 = {
    "Ambiental": 87.6,
    "Desinfectante": 69.5,
    "Selton": 93.6,
}

FORMATS_C2 = {
    "Jirafa": 100.7,
    "360g": 69.5,
}

st.title("🔋 Calculadora de Disponibilidad de GLP")

st.markdown("**Resumen:** ingresa los % de llenado de cada tanque, el % mínimo que deben quedar, selecciona la/s línea/s y formato/s y la app te dará el tiempo estimado de trabajo y si el camión alcanza para recargar.")

st.markdown("---")

# ------------------------
# Entradas de usuario
# ------------------------
col1, col2 = st.columns(2)

with col1:
    tank1_percent = st.number_input("% Tanque Grande", min_value=0, max_value=100, value=85, step=1, help="Porcentaje actual del Tanque Grande")
with col2:
    tank2_percent = st.number_input("% Tanque Chico", min_value=0, max_value=100, value=85, step=1, help="Porcentaje actual del Tanque Chico")

col3, col4 = st.columns(2)
with col3:
    min_percent = st.number_input("% Mínimo requerido (reservas)", min_value=0, max_value=100, value=5, step=1, help="Porcentaje mínimo que debe quedar en los tanques (editable)")
with col4:
    speed_c3 = st.number_input("Velocidad C3 (env/min)", min_value=1, max_value=5000, value=195, step=1, help="Velocidad de la máquina para la línea C3 (editable). C2 es fija en 52 env/min")

st.markdown("---")

# Selección de línea y formatos
line = st.selectbox("Línea de consumo", options=["C3", "C2", "C3 y C2"])

# Formatos condicionales
format_c3 = None
format_c2 = None
if line in ("C3", "C3 y C2"):
    format_c3 = st.selectbox("Formato C3", options=list(FORMATS_C3.keys()), index=0)
if line in ("C2", "C3 y C2"):
    format_c2 = st.selectbox("Formato C2", options=list(FORMATS_C2.keys()), index=0)

st.markdown("---")

# ------------------------
# Cálculos
# ------------------------

# Convertir volumen actual a kg
tank1_current_kg = TANK1_CAPACITY_M3 * (tank1_percent / 100.0) * DENSITY_GLP_KG_PER_M3
tank2_current_kg = TANK2_CAPACITY_M3 * (tank2_percent / 100.0) * DENSITY_GLP_KG_PER_M3
total_available_kg = tank1_current_kg + tank2_current_kg

# Minimo requerido (aplicado sobre la suma de capacidades; mantiene consistencia con versión anterior)
min_required_kg = (TANK1_CAPACITY_M3 + TANK2_CAPACITY_M3) * (min_percent / 100.0) * DENSITY_GLP_KG_PER_M3

# GLP usable por encima del mínimo
usable_glp_kg = total_available_kg - min_required_kg
if usable_glp_kg < 0:
    usable_glp_kg = 0.0

# Consumo por minuto (kg/min)
consumption_per_minute = 0.0
details_consumption = []
if line == "C3":
    g_per_env = FORMATS_C3[format_c3]
    consumption_per_minute = (g_per_env * speed_c3) / 1000.0
    details_consumption.append(f"C3: {g_per_env} g/env × {speed_c3} env/min = {consumption_per_minute:.3f} kg/min")
elif line == "C2":
    g_per_env = FORMATS_C2[format_c2]
    consumption_per_minute = (g_per_env * C2_SPEED_FIXED) / 1000.0
    details_consumption.append(f"C2: {g_per_env} g/env × {C2_SPEED_FIXED} env/min = {consumption_per_minute:.3f} kg/min")
else:  # C3 y C2
    g_c3 = FORMATS_C3[format_c3]
    g_c2 = FORMATS_C2[format_c2]
    c3_cons = (g_c3 * speed_c3) / 1000.0
    c2_cons = (g_c2 * C2_SPEED_FIXED) / 1000.0
    consumption_per_minute = c3_cons + c2_cons
    details_consumption.append(f"C3: {g_c3} g/env × {speed_c3} env/min = {c3_cons:.3f} kg/min")
    details_consumption.append(f"C2: {g_c2} g/env × {C2_SPEED_FIXED} env/min = {c2_cons:.3f} kg/min")

# Tiempo disponible (minutos)
if consumption_per_minute > 0 and usable_glp_kg > 0:
    minutes_available = usable_glp_kg / consumption_per_minute
else:
    minutes_available = 0.0

hours = int(minutes_available // 60)
minutes = int(minutes_available % 60)
minutes_available_rounded = round(minutes_available, 2)

# Capacidad del sistema en kg y posibilidad de recarga total por camión
capacity_total_kg = (TANK1_CAPACITY_M3 + TANK2_CAPACITY_M3) * DENSITY_GLP_KG_PER_M3
capacity_needed_to_full_kg = max(0.0, capacity_total_kg - total_available_kg)
truck_can_fill_fully = TRUCK_SUPPLY_KG >= capacity_needed_to_full_kg

# Si el camión llega, hasta qué nivel quedarían los tanques (kg y porcentaje)
if TRUCK_SUPPLY_KG >= capacity_needed_to_full_kg:
    # se puede llenar al 100%
    tank1_after_truck_kg = TANK1_CAPACITY_M3 * DENSITY_GLP_KG_PER_M3
    tank2_after_truck_kg = TANK2_CAPACITY_M3 * DENSITY_GLP_KG_PER_M3
else:
    # distribuir el camión de forma proporcional a la capacidad faltante por tanque
    need1 = TANK1_CAPACITY_M3 * DENSITY_GLP_KG_PER_M3 - tank1_current_kg
    need2 = TANK2_CAPACITY_M3 * DENSITY_GLP_KG_PER_M3 - tank2_current_kg
    total_need = need1 + need2
    if total_need <= 0:
        tank1_after_truck_kg = tank1_current_kg
        tank2_after_truck_kg = tank2_current_kg
    else:
        # reparto proporcional
        add1 = TRUCK_SUPPLY_KG * (need1 / total_need)
        add2 = TRUCK_SUPPLY_KG * (need2 / total_need)
        tank1_after_truck_kg = min(TANK1_CAPACITY_M3 * DENSITY_GLP_KG_PER_M3, tank1_current_kg + add1)
        tank2_after_truck_kg = min(TANK2_CAPACITY_M3 * DENSITY_GLP_KG_PER_M3, tank2_current_kg + add2)

tank1_after_truck_pct = (tank1_after_truck_kg / (TANK1_CAPACITY_M3 * DENSITY_GLP_KG_PER_M3)) * 100.0
tank2_after_truck_pct = (tank2_after_truck_kg / (TANK2_CAPACITY_M3 * DENSITY_GLP_KG_PER_M3)) * 100.0

# ------------------------
# UI: resultados
# ------------------------
st.subheader("📊 Resultados")

colA, colB = st.columns([1, 1])

with colA:
    st.markdown(f"**Capacidad total (kg)**: {capacity_total_kg:,.0f} kg")
    st.markdown(f"**Total disponible ahora**: {total_available_kg:,.2f} kg")
    st.markdown(f"**Mínimo requerido** ({min_percent}%): {min_required_kg:,.2f} kg")
    st.markdown(f"**GLP utilizable (por encima del mínimo)**: {usable_glp_kg:,.2f} kg")

with colB:
    st.markdown("**Consumo (kg/min)**:")
    if details_consumption:
        for d in details_consumption:
            st.markdown(f"- {d}")
    else:
        st.markdown("- No hay línea/formato seleccionado")

    st.markdown(f"**Consumo total**: {consumption_per_minute:.4f} kg/min")
    st.markdown(f"**Tiempo restante**: **{hours} h {minutes} min**  ({minutes_available_rounded} min)")

st.markdown("---")

# ------------------------
# Visualización tanques (barras verticales)
# ------------------------
st.subheader("🛢️ Niveles de Tanques")
col1_viz, spacer, col2_viz = st.columns([1, 0.1, 1])

def color_for_pct(pct):
    return "#ef4444" if pct <= min_percent else "#10b981"  # rojo si <= min, verde si > min

with col1_viz:
    st.markdown("**Tanque Grande**")
    pct1 = max(0, min(100, tank1_percent))
    color1 = color_for_pct(pct1)
    st.markdown(f"""
    <div style="width:120px; margin:auto; text-align:center;">
      <div style="font-weight:600; margin-bottom:6px;">{pct1:.0f}%</div>
      <div style="height:260px; width:80px; border-radius:14px; background:#e5e7eb; border:1px solid #cbd5e1; margin:auto; position:relative; overflow:hidden;">
        <div style="position:absolute; bottom:0; left:0; width:100%; height:{pct1}%; background:{color1}; transition: height 0.6s ease;"></div>
        <!-- línea mínimo -->
        {"<div style='position:absolute; left:0; width:100%; height:2px; background:#ef4444; bottom:" + str(min_percent) + "%'></div>" if pct1 <= min_percent else ""}
      </div>
      <div style="margin-top:6px; font-size:12px; color:#6b7280;">Capacidad: {TANK1_CAPACITY_M3:,} m³</div>
    </div>
    """, unsafe_allow_html=True)

with col2_viz:
    st.markdown("**Tanque Chico**")
    pct2 = max(0, min(100, tank2_percent))
    color2 = color_for_pct(pct2)
    st.markdown(f"""
    <div style="width:120px; margin:auto; text-align:center;">
      <div style="font-weight:600; margin-bottom:6px;">{pct2:.0f}%</div>
      <div style="height:260px; width:80px; border-radius:14px; background:#e5e7eb; border:1px solid #cbd5e1; margin:auto; position:relative; overflow:hidden;">
        <div style="position:absolute; bottom:0; left:0; width:100%; height:{pct2}%; background:{color2}; transition: height 0.6s ease;"></div>
        {"<div style='position:absolute; left:0; width:100%; height:2px; background:#ef4444; bottom:" + str(min_percent) + "%'></div>" if pct2 <= min_percent else ""}
      </div>
      <div style="margin-top:6px; font-size:12px; color:#6b7280;">Capacidad: {TANK2_CAPACITY_M3:,} m³</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ------------------------
# Información sobre el camión
# ------------------------
st.subheader("🚚 Reabastecimiento con camión")

st.markdown(f"- Capacidad del camión: **{TRUCK_SUPPLY_KG:,} kg**")
st.markdown(f"- Cantidad necesaria para llenar tanques al 100%: **{capacity_needed_to_full_kg:,.2f} kg**")

if truck_can_fill_fully:
    st.success("El camión alcanza para **llenar completamente** los tanques al 100%.")
else:
    st.info("El camión **no alcanza** para llenar completamente los tanques. Se repartirá proporcionalmente la carga disponible.")

st.markdown(f"- Nivel estimado Tanque Grande después del camión: **{tank1_after_truck_pct:.1f}%**")
st.markdown(f"- Nivel estimado Tanque Chico después del camión: **{tank2_after_truck_pct:.1f}%**")

st.markdown("---")

# ------------------------
# Mensajes de alerta y recomendaciones
# ------------------------
st.subheader("🔔 Alertas y recomendaciones")

if tank1_percent <= min_percent:
    st.error("⚠️ Tanque Grande está en o por debajo del mínimo configurado.")
if tank2_percent <= min_percent:
    st.error("⚠️ Tanque Chico está en o por debajo del mínimo configurado.")

if usable_glp_kg == 0:
    st.warning("No hay GLP utilizable por encima del mínimo configurado. Revisá niveles o incrementá el mínimo.")
elif consumption_per_minute == 0:
    st.info("No se está consumiendo GLP (línea no configurada).")
else:
    # Mostrar tiempo en formato más legible
    if minutes_available < 60:
        st.success(f"Tiempo estimado de operación restante: {minutes_available_rounded} minutos.")
    else:
        st.success(f"Tiempo estimado de operación restante: {hours} horas y {minutes} minutos ({minutes_available_rounded} minutos).")

st.markdown("---")

st.caption("Hecho según la lógica solicitada: conversion m³→kg con densidad 0.54, velocidad C2 fija en 52 env/min, velocidad C3 editable, y consumo por formato en g/env.")
