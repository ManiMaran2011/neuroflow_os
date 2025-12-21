import streamlit as st
import requests
import time

BACKEND_URL = "http://127.0.0.1:8000/ask"

ALL_AGENTS = [
    "TaskAgent",
    "CalendarAgent",
    "NotificationAgent",
    "ResearchAgent",
    "BrowserAgent",
    "XPAgent",
    "ReportAgent",
    "ContactAgent",
    "EnergyAgent"
]

st.set_page_config(page_title="NeuroFlow OS", layout="centered")

if "xp" not in st.session_state:
    st.session_state.xp = 0
if "level" not in st.session_state:
    st.session_state.level = 1
if "status" not in st.session_state:
    st.session_state.status = None
if "execution_plan" not in st.session_state:
    st.session_state.execution_plan = None
if "last_input" not in st.session_state:
    st.session_state.last_input = ""

st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #05050a;
    color: #e5e7eb;
}

.title {
    text-align: center;
    font-size: 3rem;
    font-weight: 900;
    color: #7c3aed;
    text-shadow: 0 0 18px rgba(124,58,237,0.8);
    margin-bottom: 0.4rem;
}

.xp-card {
    background: linear-gradient(135deg, #0b0b12, #111827);
    border: 1px solid #7c3aed;
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin: 1.2rem 0;
    box-shadow: 0 0 18px rgba(124,58,237,0.35);
}

.xp-header {
    display: flex;
    justify-content: space-between;
    font-weight: 800;
    color: #a78bfa;
    margin-bottom: 0.6rem;
}

.xp-bar {
    background: #1f2937;
    border-radius: 10px;
    overflow: hidden;
    height: 10px;
}

.xp-fill {
    height: 100%;
    background: linear-gradient(90deg, #7c3aed, #22d3ee);
}

.timeline-box {
    background: #0b0b12;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 1rem;
    margin-top: 1.2rem;
}

.agent-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 0.8rem;
    margin-top: 1rem;
}

.agent-tile {
    background: #0b0b12;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 0.9rem;
    box-shadow: 0 0 14px rgba(124,58,237,0.25);
}

.agent-name {
    font-weight: 800;
    color: #e5e7eb;
}

.agent-status {
    font-size: 0.85rem;
    margin-top: 0.4rem;
}

.status-executed {
    color: #22c55e;
}

.status-skipped {
    color: #9ca3af;
}

.status-not-required {
    color: #64748b;
}

.status-active {
    color: #facc15;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}

button {
    background: linear-gradient(90deg, #7c3aed, #22d3ee) !important;
    color: black !important;
    font-weight: 800 !important;
    border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">NeuroFlow OS</div>', unsafe_allow_html=True)

progress = min((st.session_state.xp % 50) * 2, 100)

st.markdown(
    f"""
    <div class="xp-card">
        <div class="xp-header">
            <span>⚡ Level {st.session_state.level}</span>
            <span>{st.session_state.xp} XP</span>
        </div>
        <div class="xp-bar">
            <div class="xp-fill" style="width:{progress}%"></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

user_input = st.text_area(
    "",
    placeholder="Type a command like: add task buy groceries and remind me"
)

if st.button("🚀 Execute"):
    st.session_state.last_input = user_input

    response = requests.post(
        BACKEND_URL,
        json={
            "user_input": user_input,
            "approved": False,
            "execution_plan": None
        }
    ).json()

    st.session_state.status = response["status"]
    st.session_state.execution_plan = response.get("execution_plan")

    st.markdown('<div class="timeline-box"><b>🧭 Execution Timeline</b></div>', unsafe_allow_html=True)
    for step in response.get("timeline", []):
        st.markdown(f"- {step}")

    if response["status"] == "think":
        st.markdown('<div class="timeline-box"><b>🧠 Answer</b></div>', unsafe_allow_html=True)
        st.write(response["answer"])

if st.session_state.status == "awaiting_approval":
    if st.button("✅ Approve Execution"):
        response = requests.post(
            BACKEND_URL,
            json={
                "user_input": st.session_state.last_input,
                "approved": True,
                "execution_plan": st.session_state.execution_plan
            }
        ).json()

        st.session_state.status = response["status"]
        st.session_state.execution_plan = response.get("execution_plan", st.session_state.execution_plan)

        st.markdown('<div class="timeline-box"><b>🧭 Execution Timeline</b></div>', unsafe_allow_html=True)
        for step in response.get("timeline", []):
            st.markdown(f"- {step}")

        results = response.get("results", {})

        if "XPAgent" in results:
            old_level = st.session_state.level
            st.session_state.xp = results["XPAgent"]["data"]["xp"]
            st.session_state.level = results["XPAgent"]["data"]["level"]

            if st.session_state.level > old_level:
                st.success(f"⚡ LEVEL UP! You reached Level {st.session_state.level}")
                time.sleep(0.8)

        st.markdown("### 🤖 Agent Swarm (Full View)")

        planned = set(st.session_state.execution_plan["agents"])
        executed = set(results.keys())

        container = st.container()

        with container:
            st.markdown('<div class="agent-grid">', unsafe_allow_html=True)

            for agent in ALL_AGENTS:
                if agent in executed:
                    final_status = "EXECUTED"
                    final_class = "status-executed"
                elif agent in planned:
                    final_status = "SKIPPED"
                    final_class = "status-skipped"
                else:
                    final_status = "NOT REQUIRED"
                    final_class = "status-not-required"

                st.markdown(
                    f"""
                    <div class="agent-tile">
                        <div class="agent-name">{agent}</div>
                        <div class="agent-status status-active">ACTIVE</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                time.sleep(0.3)

                st.markdown(
                    f"""
                    <div class="agent-tile">
                        <div class="agent-name">{agent}</div>
                        <div class="agent-status {final_class}">{final_status}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                time.sleep(0.15)

            st.markdown('</div>', unsafe_allow_html=True)
















