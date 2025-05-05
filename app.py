import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from tools import *

# ---- CARICAMENTO DATI ---- #
file="Scoring_Rischio_Internazionale_1.xlsx"

fattori_strategia=caricamento_dati_fattori(file)
pesi_settore=caricamento_dati_pesi(file)
rischi_paese=caricamento_dati_rischio(file)


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


# --- Funzione di calcolo dello score personalizzato --- #
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

# --- Interfaccia Streamlit --- #
st.title(" Dashboard Calcolo del Rischio Internazionale")

paese = st.selectbox(" Seleziona il Paese target", [p for p in rischi_paese.keys() if p != "Italia"])
settore = st.selectbox(" Seleziona il settore", list(pesi_settore.keys()))
strategia = st.selectbox(" Seleziona la strategia d'ingresso", list(fattori_strategia.keys()))

# --- Dati dinamici --- #
rischi_target = rischi_paese[paese]
pesi = pesi_settore[settore]
fattori = fattori_strategia[strategia]

# --- Calcolo nuovo score --- #
score_target, df_dettagli = calcola_score_nuovo(rischi_target, pesi, fattori)

# --- Bar chart dei valori finali --- #
st.markdown("###  Valori finali ponderati (per rischio)")
st.bar_chart(df_dettagli["Valore Finale"])

# --- Score finale individuale --- #
st.markdown("###  Score personalizzato per il Paese target")
st.metric("Score " + paese, value=score_target)

# --- Ranking dinamico aggiornato --- #
ranking = []
for p, rischi in rischi_paese.items():
    if p != "Italia":
        score, _ = calcola_score_nuovo(rischi, pesi, fattori)
        ranking.append((p, score))
df_rank = pd.DataFrame(sorted(ranking, key=lambda x: x[1], reverse=True), columns=["Paese", "Score"])
st.markdown("###  Classifica dei Paesi in base allo score personalizzato")
st.dataframe(df_rank)

# --- Radar Chart Comparativa --- #
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

st.markdown("### Confrontro del rischio tra tutti i Paesi")
st.plotly_chart(fig)

# --- Download Excel dettagliato --- #

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


