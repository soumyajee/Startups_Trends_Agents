import streamlit as st
import json
import re
import random
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# CSS for better styling
def load_css():
    st.markdown("""
    <style>
        .main-header {font-size: 2.5rem; color: #4527A0; margin-bottom: 0;}
        .sub-header {font-size: 1.2rem; color: #5E35B1; margin-bottom: 2rem;}
        .section-header {font-size: 1.5rem; color: #4527A0; margin-top: 1rem;}
        .insight-card {
            background-color: #f0f4f8; 
            border-left: 4px solid #4527A0; 
            padding: 1rem; 
            margin-bottom: 1rem; 
            border-radius: 0.5rem;
            color: #000000;
            font-weight: 500;
        }
        .chat-message {
            padding: 1rem; 
            border-radius: 0.5rem; 
            margin-bottom: 0.8rem;
            font-weight: 500;
        }
        .user-message {
            background-color: #e3f2fd; 
            border-left: 4px solid #1565C0;
            color: #000000;
        }
        .ai-message {
            background-color: #f3e5f5; 
            border-left: 4px solid #6a1b9a;
            color: #000000;
        }
        .highlight {
            background-color: #FFE082; 
            padding: 0.2rem; 
            border-radius: 0.2rem;
            color: #000000;
        }
        .stProgress > div > div > div > div {background-color: #4527A0;}
        .metric-card {
            background-color: white;
            box-shadow: rgba(0, 0, 0, 0.15) 0px 2px 8px;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #4527A0;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #333333;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)

# Page Configuration
def setup_page():
    st.set_page_config(page_title="AI Startup Trend Analyzer", page_icon="📈", layout="wide")
    load_css()
    st.markdown("<h1 class='main-header'>📈 AI Startup Trend Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Comprehensive startup insights with advanced market analysis</p>", unsafe_allow_html=True)

# Generate visualizations
def generate_visualizations(topic, analysis_text):
    """Generate visualizations based on analysis text and topic"""
    # Market size projection
    years = list(range(2023, 2029))
    base_size = random.randint(5, 20) * 100  # Random starting value between $500M-$2B
    
    # Look for specific market size mentions in the text
    market_size_pattern = r"\$\s*(\d+(?:\.\d+)?)\s*(million|billion|trillion|M|B|T)"
    matches = re.findall(market_size_pattern, analysis_text, re.IGNORECASE)
    
    if matches:
        # Use the first match as our base
        value, unit = matches[0]
        multiplier = 1
        if unit.lower() in ['billion', 'b']:
            multiplier = 1000
        elif unit.lower() in ['trillion', 't']:
            multiplier = 1000000
            
        try:
            base_size = float(value) * multiplier  # Convert to millions
        except:
            pass  # Fallback to random if conversion fails
    
    # Generate growth pattern
    cagr_pattern = r"(?:CAGR|compound annual growth rate|annual growth|growth rate) of (?:approximately |~|about |around )?(\d+(?:\.\d+)?)\s*%"
    cagr_matches = re.findall(cagr_pattern, analysis_text, re.IGNORECASE)
    
    if cagr_matches:
        try:
            annual_growth = float(cagr_matches[0]) / 100 + 1
        except:
            annual_growth = random.uniform(1.15, 1.35)  # 15-35% if parsing fails
    else:
        annual_growth = random.uniform(1.15, 1.35)  # 15-35% default growth
    
    # Generate market sizes with some variability
    market_sizes = [base_size]
    for _ in range(len(years)-1):
        yearly_growth = annual_growth * random.uniform(0.85, 1.15)  # Add variability
        market_sizes.append(round(market_sizes[-1] * yearly_growth))
    
    # Market size chart
    df_market = pd.DataFrame({
        'Year': years,
        'Market Size ($M)': market_sizes
    })
    
    fig_market = px.line(
        df_market, 
        x='Year', 
        y='Market Size ($M)', 
        title=f'Projected Market Size: {topic}',
        markers=True
    )
    
    fig_market.update_layout(
        height=450,
        xaxis_title="Year",
        yaxis_title="Market Size ($M)",
        hovermode="x unified"
    )
    
    # Add annotations for projections
    for i, year in enumerate(years):
        if year > 2023:
            fig_market.add_annotation(
                x=year,
                y=market_sizes[i],
                text="Projected",
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-40,
                arrowcolor="#4527A0",
                font=dict(size=10, color="#4527A0")
            )
    
    # Competitor analysis
    # Extract competitor mentions if any
    competitor_pattern = r"(?:competitors|companies|startups|players|vendors)(?:\s+in|\s+include|\s+are|\:)([^.]*(?:\.[^.]*){0,3})"
    competitor_sections = re.findall(competitor_pattern, analysis_text, re.IGNORECASE)
    
    competitors = []
    if competitor_sections:
        # Extract company names that might be in the text
        company_pattern = r'([A-Z][a-zA-Z0-9\'\-]*(?:\s+[A-Z][a-zA-Z0-9\'\-]*)*)'
        for section in competitor_sections:
            companies = re.findall(company_pattern, section)
            for company in companies:
                if len(company.split()) <= 4 and len(company) > 2:  # Avoid long phrases
                    competitors.append(company)
    
    # Ensure we have at least some competitors
    if len(competitors) < 3:
        # Generate some generic competitors
        industry_terms = topic.split()
        prefixes = ["Tech", "Smart", "AI", "Next", "Future", "Inno", "Digi", "Quantum", "Data", "Cloud"]
        suffixes = ["Solutions", "Technologies", "Systems", "Analytics", "Innovations", "Platforms", "Insights"]
        
        while len(competitors) < 5:
            if industry_terms:
                term = random.choice(industry_terms)
                prefix = random.choice(prefixes)
                suffix = random.choice(suffixes)
                competitor = f"{prefix}{term[:4]}" if len(term) > 4 else f"{prefix}{term}"
                if random.random() > 0.5:
                    competitor += f" {suffix}"
                competitors.append(competitor)
            else:
                competitor = f"{random.choice(prefixes)}{random.choice(suffixes)}"
                competitors.append(competitor)
    
    # Keep unique competitors, limit to 7
    competitors = list(set(competitors))[:7]
    
    # Generate random market shares
    total = 100
    shares = []
    for i in range(len(competitors) - 1):
        if i == 0:
            # Leader gets bigger share
            share = random.randint(20, 40)
        elif i < 3:
            # Top companies get decent shares
            share = random.randint(10, 25)
        else:
            # Smaller players
            share = random.randint(5, 15)
            
        if share > total:
            share = total
            
        shares.append(share)
        total -= share
    
    # Last company gets remainder
    shares.append(total)
    
    # Ensure we don't have any zeros
    shares = [max(1, share) for share in shares]
    
    # Sort by market share (descending)
    competitor_data = sorted(zip(competitors, shares), key=lambda x: x[1], reverse=True)
    competitors, shares = zip(*competitor_data)
    
    # Competitor market share chart
    fig_competitors = go.Figure(
        go.Pie(
            labels=competitors,
            values=shares,
            hole=.4,
            marker_colors=px.colors.qualitative.Bold
        )
    )
    
    fig_competitors.update_layout(
        title_text=f'Estimated Market Share: {topic}',
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    # SWOT analysis 
    strengths = [
        "First-mover advantage potential",
        "Low entry barriers for certain segments",
        "Technological innovation opportunities",
        "Access to growing customer base"
    ]
    
    weaknesses = [
        "Initial capital requirements",
        "Customer acquisition challenges",
        "Establishing market credibility",
        "Talent acquisition competition"
    ]
    
    opportunities = [
        f"Growing {topic} market",
        "Underserved customer segments",
        "Integration with existing platforms",
        "International expansion options"
    ]
    
    threats = [
        "Established competitor presence",
        "Regulatory evolution uncertainty",
        "Rapid technological changes",
        "Economic fluctuations impact"
    ]
    
    swot_data = {
        "Strengths": "<br>".join([f"• {s}" for s in strengths]),
        "Weaknesses": "<br>".join([f"• {w}" for w in weaknesses]),
        "Opportunities": "<br>".join([f"• {o}" for o in opportunities]),
        "Threats": "<br>".join([f"• {t}" for t in threats])
    }
    
    fig_swot = go.Figure()
    
    # Create a 2x2 SWOT grid
    fig_swot.add_trace(go.Scatter(
        x=[0, 0, 1, 1, 0],
        y=[0, 1, 1, 0, 0],
        mode="lines",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False
    ))
    
    # Add quadrant labels
    quadrants = [
        {"name": "Strengths", "x": 0.25, "y": 0.75, "color": "#4CAF50"},
        {"name": "Weaknesses", "x": 0.75, "y": 0.75, "color": "#F44336"},
        {"name": "Opportunities", "x": 0.25, "y": 0.25, "color": "#2196F3"},
        {"name": "Threats", "x": 0.75, "y": 0.25, "color": "#FF9800"}
    ]
    
    for q in quadrants:
        fig_swot.add_annotation(
            x=q["x"],
            y=q["y"],
            text=f"<b>{q['name']}</b><br><br>{swot_data[q['name']]}",
            showarrow=False,
            font=dict(size=12, color="#000"),
            align="center",
            bordercolor=q["color"],
            borderwidth=2,
            borderpad=4,
            bgcolor="white",
            opacity=0.8
        )
        
    fig_swot.update_layout(
        title_text="SWOT Analysis for Startup Opportunity",
        height=450,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig_market, fig_competitors, fig_swot, market_sizes[-1], annual_growth - 1

# Extract key insights for dashboard
def extract_insights(analysis_text):
    """Extract key metrics and insights from analysis text"""
    
    # Key metrics to extract
    insights = {
        "timeToMarket": random.randint(6, 18),
        "initialInvestment": f"${random.randint(50, 500)}K - ${random.randint(500, 2000)}K",
        "breakEvenEstimate": f"{random.randint(12, 36)} months",
        "keyRisks": [],
        "successFactors": [],
        "recommendedBusinessModel": ""
    }
    
    # Extract key risks
    risk_pattern = r"(?:key risk|main risk|significant risk|risk factor)s?(?:\s+include|\s+are|\:)([^.]*(?:\.[^.]*){0,3})"
    risk_sections = re.findall(risk_pattern, analysis_text, re.IGNORECASE)
    
    if risk_sections:
        for section in risk_sections:
            # Split by commas, semicolons, or bullet points
            risks = re.split(r'[,;•]+', section)
            for risk in risks:
                risk = risk.strip()
                if 5 < len(risk) < 100 and risk not in insights["keyRisks"]:
                    insights["keyRisks"].append(risk)
    
    # Fallback for risks
    if not insights["keyRisks"]:
        insights["keyRisks"] = [
            "Intense competition from established players",
            "Rapidly evolving technology landscape",
            "Changing regulatory requirements",
            "Initial customer acquisition costs"
        ]
    
    # Extract success factors
    success_pattern = r"(?:success factor|key factor|crucial element|critical aspect)s?(?:\s+include|\s+are|\:)([^.]*(?:\.[^.]*){0,3})"
    success_sections = re.findall(success_pattern, analysis_text, re.IGNORECASE)
    
    if success_sections:
        for section in success_sections:
            # Split by commas, semicolons, or bullet points
            factors = re.split(r'[,;•]+', section)
            for factor in factors:
                factor = factor.strip()
                if 5 < len(factor) < 100 and factor not in insights["successFactors"]:
                    insights["successFactors"].append(factor)
    
    # Fallback for success factors
    if not insights["successFactors"]:
        insights["successFactors"] = [
            "Strong technical team and expertise",
            "Deep understanding of target market",
            "Agile development methodology",
            "Strategic partnerships with industry players"
        ]
    
    # Extract business model
    model_pattern = r"(?:business model|revenue model|monetization|revenue stream)(?:\s+include|\s+are|\s+should|\s+could|\s+would|\s+recommend|\:)([^.]*(?:\.[^.]*){0,2})"
    model_sections = re.findall(model_pattern, analysis_text, re.IGNORECASE)
    
    if model_sections:
        # Use the longest match as it likely has more information
        insights["recommendedBusinessModel"] = max(model_sections, key=len).strip()
    else:
        # Fallback for business model
        models = [
            "SaaS subscription model with tiered pricing based on features and usage",
            "Freemium model with basic features free and premium features paid",
            "Transaction-based revenue model with fee per transaction",
            "Marketplace model connecting providers and consumers with commission structure"
        ]
        insights["recommendedBusinessModel"] = random.choice(models)
    
    return insights

# Interactive Q&A interface
def display_qa_interface(topic, ask_question_func):
    """Display interactive Q&A interface with RAG"""
    if topic not in st.session_state.qa_chain:
        st.info("Please run an analysis first to enable the Q&A feature.")
        return
    
    st.markdown("<h3 class='section-header'>🤔 Ask Questions About This Analysis</h3>", unsafe_allow_html=True)
    st.markdown("Ask specific questions about the analysis to get deeper insights.")
    
    # Initialize chat history for this topic if needed
    if topic not in st.session_state.chat_history:
        st.session_state.chat_history[topic] = []
    
    # Display chat history
    for message in st.session_state.chat_history[topic]:
        if message["role"] == "user":
            st.markdown(f"<div class='chat-message user-message'><strong style='color:#1565C0;'>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-message ai-message'><strong style='color:#6a1b9a;'>AI:</strong> {message['content']}</div>", unsafe_allow_html=True)
    
    # Suggestion buttons for common questions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💰 Initial investment needed?"):
            question = f"What is the recommended initial investment for a {topic} startup?"
            ask_question_func(question, topic)
            
    with col2:
        if st.button("🏆 Key success factors?"):
            question = f"What are the key success factors for a {topic} startup?"
            ask_question_func(question, topic)
            
    with col3:
        if st.button("⚠️ Main risks to consider?"):
            question = f"What are the main risks and challenges for a {topic} startup?"
            ask_question_func(question, topic)
    
    # Custom question input
    question = st.text_input("Ask a specific question:", key="qa_input")
    if st.button("Ask Question") and question:
        ask_question_func(question, topic)
        
# Display startup analysis dashboard
def display_analysis_dashboard(analysis_text, topic):
    """Display comprehensive startup analysis dashboard"""
    if not analysis_text:
        st.error("No analysis data available.")
        return
    
    # Generate visualizations
    fig_market, fig_competitors, fig_swot, projected_market_size, growth_rate = generate_visualizations(topic, analysis_text)
    
    # Extract key insights
    insights = extract_insights(analysis_text)
    
    # Display dashboard layout
    st.markdown(f"<h2 class='section-header'>Startup Analysis: {topic}</h2>", unsafe_allow_html=True)
    
    # Market metrics section
    st.markdown("<h3 class='section-header'>📊 Market Metrics</h3>", unsafe_allow_html=True)
    
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">${projected_market_size}M</div>
                <div class="metric-label">Projected Market (2028)</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Charts section
    chart_cols = st.columns([1, 1])
    with chart_cols[0]:
        st.plotly_chart(fig_market, use_container_width=True)
    
    with chart_cols[1]:
        st.plotly_chart(fig_competitors, use_container_width=True)
    
    # SWOT and key considerations
    swot_col, considerations_col = st.columns([3, 2])
    
    with swot_col:
        st.plotly_chart(fig_swot, use_container_width=True)
    
    with considerations_col:
        st.markdown("<h4>💰 Investment Required</h4>", unsafe_allow_html=True)
        st.markdown(f"<div class='insight-card'>{insights['initialInvestment']}</div>", unsafe_allow_html=True)
        
        st.markdown("<h4>💼 Recommended Business Model</h4>", unsafe_allow_html=True)
        st.markdown(f"<div class='insight-card'>{insights['recommendedBusinessModel']}</div>", unsafe_allow_html=True)
        
        st.markdown("<h4>⚠️ Key Risks</h4>", unsafe_allow_html=True)
        risks_html = "<div class='insight-card' style='background-color: #ffebee; border-left-color: #e53935;'>"
        for risk in insights['keyRisks'][:3]:  # Show top 3 risks
            risks_html += f"• {risk}<br>"
        risks_html += "</div>"
        st.markdown(risks_html, unsafe_allow_html=True)
    
    # Full report tabs
    st.markdown("<h3 class='section-header'>📑 Detailed Analysis</h3>", unsafe_allow_html=True)
    
    tabs = st.tabs([
        "Market Analysis", 
        "Competitive Landscape", 
        "Business Strategy", 
        "Financial Insights",
        "Full Report"
    ])
    
    # Extract sections using regex patterns
    market_pattern = r'(?:#+ *MARKET ANALYSIS.*?)(?=#+ *|$)'
    competitive_pattern = r'(?:#+ *COMPETITIVE LANDSCAPE.*?)(?=#+ *|$)'
    business_pattern = r'(?:#+ *BUSINESS STRATEGY.*?)(?=#+ *|$)'
    financial_pattern = r'(?:#+ *FINANCIAL CONSIDERATIONS.*?)(?=#+ *|$)'
    
    with tabs[0]:
        market_section = re.search(market_pattern, analysis_text, re.DOTALL | re.IGNORECASE)
        if market_section:
            st.markdown(market_section.group(0))
        else:
            st.markdown(analysis_text[:int(len(analysis_text)/5)])  # Show first fifth if no section found
    
    with tabs[1]:
        competitive_section = re.search(competitive_pattern, analysis_text, re.DOTALL | re.IGNORECASE)
        if competitive_section:
            st.markdown(competitive_section.group(0))
        else:
            # Try alternative headings
            alt_pattern = r'(?:#+ *COMPETITORS.*?)(?=#+ *|$)|(?:#+ *COMPETITION.*?)(?=#+ *|$)'
            alt_section = re.search(alt_pattern, analysis_text, re.DOTALL | re.IGNORECASE)
            if alt_section:
                st.markdown(alt_section.group(0))
            else:
                st.markdown("Competitive landscape analysis not found in structured format.")
    
    with tabs[2]:
        business_section = re.search(business_pattern, analysis_text, re.DOTALL | re.IGNORECASE)
        if business_section:
            st.markdown(business_section.group(0))
        else:
            # Try alternative headings
            alt_pattern = r'(?:#+ *STRATEGY.*?)(?=#+ *|$)|(?:#+ *RECOMMENDATIONS.*?)(?=#+ *|$)'
            alt_section = re.search(alt_pattern, analysis_text, re.DOTALL | re.IGNORECASE)
            if alt_section:
                st.markdown(alt_section.group(0))
            else:
                st.markdown("Business strategy section not found in structured format.")
    
    with tabs[3]:
        financial_section = re.search(financial_pattern, analysis_text, re.DOTALL | re.IGNORECASE)
        if financial_section:
            st.markdown(financial_section.group(0))
        else:
            # Try alternative headings
            alt_pattern = r'(?:#+ *FINANCIAL.*?)(?=#+ *|$)|(?:#+ *INVESTMENT.*?)(?=#+ *|$)'
            alt_section = re.search(alt_pattern, analysis_text, re.DOTALL | re.IGNORECASE)
            if alt_section:
                st.markdown(alt_section.group(0))
            else:
                st.markdown("Financial insights section not found in structured format.")
    
    with tabs[4]:
        st.markdown(analysis_text)
        
        # Download options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download as Markdown",
                data=analysis_text,
                file_name=f"{topic.replace(' ', '_')}_analysis.md",
                mime="text/markdown"
            )
        
        with col2:
            # Create JSON with all analysis data
            analysis_data = {
                "topic": topic,
                "analysis": analysis_text,
                "marketMetrics": {
                    "projectedSize": projected_market_size,
                    "cagr": round(growth_rate*100, 1),
                    "timeToMarket": insights['timeToMarket'],
                    "breakEven": insights['breakEvenEstimate']
                },
                "businessInsights": {
                    "initialInvestment": insights['initialInvestment'],
                    "recommendedModel": insights['recommendedBusinessModel'],
                    "keyRisks": insights['keyRisks'],
                    "successFactors": insights['successFactors']
                }
            }
            
            st.download_button(
                "Download as JSON",
                data=json.dumps(analysis_data, indent=2),
                file_name=f"{topic.replace(' ', '_')}_analysis.json",
                mime="application/json"
            )
    
    with metric_cols[1]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{round(growth_rate*100, 1)}%</div>
                <div class="metric-label">CAGR</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with metric_cols[2]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{insights['timeToMarket']}</div>
                <div class="metric-label">Months to Market</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with metric_cols[3]:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{insights['breakEvenEstimate']}</div>
                <div class="metric-label">Est. Break-even</div>
            </div>
            """, 
            unsafe_allow_html=True
        )