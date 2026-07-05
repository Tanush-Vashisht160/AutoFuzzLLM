import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import time

def show_loader(loader_box, timer_box, text="Running Campaign Loading Metrics..."):
    """Fires up the component frame layer structure inside app.py"""
    start_time = time.time()
    
    with loader_box:
        try:
            html = Path("ui/assets/loader.html").read_text(encoding="utf-8")
            css = Path("ui/assets/loader.css").read_text(encoding="utf-8")
            st.markdown(f"⏳ **{text}**")
            components.html(f"<style>{css}</style>{html}", height=320, scrolling=False)
        except FileNotFoundError:
            st.markdown(f"⏳ **{text}**")
            
    timer_box.markdown("🧩 *Initializing Threat Assessment Matrix...*")
    return start_time

def update_timer(timer_box, start_time):
    """Updates the standalone metrics clock display layer smoothly"""
    elapsed = round(time.time() - start_time, 1)
    timer_box.metric(label="⏱️ Elapsed Testing Time", value=f"{elapsed}s")