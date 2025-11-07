"""
Reusable UI components for Codebase Genius frontend
"""

import streamlit as st
from typing import Dict, List, Optional
import plotly.graph_objects as go
from datetime import datetime


def render_status_badge(status: str) -> None:
    """Render a status badge"""
    status_colors = {
        "pending": "#ffc107",
        "validating": "#17a2b8",
        "mapping": "#17a2b8",
        "analyzing": "#007bff",
        "generating": "#007bff",
        "completed": "#28a745",
        "failed": "#dc3545"
    }
    
    color = status_colors.get(status.lower(), "#6c757d")
    
    st.markdown(
        f"""
        <span style="
            background-color: {color};
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 0.25rem;
            font-weight: bold;
            font-size: 0.875rem;
        ">
            {status.upper()}
        </span>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(label: str, value: str, delta: Optional[str] = None, icon: str = "📊") -> None:
    """Render a metric card"""
    delta_html = ""
    if delta:
        delta_color = "#28a745" if delta.startswith("+") else "#dc3545"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.875rem;">{delta}</div>'
    
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 0.5rem;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">{label}</div>
            <div style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0;">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_progress_ring(progress: float, size: int = 120) -> None:
    """Render a circular progress indicator"""
    fig = go.Figure(data=[go.Pie(
        values=[progress, 100 - progress],
        hole=0.7,
        marker=dict(colors=['#1f77b4', '#e5e5e5']),
        textinfo='none',
        hoverinfo='none'
    )])
    
    fig.update_layout(
        showlegend=False,
        height=size,
        width=size,
        margin=dict(t=0, b=0, l=0, r=0),
        annotations=[dict(
            text=f'{progress:.0f}%',
            x=0.5, y=0.5,
            font_size=20,
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig, use_container_width=False)


def render_agent_card(
    name: str,
    icon: str,
    status: str,
    task: str,
    is_active: bool = False
) -> None:
    """Render an agent status card"""
    border_color = "#1f77b4" if is_active else "#e5e5e5"
    bg_color = "#e7f3ff" if is_active else "#f8f9fa"
    
    st.markdown(
        f"""
        <div style="
            border-left: 4px solid {border_color};
            background-color: {bg_color};
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <span style="font-weight: bold; font-size: 1.1rem;">{name}</span>
            </div>
            <div style="color: #666; font-size: 0.875rem; margin-left: 2rem;">
                {task}
            </div>
            <div style="margin-left: 2rem; margin-top: 0.5rem;">
                {render_status_badge_html(status)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_status_badge_html(status: str) -> str:
    """Return HTML for status badge"""
    status_colors = {
        "active": "#28a745",
        "idle": "#6c757d",
        "completed": "#1f77b4",
        "failed": "#dc3545"
    }
    
    color = status_colors.get(status.lower(), "#6c757d")
    
    return f"""
    <span style="
        background-color: {color};
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
    ">
        {status.upper()}
    </span>
    """


def render_timeline(stages: List[Dict[str, str]], current_stage: str) -> None:
    """Render a timeline of workflow stages"""
    st.markdown("### 🔄 Workflow Timeline")
    
    for i, stage in enumerate(stages):
        is_current = stage["id"] == current_stage
        is_completed = i < next(
            (idx for idx, s in enumerate(stages) if s["id"] == current_stage),
            len(stages)
        )
        
        if is_completed and not is_current:
            icon = "✅"
            color = "#28a745"
        elif is_current:
            icon = "🔄"
            color = "#1f77b4"
        else:
            icon = "⏳"
            color = "#6c757d"
        
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                padding: 0.75rem;
                margin: 0.25rem 0;
                border-left: 3px solid {color};
                background-color: {'#e7f3ff' if is_current else 'transparent'};
            ">
                <span style="font-size: 1.5rem; margin-right: 1rem;">{icon}</span>
                <div>
                    <div style="font-weight: bold;">{stage['name']}</div>
                    <div style="color: #666; font-size: 0.875rem;">{stage['description']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_code_stats_chart(stats: Dict[str, int]) -> None:
    """Render a chart of code statistics"""
    if not stats:
        return
    
    labels = list(stats.keys())
    values = list(stats.values())
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            marker_color='#1f77b4',
            text=values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Code Statistics",
        xaxis_title="Metric",
        yaxis_title="Count",
        height=300,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_language_pie_chart(languages: Dict[str, Dict]) -> None:
    """Render pie chart of language distribution"""
    if not languages:
        return
    
    labels = list(languages.keys())
    values = [lang.get('lines', 0) for lang in languages.values()]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    )])
    
    fig.update_layout(
        title="Language Distribution (by lines of code)",
        height=300,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_info_box(message: str, box_type: str = "info") -> None:
    """Render an info/warning/error box"""
    colors = {
        "info": {"bg": "#d1ecf1", "border": "#0c5460", "icon": "ℹ️"},
        "warning": {"bg": "#fff3cd", "border": "#856404", "icon": "⚠️"},
        "error": {"bg": "#f8d7da", "border": "#721c24", "icon": "❌"},
        "success": {"bg": "#d4edda", "border": "#155724", "icon": "✅"}
    }
    
    style = colors.get(box_type, colors["info"])
    
    st.markdown(
        f"""
        <div style="
            background-color: {style['bg']};
            border-left: 4px solid {style['border']};
            padding: 1rem;
            border-radius: 0.25rem;
            margin: 1rem 0;
        ">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{style['icon']}</span>
            <span>{message}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_session_card(session: Dict, on_click_view=None, on_click_delete=None) -> None:
    """Render a session card with actions"""
    status = session.get('status', 'unknown')
    progress = session.get('progress', 0)
    repo_url = session.get('repo_url', 'Unknown')
    session_id = session.get('session_id', '')
    
    status_emoji = {
        'completed': '✅',
        'failed': '❌',
        'pending': '⏳',
        'analyzing': '🔍',
        'generating': '📝'
    }.get(status, '🔄')
    
    col1, col2, col3 = st.columns([6, 3, 1])
    
    with col1:
        st.markdown(f"**{status_emoji} {repo_url}**")
        st.caption(f"Session: {session_id[:16]}...")
    
    with col2:
        if status == 'completed':
            st.success(f"{progress:.0f}% Complete")
        elif status == 'failed':
            st.error("Failed")
        else:
            st.info(f"{progress:.0f}% - {status}")
    
    with col3:
        if on_click_view and st.button("👁️", key=f"view_{session_id}"):
            on_click_view(session_id)


def render_loading_animation(message: str = "Processing...") -> None:
    """Render a loading animation"""
    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 2rem;
        ">
            <div style="
                border: 4px solid #f3f3f3;
                border-top: 4px solid #1f77b4;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem auto;
            "></div>
            <div style="color: #666;">{message}</div>
        </div>
        <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        """,
        unsafe_allow_html=True
    )


def render_feature_card(icon: str, title: str, description: str) -> None:
    """Render a feature card"""
    st.markdown(
        f"""
        <div style="
            background: white;
            border: 1px solid #e5e5e5;
            border-radius: 0.5rem;
            padding: 1.5rem;
            text-align: center;
            height: 100%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
            <h3 style="margin-bottom: 0.5rem;">{title}</h3>
            <p style="color: #666; margin: 0;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_copy_button(text: str, label: str = "Copy") -> None:
    """Render a copy-to-clipboard button"""
    st.markdown(
        f"""
        <button onclick="navigator.clipboard.writeText('{text}')" style="
            background-color: #1f77b4;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            cursor: pointer;
            font-size: 0.875rem;
        ">
            📋 {label}
        </button>
        """,
        unsafe_allow_html=True
    )


def render_documentation_preview(content: str, max_lines: int = 50) -> None:
    """Render documentation preview with syntax highlighting"""
    lines = content.split('\n')
    preview = '\n'.join(lines[:max_lines])
    
    if len(lines) > max_lines:
        preview += f"\n\n... ({len(lines) - max_lines} more lines)"
    
    st.code(preview, language='markdown')


def render_repo_info_panel(repo_info: Dict) -> None:
    """Render repository information panel"""
    st.markdown("### 📦 Repository Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Name:** {repo_info.get('repo_name', 'N/A')}")
        st.markdown(f"**URL:** [{repo_info.get('repo_url', 'N/A')}]({repo_info.get('repo_url', '#')})")
        st.markdown(f"**Size:** {repo_info.get('repo_size_mb', 0):.2f} MB")
    
    with col2:
        st.markdown(f"**Total Files:** {repo_info.get('total_files', 0)}")
        st.markdown(f"**Entry Points:** {len(repo_info.get('entry_points', []))}")
        
        file_stats = repo_info.get('file_stats', {})
        st.markdown(f"**Total Lines:** {file_stats.get('total_lines', 0):,}")