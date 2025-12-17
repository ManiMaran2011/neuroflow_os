import streamlit as st
import requests
import time

BACKEND_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="NeuroFlow OS",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #05050a;
    color: #e5e7eb;
}

/* Title */
.title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 900;
    color: #7c3aed;
    text-shadow: 0 0 25px rgba(124,58,237,0.9);
    margin-bottom: 0.5rem;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 1.2rem;
    color: #22d3ee;
    margin-bottom: 2rem;
    text-shadow: 0 0 12px rgba(34,211,238,0.8);
}

/* Input box */
textarea {
    background: #0b0b12 !important;
    color: #e5e7eb !important;
    border-radius: 12px !important;
    border: 1px solid #1f2937 !important;
}

/* EXECUTE BUTTON — FINAL FIX */
div[data-testid="stButton"] > button {
    background: linear-gradient(90deg, #7c3aed, #22d3ee) !important;
    color: black !important;
    font-weight: 800 !important;
    border-radius: 14px !important;
    padding: 0.7rem 1.6rem !important;
    border: none !important;
    box-shadow: 0 0 20px rgba(34,211,238,0.6) !important;
}

div[data-testid="stButton"] > button:hover {
    background: linear-gradient(90deg, #22d3ee, #7c3aed) !important;
    box-shadow: 0 0 30px rgba(124,58,237,0.9) !important;
    transform: scale(1.05);
}

/* Agent card */
.agent-card {
    background: #0b0b12;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 0 15px rgba(124,58,237,0.25);
}

/* Summary card */
.summary {
    background: linear-gradient(135deg, #0b0b12, #111827);
    border-radius: 16px;
    padding: 1.4rem;
    margin-top: 2rem;
    border: 1px solid #22d3ee;
    box-shadow: 0 0 25px rgba(34,211,238,0.5);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">NeuroFlow OS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">🧠 Command the system</div>', unsafe_allow_html=True)

user_input = st.text_area(
    "",
    placeholder="Type a command like: add task buy groceries and remind me tomorrow"
)

execute = st.button("🚀 Execute")

if execute and user_input.strip():
    with st.spinner("Initializing AI agents..."):
        time.sleep(0.6)

    response = requests.post(BACKEND_URL, json={"user_input": user_input})
    data = response.json()["response"]

    agents = data["agents"]

    st.markdown("### 🤖 Agent Execution")

    for agent_name, result in agents.items():
        with st.container():
            st.markdown(
                f"""
                <div class="agent-card">
                    <strong>{agent_name}</strong><br/>
                    <span style="color:#22d3ee">{result['message']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(0.35)

    st.markdown(
        """
        <div class="summary">
            <h3>✅ System Summary</h3>
            <ul>
                <li>📌 Task created</li>
                <li>⏰ Reminder scheduled</li>
                <li>📅 Calendar updated</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )



