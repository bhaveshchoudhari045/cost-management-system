import streamlit as st
import json
import os
from datetime import datetime, date
import hashlib

# 1. PAGE CONFIGURATION
st.set_page_config(layout="wide", page_title="Cost Management 2026")

# --- 2. AUTHENTICATION ---
USER_DB = "users.json"
def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f: return json.load(f)
    return {}

def save_user(username, password):
    users = load_users()
    users[username] = hashlib.sha256(password.encode()).hexdigest()
    with open(USER_DB, "w") as f: json.dump(users, f)

def verify_user(username, password):
    users = load_users()
    return users.get(username) == hashlib.sha256(password.encode()).hexdigest()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; padding-top:50px;'>🛡️ Secure Access</h1>", unsafe_allow_html=True)
    _, col_form, _ = st.columns(3)
    with col_form:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            with st.form("login_form"):
                l_user = st.text_input("Username")
                l_pass = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if verify_user(l_user, l_pass):
                        st.session_state.logged_in, st.session_state.username = True, l_user
                        st.rerun()
                    else: st.error("Invalid credentials")
        with tab2:
            with st.form("reg_form"):
                r_user, r_pass = st.text_input("New Username"), st.text_input("New Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if r_user and r_pass: save_user(r_user, r_pass); st.success("Account created!")
    st.stop()

# --- 3. DATA MANAGEMENT ---
DB_FILE = f"expenses_{st.session_state.username}.json"
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'expenses' not in st.session_state: st.session_state.expenses = load_data()
if 'edit_index' not in st.session_state: st.session_state.edit_index = None

def handle_delete(index):
    st.session_state.expenses.pop(index)
    save_data(st.session_state.expenses)

def handle_edit(index):
    st.session_state.edit_index = index

# --- 4. CSS: ABSOLUTE POSITIONING FOR INTERNAL BUTTONS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com');
    
    .fire-container {
        color: white; text-align: center; font-size: 70px;
        font-family: 'Sofia', sans-serif; margin-bottom: 50px;
        text-shadow: 0px 0px 12px rgba(75, 190, 18, 0.8);
    }

    /* THE CART CONTAINER */
    .cart-box {
        position: relative; /* Essential for absolute positioning of children */
        border-radius: 20px; 
        background: rgba(15, 15, 15, 0.85); 
        backdrop-filter: blur(15px);
        border: 1.5px solid rgba(255, 255, 255, 0.15);
        height: 330px; padding: 20px; text-align: center;
        margin-bottom: 20px;
    }
    
    /* BUTTON ROW POSITIONING (INSIDE CART AT BOTTOM) */
    .button-anchor {
        position: absolute;
        bottom: 15px;
        left: 0;
        right: 0;
        padding: 0 10px;
    }

    /* TEXT-ONLY BUTTON STYLING */
    div.stButton > button {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        font-weight: bold !important;
        font-size: 13px !important;
        padding: 0px !important;
        min-height: 0px !important;
    }
    
    /* Edit Color */
    div.stButton > button[key^="e_"] { color: #00ffff !important; }
    /* Delete Color */
    div.stButton > button[key^="d_"] { color: #ff4b4b !important; }

    .glow-blue { box-shadow: 0 0 15px rgba(0, 191, 255, 0.6); }
    .glow-green { box-shadow: 0 0 15px rgba(50, 205, 50, 0.6); }
    .glow-yellow { box-shadow: 0 0 15px rgba(255, 215, 0, 0.6); }
    .glow-orange { box-shadow: 0 0 15px rgba(255, 165, 0, 0.6); }
    .glow-red { box-shadow: 0 0 25px rgba(255, 69, 0, 0.8); }
    </style>
    <h1 class="font-effect-fire fire-container">Cost Management</h1>
    """, unsafe_allow_html=True
)

# --- 5. GRID ---
_, col_btn, _ = st.columns(3)
with col_btn:
    if st.button("✨ Add New Cart", use_container_width=True):
        st.session_state.expenses.append({"name": "New Item", "cost": 0, "date": str(date.today())})
        save_data(st.session_state.expenses); st.rerun()

if st.session_state.expenses:
    cols = st.columns(4, gap="large")
    for idx, item in enumerate(st.session_state.expenses):
        b_date = datetime.strptime(item['date'], "%Y-%m-%d").date()
        days = max((date.today() - b_date).days, 1)
        cpd = item['cost'] / days
        glow = "glow-blue" if cpd < 7 else "glow-green" if cpd < 15 else "glow-yellow" if cpd < 25 else "glow-orange" if cpd < 50 else "glow-red"

        with cols[idx % 4]:
            # The Cart Visual
            st.markdown(f"""
                <div class="cart-box {glow}">
                    <p style="font-family:'Sofia'; font-size:24px; color:white; margin-top:10px;">{item['name']}</p>
                    <p style="color:#aaa; font-size:11px;">📅 {item['date']}</p>
                    <hr style="opacity:0.1; margin: 15px 0;">
                    <p style="font-size:22px; font-weight:bold; color:white; margin:0;">₹{item['cost']}</p>
                    <p style="color:#4bbe12; font-size:14px; font-weight:bold; margin:0;">₹{cpd:.2f} / day</p>
                    <div class="button-anchor"></div> <!-- Invisible anchor for buttons -->
                </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons - Floating inside the container via negative margin
            st.markdown('<div style="margin-top: -55px;">', unsafe_allow_html=True)
            btn_c1, btn_c2 = st.columns([1, 1.2]) # Slightly more space for "DELETE"
            btn_c1.button("EDIT", key=f"e_{idx}", on_click=handle_edit, args=(idx,))
            btn_c2.button("DELETE", key=f"d_{idx}", on_click=handle_delete, args=(idx,))
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. EDIT FORM ---
if st.session_state.edit_index is not None:
    i = st.session_state.edit_index
    if i < len(st.session_state.expenses):
        it = st.session_state.expenses[i]
        with st.form("edit_panel"):
            st.subheader(f"✏️ Update: {it['name']}")
            f1, f2, f3 = st.columns(3)
            n, c, d = f1.text_input("Name", value=it['name']), f2.number_input("Cost", value=float(it['cost'])), f3.date_input("Date", value=datetime.strptime(it['date'], "%Y-%m-%d"))
            if st.form_submit_button("Save Changes", use_container_width=True):
                st.session_state.expenses[i] = {"name": n, "cost": c, "date": str(d)}
                save_data(st.session_state.expenses); st.session_state.edit_index = None; st.rerun()
