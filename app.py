import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from src.data_loader import DataLoader
from src.role_filter import RoleFilter  
from src.query_parser import QueryParser

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Dumroo Admin Panel",
    page_icon="🎓",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
if 'current_admin' not in st.session_state:
    st.session_state.current_admin = None

@st.cache_resource
def init_components():
    data_loader = DataLoader()
    data_loader.load_students()
    data_loader.load_admins()
    query_parser = QueryParser()
    return data_loader, query_parser

try:
    data_loader, query_parser = init_components()
except Exception as e:
    st.error(f"❌ Error initializing: {str(e)}")
    st.stop()

# Sidebar - Admin Selection
with st.sidebar:
    st.title("🎓 Admin Panel")
    st.markdown("---")
    
    admins = data_loader.admins
    admin_options = {f"{a['name']}": a['admin_id'] for a in admins}
    
    selected_admin = st.selectbox("Select Admin", list(admin_options.keys()))
    
    if selected_admin:
        admin_id = admin_options[selected_admin]
        st.session_state.current_admin = data_loader.get_admin_by_id(admin_id)
        admin = st.session_state.current_admin
        st.success(f"✅ Logged in as **{admin['name']}**")
        
        scope = RoleFilter.get_admin_scope_description(admin)
        st.info(f"**Access:** {scope}")

# Main Content
if st.session_state.current_admin is None:
    st.warning("⚠️ Please select an admin from sidebar")
    st.stop()

admin = st.session_state.current_admin

# Header
st.title("🔍 Student Query System")
st.markdown(f"Welcome, **{admin['name']}**")

# Get admin's accessible data
filtered_by_role = RoleFilter.filter_by_admin_scope(data_loader.students_df, admin)

if len(filtered_by_role) == 0:
    st.warning("⚠️ No students in your scope")
    st.stop()

# Quick Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Students", len(filtered_by_role))
with col2:
    submitted = len(filtered_by_role[filtered_by_role['homework_status'] == 'submitted'])
    st.metric("Homework Submitted", submitted)
with col3:
    pending = len(filtered_by_role[filtered_by_role['homework_status'] == 'not_submitted'])
    st.metric("Homework Pending", pending)
with col4:
    avg_score = filtered_by_role['quiz_score'].mean()
    st.metric("Average Score", f"{avg_score:.1f}")

st.markdown("---")

# Query Input
st.subheader("💬 Ask Any Question")

user_query = st.text_input(
    "Type your question:",
    placeholder="e.g., Who is the topper? Show students with pending homework",
    key="query_input"
)

# Quick Action Buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🏆 Show Topper"):
        user_query = "Who is the topper student?"
with col2:
    if st.button("📝 Pending Homework"):
        user_query = "Show students with pending homework"
with col3:
    if st.button("⭐ High Scorers (>80)"):
        user_query = "Show students who scored above 80"
with col4:
    if st.button("📊 All Students"):
        user_query = "Show all students"

# Process Query
if user_query:
    with st.spinner("🤔 Processing your query..."):
        try:
            # Parse query
            available_columns = list(filtered_by_role.columns)
            parsed_query = query_parser.parse_query(user_query, available_columns)
            
            # Execute query
            results = query_parser.execute_query(filtered_by_role, parsed_query)
            
            # Display Results
            st.markdown("---")
            st.subheader("📋 Results")
            
            # Summary
            if results['count'] > 0:
                st.success(f"✅ Found **{results['count']}** record(s)")
            else:
                st.info("ℹ️ No records found")
            
            # Show count only
            if results['intent'] == 'count':
                st.markdown(f"## Total: {results['count']}")
            
            # Show data table
            elif results['count'] > 0:
                result_df = results['data'].copy()
                
                # Rename columns for display
                display_columns = {
                    'student_name': 'Student Name',
                    'grade': 'Grade',
                    'class': 'Class',
                    'homework_status': 'Homework Status',
                    'quiz_score': 'Quiz Score',
                    'date': 'Date',
                    'region': 'Region'
                }
                
                # Only rename columns that exist
                rename_dict = {k: v for k, v in display_columns.items() if k in result_df.columns}
                result_df = result_df.rename(columns=rename_dict)
                
                # Display table
                st.dataframe(
                    result_df,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
                # Export to CSV
                csv = results['data'].to_csv(index=False)
                st.download_button(
                    label="📥 Export to CSV",
                    data=csv,
                    file_name=f"query_results_{admin['admin_id']}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Basic Stats
                st.markdown("### 📊 Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Score", f"{result_df['Quiz Score'].mean():.2f}" if 'Quiz Score' in result_df.columns else "N/A")
                with col2:
                    st.metric("Highest Score", f"{result_df['Quiz Score'].max()}" if 'Quiz Score' in result_df.columns else "N/A")
                with col3:
                    st.metric("Lowest Score", f"{result_df['Quiz Score'].min()}" if 'Quiz Score' in result_df.columns else "N/A")
        
        except Exception as e:
            st.error(f"❌ Error processing query: {str(e)}")
            st.info("💡 Try rephrasing your question or use the quick action buttons")

# Footer
st.markdown("---")
st.caption("⚡ Powered by Groq AI | 🔒 Role-Based Access Control")