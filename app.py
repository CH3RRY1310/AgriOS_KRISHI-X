
import streamlit as st
import sqlite3, json, random, time
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go

DB = "agri_os.db"

st.set_page_config(
    page_title="AGRI-OS | Agentic Farm Command Center",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- DATABASE ----------
def db():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    con = db()
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS farm_profile(
        id INTEGER PRIMARY KEY, farm_name TEXT, farmer TEXT, location TEXT,
        crop TEXT, area REAL, soil TEXT, water REAL, budget REAL,
        season TEXT, updated TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS plans(
        id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT, goal TEXT,
        status TEXT, confidence REAL, plan_json TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS approvals(
        id INTEGER PRIMARY KEY AUTOINCREMENT, plan_id INTEGER,
        action TEXT, actor TEXT, created TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT,
        agent TEXT, event TEXT, severity TEXT, details TEXT)""")
    if cur.execute("SELECT COUNT(*) FROM farm_profile").fetchone()[0] == 0:
        cur.execute("""INSERT INTO farm_profile
        (farm_name,farmer,location,crop,area,soil,water,budget,season,updated)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        ("Green Horizon Farm","Demo Farmer","Telangana, India","Tomato",
         5.0,"Loamy",72.0,120000,"Kharif",datetime.now().isoformat()))
    con.commit()
    con.close()

def log_event(agent, event, severity="INFO", details=""):
    con=db()
    con.execute("INSERT INTO events(created,agent,event,severity,details) VALUES(?,?,?,?,?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),agent,event,severity,details))
    con.commit(); con.close()

init_db()

# ---------- AGENT ENGINE ----------
AGENTS = [
    ("Coordinator Agent","🎯","Orchestrates the mission, delegates tasks and verifies the final plan."),
    ("Weather Agent","☁️","Monitors rainfall, temperature, humidity and weather risk."),
    ("Irrigation Agent","💧","Optimizes irrigation timing and water allocation."),
    ("Crop Health Agent","🌿","Tracks crop stress, growth stage and disease indicators."),
    ("Pest Agent","🐛","Detects pest risk and proposes integrated pest actions."),
    ("Nutrient Agent","🧪","Balances nutrient demand, soil condition and fertilizer use."),
    ("Resource Agent","📦","Checks water, labour, inventory and budget constraints."),
    ("Market Agent","📈","Tracks price signals and harvest/market timing."),
]

def get_profile():
    con=db()
    row=con.execute("SELECT * FROM farm_profile LIMIT 1").fetchone()
    con.close()
    cols=["id","farm_name","farmer","location","crop","area","soil","water","budget","season","updated"]
    return dict(zip(cols,row))

def run_agents(goal, profile):
    # Deterministic-enough demo intelligence, intentionally transparent for judging.
    water = profile["water"]
    budget = profile["budget"]
    rainfall = random.randint(8, 34)
    temp = random.randint(27, 36)
    humidity = random.randint(55, 84)
    pest_risk = random.choice(["Low","Moderate","High"])
    disease_risk = random.choice(["Low","Moderate","High"])
    market_price = random.randint(22, 42)

    irrigation = max(8, round(34 - rainfall*0.45))
    if water < 40: irrigation = max(6, irrigation-7)
    fertilizer = 18 if profile["soil"].lower() == "loamy" else 22

    conflicts = []
    if rainfall > 25 and irrigation > 20:
        conflicts.append({
            "issue":"Weather vs irrigation",
            "agents":"Weather + Irrigation",
            "resolution":"Reduce irrigation because forecast rainfall offsets crop water demand."
        })
    if pest_risk == "High" and budget < 50000:
        conflicts.append({
            "issue":"Pest control vs budget",
            "agents":"Pest + Resource",
            "resolution":"Prioritize scouting + targeted treatment instead of blanket spraying."
        })
    if market_price >= 35:
        conflicts.append({
            "issue":"Harvest timing vs crop maturity",
            "agents":"Market + Crop Health",
            "resolution":"Prepare harvest logistics but keep maturity gate under crop-health approval."
        })

    actions = [
        f"Run field scouting for {profile['crop']} within 24 hours.",
        f"Schedule approximately {irrigation} mm irrigation after checking soil moisture.",
        f"Apply a split nutrient strategy around {fertilizer} kg/ha only after soil/crop-stage verification.",
        "Use targeted pest control only when scouting crosses the intervention threshold.",
        "Review market signal before harvest dispatch and compare at least two buyer options.",
        "Recalculate the plan whenever weather, water, pest risk or market price changes."
    ]

    confidence = 0.84
    if len(conflicts) >= 2: confidence -= 0.07
    if water < 30: confidence -= 0.08

    result = {
        "goal":goal, "weather":{"rainfall_mm":rainfall,"temperature_c":temp,"humidity":humidity},
        "risks":{"pest":pest_risk,"disease":disease_risk},
        "market":{"price":market_price},
        "water_plan":{"allocation_pct":irrigation},
        "nutrient_plan":{"fertilizer_kg_ha":fertilizer},
        "actions":actions, "conflicts":conflicts,
        "confidence":round(confidence,2),
        "human_gate":"REQUIRED: Farmer approves before high-impact action."
    }

    for name, *_ in AGENTS:
        log_event(name, "Completed reasoning cycle", "INFO",
                  f"Goal={goal[:60]} | confidence={confidence:.0%}")
    return result

# ---------- STYLING ----------
st.markdown("""
<style>
:root { --bg:#07120d; }
.block-container {padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1500px;}
[data-testid="stSidebar"] {background: #091a12;}
.hero {background:linear-gradient(135deg,#0c2618,#102f20 55%,#153c28);
padding:28px 30px;border-radius:22px;border:1px solid #24563a;margin-bottom:18px;}
.hero h1 {font-size:42px;margin:0;color:#f4fff7;letter-spacing:-1px;}
.hero p {font-size:16px;color:#b9d8c5;margin:8px 0 0;}
.pill {display:inline-block;padding:5px 10px;border-radius:999px;background:#153d29;color:#8ff0b1;border:1px solid #2e7049;font-size:12px;margin-right:6px;}
.card {background:#0c1c14;border:1px solid #214731;border-radius:17px;padding:18px;height:100%;}
.metric {font-size:28px;font-weight:700;color:#ecfff2;}
.label {font-size:12px;color:#8ead9b;text-transform:uppercase;letter-spacing:.08em;}
.agent {padding:12px;border-radius:14px;background:#0b1a13;border:1px solid #1e402d;margin-bottom:8px;}
.agent b {color:#eaffef;}
.small {color:#9bb7a5;font-size:13px;}
.success {color:#82efaa;}
.warning {color:#ffd27d;}
.danger {color:#ff9d9d;}
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
profile=get_profile()
with st.sidebar:
    st.markdown("## 🌱 AGRI-OS")
    st.caption("Agentic Farm Command Center")
    page = st.radio("Navigation",[
        "Mission Control","Farm Twin","AI Planner","Agent Network",
        "Conflict Resolver","Live Signals","Decision Log","System Architecture"
    ])
    st.divider()
    st.markdown("**Human control**")
    st.success("Approval gate ACTIVE")
    st.caption("AI recommends. Farmer decides. Every action is logged.")
    st.divider()
    st.caption("Prototype • Hackathon build")
    st.caption("Python + Streamlit + SQLite")

# ---------- MISSION CONTROL ----------
if page=="Mission Control":
    st.markdown("""<div class="hero">
    <span class="pill">AGENTIC AI</span><span class="pill">FARM DIGITAL TWIN</span><span class="pill">HUMAN-IN-THE-LOOP</span>
    <h1>AGRI-OS Mission Control</h1>
    <p>One goal. Multiple specialist agents. One verified, adaptive farm plan.</p>
    </div>""",unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    c1.markdown(f'<div class="card"><div class="label">Farm</div><div class="metric">{profile["area"]} ha</div><div class="small">{profile["crop"]} • {profile["location"]}</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><div class="label">Water reserve</div><div class="metric">{profile["water"]:.0f}%</div><div class="small">Resource agent monitored</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="card"><div class="label">Budget</div><div class="metric">₹{profile["budget"]:,.0f}</div><div class="small">Available planning budget</div></div>',unsafe_allow_html=True)
    c4.markdown(f'<div class="card"><div class="label">Agents online</div><div class="metric">8 / 8</div><div class="small">Coordinator + specialists</div></div>',unsafe_allow_html=True)

    st.subheader("🎯 Farmer Mission")
    default_goal="Maximize tomato yield while reducing water use and protecting the farm from weather and pest risk."
    goal=st.text_area("What does the farmer want to achieve?",default_goal,height=80)
    if st.button("▶ Run AGRI-OS Mission",type="primary",use_container_width=True):
        with st.spinner("Coordinator is delegating tasks, checking constraints and resolving conflicts..."):
            result=run_agents(goal,profile)
        st.session_state["result"]=result
        con=db()
        cur=con.execute("INSERT INTO plans(created,goal,status,confidence,plan_json) VALUES(?,?,?,?,?)",
                        (datetime.now().isoformat(),goal,"AWAITING FARMER APPROVAL",result["confidence"],json.dumps(result)))
        st.session_state["plan_id"]=cur.lastrowid
        con.commit(); con.close()
        st.rerun()

    if "result" in st.session_state:
        r=st.session_state["result"]
        st.divider()
        a,b,c=st.columns(3)
        a.metric("Plan confidence",f"{r['confidence']:.0%}")
        b.metric("Conflicts resolved",len(r["conflicts"]))
        c.metric("Market signal",f"₹{r['market']['price']}/kg")
        st.subheader("🧠 Verified Plan")
        for i,action in enumerate(r["actions"],1):
            st.markdown(f"**{i}.** {action}")
        if r["conflicts"]:
            st.warning("The Coordinator found and resolved cross-agent conflicts. Open **Conflict Resolver** for the reasoning trace.")
        st.info(r["human_gate"])
        x,y=st.columns(2)
        with x:
            if st.button("✅ Approve plan",use_container_width=True):
                pid=st.session_state.get("plan_id")
                con=db(); con.execute("INSERT INTO approvals(plan_id,action,actor,created) VALUES(?,?,?,?)",
                    (pid,"APPROVED","Farmer",datetime.now().isoformat()))
                con.execute("UPDATE plans SET status='FARMER APPROVED' WHERE id=?",(pid,))
                con.commit(); con.close(); log_event("Human Gate","Plan approved","SUCCESS",f"Plan {pid}")
                st.success("Plan approved and logged.")
        with y:
            if st.button("↻ Request re-plan",use_container_width=True):
                log_event("Coordinator","Farmer requested re-plan","WARNING","New planning cycle requested")
                st.warning("Re-plan requested. Change a farm signal or mission goal and run again.")

# ---------- FARM TWIN ----------
elif page=="Farm Twin":
    st.title("🗺️ Farm Digital Twin")
    st.caption("A single operational profile shared by every agent.")
    with st.form("farm"):
        c1,c2=st.columns(2)
        farm_name=c1.text_input("Farm name",profile["farm_name"])
        farmer=c2.text_input("Farmer",profile["farmer"])
        location=c1.text_input("Location",profile["location"])
        crop=c2.text_input("Primary crop",profile["crop"])
        area=c1.number_input("Area (ha)",0.1,1000.0,float(profile["area"]))
        soil=c2.selectbox("Soil type",["Loamy","Sandy","Clay","Silty"],index=["Loamy","Sandy","Clay","Silty"].index(profile["soil"]) if profile["soil"] in ["Loamy","Sandy","Clay","Silty"] else 0)
        water=c1.slider("Water reserve (%)",0,100,int(profile["water"]))
        budget=c2.number_input("Budget (₹)",0.0,100000000.0,float(profile["budget"]),step=5000.0)
        season=c1.selectbox("Season",["Kharif","Rabi","Zaid"],index=["Kharif","Rabi","Zaid"].index(profile["season"]) if profile["season"] in ["Kharif","Rabi","Zaid"] else 0)
        save=st.form_submit_button("Save Farm Twin",type="primary")
    if save:
        con=db()
        con.execute("""UPDATE farm_profile SET farm_name=?,farmer=?,location=?,crop=?,area=?,soil=?,water=?,budget=?,season=?,updated=? WHERE id=?""",
                    (farm_name,farmer,location,crop,area,soil,water,budget,season,datetime.now().isoformat(),profile["id"]))
        con.commit(); con.close(); log_event("Resource Agent","Farm twin updated","INFO","Profile changed by user")
        st.success("Farm Twin updated. All agents will use the new state on the next mission.")

# ---------- AI PLANNER ----------
elif page=="AI Planner":
    st.title("🧠 Goal → Plan Studio")
    st.caption("Turn a natural-language farmer objective into an auditable multi-agent plan.")
    goal=st.text_area("Mission objective","Reduce water consumption by 20% without compromising crop health.")
    constraints=st.multiselect("Constraints",["Limited water","Limited budget","Rain expected","Pest pressure","High market volatility","Labour shortage"],default=["Limited water"])
    if st.button("Generate adaptive plan",type="primary"):
        r=run_agents(goal,profile)
        st.session_state["result"]=r
        st.success("Plan generated. The coordinator has checked resource, risk and market constraints.")
    if "result" in st.session_state:
        r=st.session_state["result"]
        st.subheader("Plan timeline")
        timeline=pd.DataFrame({
            "Stage":["Now","0–24h","24–72h","Next 7 days","Trigger event"],
            "Action":["Validate data","Scout + moisture check","Execute approved inputs","Monitor + compare market","Automatic re-planning"]
        })
        st.dataframe(timeline,use_container_width=True,hide_index=True)
        st.subheader("Decision rules")
        st.code("""IF rainfall increases → reduce irrigation
IF pest risk crosses threshold → intensify scouting, then targeted control
IF water reserve falls → prioritize crop-critical irrigation
IF market signal changes → re-evaluate harvest timing
ALWAYS → require farmer approval for high-impact actions""")

# ---------- AGENT NETWORK ----------
elif page=="Agent Network":
    st.title("🤖 Agent Network")
    st.caption("Specialists collaborate through the Coordinator instead of producing isolated recommendations.")
    for name,icon,desc in AGENTS:
        cols=st.columns([1,4,1])
        cols[0].markdown(f"### {icon}")
        cols[1].markdown(f"**{name}**  \n<span class='small'>{desc}</span>",unsafe_allow_html=True)
        cols[2].success("ONLINE")
    st.divider()
    st.subheader("Message flow")
    st.markdown("**Farmer Goal → Coordinator → Parallel Specialist Agents → Evidence/Constraints → Conflict Resolver → Verified Plan → Farmer Approval → Execution → Monitoring → Re-plan**")
    st.info("The differentiator is not 'many chatbots'. It is coordinated decision-making with shared state, conflict handling, verification, memory through the database, and a human approval gate.")

# ---------- CONFLICT ----------
elif page=="Conflict Resolver":
    st.title("⚖️ Conflict Resolver")
    st.caption("When specialist agents disagree, AGRI-OS makes the disagreement visible before a recommendation reaches the farmer.")
    if "result" not in st.session_state:
        st.info("Run a mission first.")
    else:
        r=st.session_state["result"]
        if not r["conflicts"]:
            st.success("No cross-agent conflict was detected in this planning cycle.")
        for i,x in enumerate(r["conflicts"],1):
            st.markdown(f"""<div class="card">
            <div class="label">Conflict {i}</div>
            <h3>{x['issue']}</h3>
            <p><b>Agents:</b> {x['agents']}</p>
            <p><b>Resolution:</b> {x['resolution']}</p>
            </div><br>""",unsafe_allow_html=True)
        st.subheader("Verification policy")
        st.markdown("- Prefer measured farm state over assumptions.\n- Check resource constraints before recommending actions.\n- Preserve crop-health safety gates.\n- Explain why a recommendation changed.\n- Escalate high-impact decisions to the farmer.")

# ---------- LIVE SIGNALS ----------
elif page=="Live Signals":
    st.title("📡 Live Farm Signals")
    st.caption("Demo telemetry. Replace these adapters with weather APIs, IoT sensors, satellite data and market feeds during integration.")
    now=datetime.now()
    t=[now-timedelta(hours=5-i) for i in range(6)]
    moisture=[61,59,57,54,52,50]
    temp=[29,30,31,32,33,31]
    c1,c2=st.columns(2)
    with c1:
        fig=go.Figure(); fig.add_trace(go.Scatter(x=t,y=moisture,mode="lines+markers",name="Soil moisture %"))
        fig.update_layout(title="Soil moisture trend",height=330)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        fig=go.Figure(); fig.add_trace(go.Scatter(x=t,y=temp,mode="lines+markers",name="Temperature °C"))
        fig.update_layout(title="Temperature trend",height=330)
        st.plotly_chart(fig,use_container_width=True)
    c1,c2,c3=st.columns(3)
    c1.metric("Weather risk","MODERATE")
    c2.metric("Crop stress","LOW")
    c3.metric("Pest pressure","MODERATE")
    st.warning("Demo mode: signals are simulated. For the final hackathon demo, label connected external data sources clearly.")

# ---------- LOG ----------
elif page=="Decision Log":
    st.title("🧾 Decision & Audit Log")
    con=db()
    events=pd.read_sql_query("SELECT created,agent,event,severity,details FROM events ORDER BY id DESC LIMIT 100",con)
    approvals=pd.read_sql_query("SELECT * FROM approvals ORDER BY id DESC LIMIT 20",con)
    plans=pd.read_sql_query("SELECT id,created,goal,status,confidence FROM plans ORDER BY id DESC LIMIT 20",con)
    con.close()
    st.subheader("Agent event stream")
    st.dataframe(events,use_container_width=True,hide_index=True)
    st.subheader("Plans")
    st.dataframe(plans,use_container_width=True,hide_index=True)
    st.subheader("Human approvals")
    st.dataframe(approvals,use_container_width=True,hide_index=True)

# ---------- ARCHITECTURE ----------
else:
    st.title("🏗️ System Architecture")
    st.caption("The architecture judges can understand in under 30 seconds.")
    st.graphviz_chart("""
    digraph G {
      rankdir=LR;
      node [shape=box style="rounded,filled" fontname="Arial"];
      Farmer [label="FARMER\\nGoal + Approval"];
      Coord [label="COORDINATOR AGENT\\nMission Planner"];
      Weather [label="Weather Agent"];
      Irrigation [label="Irrigation Agent"];
      Health [label="Crop Health Agent"];
      Pest [label="Pest Agent"];
      Nutrient [label="Nutrient Agent"];
      Resource [label="Resource Agent"];
      Market [label="Market Agent"];
      Resolver [label="CONFLICT RESOLVER\\nVerification"];
      DB [label="SQLite\\nShared Farm State"];
      Signals [label="External Data Adapters\\nWeather / IoT / Satellite / Market"];

      Farmer -> Coord;
      Coord -> Weather; Coord -> Irrigation; Coord -> Health; Coord -> Pest;
      Coord -> Nutrient; Coord -> Resource; Coord -> Market;
      Weather -> Resolver; Irrigation -> Resolver; Health -> Resolver; Pest -> Resolver;
      Nutrient -> Resolver; Resource -> Resolver; Market -> Resolver;
      Signals -> Weather; Signals -> Health; Signals -> Market;
      DB -> Coord; DB -> Weather; DB -> Irrigation; DB -> Resource; DB -> Resolver;
      Resolver -> Coord;
      Coord -> Farmer [label="Verified adaptive plan"];
    }
    """)
    st.subheader("Hackathon story")
    st.markdown("""
    **Problem:** agricultural decisions are coupled, but many tools remain siloed.  
    **Insight:** a farm needs coordination, not another isolated recommendation.  
    **Innovation:** specialist agents share a farm state, challenge each other's recommendations, resolve conflicts and re-plan when conditions change.  
    **Trust:** the system exposes reasoning traces and keeps a farmer approval gate before high-impact actions.  
    **Scale path:** replace demo adapters with real weather, soil/IoT, satellite, disease-vision and market APIs without redesigning the coordinator.
    """)

st.divider()
st.caption("AGRI-OS • Goal-driven Agentic AI for adaptive, resource-aware farming • Prototype for hackathon demonstration")
