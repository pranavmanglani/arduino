import streamlit as st
from supabase import create_client, Client

# --- SUPABASE CREDENTIALS ---
SUPABASE_URL = "https://snuhhlktfympkhfvtuks.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNudWhobGt0ZnltcGtoZnZ0dWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5Mzc4NzAsImV4cCI6MjA5NDUxMzg3MH0.2S0cIX_gg2C_zBnGAmTD9xWa23VH10kf2zjtlgnkV5c"

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Arduino Code Hub", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATABASE CONNECTION ---
@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    db = get_supabase_client()
except Exception as e:
    st.error(f"Failed to initialize Supabase connection: {e}")
    st.stop()

# --- STYLING HEADER ---
st.markdown("""
    <style>
    .main-title { font-size:2.4rem; font-weight:700; color: #00979D; margin-bottom: 0.2rem; }
    .sub-title { font-size:1.1rem; color: #666; margin-bottom: 2rem; }
    </style>
    """, unsafe_html=True)

st.markdown('<div class="main-title">🤖 Arduino Code Central Registry</div>', unsafe_html=True)
st.markdown('<div class="sub-title">A global repository to share, discover, and copy community-driven Arduino sketches.</div>', unsafe_html=True)

# --- SIDEBAR: PUBLISHING SYSTEM ---
with st.sidebar:
    st.markdown("<h2 style='color: #00979D;'>📤 Share a Sketch</h2>", unsafe_html=True)
    st.write("Fill out the details below to upload your snippet to the live Supabase server.")
    st.markdown("---")
    
    # Input bindings
    author_input = st.text_input("Creator Name", placeholder="e.g., Maker_Rob", help="Your nickname or handle")
    title_input = st.text_input("Sketch Title", placeholder="e.g., I2C LCD Display Driver", help="Keep it brief and descriptive")
    
    # Custom boilerplate preloaded inside code text area
    boilerplate = """// Title: Your Project Title\nvoid setup() {\n  // put your setup code here, to run once:\n\n}\n\nvoid loop() {\n  // put your main code here, to run repeatedly:\n\n}"""
    code_input = st.text_area("Arduino Source Code (C++)", value=boilerplate, height=320)
    
    st.markdown("---")
    publish_clicked = st.button("🚀 Push to Cloud Registry", use_container_width=True)
    
    if publish_clicked:
        # Field validation
        if not author_input.strip():
            st.error("Error: Please provide a creator handle.")
        elif not title_input.strip():
            st.error("Error: Your sketch needs a title.")
        elif not code_input.strip() or code_input == boilerplate:
            st.error("Error: Please enter your unique code payload.")
        else:
            with st.spinner("Writing records to Supabase storage..."):
                payload = {
                    "title": title_input.strip(),
                    "author": author_input.strip(),
                    "code": code_input.strip()
                }
                try:
                    db.table("snippets").insert(payload).execute()
                    st.success("🎉 Data successfully written to the cloud!")
                    st.balloons()
                    st.rerun()
                except Exception as db_err:
                    st.error(f"Database write failed. Check if your table is named 'snippets'. Details: {db_err}")

# --- MAIN INTERFACE: REPOSITORY VIEW ---
st.markdown("### 📥 Live Sketch Stream")

# Live query execution loop
try:
    query_result = db.table("snippets").select("*").order("created_at", descending=True).execute()
    records = query_result.data

    if not records:
        st.info("The database repository is currently empty. Use the sidebar module to populate the first entry!")
    else:
        # Integrated runtime search filter
        search_filter = st.text_input("🔍 Filter database instantly by Title or Creator", placeholder="Type keyword...").strip().lower()
        
        st.markdown("<br>", unsafe_html=True)
        
        for record in records:
            # Runtime matching evaluation
            match_title = search_filter in record.get('title', '').lower()
            match_author = search_filter in record.get('author', '').lower()
            
            if match_title or match_author:
                # Clean up ISO timestamp string format visually
                raw_time = record.get('created_at', 'N/A')
                display_time = raw_time[:16].replace("T", " ") if "T" in raw_time else raw_time
                
                expander_label = f"📝 {record.get('title')} — Created by {record.get('author')} [{display_time} UTC]"
                
                with st.expander(expander_label):
                    # Output blocks with high-contrast C++ engine layout formatting
                    st.code(record.get('code'), language="cpp")
                    
except Exception as fetch_err:
    st.error(f"Unable to read live streaming data: {fetch_err}")
    st.info("Double check that your table structure inside the Supabase SQL editor matches table name: 'snippets' with columns: 'title', 'author', and 'code'.")
