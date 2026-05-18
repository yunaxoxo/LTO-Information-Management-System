from pathlib import Path
import streamlit as st

def css_style(style):
    try:
        # 1. Finds the absolute path of this current file (1_Drivers.py)
        current_dir = Path(__file__).parent
        
        # 2. Moves up one level to 'src/' and goes into 'css/style.css'
        css_path = current_dir.parent / "css" / style
        
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
    except FileNotFoundError:
        st.error(f"Couldn't find CSS file at: {css_path}")

# Call it with just the file name
css_style("style.css")