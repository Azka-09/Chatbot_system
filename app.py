import uuid
from datetime import datetime

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openai import (
    APIConnectionError,
    AuthenticationError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)

st.set_page_config(page_title="Mini GPT", page_icon="🤖", layout="wide")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
st.session_state.setdefault("chats", {})
st.session_state.setdefault("active_chat", None)
st.session_state.setdefault("api_key", "")      # kept server-side in the session only
st.session_state.setdefault("connected", False)
st.session_state.setdefault("animate_in", False)
st.session_state.setdefault("pending_prompt", None)

connected = st.session_state.connected

# ---------------------------------------------------------------------------
# Styling (royal blue / deep navy theme)
# ---------------------------------------------------------------------------
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root{
  --royal:#4169E1; --blue:#2563EB; --sky:#38BDF8; --lav:#A5B4FC;
  --navy:#0B1224; --card:#111C35; --text:#F8FAFC; --muted:#CBD5E1;
  --border:rgba(165,180,252,.18);
}

html, body, .stApp, [class*="css"]{ font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif; }
.stApp{
  color:var(--text); font-size:16px; line-height:1.65;
  background:
    radial-gradient(ellipse 60% 50% at 15% 10%, rgba(65,105,225,.30), transparent 70%),
    radial-gradient(ellipse 50% 45% at 90% 90%, rgba(56,189,248,.16), transparent 70%),
    radial-gradient(ellipse 40% 40% at 80% 5%, rgba(165,180,252,.10), transparent 70%),
    var(--navy);
  background-size:140% 140%, 140% 140%, 140% 140%, auto;
  animation:drift 22s ease-in-out infinite alternate;
}
@keyframes drift{ 0%{background-position:0% 0%,100% 100%,100% 0%,0 0;} 100%{background-position:30% 20%,70% 80%,60% 30%,0 0;} }
@keyframes fadeUp{ from{opacity:0; transform:translateY(18px);} to{opacity:1; transform:none;} }
@keyframes popIn{ from{opacity:0; transform:translateY(10px) scale(.985);} to{opacity:1; transform:none;} }
@keyframes glow{ 0%,100%{box-shadow:0 0 14px rgba(65,105,225,.45), 0 4px 14px rgba(0,0,0,.35);} 50%{box-shadow:0 0 26px rgba(56,189,248,.55), 0 4px 14px rgba(0,0,0,.35);} }
@keyframes floaty{ 0%,100%{transform:translateY(0);} 50%{transform:translateY(-8px);} }
@keyframes dot{ 0%,80%,100%{opacity:.25; transform:scale(.7);} 40%{opacity:1; transform:scale(1);} }
@keyframes pulse{ 0%,100%{opacity:1;} 50%{opacity:.45;} }

#MainMenu, footer{ visibility:hidden; }
header[data-testid="stHeader"]{ background:transparent; }
.block-container{ padding-top:2rem; padding-bottom:7rem; max-width:920px; }

/* Typography */
h1,h2,h3,h4{ color:var(--text); letter-spacing:-.01em; font-weight:700; }
h1{ font-size:2rem; } h2{ font-size:1.5rem; } h3{ font-size:1.2rem; }
p, li, label, .stMarkdown{ color:var(--text); font-size:1rem; }
[data-testid="stCaptionContainer"], .stCaption, small{ color:var(--muted)!important; font-size:.875rem; }
a{ color:var(--sky); }

