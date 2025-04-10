
import streamlit as st
import os
import logging
import json
import time
from agents import run_analysis, setup_rag_system
from ui import (setup_page, load_css, display_analysis_dashboard, 
               display_qa_interface, generate_visualizations, extract_insights)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session state initialization
def init_session_state():
    if 'saved_analyses' not in st.session_state:
        st.session_state.saved_analyses = {}
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = {}
    if 'qa_chain' not in st.session_state:
        st.session_state.qa_chain = {}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = None

def ask_question(question, topic):
    """Process a question using the RAG system"""
    if topic not in st.session_state.qa_chain:
        st.error("Q&A system not initialized for this topic.")
        return
    
    qa_chain = st.session_state.qa_chain[topic]
    
    # Add question to history
    st.session_state.chat_history[topic].append({"role": "user", "content": question})
    
    # Get answer
    with st.spinner("Searching for answer..."):
        try:
            result = qa_chain({"question": question})
            
            # Highlight key terms in the response for better visibility
            answer = result.get("answer", "I couldn't find specific information about that in the analysis.")
            
            # If it's a financial risks question, ensure visibility with formatting
            if "financial risk" in question.lower() or "risks" in question.lower():
                risks_terms = ["risk", "challenge", "uncertainty", "threat", "concern"]
                for term in risks_terms:
                    answer = answer.replace(term, f"<span style='color: #e53935; font-weight: bold;'>{term}</span>")
            
            # Add answer to history
            st.session_state.chat_history[topic].append({"role": "assistant", "content": answer})
            
            # Rerun to update the UI
            st.experimental_rerun()
            
        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}")
            st.error(f"Error retrieving answer: {str(e)}")


# Main application function
def main():
    """Main application entry point"""
    # Initialize session state
    init_session_state()
    
    # Setup page
    setup_page()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API key setup
        openai_api_key = st.text_input(
            "OpenAI API Key", 
            type="password", 
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Required for analysis and Q&A"
        )
        
        # Model selection
        model_options = ["gpt-3.5-turbo", "gpt-4o", "gpt-4"]
        selected_model = st.selectbox(
            "AI Model", 
            options=model_options, 
            index=0,
            help="GPT-4 provides more detailed analysis but costs more"
        )
        
        # Analysis parameters
        temperature = st.slider(
            "Temperature", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.1,
            help="Lower values give more consistent results"
        )
        
        articles_count = st.slider(
            "Research Depth", 
            min_value=3, 
            max_value=10, 
            value=5,
            help="Number of sources to analyze"
        )
        
        # Enable RAG
        enable_rag = st.checkbox(
            "Enable Q&A System", 
            value=True,
            help="Allow asking questions about the analysis"
        )
        
        # Previous analyses
        if st.session_state.saved_analyses:
            st.header("Saved Analyses")
            for saved_topic in st.session_state.saved_analyses:
                if st.button(f"📁 {saved_topic}", key=f"load_{saved_topic}"):
                    st.session_state.current_topic = saved_topic
                    st.experimental_rerun()
    
    # Main content area
    st.markdown("<h3 class='section-header'>Enter Startup Topic</h3>", unsafe_allow_html=True)
    
    # Topic input area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input("Enter the area of interest for your startup:", key="topic_input")
    
    with col2:
        # Example topics dropdown
        examples = [
            "Select an example...",
            "AI-powered healthcare diagnostics",
            "Sustainable packaging solutions",
            "EdTech for personalized learning",
            "Fintech for small businesses",
            "Smart home energy management",
            "Plant-based meat alternatives",
            "Last-mile delivery automation"
        ]
        
        selected_example = st.selectbox("Or choose an example:", options=examples, key="example_selector")
        
        if selected_example != "Select an example..." and not topic:
            topic = selected_example
    


    
    # Analyze button
    if topic:
        analyze_col1, analyze_col2 = st.columns([1, 3])
        with analyze_col1:
            analyze_clicked = st.button("🔍 Analyze Opportunity", type="primary", key="analyze_button", use_container_width=True)
        
        with analyze_col2:
            st.markdown("""
            <div style="padding-top: 5px; color: #666;">
            Analysis includes market size, competitors, business model, investment needs, and success factors
            </div>
            """, unsafe_allow_html=True)
    
    # Run analysis when button clicked
    if topic and analyze_clicked:
        if not openai_api_key:
            st.error("Please enter your OpenAI API Key in the sidebar to continue.")
        else:
            # Set API key as environment variable
            os.environ["OPENAI_API_KEY"] = openai_api_key
            
            # Run analysis
            analysis_result = run_analysis(topic, openai_api_key, selected_model, temperature, articles_count)
            
            if analysis_result:
                # Store result
                st.session_state.saved_analyses[topic] = analysis_result
                st.session_state.current_topic = topic
                
                # Setup RAG for Q&A
                setup_rag_system(analysis_result, openai_api_key, selected_model, temperature, topic)
                
                # Display dashboard
                display_analysis_dashboard(analysis_result, topic)
                
                # Display Q&A interface if enabled
                if enable_rag:
                    display_qa_interface(topic, ask_question)
    
    # Show existing analysis if available
    elif st.session_state.current_topic:
        topic = st.session_state.current_topic
        if topic in st.session_state.saved_analyses:
            analysis_text = st.session_state.saved_analyses[topic]
            
            # Display dashboard
            display_analysis_dashboard(analysis_text, topic)
            
            # Display Q&A interface if enabled
            if enable_rag:
                display_qa_interface(topic, ask_question)

# Run the app
if __name__ == "__main__":
    main()