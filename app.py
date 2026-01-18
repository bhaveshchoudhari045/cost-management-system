import streamlit as st
import json
import os
from datetime import datetime, date

# 1. PAGE CONFIGURATION
st.set_page_config(layout="wide", page_title="Cost Management 2026")

DB_FILE = "expenses_final_2026.json"

# --- PERSISTENCE LOGIC ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Initialize Session State
if 'expenses' not in st.session_state:
    st.session_state.expenses = load_data()
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# Detect Integrated Actions via URL Params
params = st.query_params
if "action" in params:
    act = params["action"]
    idx = int(params["id"])
    if act == "delete" and idx < len(st.session_state.expenses):
        st.session_state.expenses.pop(idx)
        save_data(st.session_state.expenses)
        st.query_params.clear()
        st.rerun()
    elif act == "edit" and idx < len(st.session_state.expenses):
        st.session_state.edit_index = idx
        st.query_params.clear()
        st.rerun()

# --- 2. ADVANCED CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css?=Sofia');
    @import url('https://fonts.googleapis.com');

    .fire-container {
        color: BLACK; text-align: center; font-size: 70px;
        font-family: 'Sofia', sans-serif; margin-bottom: 100px; padding-top: 40px;
        text-shadow: 0px 0px 12px rgba(75, 190, 18, 0.8), 0px 0px 3px rgba(255, 255, 255, 0.5);
    }

    .cart-container {
        border-radius: 20px; margin: 15px auto;
        background: rgba(255, 255, 255, 0.08); 
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border: 1.5px solid rgba(255, 255, 255, 0.1);
        transition: all 0.4s ease-in-out;
        height: 360px; width: 230px;
        display: flex; flex-direction: column; overflow: hidden;
        color: white; font-family: 'Inter', sans-serif;
    }
    .cart-container:hover { transform: scale(1.06); }

    .cart-body { padding: 20px; flex-grow: 1; text-align: center; display: flex; flex-direction: column; justify-content: space-around; }

    .cart-footer { display: flex; height: 55px; border-top: 1px solid rgba(255, 255, 255, 0.1); }

    .btn-action {
        flex: 1; display: flex; align-items: center; justify-content: center;
        font-weight: bold; font-size: 14px; text-decoration: none !important; 
        transition: 0.3s; cursor: pointer;
    }
    .btn-edit { background: rgba(0, 255, 255, 0.15); color: #00ffff !important; border-right: 1px solid rgba(255,255,255,0.1); }
    .btn-edit:hover { background: rgba(0, 255, 255, 0.4); color: white !important; }
    .btn-del { background: rgba(255, 0, 0, 0.15); color: #ff4b4b !important; }
    .btn-del:hover { background: rgba(255, 0, 0, 0.4); color: white !important; }

    /* Shadow Colors [Target User Specifications] */
    .glow-blue { box-shadow: 0 0 20px rgba(0, 191, 255, 0.6); }
    .glow-green { box-shadow: 0 0 20px rgba(50, 205, 50, 0.6); }
    .glow-yellow { box-shadow: 0 0 20px rgba(255, 215, 0, 0.6); }
    .glow-orange { box-shadow: 0 0 20px rgba(255, 165, 0, 0.6); }
    .glow-red { box-shadow: 0 0 30px rgba(255, 69, 0, 0.8); }
    </style>
    
    <h1 class="font-effect-fire fire-container">Cost Management</h1>
    """, unsafe_allow_html=True
)

# --- 3. ACTIONS ---
col_a, col_btn, col_c = st.columns([2, 1, 2])
with col_btn:
    if st.button("✨ Add New Cart", use_container_width=True):
        new_item = {"name": "Product Name", "cost": 0, "date": str(date.today())}
        st.session_state.expenses.append(new_item)
        save_data(st.session_state.expenses)
        st.rerun()

# --- 4. DYNAMIC GRID (4 PER ROW) ---
if st.session_state.expenses:
    cols = st.columns(4, gap="large") # Wide mode fix
    for idx, item in enumerate(st.session_state.expenses):
        # CPD Calculation Logic
        b_date = datetime.strptime(item['date'], "%Y-%m-%d").date()
        days = (date.today() - b_date).days or 1
        cpd = item['cost'] / days
        
        # Color Thresholds per User Specification
        if cpd < 7: glow = "glow-blue"
        elif cpd < 15: glow = "glow-green"
        elif cpd < 25: glow = "glow-yellow"
        elif cpd < 50: glow = "glow-orange"
        else: glow = "glow-red"

        with cols[idx % 4]:
            st.markdown(f"""
                <div class="cart-container {glow}">
                    <div class="cart-body">
                        <div>
                            <h2 style="margin:0; font-family:'Sofia', sans-serif; font-size:22px;">{item['name']}</h2>
                            <p style="color:gray; font-size:11px; margin-top:4px;">📅 {item['date']}</p>
                        </div>
                        <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top:10px;">
                            <p style="font-size:22px; font-weight:bold; margin:0;">₹{item['cost']}</p>
                            <p style="color:#4bbe12; font-size:14px; margin:0; font-weight:bold;">₹{cpd:.2f} / day</p>
                        </div>
                    </div>
                    <div class="cart-footer">
                        <a href="/?action=edit&id={idx}" target="_self" class="btn-action btn-edit">EDIT</a>
                        <a href="/?action=delete&id={idx}" target="_self" class="btn-action btn-del">DELETE</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 5. SAFE EDIT FORM ---
if st.session_state.edit_index is not None:
    i = st.session_state.edit_index
    if i < len(st.session_state.expenses): # Index safety fix
        item_to_edit = st.session_state.expenses[i]
        st.divider()
        with st.form("edit_panel"):
            st.subheader(f"✏️ Update: {item_to_edit['name']}")
            f1, f2, f3 = st.columns(3)
            new_n = f1.text_input("Product Name", value=item_to_edit['name'])
            new_c = f2.number_input("Total Cost (₹)", value=float(item_to_edit['cost']))
            new_d = f3.date_input("Date", value=datetime.strptime(item_to_edit['date'], "%Y-%m-%d"))
            
            sc1, sc2 = st.columns(2)
            if sc1.form_submit_button("💾 Save Changes", use_container_width=True):
                st.session_state.expenses[i] = {"name": new_n, "cost": new_c, "date": str(new_d)}
                save_data(st.session_state.expenses)
                st.session_state.edit_index = None
                st.rerun()
            if sc2.form_submit_button("🚫 Cancel", use_container_width=True):
                st.session_state.edit_index = None
                st.rerun()
    else:
        st.session_state.edit_index = None
        st.rerun()