/* Sidebar */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0E1A38 0%,#0B1224 100%);
  border-right:1px solid var(--border);
  transition:all .3s ease;
}
[data-testid="stSidebar"] *{ color:var(--text); }
.brand{ display:flex; align-items:center; gap:.7rem; margin:.2rem 0 1rem; }
.brand .logo{
  width:42px; height:42px; border-radius:12px; display:grid; place-items:center; font-size:1.4rem;
  background:linear-gradient(135deg,var(--royal),var(--sky)); box-shadow:0 0 18px rgba(65,105,225,.55);
}
.brand .name{ font-size:1.25rem; font-weight:700; }
.brand .sub{ font-size:.8rem; color:var(--muted); }
.status-pill{
  display:inline-flex; align-items:center; gap:.5rem; padding:.35rem .8rem; border-radius:999px;
  background:rgba(34,197,94,.12); border:1px solid rgba(34,197,94,.4); color:#86EFAC; font-size:.85rem; font-weight:500;
}
.status-pill i{ width:8px; height:8px; border-radius:50%; background:#22C55E; animation:pulse 2s infinite; }

/* Buttons */
.stButton > button, [data-testid="stFormSubmitButton"] > button{
  border-radius:12px; border:1px solid var(--border); background:var(--card); color:var(--text);
  font-weight:500; font-size:.95rem; padding:.55rem .9rem; transition:all .2s ease;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover{
  border-color:var(--sky); background:#162548; transform:translateY(-1px); box-shadow:0 6px 16px rgba(37,99,235,.25); color:#fff;
}
.stButton > button:active, [data-testid="stFormSubmitButton"] > button:active{ transform:scale(.98); }
button[kind="primary"], button[kind="primaryFormSubmit"], [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"]{
  background:linear-gradient(135deg,var(--royal),var(--blue) 55%,var(--sky))!important; border:none!important; color:#fff!important;
  font-weight:600!important; font-size:1rem!important; padding:.7rem 1rem!important; animation:glow 3.5s ease-in-out infinite;
}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primaryFormSubmit"]:hover{
  transform:translateY(-2px); filter:brightness(1.08);
}

/* Inputs */
input, textarea, [data-baseweb="select"] > div{
  background:var(--card)!important; color:var(--text)!important; border-radius:12px!important;
  border:1px solid var(--border)!important; font-size:1rem!important;
}
input::placeholder, textarea::placeholder{ color:#94A3B8!important; opacity:1; }
input:focus, textarea:focus{ border-color:var(--sky)!important; box-shadow:0 0 0 3px rgba(56,189,248,.25)!important; }
[data-baseweb="popover"] ul{ background:var(--card)!important; }
[data-baseweb="popover"] li{ color:var(--text)!important; }
[data-testid="stForm"]{
  background:linear-gradient(180deg,rgba(17,28,53,.92),rgba(17,28,53,.78)); border:1px solid var(--border);
  border-radius:20px; padding:1.4rem; box-shadow:0 20px 50px rgba(0,0,0,.4);
}
[data-testid="stExpander"]{ background:var(--card); border:1px solid var(--border)!important; border-radius:12px; }
hr{ border-color:var(--border)!important; }

/* Chat */
[data-testid="stChatMessage"]{
  border-radius:18px; padding:1rem 1.15rem; margin-bottom:.9rem; border:1px solid var(--border);
  background:var(--card); box-shadow:0 6px 18px rgba(0,0,0,.28); animation:popIn .35s ease both;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){
  background:linear-gradient(135deg,rgba(65,105,225,.55),rgba(37,99,235,.35)); border-color:rgba(65,105,225,.6);
}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li{ line-height:1.7; }
[data-testid="stChatMessage"] [data-testid="stCaptionContainer"]{ font-size:.8rem; margin-top:.3rem; }

/* Code blocks: scroll horizontally, keep readable */
pre, [data-testid="stCode"]{ border-radius:12px!important; border:1px solid var(--border); background:#0A1020!important; overflow-x:auto!important; }
code{ font-family:'JetBrains Mono',ui-monospace,Consolas,monospace!important; font-size:.9rem!important; }
:not(pre) > code{ background:rgba(65,105,225,.2)!important; color:var(--lav)!important; padding:.1rem .4rem; border-radius:6px; }

/* Chat input pinned to bottom */
[data-testid="stBottom"], [data-testid="stBottom"] > div{ background:linear-gradient(180deg,transparent,var(--navy) 40%)!important; }
[data-testid="stChatInput"]{ background:var(--card); border:1px solid var(--border); border-radius:16px; box-shadow:0 8px 28px rgba(0,0,0,.4); transition:all .2s; }
[data-testid="stChatInput"]:focus-within{ border-color:var(--sky); box-shadow:0 0 0 3px rgba(56,189,248,.22), 0 8px 28px rgba(0,0,0,.4); }
[data-testid="stChatInput"] textarea{ border:none!important; box-shadow:none!important; background:transparent!important; }
[data-testid="stChatInput"] button{ background:linear-gradient(135deg,var(--royal),var(--sky))!important; border-radius:10px; transition:transform .2s; }
[data-testid="stChatInput"] button:hover{ transform:scale(1.1) rotate(-6deg); }

/* Typing indicator */
.typing{ display:inline-flex; gap:6px; padding:.5rem .2rem; }
.typing span{ width:9px; height:9px; border-radius:50%; background:var(--sky); animation:dot 1.3s infinite ease-in-out; }
.typing span:nth-child(2){ animation-delay:.18s; } .typing span:nth-child(3){ animation-delay:.36s; }

/* Welcome + empty state */
.hero{ text-align:center; margin:2.5rem 0 1.5rem; }
.hero .orb{
  width:96px; height:96px; margin:0 auto 1.2rem; border-radius:28px; display:grid; place-items:center; font-size:3rem;
  background:linear-gradient(135deg,var(--royal),var(--sky)); animation:floaty 5s ease-in-out infinite, glow 3.5s ease-in-out infinite;
}
.hero h1{ font-size:2.4rem; margin:0 0 .4rem;
  background:linear-gradient(90deg,#fff,var(--lav),var(--sky)); -webkit-background-clip:text; background-clip:text; color:transparent; }
.hero p{ color:var(--muted); font-size:1.1rem; max-width:520px; margin:0 auto; }
.empty{ text-align:center; margin:3rem 0 1.5rem; animation:fadeUp .6s ease both; }
.empty h2{ font-size:1.8rem; margin-bottom:.3rem; }
.empty p{ color:var(--muted); }
.topbar{ display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem; }
.topbar h2{ margin:0; font-size:1.5rem; }
.privacy{ color:var(--muted); font-size:.85rem; text-align:center; margin-top:.8rem; }

/* Responsive */
@media (max-width:768px){
  .block-container{ padding:1rem .8rem 7rem; }
  .hero h1{ font-size:1.9rem; } .hero p{ font-size:1rem; }
  h1{ font-size:1.6rem; } .empty h2{ font-size:1.5rem; }
  [data-testid="stChatMessage"]{ padding:.8rem .85rem; }
  [data-testid="stForm"]{ padding:1rem; }
}
html, body{ overflow-x:hidden; }

@media (prefers-reduced-motion: reduce){
  *, *::before, *::after{ animation:none!important; transition:none!important; }
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

if not connected:
    # Hide the sidebar completely until a key has been verified
    st.markdown(
        """<style>[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"]{display:none!important;}</style>""",
        unsafe_allow_html=True,
    )
if st.session_state.animate_in:
    st.markdown(
        "<style>.block-container{animation:fadeUp .7s ease both;}</style>", unsafe_allow_html=True
    )
    st.session_state.animate_in = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {"title": "New Chat", "messages": [], "times": []}
    st.session_state.active_chat = chat_id


def now_label():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


def add_message(chat, message):
    chat["messages"].append(message)
    chat.setdefault("times", [])
    chat["times"].append(now_label())


def friendly_error(exc):
    """Readable messages that never echo the raw exception (it can contain key fragments)."""
    if isinstance(exc, AuthenticationError):
        return "That API key wasn't accepted. Please double-check it and try again."
    if isinstance(exc, PermissionDeniedError):
        return "This key doesn't have permission for that request or model."
    if isinstance(exc, RateLimitError):
        return "Rate limit or quota reached. Check your OpenAI billing and usage limits."
    if isinstance(exc, APIConnectionError):
        return "Couldn't reach OpenAI. Check your internet connection and try again."
    return "Something went wrong while contacting the model. Please try again."


def verify_key(key):
    try:
        OpenAI(api_key=key, timeout=15, max_retries=0).models.list()
        return True, ""
    except Exception as exc:  # noqa: BLE001 - mapped to safe messages
        return False, friendly_error(exc)


def connect(key):
    key = (key or "").strip()
    if not key:
        return False, "Please enter your API key to continue."
    with st.spinner("Verifying your key..."):
        ok, message = verify_key(key)
    if ok:
        st.session_state.api_key = key
        st.session_state.connected = True
        st.session_state.animate_in = True
    return ok, message


# ---------------------------------------------------------------------------
# Welcome screen (API key first)
# ---------------------------------------------------------------------------
if not connected:
    st.markdown(
        """
        <div class="hero">
          <div class="orb">🤖</div>
          <h1>Welcome to Mini GPT</h1>
          <p>Your smart AI assistant is one step away. Enter your OpenAI API key to get started.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("connect_form"):
            key_input = st.text_input(
                "OpenAI API key", type="password", placeholder="sk-...",
                help="Use the eye icon in the field to show or hide the key.",
            )
            submitted = st.form_submit_button(
                "Connect and Continue", type="primary", use_container_width=True
            )
        if submitted:
            ok, message = connect(key_input)
            if ok:
                st.rerun()
            st.error(message)
        st.markdown(
            '<div class="privacy">🔒 Your key stays in this session only. It is never written to disk or shown in the page.</div>',
            unsafe_allow_html=True,
        )
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar (connected)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="logo">🤖</div><div><div class="name">Mini GPT</div>'
        '<div class="sub">AI assistant</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<span class="status-pill"><i></i>Connected</span>', unsafe_allow_html=True)

    with st.expander("🔑 API key"):
        with st.form("reconnect_form", clear_on_submit=True):
            new_key = st.text_input("New OpenAI API key", type="password", placeholder="sk-...")
            reconnect = st.form_submit_button("Update key", use_container_width=True)
        if reconnect:
            ok, message = connect(new_key)
            if ok:
                st.success("Key updated.")
            else:
                st.error(message)
        if st.button("Disconnect", use_container_width=True):
            st.session_state.api_key = ""
            st.session_state.connected = False
            st.rerun()

    st.subheader("⚙️ Settings")
    model = st.selectbox("Model", ["gpt-4.1-mini", "gpt-4.1"], index=0)
    system_prompt = st.text_area(
        "Assistant instructions",
        value="You are a helpful assistant. Explain things clearly and accurately.",
        height=100,
    )
    st.divider()
    st.subheader("💬 Chat history")
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        new_chat()
        st.rerun()
    for chat_id, data in list(st.session_state.chats.items()):
        is_active = chat_id == st.session_state.active_chat
        label = ("● " if is_active else "") + data["title"]
        if st.button(label, key=f"open_{chat_id}", use_container_width=True):
            st.session_state.active_chat = chat_id
            st.rerun()
    if st.button("🗑️ Clear all chats", use_container_width=True):
        st.session_state.chats = {}
        st.session_state.active_chat = None
        st.rerun()

api_key = st.session_state.api_key

# ---------------------------------------------------------------------------
# Main chat area
# ---------------------------------------------------------------------------
if st.session_state.active_chat not in st.session_state.chats:
    new_chat()

chat = st.session_state.chats[st.session_state.active_chat]
chat.setdefault("times", [])

st.markdown(
    f'<div class="topbar"><h2>{"💬 Chat" if chat["messages"] else "🤖 Mini GPT"}</h2>'
    f'<span class="status-pill"><i></i>{model}</span></div>',
    unsafe_allow_html=True,
)

for i, message in enumerate(chat["messages"]):
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(str(message.content))
        if i < len(chat["times"]):
            st.caption(chat["times"][i])

SUGGESTIONS = [
    "✨ Explain quantum computing simply",
    "🐍 Write a Python function to sort a list",
    "📝 Help me draft a professional email",
    "💡 Give me 5 project ideas to learn AI",
]

if not chat["messages"]:
    st.markdown(
        '<div class="empty"><h2>How can I help you today?</h2>'
        "<p>Ask anything, or try one of these to get started.</p></div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for idx, suggestion in enumerate(SUGGESTIONS):
        if cols[idx % 2].button(suggestion, key=f"sugg_{idx}", use_container_width=True):
            st.session_state.pending_prompt = suggestion.split(" ", 1)[1]
            st.rerun()

prompt = st.chat_input("Ask me anything...")
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt:
    add_message(chat, HumanMessage(content=prompt))
    if chat["title"] == "New Chat":
        chat["title"] = (prompt[:32] + "…") if len(prompt) > 32 else prompt
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(chat["times"][-1])
    with st.chat_message("assistant"):
        slot = st.empty()
        slot.markdown(
            '<div class="typing"><span></span><span></span><span></span></div>',
            unsafe_allow_html=True,
        )
        try:
            llm = ChatOpenAI(model=model, api_key=api_key)
            response = llm.invoke([SystemMessage(content=system_prompt)] + chat["messages"])
            answer = response.content
            if not isinstance(answer, str):
                answer = str(answer)
            if not answer:
                answer = "The model returned an empty response."
            add_message(chat, AIMessage(content=answer))
            with slot.container():
                st.markdown(answer)
                st.caption(chat["times"][-1])
        except Exception as exc:  # noqa: BLE001 - shown via a safe, friendly message
            slot.error(friendly_error(exc))
            st.caption("Check your API key, account billing, model access, and internet connection. "
                       "You can update the key from the sidebar.")
