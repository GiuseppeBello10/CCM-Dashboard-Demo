import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO


# --- Dati dei rischi base per i Paesi (inclusa Italia) ---
rischi_paese = {
    "India": {"Politico": 65, "Economico": 60, "Culturale": 70, "Legale": 60, "Innovazione": 30},
    "Cina": {"Politico": 60, "Economico": 55, "Culturale": 65, "Legale": 50, "Innovazione": 40},
    "Giappone": {"Politico": 20, "Economico": 25, "Culturale": 50, "Legale": 30, "Innovazione": 20},
    "Emirati Arabi": {"Politico": 30, "Economico": 35, "Culturale": 55, "Legale": 35, "Innovazione": 25},
    "Sud Africa": {"Politico": 75, "Economico": 70, "Culturale": 60, "Legale": 80, "Innovazione": 60}
}

# --- Dizionari pesi e fattori ---
pesi_settore = {
    "Tecnologia / IT": {"Politico": 10, "Economico": 20, "Culturale": 20, "Legale": 20, "Innovazione": 30},
    "Energia / Risorse": {"Politico": 30, "Economico": 30, "Culturale": 10, "Legale": 30, "Innovazione": 0},
    "Retail / Moda / Consumer": {"Politico": 15, "Economico": 25, "Culturale": 30, "Legale": 20, "Innovazione": 10},
    "Pharma / Life Sciences": {"Politico": 20, "Economico": 25, "Culturale": 10, "Legale": 25, "Innovazione": 20},
    "Manifatturiero": {"Politico": 25, "Economico": 35, "Culturale": 10, "Legale": 20, "Innovazione": 10},
} 

fattori_strategia = {
    "Joint Venture": {"Culturale": 1.2, "Legale": 1.1, "Politico": 1.1},
    "Export Diretto": {"Culturale": 0.8, "Legale": 0.9, "Politico": 1.1},
    "Wholly Owned Subsidiary": {"Culturale": 1.2, "Legale": 1.2, "Politico": 1.2},
    "Franchising / Licensing": {"Culturale": 1.1, "Legale": 0.9, "Politico": 0.9},
}


# --- LOGIN --- #
PASSWORD_CORRETTA = st.secrets["DASHBOARD_PASSWORD"]

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "login_submitted" not in st.session_state:
    st.session_state["login_submitted"] = False

if not st.session_state["logged_in"]:
    with st.sidebar:
        st.image("logo3clab.png", width=180)
        st.header("🔐 Login")
        password = st.text_input("Password", type="password")
        login_button = st.button("Accedi")
        if login_button:
            st.session_state["login_submitted"] = True
            if password == PASSWORD_CORRETTA:
                st.session_state["logged_in"] = True
            else:
                st.error("❌ Password errata")
    if not st.session_state["logged_in"]:
        st.stop()
        
if st.session_state["logged_in"]:
    st.image("logo3clab.png", width=160)





# --- Nuova funzione di calcolo score aggiornato ---
def calcola_score_nuovo(rischi, pesi, fattori):
    dettagli = []
    score_totale = 0
    for rischio, valore in rischi.items():
        peso = pesi[rischio]
        moltiplicatore = fattori.get(rischio, 1.0)
        valore_pesato = valore * peso / 100
        valore_finale = valore_pesato * moltiplicatore
        score_totale += valore_finale
        dettagli.append({
            "Tipo di Rischio": rischio,
            "Valore Iniziale": valore,
            "Peso Settore (%)": peso,
            "Valore Pesato": round(valore_pesato, 2),
            "Moltiplicatore Strategia": moltiplicatore,
            "Valore Finale": round(valore_finale, 2)
        })
    df_dettagli = pd.DataFrame(dettagli).set_index("Tipo di Rischio")
    return round(score_totale, 2), df_dettagli

# --- UI Streamlit ---
st.title(" Dashboard Calcolo del Rischio Internazionale")

paese = st.selectbox(" Seleziona il Paese target", [p for p in rischi_paese.keys() if p != "Italia"])
settore = st.selectbox(" Seleziona il settore", list(pesi_settore.keys()))
strategia = st.selectbox(" Seleziona la strategia d'ingresso", list(fattori_strategia.keys()))

# --- Dati dinamici ---
rischi_target = rischi_paese[paese]
pesi = pesi_settore[settore]
fattori = fattori_strategia[strategia]

# --- Calcolo nuovo score ---
score_target, df_dettagli = calcola_score_nuovo(rischi_target, pesi, fattori)

# --- Radar Chart Comparativa ---
fig = go.Figure()
theta = ["Politico", "Economico", "Culturale", "Legale", "Innovazione"]
theta = theta + [theta[0]]  # chiudere il radar

# Ciclo su tutti i paesi
for nome_paese, rischi in rischi_paese.items():
    valori = list(rischi.values())
    valori = valori + [valori[0]]  # chiudere il radar
    fig.add_trace(go.Scatterpolar(
        r=valori,
        theta=theta,
        fill='toself',
        name=nome_paese
    ))

fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100])
    ),
    showlegend=True
)

st.markdown("### 📈 Confronto tra tutti i Paesi")
st.plotly_chart(fig)


# --- Bar chart dei valori finali ---
st.markdown("###  Valori finali ponderati (per rischio)")
st.bar_chart(df_dettagli["Valore Finale"])

# --- Score finale individuale ---
st.markdown("###  Score personalizzato per il Paese target")
st.metric("Score " + paese, value=score_target)

# --- Ranking dinamico aggiornato ---
ranking = []
for p, rischi in rischi_paese.items():
    if p != "Italia":
        score, _ = calcola_score_nuovo(rischi, pesi, fattori)
        ranking.append((p, score))
df_rank = pd.DataFrame(sorted(ranking, key=lambda x: x[1], reverse=True), columns=["Paese", "Score"])
st.markdown("###  Classifica dei Paesi in base allo score personalizzato")
st.dataframe(df_rank)

# --- Download Excel dettagliato ---

df_export = df_dettagli.copy()
df_export.loc["Totale"] = df_export[["Valore Finale"]].sum()

buffer = BytesIO()
df_export.to_excel(buffer, index=True, engine='openpyxl')
buffer.seek(0)

st.download_button(
    label=" Scarica Excel con dettagli di calcolo",
    data=buffer,
    file_name=f"Score_{paese}_{settore}_{strategia}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
