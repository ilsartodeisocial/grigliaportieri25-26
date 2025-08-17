import streamlit as st
import pandas as pd

st.set_page_config(page_title="Serie A Partner Finder", layout="wide")
st.title("Serie A 2025/26 — Partner Match Finder")

DEFAULT_BIGS = ["Inter", "Napoli", "Milan", "Juventus", "Roma"]

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

def normalize(s):
    return s.strip() if isinstance(s, str) else s

st.sidebar.header("Dati")
use_uploaded = st.sidebar.checkbox("Carica file personalizzati")

if use_uploaded:
    cal_up = st.sidebar.file_uploader("Calendario (CSV: giornata,home,away)", type=["csv"])
    pairs_up = st.sidebar.file_uploader("Coppie (CSV: principal,partner)", type=["csv"])
    bigs_text = st.sidebar.text_input("Big Five (separate da virgola)", ",".join(DEFAULT_BIGS))
    if cal_up and pairs_up:
        calendar_df = pd.read_csv(cal_up)
        pairs_df = pd.read_csv(pairs_up)
        bigs = [normalize(x) for x in bigs_text.split(",")]
    else:
        st.stop()
else:
    calendar_df = load_csv("data/calendar_sample.csv")
    pairs_df = load_csv("data/pairs_sample.csv")
    bigs = DEFAULT_BIGS

calendar_df["home"] = calendar_df["home"].map(normalize)
calendar_df["away"] = calendar_df["away"].map(normalize)
pairs_df["principal"] = pairs_df["principal"].map(normalize)
pairs_df["partner"] = pairs_df["partner"].map(normalize)

pair_options = [f"{row.principal} - {row.partner}" for row in pairs_df.itertuples()]
selected_pair = st.selectbox("Seleziona una coppia", pair_options)

calendar_by_day = {g: df for g, df in calendar_df.groupby("giornata")}

def team_match(day_df, team):
    if day_df is None:
        return None
    m = day_df[(day_df["home"] == team) | (day_df["away"] == team)]
    return m.iloc[0] if not m.empty else None

def opponent_and_venue(row, team):
    if row is None:
        return None, None
    if row["home"] == team:
        return row["away"], "Casa"
    return row["home"], "Trasferta"

principal, partner = [x.strip() for x in selected_pair.split("-")]
rows = []
for day, df in sorted(calendar_by_day.items(), key=lambda x: x[0]):
    pm = team_match(df, principal)
    if pm is None:
        continue
    p_opp, _ = opponent_and_venue(pm, principal)
    if p_opp in bigs:
        pr = team_match(df, partner)
        partner_opp, venue = opponent_and_venue(pr, partner)
        rows.append({
            "Giornata": day,
            "Big match": f"{principal} vs {p_opp}" if pm['home']==principal else f"{p_opp} vs {principal}",
            "Partner": partner,
            "Avversario Partner": partner_opp if partner_opp else "(non trovato)",
            "Casa/Fuori": venue if venue else "-"
        })

result_df = pd.DataFrame(rows)
st.subheader("Risultati")
st.dataframe(result_df, use_container_width=True)

csv = result_df.to_csv(index=False).encode("utf-8")
st.download_button("Scarica CSV", data=csv, file_name="risultati_partner.csv", mime="text/csv")
