import streamlit as st
import logging
import time
import re
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from urllib.parse import urlparse
from duckduckgo_search import DDGS
from newspaper import Article

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define tools
def duckduckgo_search(query):
    """Search for articles using DuckDuckGo"""
    try:
        with DDGS() as ddg:
            results = list(ddg.text(query, max_results=8))
        urls = [result["href"] for result in results if result.get("href")]
        return urls if urls else ["No valid search results found."]
    except Exception as e:
        logger.error(f"Error in DuckDuckGo search: {str(e)}")
        return [f"Error performing search: {str(e)}"]

def fetch_article(url):
    """Fetch and parse article content"""
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return f"Invalid URL format: {url}"
        article = Article(url, timeout=10)
        article.download()
        article.parse()
        content = article.text
        return content[:3000] if content and len(content) > 50 else f"Insufficient content from {url}"
    except Exception as e:
        logger.error(f"Error fetching article from {url}: {str(e)}")
        return f"Error fetching content from {url}: {str(e)}"


# Setup RAG system
def setup_rag_system(content, openai_api_key, model, temperature, topic):
    """Setup RAG system for interactive Q&A"""
    try:
        # Ensure content is string
        if not isinstance(content, str):
            if hasattr(content, 'raw'):
                content = str(content.raw)
            elif hasattr(content, 'output'):
                content = str(content.output)
            else:
                content = str(content)
                
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Create chunks and vectorize
        chunks = text_splitter.split_text(content)
        vectorstore = FAISS.from_texts(chunks, embeddings)
        
        # Initialize memory and QA chain
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(api_key=openai_api_key, model=model, temperature=temperature),
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
            memory=memory
        )
        
        # Store in session state
        st.session_state.vectorstore[topic] = vectorstore
        st.session_state.qa_chain[topic] = qa_chain
        
        if topic not in st.session_state.chat_history:
            st.session_state.chat_history[topic] = []
            
        return qa_chain
        
    except Exception as e:
        logger.error(f"Error setting up RAG system: {str(e)}")
        st.error(f"Error setting up RAG system: {str(e)}")
        return None

