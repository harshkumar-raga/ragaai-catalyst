import os
from dotenv import load_dotenv
from openai import OpenAI

from ragaai_catalyst.tracers import Tracer
from ragaai_catalyst import RagaAICatalyst
import os
import requests
from dotenv import load_dotenv
load_dotenv()

catalyst = RagaAICatalyst(
    access_key="access_key",
    secret_key="secret_key",
    base_url="base_url"
)
# Initialize tracer
tracer = Tracer(
    project_name="project_name",
    dataset_name="dataset_name",
    tracer_type="tracer_type",
    metadata={
        "model": "gpt-4o-mini",
        "environment": "development"
    },
    pipeline={
        "llm_model": "gpt-4o-mini",
        "vector_store": "faiss",
        "embed_model": "text-embedding-ada-002",
    }
)
load_dotenv()


tracer.start()

@tracer.trace_llm(name="llm_call", tags=["default_llm_call"])
def llm_call(prompt, max_tokens=512, model="gpt-4o-mini"):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    response_data = response.choices[0].message.content.strip()
    print('response_data: ', response_data)
    return response_data

class SummaryAgent:
    def __init__(self, persona="Summary Agent"):
        self.persona = persona

    @tracer.trace_agent(name="summary_agent", tags=['basic_agent'])
    def summarize(self, text):
        # Make an LLM call
        prompt = f"Please summarize this text concisely: {text}"
        summary = llm_call(prompt)
        return summary
        
class AnalysisAgent:
    def __init__(self, persona="Analysis Agent"):
        self.persona = persona
        self.summary_agent = SummaryAgent()

    @tracer.trace_agent(name="analysis_agent", tags=['coordinator_agent'])
    def analyze(self, text):
        # First use the summary agent
        summary = self.summary_agent.summarize(text)
        
        # Then make our own LLM call for analysis
        prompt = f"Given this summary: {summary}\nProvide a brief analysis of the main points."
        analysis = llm_call(prompt)
        
        return {
            "summary": summary,
            "analysis": analysis
        }

class RecommendationAgent:
    def __init__(self, persona="Recommendation Agent"):
        self.persona = persona
        self.analysis_agent = AnalysisAgent()

    @tracer.trace_agent(name="recommendation_agent", tags=['coordinator_agent'])
    def recommend(self, text):
        # First get analysis from analysis agent (which internally uses summary agent)
        analysis_result = self.analysis_agent.analyze(text)
        
        # Then make our own LLM call for recommendations
        prompt = f"""Given this summary: {analysis_result['summary']}
        And this analysis: {analysis_result['analysis']}
        Provide 2-3 actionable recommendations."""
        
        recommendations = llm_call(prompt)
        
        return {
            "summary": analysis_result["summary"],
            "analysis": analysis_result["analysis"],
            "recommendations": recommendations
        }

@tracer.trace_agent(name="get_recommendation", tags=['coordinator_agent'])
def get_recommendation(agent, text):
    recommendation = agent.recommend(text)
    return recommendation

def main():
    # Sample text to analyze
    text = """
    Artificial Intelligence has transformed various industries in recent years.
    From healthcare to finance, AI applications are becoming increasingly prevalent.
    Machine learning models are being used to predict market trends, diagnose diseases,
    and automate routine tasks. The impact of AI on society continues to grow,
    raising both opportunities and challenges for the future.
    """
    
    tracer.span('get_recommendation').add_tags(['main_agent(main_function)'])
    # Create and use the recommendation agent
    recommendation_agent = RecommendationAgent()
    # result = recommendation_agent.recommend(text)
    result = get_recommendation(recommendation_agent, text)
    tracer.span('llm_call').add_metadata({'is_completed': True})
    
    print("\nResults:")
    print("Summary:", result["summary"])
    print("\nAnalysis:", result["analysis"])
    print("\nRecommendations:", result["recommendations"])
    

if __name__ == "__main__":
    main()  
    tracer.stop()  
