import streamlit as st
import math

# Nastavitve strani
st.set_page_config(page_title="Varilni kalkulator WL10", layout="centered")

# Podatki: (rho [Ωm], cp [J/kgK], gostota [kg/m3], T_taljenja [°C])
MATERIALI = {
    "Cu": (1.7e-8, 385, 8960, 1085),
    "CuZn33": (6.4e-8, 380, 8500, 920),
    "ElCu90": (1.78e-8, 390, 8900, 1083)
}
WL10_RHO, WL10_CP, WL10_DENS = 5.6e-8, 134, 19250

st.title("⚡ Varilni kalkulator WL10 v3.6")

# --- STRANSKA VRSTICA: PREDGRETJE ---
st.sidebar.header("🔥 Predgretje (WL10)")
I_gr = st.sidebar.number_input("Tok grelca (A)", value=1670)
t_gr_ms = st.sidebar.number_input("Čas gretja (ms)", value=100)
W_gr = st.sidebar.number_input("Širina grelca (mm)", value=3.2)
H_gr = st.sidebar.number_input("Višina grelca (mm)", value=1.2)
T_amb = st.sidebar.number_input("Sobna T (°C)", value=25)

# --- GLAVNI DEL: PARAMETRI VARJENJA ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("⚙️ Varjenje")
    I_v = st.number_input("Tok varjenja (A)", value=1600)
    t_v_ms = st.number_input("Čas varjenja (ms)", value=7)
    d_el = st.number_input("Premer elektrode (mm)", value=1.5)
    p_vpis = st.number_input("Pritisk (MPa)", value=55)

# --- PLOČEVINE ---
st.divider()
c1, c2 = st.columns(2)

def mat_input(col, naslov, default_mat, dl, dw, dh):
    with col:
        st.markdown(f"**{naslov}**")
        m_ime = st.selectbox(f"Material {naslov}", list(MATERIALI.keys()), index=list(MATERIALI.keys()).index(default_mat))
        l = st.number_input(f"L (mm) - {naslov}", value=float(dl))
        w = st.number_input(f"W (mm) - {naslov}", value=float(dw))
        h = st.number_input(f"H (mm) - {naslov}", value=float(dh))
        
        rho, cp, dens, melt = MATERIALI[m_ime]
        presek = (w * 1e-3) * (h * 1e-3)
        m_kg = (l * 1e-3) * presek * dens
        R_o = rho * (l * 1e-3) / presek
        return m_kg, R_o, cp, melt

m1, R1, cp1, melt1 = mat_input(c1, "Pločevina 1", "ElCu90", 0.05, 2, 1)
m2, R2, cp2, melt2 = mat_input(c2, "Pločevina 2", "CuZn33", 25, 2, 0.6)

# --- IZRAČUN ---
if st.button("IZRAČUNAJ", type="primary", use_container_width=True):
    # Predgretje
    t_gr_s = t_gr_ms / 1000
    A_gr_m2 = (W_gr * 1e-3) * (H_gr * 1e-3)
    dT_gr = (I_gr**2 * WL10_RHO * t_gr_s) / (A_gr_m2**2 * WL10_DENS * WL10_CP)
    T_start = T_amb + dT_gr

    # Varjenje
    t_v_s = t_v_ms / 1000
    A_el = math.pi * (d_el / 2)**2
    R_b = R1 + R2
    C_sist = (m1 * cp1) + (m2 * cp2)

    st.success(f"**T_start po predgretju:** {T_start:.1f} °C")

    # Scenariji
    scenariji = [("Dober", 1e-6), ("Slab", 500e-6), ("Kritičen", 5000e-6)]
    cols = st.columns(3)

    for i, (ime, R_cont) in enumerate(scenariji):
        R_tot = R_b + R_cont
        Q = (I_v**2) * R_tot * t_v_s
        dT = Q / C_sist
        T_kon = T_start + dT
        procent = (T_kon / min(melt1, melt2)) * 100
        
        with cols[i]:
            st.metric(label=f"Stik: {ime}", value=f"{T_kon:.0f} °C", delta=f"{procent:.1f}% tal.")
            if T_kon > min(melt1, melt2):
                st.error("❌ TALJENJE")
            elif procent > 75:
                st.warning("⚠️ KRITIČNO")
            else:
                st.success("✅ VARNO")
