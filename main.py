import random

import streamlit as st

from combos import pick_triple, slugify

RNG = random.Random()

# Store the initial value of widgets in session state
if "disabled" not in st.session_state:
    st.session_state.disabled = True

if "chaos" not in st.session_state:
    st.session_state.chaos = False

if "domain_description" not in st.session_state:
    st.session_state.domain_description = ''

if "user_description" not in st.session_state:
    st.session_state.user_description = ''

if "mechanic_description" not in st.session_state:
    st.session_state.mechanic_description = ''

st.markdown(
    """
    <style>
    .block-container {
        max-width: min(1200px, 85vw);
        padding-top: 2rem;
    }
    div[data-testid="stTextInput"] {
        padding: 2rem;
        margin: 1rem;
    }
    div[data-testid="stTextInput"] input {
        padding: 2rem 1.5rem;
        font-size: 1.3rem;
        text-align: center;
    }
    .field-separator {
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0.25rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

domain = st.text_input(
        'Domain',
        disabled=st.session_state.disabled,
        key='domain',
        help=st.session_state.domain_description or None,
    )

st.markdown('<div class="field-separator">X</div>', unsafe_allow_html=True)

user = st.text_input(
        'User',
        disabled=st.session_state.disabled,
        key='user',
        help=st.session_state.user_description or None,
    )

st.markdown('<div class="field-separator">X</div>', unsafe_allow_html=True)

mechanic = st.text_input(
        'Mechanic',
        disabled=st.session_state.disabled,
        key='mechanic',
        help=st.session_state.mechanic_description or None,
    )

def generate_side_project():
    chosen_domain, chosen_user, chosen_mechanic = pick_triple(
        RNG, chaos=st.session_state.chaos
    )
    st.session_state.domain = chosen_domain["domain"]
    st.session_state.domain_description = chosen_domain["description"]
    st.session_state.user = chosen_user["user"]
    st.session_state.user_description = chosen_user["description"]
    st.session_state.mechanic = chosen_mechanic["mechanic"]
    st.session_state.mechanic_description = chosen_mechanic["description"]


_, button_col, _ = st.columns([1, 1, 1])
with button_col:
    st.button(
        "Generate",
        on_click=generate_side_project,
        type="primary",
        use_container_width=True,
    )
    st.checkbox(
        "Chaos mode",
        key="chaos",
        help="Ignore whether the topic, audience, and mechanic fit together.",
    )


if st.session_state.domain and st.session_state.user and st.session_state.mechanic:
    st.session_state.project_name = f"{st.session_state.domain} {st.session_state.user} {st.session_state.mechanic}".strip()
    slug = slugify(st.session_state.project_name)
    with st.expander("Quickstart", expanded=True):
        st.code(
            f"mkdir {slug}\n"
            f"cd {slug}\n"
            f"git init\n"
            f"git checkout -b {slug}",
            language="bash",
        )