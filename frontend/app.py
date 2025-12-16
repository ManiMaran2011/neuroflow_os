import streamlit as st
import requests

st.set_page_config(
    page_title="NeuroFlow OS",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

body {
    background: radial-gradient(circle at top right, #2b3a42, #0f172a);
    color: #e5e7eb;
}

.main {
    background: transparent;
}

.container {
    max-width: 1200px;
    margin: auto;
    padding-top: 4rem;
}

.hero {
    margin-bottom: 3rem;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 300;
    letter-spacing: 0.08em;
    line-height: 1.1;
}

.hero-subtitle {
    margin-top: 1rem;
    max-width: 520px;
    font-size: 0.95rem;
    color: #9ca3af;
}

.panel {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 1.6rem;
    margin-bottom: 2rem;
}

.run-btn button {
    background: #e5e7eb;
    color: #0f172a;
    border-radius: 999px;
    font-weight: 500;
    height: 2.8rem;
}

.agent-block {
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 1rem 0;
}

.agent-name {
    font-size: 0.8rem;
    letter-spacing: 0.12em;
    color: #9ca3af;
    margin-bottom: 0.4rem;
}

.agent-output {
    font-size: 0.95rem;
    color: #e5e7eb;
    white-space: pre-wrap;
}

.footer {
    margin-top: 5rem;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    color: #6b7280;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='container'>", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-title">NEUROFLOW OS</div>
    <div class="hero-subtitle">
        A multi-agent artificial intelligence operating system for structured thinking,
        productivity, and autonomous decision workflows.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='panel'>", unsafe_allow_html=True)
user_input = st.text_area(
    "Command",
    placeholder="Add buy groceries to my tasks and schedule it tomorrow",
    height=90
)
run = st.button("Execute", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

if run and user_input.strip():
    with st.spinner("Processing…"):
        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json={"user_input": user_input}
        )

    if response.status_code == 200:
        raw = response.json().get("response", "")
        st.markdown("<div class='panel'>", unsafe_allow_html=True)

        for line in raw.split("\n"):
            if ":" in line:
                agent, content = line.split(":", 1)
                st.markdown(f"""
                <div class="agent-block">
                    <div class="agent-name">{agent.upper()}</div>
                    <div class="agent-output">{content.strip()}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Backend error")

elif run:
    st.warning("Please enter a command")

st.markdown("""
<div class="footer">
    MULTI-AGENT ARCHITECTURE · PARENT–CHILD ORCHESTRATION · GENAI SYSTEM
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

