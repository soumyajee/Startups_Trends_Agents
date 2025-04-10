conda create -n lang6 python=3.11 -y
conda activate lang6
pip install -r requirements.txt

#run 
streamlit run startup_agent.py

langchain==0.3.13
langchain-core==0.3.28
langchain-community==0.3.13
langchain-openai==0.2.14



pip install crewai>=0.100.0
pip install crewai-tools
pip install langchain>=0.3.13
pip install langchain-core>=0.3.35
pip install langchain-openai>=0.3.1
pip install streamlit
pip install newspaper3k
pip install duckduckgo-search