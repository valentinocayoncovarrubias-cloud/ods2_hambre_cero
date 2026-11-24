import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ------------------------------------------------------------
# PAGE CONFIGURATION AND DATABASE
# ------------------------------------------------------------
st.set_page_config(
    page_title="Zero Hunger | Mexico & Guanajuato",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "ods2_base_datos_completa.csv"
REQUIRED_COLUMNS = ["ID", "Seccion", "Tema", "Informacion", "Fuente", "Enlace"]

@st.cache_data
def load_database(file_path, modified_time):
    data = pd.read_csv(file_path, encoding="utf-8-sig")
    data.columns = [str(column).strip() for column in data.columns]
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    data["ID"] = pd.to_numeric(data["ID"], errors="coerce")
    for column in ["Seccion", "Tema", "Informacion", "Fuente", "Enlace"]:
        data[column] = data[column].fillna("").astype(str).str.strip()
    return data

try:
    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_FILE.name}. "
            "Place the CSV file in the same folder as app.py."
        )
    DATABASE = load_database(str(DATABASE_FILE), DATABASE_FILE.stat().st_mtime)
except Exception as error:
    st.error("The content database could not be loaded.")
    st.exception(error)
    st.stop()

def section_rows(section_name):
    return DATABASE[DATABASE["Seccion"].str.casefold() == section_name.casefold()].copy()

def get_record(section_name, topic):
    rows = section_rows(section_name)
    match = rows[rows["Tema"].str.casefold() == topic.casefold()]
    return None if match.empty else match.iloc[0]

def render_record(record, show_source=True, style="card"):
    if record is None:
        return
    title = record["Tema"]
    body = record["Informacion"]
    source = record["Fuente"]
    link = record["Enlace"]
    if style == "card":
        st.markdown(
            f'<div class="card"><h3>{title}</h3><p>{body}</p></div>',
            unsafe_allow_html=True
        )
    else:
        st.subheader(title)
        st.write(body)
    if show_source and (source or link):
        source_text = f"**Source:** {source}" if source else ""
        link_text = f" · [Open source ↗]({link})" if link else ""
        st.markdown(source_text + link_text)

def render_section(section_name, columns=1, show_sources=True):
    records = section_rows(section_name)
    if records.empty:
        st.info(f"No records are available for: {section_name}")
        return
    if columns == 1:
        for _, record in records.iterrows():
            render_record(record, show_sources, "plain")
            st.divider()
    else:
        cols = st.columns(columns)
        for index, (_, record) in enumerate(records.iterrows()):
            with cols[index % columns]:
                render_record(record, show_sources, "card")

