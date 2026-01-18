import streamlit as st
import json
import os
from datetime import datetime, date
import hashlib
import base64

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
                u, p = st.text_input("Username"), st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if verify_user(u, p):
                        st.session_state.logged_in, st.session_state.username = True, u
                        st.rerun()
                    else: st.error("Invalid credentials")
        with tab2:
            with st.form("reg"):
                ru, rp = st.text_input("New Username"), st.text_input("New Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if ru and rp: save_user(ru, rp); st.success("Account created!")
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

if 'expenses' not in st.session_state:
    st.session_state.expenses = load_data()
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

def handle_delete(index):
    st.session_state.expenses.pop(index)
    save_data(st.session_state.expenses)

def handle_edit(index):
    st.session_state.edit_index = index

# --- 4. CUSTOM CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com');
    
    .fire-container {
        color: white; text-align: center; font-size: 70px;
        font-family: 'Sofia', sans-serif; margin-bottom: 80px; padding-top: 30px;
        text-shadow: 0px 0px 12px rgba(75, 190, 18, 0.8), 0px 0px 3px rgba(255, 255, 255, 0.5);
    }

    .cart-box {
        position: relative; border-radius: 20px; 
        background: rgba(15, 15, 15, 0.85); backdrop-filter: blur(15px);
        border: 1.5px solid rgba(255, 255, 255, 0.15);
        height: 420px; padding: 0px; text-align: center; margin-bottom: 15px;
        overflow: hidden;
    }
    
    .cart-img { width: 100%; height: 160px; object-fit: cover; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .cart-no-img { width: 100%; height: 160px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; color: #555; font-size: 12px; }

    div.stButton > button {
        background: none !important; border: none !important;
        box-shadow: none !important; font-weight: bold !important;
        font-size: 13px !important; padding: 0px !important;
    }
    div.stButton > button[key^="e_"] { color: #00ffff !important; }
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

# --- 5. GRID & DISPLAY ---
_, col_btn, _ = st.columns(3)
with col_btn:
    if st.button("✨ Add New Cart", use_container_width=True):
        st.session_state.expenses.append({"name": "New Item", "cost": 0, "date": str(date.today()), "image": None})
        save_data(st.session_state.expenses); st.rerun()

if st.session_state.expenses:
    cols = st.columns(4, gap="large")
    for idx, item in enumerate(st.session_state.expenses):
        b_date = datetime.strptime(item['date'], "%Y-%m-%d").date()
        days = max((date.today() - b_date).days, 1)
        cpd = item['cost'] / days
        
        # Color Logic
        glow = "glow-blue" if cpd < 7 else "glow-green" if cpd < 15 else "glow-yellow" if cpd < 25 else "glow-orange" if cpd < 50 else "glow-red"

        with cols[idx % 4]:
            # Image Header Logic
            img_html = f'<img src="{item["image"]}" class="cart-img">' if item.get("image") else '<div class="cart-no-img">No Image</div>'
            
            st.markdown(f"""
                <div class="cart-box {glow}">
                    {img_html}
                    <div style="padding: 15px;">
                        <p style="font-family:'Sofia'; font-size:22px; color:white; margin:0;">{item['name']}</p>
                        <p style="color:#aaa; font-size:11px;">📅 {item['date']}</p>
                        <hr style="opacity:0.1; margin: 10px 0;">
                        <p style="font-size:20px; font-weight:bold; color:white; margin:0;">₹{item['cost']}</p>
                        <p style="color:#4bbe12; font-size:13px; font-weight:bold; margin:0;">₹{cpd:.2f} / day</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons positioned inside padding via negative margin
            st.markdown('<div style="margin-top: -55px; margin-bottom: 25px;">', unsafe_allow_html=True)
            bc1, bc2 = st.columns([1, 1.2])
            bc1.button("EDIT", key=f"e_{idx}", on_click=handle_edit, args=(idx,))
            bc2.button("DELETE", key=f"d_{idx}", on_click=handle_delete, args=(idx,))
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. EDIT FORM WITH IMAGE UPLOADER ---
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
            
            uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "png", "jpeg"])
            
            sc1, sc2 = st.columns(2)
            if sc1.form_submit_button("Save Changes", use_container_width=True):
                # Process Image
                img_data = it.get("image") # Keep old image by default
                if uploaded_file:
                    base64_img = base64.b64encode(uploaded_file.getvalue()).decode()
                    img_data = f"data:image/png;base64,{base64_img}"
                
                st.session_state.expenses[i] = {"name": n, "cost": c, "date": str(d), "image": img_data}
                save_data(st.session_state.expenses); st.session_state.edit_index = None; st.rerun()
            
            if sc2.form_submit_button("Cancel", use_container_width=True):
                st.session_state.edit_index = None; st.rerun()
