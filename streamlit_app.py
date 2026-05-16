import streamlit as st
from supabase import create_client

# --- SUPABASE CONFIG ---
URL = "https://snuhhlktfympkhfvtuks.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNudWhobGt0ZnltcGtoZnZ0dWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5Mzc4NzAsImV4cCI6MjA5NDUxMzg3MH0.2S0cIX_gg2C_zBnGAmTD9xWa23VH10kf2zjtlgnkV5c"

st.set_page_config(page_title="Arduino Hub", page_icon="🤖", layout="wide")

try:
    db = create_client(URL, KEY)
except Exception as init_err:
    st.error(f"Supabase Connection Initialization Failed: {init_err}")
    st.stop()

# --- HEADER LAYOUT ---
st.title("🤖 Arduino Code Central Registry")
st.caption("A global repository to share, discover, and copy community-driven Arduino sketches.")
st.markdown("---")

col_side, col_main = st.columns([1, 2], gap="large")

# --- LEFT SIDE: PUBLISHING FORM ---
with col_side:
    st.subheader("📤 Share a Sketch")
    
    author_input = st.text_input("Creator Name", placeholder="e.g., Maker_Rob")
    title_input = st.text_input("Sketch Title", placeholder="e.g., I2C LCD Driver")
    
    boilerplate = "// Arduino Sketch\nvoid setup() {\n  \n}\n\nvoid loop() {\n  \n}"
    code_input = st.text_area("Source Code", value=boilerplate, height=280)
    
    if st.button("🚀 Push to Cloud Registry", use_container_width=True):
        if not author_input.strip() or not title_input.strip() or not code_input.strip():
            st.error("⚠️ All fields are required to publish.")
        else:
            with st.spinner("Writing to cloud database..."):
                try:
                    payload = {
                        "title": title_input.strip(),
                        "author": author_input.strip(),
                        "code": code_input.strip()
                    }
                    db.table("snippets").insert(payload).execute()
                    st.success("🎉 Published successfully!")
                    st.rerun()
                except Exception as db_write_err:
                    st.error("❌ Database Write Failure!")
                    st.code(str(db_write_err), language="text")

# --- RIGHT SIDE: REPOSITORY VIEW ---
with col_main:
    st.subheader("📥 Live Sketch Stream")
    
    try:
        # FIXED EXPLICIT PARAMETER FOR POSTGREST SYNTAX
        query = db.table("snippets").select("*").order("created_at", desc=True).execute()
        records = query.data

        if not records:
            st.info("The repository is currently empty. Be the first to add a sketch!")
        else:
            search_filter = st.text_input("🔍 Search by Title or Creator", placeholder="Type keywords...").strip().lower()
            
            for record in records:
                t_val = record.get('title', '')
                a_val = record.get('author', '')
                
                if search_filter in t_val.lower() or search_filter in a_val.lower():
                    raw_time = record.get('created_at', '')
                    clean_time = raw_time[:16].replace("T", " ") if "T" in raw_time else "Recent"
                    
                    with st.expander(f"📝 {t_val} — by {a_val} ({clean_time})"):
                        st.code(record.get('code', '// No code found'), language="cpp")

    except Exception as db_read_err:
        st.error("❌ Database Read Failure!")
        st.code(str(db_read_err), language="text")
