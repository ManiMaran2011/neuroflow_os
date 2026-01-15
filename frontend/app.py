import streamlit as st
import requests

from voice import listen_from_mic  # LOCAL MIC ONLY

API_BASE = "http://127.0.0.1:8000"

# ======================
# SESSION INIT
# ======================
if "token" not in st.session_state:
    st.session_state.token = None

if "email" not in st.session_state:
    st.session_state.email = None

if "execution_plan" not in st.session_state:
    st.session_state.execution_plan = None

if "execution_id" not in st.session_state:
    st.session_state.execution_id = None

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

# ======================
# HEADER
# ======================
st.markdown(
    """
    <h1 style='text-align: center;'>🧠 NeuroFlow OS</h1>
    <p style='text-align: center; color: gray;'>Agentic AI Execution System</p>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ======================
# LOGIN
# ======================
if not st.session_state.token:
    st.markdown("### Login")

    email = st.text_input(
        "Email",
        placeholder="Enter your email",
        label_visibility="collapsed"
    )

    if st.button("Login", use_container_width=True):
        if not email:
            st.warning("Please enter your email")
        else:
            try:
                res = requests.post(
                    f"{API_BASE}/auth/login",
                    json={"email": email},
                    timeout=5
                )

                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.email = email
                    st.success("Logged in")
                    st.rerun()
                else:
                    st.error("Login failed")

            except Exception:
                st.error("Backend not reachable")

    st.stop()

# ======================
# MAIN INTERFACE
# ======================
st.markdown(f"Logged in as **{st.session_state.email}**")
st.divider()

st.markdown("### Type or Speak your request")

col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "User Request",
        value=st.session_state.voice_text,
        placeholder="Type your request here...",
        label_visibility="collapsed"
    )

with col2:
    if st.button("🎤", use_container_width=True):
        with st.spinner("Listening..."):
            spoken = listen_from_mic()
            if spoken:
                st.session_state.voice_text = spoken
                st.rerun()
            else:
                st.warning("Could not understand speech")

# ======================
# EXECUTE
# ======================
if st.button("Execute", use_container_width=True):
    final_input = user_input or st.session_state.voice_text

    if not final_input:
        st.warning("Please enter or speak a request")
    else:
        try:
            res = requests.post(
                f"{API_BASE}/ask",
                headers={
                    "Authorization": f"Bearer {st.session_state.token}"
                },
                json={
                    "user_input": final_input
                },
                timeout=10
            )

            if res.status_code == 200:
                data = res.json()
                st.session_state.execution_plan = data.get("execution_plan", {})
                st.session_state.execution_id = data.get("execution_id")
                st.success("Execution plan generated")
            else:
                st.error("Failed to generate execution plan")

        except Exception:
            st.error("Backend not reachable")

# ======================
# SHOW EXECUTION PLAN
# ======================
if st.session_state.execution_plan is not None:
    plan = st.session_state.execution_plan

    st.divider()
    st.markdown("### Execution Plan")

    st.json({
        "intent": plan.get("intent"),
        "agents": plan.get("agents"),
        "actions": plan.get("actions"),
        "params": plan.get("params"),
        "requires_approval": plan.get("requires_approval"),
    })

# ======================
# APPROVAL
# ======================
if (
    st.session_state.execution_id
    and st.session_state.execution_plan
    and st.session_state.execution_plan.get("requires_approval")
):
    st.divider()
    st.markdown("### Approval Required")

    if st.button("Approve & Execute", use_container_width=True):
        try:
            res = requests.post(
                f"{API_BASE}/executions/{st.session_state.execution_id}/approve",
                headers={
                    "Authorization": f"Bearer {st.session_state.token}"
                },
                timeout=10
            )

            if res.status_code == 200:
                st.success("Execution completed")
                st.json(res.json())
            else:
                st.warning(res.json().get("detail", "Approval failed"))

        except Exception:
            st.error("Backend not reachable")
























