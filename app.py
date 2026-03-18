import streamlit as st
import math

# Nastavitve strani
st.set_page_config(page_title="Varilni kalkulator WL10", layout="centered")

# Podatki
MATERIALI = {
    "Cu": (1.7e-8, 385, 8960, 1085),
    "CuZn33": (6.4e-8, 380, 8500, 920),
    "ElCu90": (1.78e-8, 390, 8900, 1083)
}
WL10_RHO, WL10_CP, WL10_DENS = 5.6e-8, 134, 19250

st.title("⚡ Varilni kalkulator WL10 v3.6")

# --- VHODNI PODATKI ---
with st.sidebar:
    st.header("🔥 Predgretje (WL10)")
    I_gr = st.number_input("Tok grelca (A)", value=1670)
    t_gr_ms = st.number_input("Čas gretja (ms)", value=100)
    W_gr = st.number_input("Širina (mm)", value=3.2)
    H_gr = st.number_input("Višina (mm)", value=1.2)
    T_amb = st.number_input("Sobna T (°C)", value=25)

col1, col2 = st.columns(2)
with col1:
    st.subheader("⚙️ Varjenje")
    I_v = st.number_input("Tok varjenja (A)", value=1600)
    t_v_ms = st.number_input("Čas varjenja (ms)", value=7)
with col2:
    st.subheader("📏 Geometrija")
    d_el = st.number_input("Premer elektrode (mm)", value=1.5)
    p_vpis = st.number_input("Pritisk (MPa)", value=55)

st.divider()
c1, c2 = st.columns(2)

def mat_ui(col, naslov, def_mat, dl, dw, dh):
    with col:
        st.markdown(f"### {naslov}")
        m_ime = st.selectbox(f"Mat.", list(MATERIALI.keys()), index=list(MATERIALI.keys()).index(def_mat), key=naslov)
        l = st.number_input(f"L (mm)", value=float(dl), key=naslov+"l")
        w = st.number_input(f"W (mm)", value=float(dw), key=naslov+"w")
        h = st.number_input(f"H (mm)", value=float(dh), key=naslov+"h")
        return m_ime, l, w, h

n1, l1, w1, h1 = mat_ui(c1, "Pločevina 1", "ElCu90", 0.05, 2, 1)
n2, l2, w2, h2 = mat_ui(c2, "Pločevina 2", "CuZn33", 25, 2, 0.6)

# --- LOGIKA IZRAČUNA (Enaka kot v originalu) ---
if st.button("IZRAČUNAJ S POSTOPKOM", type="primary", use_container_width=True):
    # Funkcija za preračun lastnosti (kot v originalu)
    def get_props(m_ime, l_mm, w_mm, h_mm):
        rho, cp, dens, melt = MATERIALI[m_ime]
        presek = (w_mm*1e-3)*(h_mm*1e-3)
        m_kg = (l_mm*1e-3) * presek * dens
        R_o = rho * (l_mm*1e-3) / presek
        return m_kg, R_o, cp, melt

    m1, R1, cp1, melt1 = get_props(n1, l1, w1, h1)
    m2, R2, cp2, melt2 = get_props(n2, l2, w2, h2)

    # Izračun predgretja
    t_gr_s = t_gr_ms / 1000
    A_gr_m2 = (W_gr * 1e-3) * (H_gr * 1e-3)
    dT_gr = (I_gr**2 * WL10_RHO * t_gr_s) / (A_gr_m2**2 * WL10_DENS * WL10_CP)
    T_start = T_amb + dT_gr

    # Izračun varjenja
    t_v_s = t_v_ms / 1000
    A_el = math.pi * (d_el / 2)**2
    F_sila = p_vpis * A_el
    R_b, C_sist = R1 + R2, (m1 * cp1) + (m2 * cp2)

    # SESTAVLJANJE IZPISA (Točno kot v originalu)
    txt = "PODROBEN IZRAČUN IN POSTOPEK\n" + "="*55 + "\n"
    txt += "VHODNI PODATKI PREDGRETJA (WL10):\n"
    txt += f"Tok (I_gr) = {I_gr} A | Čas (t_gr) = {t_gr_ms} ms\n"
    txt += f"Presek grelca = {W_gr} x {H_gr} mm\n\n"
    txt += "IZRAČUN PREDGRETJA:\n"
    txt += f"• Segretje grelca: ΔT = {dT_gr:.1f} K\n"
    txt += f"• Končna T predgretja: T_start = {T_start:.1f} °C\n\n"
    txt += "VHODNI PODATKI VARJENJA:\n"
    txt += f"I = {I_v} A | t = {t_v_s} s | T_start = {T_start:.1f} °C\n\n"
    txt += "1. GEOMETRIJA IN LASTNOSTI:\n"
    txt += f"P1 ({n1}): {l1}x{w1}x{h1}mm | m={m1*1000:.3f}g, R={R1*1e6:.1f}µΩ\n"
    txt += f"P2 ({n2}): {l2}x{w2}x{h2}mm | m={m2*1000:.3f}g, R={R2*1e6:.1f}µΩ\n"
    txt += f"Spec. toplota: cp1={cp1} J/kgK, cp2={cp2} J/kgK\n\n"
    txt += "2. SILA VARJENJA:\n"
    txt += f"• Premer elektrode: d = {d_el} mm\n"
    txt += f"• Površina stika: A = π * (d/2)² = {A_el:.2f} mm²\n"
    txt += f"• Potrebna sila: F = p * A = {p_vpis} MPa * {A_el:.2f} mm² = {F_sila:.1f} N\n\n"
    txt += "3. UPORABLJENE ENAČBE:\n"
    txt += f"• Upornost bulk: R_b = R1 + R2 = {R_b*1e6:.1f} µΩ\n"
    txt += f"• Topl. kapaciteta: C = (m1*cp1) + (m2*cp2)\n"
    txt += f"  C = ({m1:.7f}*{cp1}) + ({m2:.7f}*{cp2}) = {C_sist:.5f} J/K\n"
    txt += "="*55 + "\n\n"

    for ime, R_cont in [("Dober (1µΩ)", 1e-6), ("Slab (500µΩ)", 500e-6), ("Kritičen (5000µΩ)", 5000e-6)]:
        R_tot = R_b + R_cont
        Q = (I_v**2) * R_tot * t_v_s
        dT = Q / C_sist
        T_kon = T_start + dT
        min_melt = min(melt1, melt2)
        procent = (T_kon / min_melt) * 100
        status = "✅ VARNO" if T_kon < min_melt else "❌ TALJENJE!"
        txt += f"🔹 SCENARIJ: {ime}\n"
        txt += f"   T_končna = {T_kon:.1f} °C ({procent:.1f}% tališča) | {status}\n\n"

    # IZPIS V STREMLIT (v stilu poročila)
    st.subheader("📋 Poročilo o izračunu")
    st.text(txt)  # Uporabimo st.text za Courier font