# Run analysis with CrewAI
def run_analysis(topic, openai_api_key, model, temperature, articles_count):
    """Run comprehensive analysis with CrewAI"""
    # Initialize progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_status(message, progress):
        status_text.info(message)
        progress_bar.progress(progress)
        time.sleep(0.2)
    
    update_status("Initializing analysis pipeline...", 5)
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model,
            temperature=temperature
        )
        
        # Tools setup
        search_tool = Tool(
            name="DuckDuckGoSearch",
            func=duckduckgo_search,
            description="Perform DuckDuckGo searches and retrieve top URLs."
        )
        
        fetch_tool = Tool(
            name="FetchArticle",
            func=fetch_article,
            description="Fetch article text from URLs with robust error handling."
        )
        
        update_status("Creating specialized research agents...", 15)
        
        # Create specialized agents
        market_researcher = Agent(
            role="Market Research Specialist",
            goal=f"Find comprehensive market data about {topic} including size, growth, trends",
            backstory="Expert at analyzing market dynamics and extracting valuable insights.",
            tools=[search_tool, fetch_tool],
            llm=llm,
            verbose=True
        )
        
        competitor_analyst = Agent(
            role="Competitive Intelligence Expert",
            goal=f"Identify key competitors in the {topic} space and analyze their strategies",
            backstory="Specialist in competitive analysis with deep industry knowledge.",
            tools=[search_tool, fetch_tool],
            llm=llm,
            verbose=True
        )
        
        business_strategist = Agent(
            role="Business Strategist",
            goal=f"Develop comprehensive business strategy for a {topic} startup",
            backstory="Experienced business consultant who has helped numerous startups succeed.",
            tools=[search_tool],
            llm=llm,
            verbose=True
        )
        
        financial_analyst = Agent(
            role="Financial Analyst",
            goal=f"Provide financial insights for a {topic} startup",
            backstory="Expert in startup financial modeling with experience in venture funding.",
            llm=llm,
            verbose=True
        )
        
        update_status("Setting up specialized research tasks...", 25)
        
        # Create detailed tasks
        market_research_task = Task(
            description=f"""
            Research the {topic} market thoroughly. Find and analyze:
            1. Market size (in $ value)
            2. Growth rate and CAGR
            3. Key market segments
            4. Regional distribution
            5. Major trends and drivers
            6. Challenges and barriers
            
            Use specific data points, statistics, and cite sources when possible.
            """,
            agent=market_researcher,
            expected_output="Comprehensive market analysis with specific data points"
        )
        
        competitor_analysis_task = Task(
            description=f"""
            Conduct a detailed competitor analysis for the {topic} space:
            1. Identify at least 5 key competitors
            2. Analyze their business models
            3. Evaluate their strengths and weaknesses
            4. Assess their market positioning
            5. Identify potential gaps in the market
            
            Focus on both established players and innovative startups.
            """,
            agent=competitor_analyst,
            context=[market_research_task],
            expected_output="Detailed competitor landscape analysis"
        )
        
        business_strategy_task = Task(
            description=f"""
            Develop a comprehensive business strategy for a {topic} startup:
            1. Recommend optimal business model(s)
            2. Identify target customer segments
            3. Suggest unique value proposition
            4. Outline go-to-market strategy
            5. Propose partnership opportunities
            
            Base recommendations on market research and competitor analysis.
            """,
            agent=business_strategist,
            context=[market_research_task, competitor_analysis_task],
            expected_output="Comprehensive business strategy recommendations"
        )
        
        financial_insights_task = Task(
            description=f"""
            Provide financial insights for a {topic} startup:
            1. Estimate initial investment required
            2. Suggest revenue streams and pricing models
            3. Identify key cost factors
            4. Estimate timeline to profitability
            5. Highlight financial risks and mitigation strategies
            
            Provide realistic ranges based on industry benchmarks.
            """,
            agent=financial_analyst,
            context=[market_research_task, business_strategy_task],
            expected_output="Financial analysis and recommendations"
        )
        
        final_report_task = Task(
            description=f"""
            Create a comprehensive startup analysis report for {topic} that includes:
            
            # MARKET ANALYSIS
            - Market size, growth projections, and trends
            - Key drivers and barriers
            - Regulatory considerations
            
            # COMPETITIVE LANDSCAPE
            - Key players and their market positions
            - Competitor strengths and weaknesses
            - Market gaps and opportunities
            
            # BUSINESS STRATEGY
            - Recommended business model(s)
            - Target customer segments
            - Unique value proposition
            - Go-to-market strategy
            
            # FINANCIAL CONSIDERATIONS
            - Initial investment requirements
            - Revenue model recommendations
            - Path to profitability
            - Key financial risks
            
            # RECOMMENDATIONS
            - Critical success factors
            - Key risks and mitigation strategies
            - Timeline considerations
            - Next steps for entrepreneurs
            
            Format as a well-structured markdown report with clear sections and specific data points.
            """,
            agent=business_strategist,
            context=[market_research_task, competitor_analysis_task, business_strategy_task, financial_insights_task],
            expected_output="Comprehensive startup opportunity analysis report"
        )
        
        update_status("Assembling expert crew and initializing analysis...", 35)
        
        # Create and run the crew
        crew = Crew(
            agents=[market_researcher, competitor_analyst, business_strategist, financial_analyst],
            tasks=[market_research_task, competitor_analysis_task, business_strategy_task, financial_insights_task, final_report_task],
            verbose=True,
            process=Process.sequential
        )
        
        update_status("Conducting in-depth market research...", 45)
        time.sleep(1)
        update_status("Analyzing competitor landscape...", 55)
        time.sleep(1)
        update_status("Developing business strategy recommendations...", 65)
        time.sleep(1)
        update_status("Compiling financial insights...", 75)
        time.sleep(1)
        update_status("Generating comprehensive report...", 85)
        
        # Run analysis
        result = crew.kickoff()
        
        # Convert result to string
        if hasattr(result, 'raw'):
            final_result = str(result.raw)
        elif hasattr(result, 'output'):
            final_result = str(result.output)
        else:
            final_result = str(result)
        
        update_status("Analysis complete!", 100)
        
        return final_result
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        st.error(f"An error occurred during analysis: {str(e)}")
        return None


