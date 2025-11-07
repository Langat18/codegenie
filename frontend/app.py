"""
Codebase Genius - Streamlit Frontend
"""

import streamlit as st
import requests
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Codebase Genius",
    page_icon="📚",
    layout="wide"
)

# API URL
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .status-completed {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .status-failed {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .status-pending {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


class APIClient:
    """API Client"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def health_check(self):
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return {"status": "healthy", "data": response.json()}
        except:
            return {"status": "unhealthy"}
    
    def generate_docs(self, repo_url: str):
        try:
            response = requests.post(
                f"{self.base_url}/generate_docs",
                json={"repo_url": repo_url},
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self, session_id: str):
        try:
            response = requests.get(f"{self.base_url}/status/{session_id}", timeout=5)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_sessions(self):
        try:
            response = requests.get(f"{self.base_url}/sessions", timeout=5)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except:
            return {"success": False}


@st.cache_resource
def get_client():
    return APIClient(API_BASE_URL)


def render_sidebar():
    with st.sidebar:
        st.title("📚 Codebase Genius")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["🏠 Home", "📊 Sessions", "ℹ️ About"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.subheader("System Status")
        client = get_client()
        health = client.health_check()
        
        if health["status"] == "healthy":
            st.success("✅ API Connected")
            data = health.get("data", {})
            st.caption(f"Provider: {data.get('llm_provider', 'N/A')}")
            st.caption(f"Model: {data.get('model', 'N/A')}")
        else:
            st.error("❌ API Disconnected")
        
        st.markdown("---")
        st.caption("Powered by Google Gemini")
        
        return page


def render_home_page():
    st.markdown('<div class="main-header">📚 Codebase Genius</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #666; margin-bottom: 2rem;">AI-Powered Code Documentation with Google Gemini</div>', unsafe_allow_html=True)
    
    st.header("Generate Documentation")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repository"
        )
    
    with col2:
        st.write("")
        st.write("")
        generate_button = st.button("🚀 Generate", type="primary", use_container_width=True)
    
    with st.expander("📌 Example Repositories"):
        st.markdown("""
        - `https://github.com/psf/requests`
        - `https://github.com/pallets/flask`
        """)
    
    if generate_button and repo_url:
        if not repo_url.startswith("https://github.com/"):
            st.error("❌ Please enter a valid GitHub URL")
            return
        
        client = get_client()
        
        with st.spinner("🔄 Starting generation..."):
            result = client.generate_docs(repo_url)
        
        if result["success"]:
            session_id = result["data"].get("session_id")
            st.success(f"✅ Generation started!")
            st.info(f"Session ID: `{session_id}`")
            
            st.session_state.current_session = session_id
            render_progress_tracker(session_id)
        else:
            st.error(f"❌ Error: {result.get('error')}")


def render_progress_tracker(session_id: str):
    client = get_client()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    max_iterations = 60
    iteration = 0
    
    while iteration < max_iterations:
        status_result = client.get_status(session_id)
        
        if not status_result["success"]:
            st.error("Error fetching status")
            break
        
        data = status_result["data"]
        status = data.get("status", "unknown")
        progress = data.get("progress", 0.0)
        
        progress_bar.progress(progress / 100.0)
        status_text.write(f"**Status:** {status.upper()} ({progress:.1f}%)")
        
        if status == "completed":
            st.success("🎉 Documentation completed!")
            break
        elif status == "failed":
            st.error("❌ Generation failed")
            break
        
        time.sleep(5)
        iteration += 1


def render_sessions_page():
    st.header("📊 Documentation Sessions")
    
    client = get_client()
    
    if st.button("🔄 Refresh"):
        st.rerun()
    
    sessions_data = client.list_sessions()
    
    if not sessions_data["success"]:
        st.error("Error loading sessions")
        return
    
    sessions = sessions_data["data"].get("sessions", [])
    
    if not sessions:
        st.info("No active sessions")
        return
    
    st.write(f"**{len(sessions)}** session(s)")
    
    for session in sessions:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{session['repo_url']}**")
            
            with col2:
                status = session['status']
                progress = session['progress']
                
                if status == "completed":
                    st.success(f"✅ {status.upper()}")
                elif status == "failed":
                    st.error(f"❌ {status.upper()}")
                else:
                    st.warning(f"🔄 {status.upper()} ({progress:.0f}%)")
            
            st.markdown("---")


def render_about_page():
    st.header("ℹ️ About Codebase Genius")
    
    st.markdown("""
    ## AI-Powered Code Documentation
    
    Codebase Genius automatically generates comprehensive documentation using **Google Gemini AI**.
    
    ### Features
    - 🤖 Powered by Google Gemini 1.5 Pro
    - 🔍 Deep code analysis
    - 📝 Markdown documentation
    - 🚀 Fast processing
    
    ### Supported Languages
    - ✅ Python
    - ✅ JavaScript/TypeScript
    - ✅ Java
    - ✅ Jac
    
    ### How It Works
    1. Enter GitHub repository URL
    2. System clones and analyzes code
    3. Gemini AI generates documentation
    4. Download markdown file
    
    ### Technology Stack
    - **AI**: Google Gemini 1.5 Pro
    - **Backend**: Jac, FastAPI
    - **Frontend**: Streamlit
    """)


def main():
    if "current_session" not in st.session_state:
        st.session_state.current_session = None
    
    page = render_sidebar()
    
    if page == "🏠 Home":
        render_home_page()
    elif page == "📊 Sessions":
        render_sessions_page()
    elif page == "ℹ️ About":
        render_about_page()


if __name__ == "__main__":
    main()