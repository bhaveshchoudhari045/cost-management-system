import streamlit as st
import json
import os
from datetime import datetime, date
import hashlib

# 1. PAGE CONFIGURATION
st.set_page_config(layout="wide", page_title="Cost Management 2026")

# --- 2. AUTHENTICATION SYSTEM ---
USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f: return json.load(f)
    return {}

def save_user(username, password):
    users = load_users()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    users[username] = hashed_pw
    with open(USER_DB, "w") as f: json.dump(users, f)

def verify_user(username, password):
    users = load_users()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    return users.get(username) == hashed_pw

# Initialize Session States
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# --- LOGIN / REGISTER UI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; padding-top:50px;'>🛡️ Secure Access</h1>", unsafe_allow_html=True)
    col_a, col_form, col_c = st.columns([1,2,1])
    
    with col_form:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            with st.form("login_form"):
                l_user = st.text_input("Username")
                l_pass = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if verify_user(l_user, l_pass):
                        st.session_state.logged_in = True
                        st.session_state.username = l_user
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        with tab2:
            with st.form("reg_form"):
                r_user = st.text_input("New Username")
                r_pass = st.text_input("New Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if r_user and r_pass:
                        save_user(r_user, r_pass)
                        st.success("Account created! Go to Login tab.")
    st.stop()

# --- 3. DATA MANAGEMENT (POST-LOGIN) ---
CURRENT_USER = st.session_state.username
DB_FILE = f"expenses_{CURRENT_USER}.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'expenses' not in st.session_state:
    st.session_state.expenses = load_data()
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# Sidebar
st.sidebar.title(f"👤 {CURRENT_USER}")
if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- 4. CALLBACK FUNCTIONS (The "No-Logout" Fix) ---
def handle_delete(index):
    st.session_state.expenses.pop(index)
    save_data(st.session_state.expenses)

def handle_edit(index):
    st.session_state.edit_index = index

# --- 5. CUSTOM CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com');
    .fire-container {
        color: white; text-align: center; font-size: 70px;
        font-family: 'Sofia', sans-serif; margin-bottom: 50px; padding-top: 30px;
        text-shadow: 0px 0px 12px rgba(75, 190, 18, 0.8), 0px 0px 3px rgba(255, 255, 255, 0.5);
    }
    .cart-container {
        border-radius: 20px; 
        background: rgba(15, 15, 15, 0.85); 
        backdrop-filter: blur(15px);
        border: 1.5px solid rgba(255, 255, 255, 0.15);
        height: 300px; padding: 20px; text-align: center;
        transition: transform 0.4s ease-in-out;
    }
    .cart-container:hover { transform: scale(1.04); }
    .product-title { font-family: 'Sofia', sans-serif; font-size: 24px; color: white; margin-bottom: 5px; }
    
    /* CPD Shadow Colors */
    .glow-blue { box-shadow: 0 0 15px rgba(0, 191, 255, 0.6); }
    .glow-green { box-shadow: 0 0 15px rgba(50, 205, 50, 0.6); }
    .glow-yellow { box-shadow: 0 0 15px rgba(255, 215, 0, 0.6); }
    .glow-orange { box-shadow: 0 0 15px rgba(255, 165, 0, 0.6); }
    .glow-red { box-shadow: 0 0 25px rgba(255, 69, 0, 0.8); }
    </style>
    <h1 class="font-effect-fire fire-container">Cost Management</h1>
    """, unsafe_allow_html=True
)

# --- 6. GRID & ACTIONS ---
_, col_btn, _ = st.columns([1,1,1])
with col_btn:
    if st.button("✨ Add New Cart", use_container_width=True):
        st.session_state.expenses.append({"name": "New Product", "cost": 0, "date": str(date.today())})
        save_data(st.session_state.expenses)
        st.rerun()

if st.session_state.expenses:
    cols = st.columns(4, gap="medium")
    for idx, item in enumerate(st.session_state.expenses):
        b_date = datetime.strptime(item['date'], "%Y-%m-%d").date()
        days = (date.today() - b_date).days or 1
        cpd = item['cost'] / days
        glow = "glow-blue" if cpd < 7 else "glow-green" if cpd < 15 else "glow-yellow" if cpd < 25 else "glow-orange" if cpd < 50 else "glow-red"

        with cols[idx % 4]:
            # Visual Cart
            st.markdown(f"""
                <div class="cart-container {glow}">
                    <p class="product-title">{item['name']}</p>
                    <p style="color:#aaa; font-size:11px;">📅 {item['date']}</p>
                    <hr style="opacity:0.1">
                    <p style="font-size:22px; font-weight:bold; margin:0; color:white;">₹{item['cost']}</p>
                    <p style="color:#4bbe12; font-size:14px; margin:0; font-weight:bold;">₹{cpd:.2f} / day</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Action Row (Built-in Streamlit buttons for stability)
            btn_col1, btn_col2 = st.columns(2)
            btn_col1.button("Edit 📝", key=f"e_{idx}", on_click=handle_edit, args=(idx,), use_container_width=True)
            btn_col2.button("Del 🗑️", key=f"d_{idx}", on_click=handle_delete, args=(idx,), use_container_width=True)

# --- 7. EDIT FORM ---
if st.session_state.edit_index is not None:
    i = st.session_state.edit_index
    if i < len(st.session_state.expenses):
        it = st.session_state.expenses[i]
        st.divider()
        with st.form("edit_panel"):
            st.subheader(f"✏️ Update: {it['name']}")
            f1, f2, f3 = st.columns(3)
            n = f1.text_input("Name", value=it['name'])
            c = f2.number_input("Cost (₹)", value=float(it['cost']))
            d = f3.date_input("Date", value=datetime.strptime(it['date'], "%Y-%m-%d"))
            
            sc1, sc2 = st.columns(2)
            if sc1.form_submit_button("💾 Save Changes", use_container_width=True):
                st.session_state.expenses[i] = {"name": n, "cost": c, "date": str(d)}
                save_data(st.session_state.expenses)
                st.session_state.edit_index = None
                st.rerun()
            if sc2.form_submit_button("Cancel", use_container_width=True):
                st.session_state.edit_index = None
                st.rerun()
