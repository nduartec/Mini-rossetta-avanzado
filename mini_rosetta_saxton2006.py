
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mini-ROSETTA PTFs Avanzado", layout="centered")

st.title("🌱 Mini-ROSETTA: PTFs + Saxton & Rawls (2006)")

st.write("""Esta versión ahora usa las ecuaciones actualizadas de Saxton & Rawls (2006) para:
- **Capacidad de campo (CC)** a 33 kPa
- **Punto de marchitez permanente (PMP)** a 1500 kPa
- **Agua disponible (AD)**
Y grafica ambos puntos sobre la curva de retención de humedad con eje en kPa.
""")

# Entradas
sand = st.number_input("Arena (%)", min_value=0.0, max_value=100.0, value=65.0)
silt = st.number_input("Limo (%)", min_value=0.0, max_value=100.0, value=25.0)
clay = st.number_input("Arcilla (%)", min_value=0.0, max_value=100.0, value=10.0)
bd = st.number_input("Densidad aparente (g/cm³)", min_value=0.5, max_value=2.2, value=1.45)
om = st.number_input("Materia orgánica (%)", min_value=0.0, max_value=10.0, value=1.8)

if st.button("🔍 Calcular PTFs"):

    # --- Rawls et al. para Ks ---
    a, b, c, d, e = -0.884, 0.0153, -0.0003, -0.197, 0.112
    log_Ks = a + b*sand + c*clay + d*bd + e*om
    Ks = 10 ** log_Ks

    # --- van Genuchten ---
    theta_s = 1 - bd/2.65
    theta_r = 0.045
    alpha = 0.075
    n = 1.89

    # --- Saxton & Rawls (2006) ---
    sand_f = sand / 100
    clay_f = clay / 100
    om_f = om / 100

    # Capacidad de campo (33 kPa)
    CC = (-0.251 + 0.195 * clay_f + 0.011 * om_f +
          0.006 * clay_f * om_f - 0.027 * sand_f * om_f +
          0.452 * sand_f * clay_f + 0.299)

    # Punto de marchitez permanente (1500 kPa)
    PMP = (-0.024 + 0.487 * clay_f + 0.006 * om_f +
           0.005 * clay_f * om_f - 0.013 * sand_f * om_f +
           0.068 * sand_f * clay_f + 0.031)

    AD = CC - PMP

    st.subheader("✅ Resultados estimados")
    st.write(f"**Ks:** {Ks:.2f} cm/h")
    st.write(f"**θs:** {theta_s:.3f}")
    st.write(f"**θr:** {theta_r:.3f}")
    st.write(f"**α:** {alpha:.3f} 1/cm")
    st.write(f"**n:** {n:.2f}")
    st.write(f"**Capacidad de campo (CC, Saxton 2006):** {CC:.3f} cm³/cm³")
    st.write(f"**Punto de marchitez permanente (PMP, Saxton 2006):** {PMP:.3f} cm³/cm³")
    st.write(f"**Agua disponible (AD):** {AD:.3f} cm³/cm³")

    # --- Curva van Genuchten con eje en kPa ---
    h = np.logspace(-1, 3.2, 100)  # h en cm
    psi = h / 102.04  # kPa
    Se = 1 / (1 + (alpha * h)**n)**(1 - 1/n)
    theta = theta_r + Se * (theta_s - theta_r)

    fig, ax = plt.subplots()
    ax.plot(psi, theta, label="Curva de retención")

    ax.axhline(CC, color='g', linestyle='--', label="CC (Saxton 2006)")
    ax.axhline(PMP, color='r', linestyle='--', label="PMP (Saxton 2006)")

    ax.set_xscale('log')
    ax.set_xlabel('Suction (kPa)')
    ax.set_ylabel('Contenido volumétrico de agua (cm³/cm³)')
    ax.set_title('Curva de retención (van Genuchten) con CC y PMP')
    ax.legend()
    ax.invert_xaxis()

    st.pyplot(fig)

    # Exportar
    df = pd.DataFrame({
        'h (cm)': h,
        'Suction (kPa)': psi,
        'θ (cm³/cm³)': theta
    })
    st.download_button("📥 Descargar curva (CSV)", df.to_csv(index=False), "curva_retencion.csv")

st.caption("Demo versión Saxton & Rawls (2006) | Desarrollado con Streamlit")