COLORS = {
    "forest": "#405B35", "leaf": "#76945A", "orange": "#D97822",
    "yellow": "#F2B84B", "cream": "#F3EBDD", "paper": "#FFFFFF",
    "ink": "#26332B", "muted": "#66736A", "line": "#E5E0D5"
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --forest:#405B35; --leaf:#76945A; --orange:#D97822; --yellow:#F2B84B; --cream:#F3EBDD; --paper:#fff; --ink:#26332B; --muted:#66736A; --line:#E5E0D5; }
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;} .stApp{background:var(--cream);color:var(--ink)}
[data-testid="stHeader"]{background:rgba(243,235,221,.88)} [data-testid="stSidebar"]{background:var(--forest)}
[data-testid="stSidebar"] *{color:#fff!important} [data-testid="stSidebar"] [data-testid="stRadio"] label{padding:8px 7px;border-radius:9px}
h1,h2,h3{font-family:'Manrope',sans-serif;color:var(--ink);letter-spacing:-.035em} h1{font-weight:800}
p,li{color:#435047;line-height:1.68}
.hero{background:linear-gradient(105deg,rgba(23,43,29,.96),rgba(64,91,53,.78) 65%,rgba(217,120,34,.4)),url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=85') center/cover;padding:4.2rem 3.2rem;border-radius:28px;color:white;margin-bottom:1.5rem;min-height:330px;display:flex;flex-direction:column;justify-content:center;box-shadow:0 18px 45px rgba(38,51,43,.16)}
.hero h1,.hero p,.hero span{color:white!important}.hero h1{font-size:clamp(2.5rem,5vw,4.5rem);line-height:1.02;margin:.7rem 0 1rem}.hero p{max-width:760px;font-size:1.08rem;color:#F5F4ED!important}
.eyebrow,.section-kicker{color:#A6531C;font-size:.76rem;font-weight:700;text-transform:uppercase;letter-spacing:.13em}
.pill{display:inline-block;background:#FCE8C7;color:#75451F;padding:.35rem .7rem;border-radius:999px;font-size:.78rem;font-weight:700;letter-spacing:.03em}
.card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:1.35rem 1.4rem;height:100%;box-shadow:0 8px 24px rgba(38,51,43,.055)} .card h3{margin-top:.2rem;font-size:1.12rem}
.feature-band{background:#E6EAD9;border:1px solid #D8DEC9;border-radius:22px;padding:1.4rem 1.6rem}.metric{background:#fff;border:1px solid var(--line);border-radius:16px;padding:1.1rem 1.2rem;box-shadow:0 5px 18px rgba(38,51,43,.045)}
.metric .number{font-family:'Manrope';font-size:2rem;font-weight:800;color:var(--forest)}.metric .label{font-size:.88rem;color:var(--muted)}
.note{background:#FFF4DF;border-left:4px solid var(--orange);padding:.9rem 1rem;border-radius:8px;color:#634B2D;font-size:.9rem}
.footer-panel{background:#263D2C;color:#fff;padding:1.7rem;border-radius:22px}.footer-panel h3,.footer-panel p{color:#fff!important}
div.stButton>button{border-radius:999px;border:0;background:var(--orange);color:#fff;font-weight:700;padding:.65rem 1.2rem}div.stButton>button:hover{background:#B95E19;color:#fff}
.stTabs [data-baseweb="tab"]{font-weight:700}.stTabs [aria-selected="true"]{color:var(--forest)!important}[data-testid="stMetric"]{background:#fff;padding:14px;border:1px solid var(--line);border-radius:14px}[data-testid="stImage"] img{border-radius:16px}
a{color:#8A4C1D!important;font-weight:700}[data-testid="stMetricValue"]{color:var(--forest)}[data-testid="stMetricLabel"]{color:var(--muted)}footer{visibility:hidden}
@media(max-width:700px){.hero{padding:2.2rem 1.4rem}}
</style>
""", unsafe_allow_html=True)

for key, default in {
    "saved_projects": [], "game_round": 0, "game_score": 0,
    "game_answers": {}, "game_finished": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

def navigate_to(page_name):
    """Update the sidebar radio value through a button callback."""
    st.session_state["page_choice"] = page_name


PAGES = [
    "Home", "SDG 2: Zero Hunger", "All 17 SDGs", "2050 Simulator",
    "Take Action", "Food Systems Challenge", "User Area", "Resources"
]

with st.sidebar:
    st.markdown("## 🌾 ZERO HUNGER")
    st.markdown("**SDG 2 · 2030 Agenda**")
    st.caption("Knowledge · Sustainability · Action")
    st.divider()
    page = st.radio("NAVIGATION", PAGES, key="page_choice")
    st.divider()
    st.markdown("**Our mission**")
    st.caption("Inform, engage, and promote collective action toward a future with food security.")
    st.caption("Educational project · Mexico")
    st.markdown("---")
    st.caption(f"Content database · {len(DATABASE)} records")

def header(kicker, title, subtitle=None):
    st.markdown(f'<div class="section-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    if subtitle:
        st.write(subtitle)

def metric_card(number, label, detail=""):
    st.markdown(
        f'<div class="metric"><div class="number">{number}</div>'
        f'<div class="label">{label}</div><div style="font-size:.82rem;color:#66736A">{detail}</div></div>',
        unsafe_allow_html=True
    )

def photo_strip(items, columns=3):
    cols = st.columns(columns)
    for i, (url, caption) in enumerate(items):
        with cols[i % columns]:
            st.image(url, caption=caption, use_container_width=True)

def source_note():
    st.markdown(
        '<div class="note"><b>Data note:</b> simulator values are illustrative, not scientific forecasts. '
        'Always check the institution, publication year, methodology, and link before using a statistic.</div>',
        unsafe_allow_html=True
    )

# ------------------------------------------------------------
# HOME
# ------------------------------------------------------------
if page == "Home":
    home_intro = get_record("Home", "Main headline")
    headline = home_intro["Informacion"] if home_intro is not None else "Ending hunger takes more than producing food."
    st.markdown(
        f'<div class="hero"><span class="pill">SDG 2 · 2030 AGENDA</span>'
        f'<h1>Food security in Mexico<br>and Guanajuato.</h1><p>{headline}</p></div>',
        unsafe_allow_html=True
    )
    b1, b2, b3 = st.columns(3)
    with b1:
        st.button(
            "Explore SDG 2 →", use_container_width=True,
            on_click=navigate_to, args=("SDG 2: Zero Hunger",)
        )
    with b2:
        st.button(
            "Try the 2050 simulator →", use_container_width=True,
            on_click=navigate_to, args=("2050 Simulator",)
        )
    with b3:
        st.button(
            "Play the food challenge →", use_container_width=True,
            on_click=navigate_to, args=("Food Systems Challenge",)
        )

    st.markdown('<div class="section-kicker">MEXICO · GUANAJUATO</div>', unsafe_allow_html=True)
    st.subheader("Food security in Mexico and Guanajuato")
    intro = get_record("Home", "Introduction")
    if intro is not None:
        st.write(intro["Informacion"])
        if intro["Enlace"]:
            st.caption(f"Source: {intro['Fuente']} · {intro['Enlace']}")

    # The displayed figures are stored as complete sourced text in the database.
    home_records = section_rows("Home")
    for topic in ["Mexico indicator: food access deprivation",
                  "Guanajuato indicator: food access deprivation",
                  "Mexico indicator: food security and dietary diversity",
                  "Change between 2022 and 2024"]:
        record = get_record("Home", topic)
        if record is not None:
            render_record(record, True, "card")

    st.subheader("Explore the topic from four perspectives")
    cols = st.columns(4)
    perspective_records = [
        ("Home", "Explore the topic: Understand"),
        ("Home", "Explore the topic: Investigate"),
        ("Home", "Explore the topic: Imagine"),
        ("Home", "Explore the topic: Take action")
    ]
    for col, (_, topic) in zip(cols, perspective_records):
        record = get_record("Home", topic)
        with col:
            if record is not None:
                st.markdown(
                    f'<div class="card"><h3>{topic.split(": ",1)[-1]}</h3>'
                    f'<p>{record["Informacion"]}</p></div>', unsafe_allow_html=True
                )

    st.subheader("Food is part of a connected system")
    connected = get_record("Home", "Food is part of a connected system")
    if connected is not None:
        st.write(connected["Informacion"])
        st.caption(f"Source: {connected['Fuente']}")
    photo_strip([
        ("https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=900&q=85", "Nutrition and food diversity"),
        ("https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&w=900&q=85", "Gardens and local production"),
        ("https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=900&q=85", "Responsible consumption")
    ])
    st.subheader("Related Sustainable Development Goals")
    related = section_rows("Home")
    related = related[related["Tema"].str.startswith("Related goal:")]
    render_section("Home", columns=2, show_sources=True) if False else None
    for _, record in related.iterrows():
        with st.expander(record["Tema"]):
            st.write(record["Informacion"])
            if record["Enlace"]:
                st.markdown(f"[{record['Fuente']} ↗]({record['Enlace']})")

    # Our team's video is placed at the very bottom of the Home page.
    st.markdown("---")
    st.subheader("Our project video")
    st.video("https://www.youtube.com/watch?v=xFtQQ0PsWH4")

# ------------------------------------------------------------
# SDG 2 CONTENT
# ------------------------------------------------------------
elif page == "SDG 2: Zero Hunger":
    header("LEARN", "SDG 2: Zero Hunger in Mexico and Guanajuato",
           "Explore national and state-level evidence, local challenges, and practical responses for communities in Guanajuato.")
    tab_names = ["Overview", "Causes", "Consequences", "Data & Charts", "What Can You Do?"]
    tabs = st.tabs(tab_names)

    with tabs[0]:
        render_section("SDG 2: Zero Hunger / Overview", columns=1)
        st.markdown("### Featured video: Understanding Zero Hunger")
        st.video("https://www.youtube.com/watch?v=IpeFw9AcBPg")
        st.caption("Educational video by ECLAC (CEPAL). The video is in Spanish.")

    with tabs[1]:
        st.subheader("Main causes")
        render_section("SDG 2: Zero Hunger / Causes", columns=2)

    with tabs[2]:
        st.subheader("Consequences for people and communities")
        render_section("SDG 2: Zero Hunger / Consequences", columns=2)

    with tabs[3]:
        st.subheader("Mexico and Guanajuato: access to nutritious and quality food")
        render_section("SDG 2: Zero Hunger / Data & Charts", columns=1)
        st.markdown("### Comparison: Mexico and Guanajuato (2022–2024)")
        comparison = pd.DataFrame({
            "Year": [2022, 2022, 2024, 2024],
            "Geographic level": ["Mexico", "Guanajuato", "Mexico", "Guanajuato"],
            "Population with deprivation (%)": [18.2, 18.3, 14.4, 16.9]
        })
        fig = px.bar(
            comparison, x="Year", y="Population with deprivation (%)",
            color="Geographic level", barmode="group", text="Population with deprivation (%)",
            title="Population with deprivation in access to nutritious and quality food"
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(
            xaxis_title="", yaxis_title="Population (%)", yaxis_range=[0, 23],
            plot_bgcolor="white", paper_bgcolor="white", legend_title_text="Geographic level"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Sources: CONEVAL (2022) and INEGI (2024). Estimates refer to the same multidimensional poverty indicator; consult the linked reports for methodology notes.")
        with st.expander("Optional: upload your own CSV data"):
            st.write("Upload a dataset from an official source or a school research project.")
            uploaded = st.file_uploader("Choose a CSV file", type=["csv"], key="ods2_data_upload")
            if uploaded is not None:
                try:
                    data = pd.read_csv(uploaded)
                    st.dataframe(data, use_container_width=True)
                    numeric_columns = data.select_dtypes(include="number").columns.tolist()
                    if numeric_columns:
                        category = st.selectbox("Category column", data.columns.tolist(), key="csv_label_col")
                        value = st.selectbox("Numeric values", numeric_columns, key="csv_value_col")
                        st.plotly_chart(px.bar(data, x=category, y=value, title="Indicators from your file"),
                                        use_container_width=True)
                    else:
                        st.warning("The CSV needs at least one numeric column to create a chart.")
                except Exception as error:
                    st.error(f"Could not read the CSV: {error}")

    with tabs[4]:
        st.subheader("Small actions that can make a difference")
        actions = section_rows("SDG 2: Zero Hunger / What Can You Do?")
        for index, (_, record) in enumerate(actions.iterrows()):
            st.checkbox(record["Tema"], key=f"action_{index}")
            st.caption(record["Informacion"])
            if record["Enlace"]:
                st.markdown(f"[Source: {record['Fuente']} ↗]({record['Enlace']})")
        st.info("Individual actions do not replace public policies, but they can complement community efforts.")

# ------------------------------------------------------------
# ALL 17 SDGS
# ------------------------------------------------------------
elif page == "All 17 SDGs":
    header("THE 2030 AGENDA", "Explore all 17 Sustainable Development Goals",
           "The goals are interconnected. Progress in one area can support progress in many others.")
    goals = section_rows("All 17 SDGs")
    for start in range(0, len(goals), 4):
        cols = st.columns(4)
        batch = goals.iloc[start:start + 4]
        for column, (_, goal) in zip(cols, batch.iterrows()):
            with column:
                try:
                    goal_number = int(str(goal["Tema"]).split(".", 1)[0])
                    icon_url = f"https://sdgs.un.org/sites/default/files/goals/E_SDG_Icons-{goal_number:02d}.jpg"
                    st.image(icon_url, use_container_width=True)
                except Exception:
                    pass
                st.markdown(f"**{goal['Tema']}**")
                st.write(goal["Informacion"])
                if goal["Enlace"]:
                    st.markdown(f"[Official UN goal page ↗]({goal['Enlace']})")
    st.caption("Goal descriptions and links are loaded from the CSV content database.")

# ------------------------------------------------------------
# 2050 SIMULATOR
# ------------------------------------------------------------
elif page == "2050 Simulator":
    header("INTERACTIVE SIMULATION", "Explore possible futures toward 2050",
           "Use Mexico and Guanajuato as the context for an educational scenario. Adjust the variables and compare possible pathways; results are illustrative, not forecasts.")
    render_section("2050 Simulator", columns=1)
    source_note()
    st.markdown("### Adjust the variables")
    c1, c2 = st.columns(2)
    with c1:
        population = st.slider("Population growth (%)", 0, 60, 20, 1)
        production = st.slider("Improvement in food production (%)", -20, 60, 15, 1)
    with c2:
        consumption = st.slider("Improvement in responsible consumption (%)", 0, 60, 10, 1)
        policies = st.slider("Implementation of sustainable policies (%)", 0, 100, 65, 1)

    pressure = population * .45 - production * .55 - consumption * .20 - policies * .18
    food_index = max(0, min(100, 60 - pressure * .65))
    waste_index = max(0, min(100, consumption * .65 + policies * .35))
    production_index = max(0, min(100, 50 + production * .8))

    st.markdown("### Your scenario results")
    a, b, c = st.columns(3)
    with a:
        metric_card(f"{food_index:.0f}/100", "Illustrative food security index", "Educational indicator")
    with b:
        metric_card(f"{production_index:.0f}/100", "Illustrative production index", "Educational indicator")
    with c:
        metric_card(f"{waste_index:.0f}/100", "Responsible consumption index", "Educational indicator")

    st.markdown("### Compare scenarios")
    scenarios = pd.DataFrame({
        "Scenario": ["Optimistic", "Baseline", "Challenging", "Your scenario"],
        "Food security index": [82, 60, 35, food_index],
        "Production index": [78, 60, 42, production_index],
        "Responsible consumption index": [80, 48, 25, waste_index]
    })
    selected = st.selectbox("Indicator to compare", [
        "Food security index", "Production index", "Responsible consumption index"
    ])
    chart = px.bar(scenarios, x="Scenario", y=selected, color="Scenario",
                   title=f"Illustrative comparison: {selected}", range_y=[0, 100])
    chart.update_layout(yaxis_title="Illustrative index (0–100)", xaxis_title="")
    st.plotly_chart(chart, use_container_width=True)

    if food_index >= 70:
        st.success("Your combination represents a relatively favorable educational scenario.")
    elif food_index >= 45:
        st.info("Your combination represents an intermediate scenario. Sustainable production and policy improvements can influence the result.")
    else:
        st.warning("Your combination represents a scenario with greater challenges. Review how each variable affects the result.")

# ------------------------------------------------------------
# TAKE ACTION
# ------------------------------------------------------------
elif page == "Take Action":
    header("CITIZEN PARTICIPATION", "Your actions can help communities",
           "Explore examples of actions that can support food security and sustainability.")
    photo_strip([
        ("https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&w=900&q=85", "Community gardens"),
        ("https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=900&q=85", "Fresh food and consumption"),
        ("https://images.unsplash.com/photo-1511632765486-a01980e01a18?auto=format&fit=crop&w=900&q=85", "Community collaboration")
    ])
    action_records = section_rows("Take Action")
    cols = st.columns(3)
    for index, (_, record) in enumerate(action_records.iterrows()):
        with cols[index % 3]:
            st.markdown(
                f'<div class="card"><h3>{record["Tema"]}</h3>'
                f'<p>{record["Informacion"]}</p></div>', unsafe_allow_html=True
            )
            if record["Enlace"]:
                st.markdown(f"[{record['Fuente']} ↗]({record['Enlace']})")
            if st.button("Save project", key=f"save_project_{int(record['ID'])}"):
                name = record["Tema"]
                if name not in st.session_state.saved_projects:
                    st.session_state.saved_projects.append(name)
                st.success("Project saved to your User Area.")

    st.info("This is an educational demonstration: it does not process donations or register volunteers. Verify organizations before participating.")

# ------------------------------------------------------------
# FOOD SYSTEMS CHALLENGE
# ------------------------------------------------------------
elif page == "Food Systems Challenge":
    header("LEARN BY PLAYING", "Food Systems Challenge",
           "Make decisions about everyday food-system challenges. Earn points and learn why each choice matters.")

    game_records = section_rows("Food Systems Challenge")
    game_records = game_records[game_records["Tema"].str.startswith("Round ")]
    questions = [
        {
            "topic": "Round 1: Food waste at school",
            "question": "Your school cafeteria has a lot of uneaten food at the end of lunch. What is the best first step?",
            "options": ["Measure what is being wasted and learn why", "Throw everything away without checking", "Order more food every day"],
            "correct": 0
        },
        {
            "topic": "Round 2: Water shortages on farms",
            "question": "A farming community is experiencing water shortages. Which approach can help use water more sustainably?",
            "options": ["Ignore water use", "Explore efficient irrigation and soil-moisture practices", "Use more water at the hottest time of day"],
            "correct": 1
        },
        {
            "topic": "Round 3: Access to nutritious food",
            "question": "A neighborhood has limited access to varied, nutritious food. Which response is most useful?",
            "options": ["Assume everyone can travel elsewhere", "Focus only on advertising snacks", "Work with the community to identify barriers and improve access"],
            "correct": 2
        },
        {
            "topic": "Round 4: Food loss during transport",
            "question": "Fresh produce is being lost before reaching stores. What could help reduce these losses?",
            "options": ["Improve storage, handling, and transport conditions", "Leave produce exposed to heat", "Avoid checking the condition of deliveries"],
            "correct": 0
        },
        {
            "topic": "Round 5: Responsible consumption",
            "question": "You want to reduce food waste at home. Which habit is a good place to start?",
            "options": ["Buy more than you can use", "Plan meals and check what you already have", "Throw away food as soon as it is not perfectly shaped"],
            "correct": 1
        }
    ]

    if not st.session_state.game_finished:
        round_index = st.session_state.game_round
        if round_index < len(questions):
            question = questions[round_index]
            db_record = get_record("Food Systems Challenge", question["topic"])
            st.progress(round_index / len(questions), text=f"Round {round_index + 1} of {len(questions)}")
            st.markdown(
                f'<div class="feature-band"><div class="section-kicker">{question["topic"].split(": ",1)[-1]}</div>'
                f'<h3>{question["question"]}</h3></div>', unsafe_allow_html=True
            )
            answer = st.radio("Choose your answer:", question["options"],
                             key=f"game_answer_{round_index}", index=None)
            if st.button("Submit answer", disabled=answer is None):
                selected_answer = question["options"].index(answer)
                st.session_state.game_answers[round_index] = selected_answer
                if selected_answer == question["correct"]:
                    st.session_state.game_score += 1
                st.session_state.game_round += 1
                if st.session_state.game_round >= len(questions):
                    st.session_state.game_finished = True
                st.rerun()
            if db_record is not None:
                st.caption(f"Learning source: {db_record['Fuente']}")
    else:
        st.progress(1.0, text="Challenge completed")
        st.markdown(
            f'<div class="feature-band"><div class="section-kicker">FINAL SCORE</div>'
            f'<h2>{st.session_state.game_score} / {len(questions)}</h2>'
            f'<p>{"Excellent work! You made thoughtful choices across the food system." if st.session_state.game_score >= 4 else "Good effort! Review the explanations and try again to strengthen your understanding."}</p></div>',
            unsafe_allow_html=True
        )
        for index, question in enumerate(questions):
            db_record = get_record("Food Systems Challenge", question["topic"])
            selected_answer = st.session_state.game_answers.get(index, -1)
            st.markdown(f"**{index + 1}. {question['topic'].split(': ',1)[-1]}**")
            if selected_answer == question["correct"]:
                st.success(f"Correct: {question['options'][question['correct']]}")
            else:
                st.warning(f"Correct answer: {question['options'][question['correct']]}")
            if db_record is not None:
                st.write(db_record["Informacion"])
                if db_record["Enlace"]:
                    st.markdown(f"[{db_record['Fuente']} ↗]({db_record['Enlace']})")
        if st.button("Play again"):
            st.session_state.game_round = 0
            st.session_state.game_score = 0
            st.session_state.game_answers = {}
            st.session_state.game_finished = False
            st.rerun()

    intro_game = get_record("Food Systems Challenge", "Game introduction")
    if intro_game is not None:
        st.caption(intro_game["Informacion"])

# ------------------------------------------------------------
# USER AREA
# ------------------------------------------------------------
elif page == "User Area":
    header("YOUR SPACE", "User Area", "Review the projects you have saved.")
    st.subheader("Saved projects")
    if st.session_state.saved_projects:
        for project in st.session_state.saved_projects:
            st.markdown(f"- {project}")
        if st.button("Clear saved projects"):
            st.session_state.saved_projects = []
            st.rerun()
    else:
        st.write("You have not saved any projects yet. Visit Take Action to explore examples.")


# ------------------------------------------------------------
# RESOURCES
# ------------------------------------------------------------
elif page == "Resources":
    header("LIBRARY", "Reliable resources and sources",
           "Explore institutions and materials to learn more about SDG 2 and food security.")
    resources = section_rows("Resources")
    for index, (_, record) in enumerate(resources.iterrows()):
        st.markdown(
            f'<div class="card"><h3>{record["Tema"]}</h3>'
            f'<p>{record["Informacion"]}</p></div>', unsafe_allow_html=True
        )
        if record["Enlace"]:
            st.markdown(f"[{record['Fuente']} ↗]({record['Enlace']})")
        st.write("")

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
footer = get_record("General / Footer", "Educational disclaimer")
st.markdown("---")
st.markdown(
    '<div class="footer-panel"><div class="section-kicker">SDG 2 · ZERO HUNGER</div>'
    '<h3>A fairer future is built together.</h3>'
    '<p>Educational platform · Mexico · 2030 Agenda</p>'
    '<p style="font-size:.82rem;opacity:.82">Informational content. Consult institutional sources for the methodology, date, and scope of each indicator. Simulations are illustrative and are not predictions.</p></div>',
    unsafe_allow_html=True
)
if footer is not None:
    st.caption(footer["Informacion"])
    if footer["Enlace"]:
        st.caption(f"General source: {footer['Fuente']} · {footer['Enlace']}")
st.caption(f"Content loaded from {DATABASE_FILE.name} · {len(DATABASE)} records.")
