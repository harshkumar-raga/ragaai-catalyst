import os
import json
import requests
from urllib.parse import urlparse
from typing import List, Dict
from dotenv import load_dotenv

from bs4 import BeautifulSoup
from litellm import completion

# Import RagaAI Catalyst for tracing
from ragaai_catalyst.tracers import Tracer
from ragaai_catalyst import (
    RagaAICatalyst,
    trace_tool,
    trace_llm,
    trace_agent,
    init_tracing,
)

# Load environment variables
load_dotenv()

# Initialize RagaAI Catalyst
catalyst = RagaAICatalyst(
    access_key=os.getenv("RAGAAI_CATALYST_ACCESS_KEY"),
    secret_key=os.getenv("RAGAAI_CATALYST_SECRET_KEY"),
    base_url=os.getenv("RAGAAI_CATALYST_BASE_URL"),
)

# Set up the tracer to track interactions
tracer = Tracer(
    project_name="alteryx_copilot-tan",
    dataset_name="testing-3",
    tracer_type="Agentic",
)

# Initialize tracing with RagaAI Catalyst
init_tracing(catalyst=catalyst, tracer=tracer)

class FinancialReportGenerator:
    # We can trace the tools using the @trace_tool decorator
    # Using the @trace_tool decorator will trace tool scrape_website
    @trace_tool("scrape_website")
    def scrape_website(self, url: str) -> str:
        """
        Scrape content from a given URL
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=" ", strip=True)
            return text
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return ""

    # Using the @trace_llm decorator will trace llm analyze_sentiment
    @trace_llm(name="analyze_sentiment")
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text using LiteLLM
        """
        try:
            response = completion(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the following text and provide sentiment analysis focused on financial implications. Return a JSON with 'sentiment' (positive/negative/neutral), 'confidence' (0-1), and 'key_points'.",
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=500,
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            return {"sentiment": "neutral", "confidence": 0, "key_points": []}
        
    # Using the @trace_llm decorator will trace llm get_report
    @trace_llm(name="get_report")
    def get_report(self, report_prompt: str) -> str:
        response = completion(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst. Generate a comprehensive financial report based on the provided data. Include market analysis, stock performance, and key insights.",
                },
                {"role": "user", "content": report_prompt},
            ],
            max_tokens=1500,
        )
        print("Report generated successfully.")
        return response.choices[0].message.content

    # Using the @trace_agent decorator to trace the generate_report agent
    @trace_agent(name="generate_report")
    def generate_report(self, urls: List[str]) -> str:
        """
        Generate a comprehensive financial report from multiple sources
        """
        # Collect data from all sources
        website_contents = []
        sentiments = []

        print("Processing URLs...")
        # Process URLs
        for url in urls:
            content = self.scrape_website(url)
            if content:
                website_contents.append(
                    {"url": url, "content": content, "domain": urlparse(url).netloc}
                )
                print(f"Scraped content from {url}")

                # Analyze sentiment
                print("Analyzing sentiment...")
                sentiments.append(self.analyze_sentiment(content))

        print("Generating report...")
        # Generate report using LiteLLM
        report_prompt = self._create_report_prompt(website_contents, sentiments)

        report = self.get_report(report_prompt)
        return report

    # Using the @trace_tool decorator will trace tool create_report_prompt
    @trace_tool("create_report_prompt")
    def _create_report_prompt(
        self, website_contents: List[Dict], sentiments: List[Dict]
    ) -> str:
        print("Creating report prompt...")
        """
        Create a structured prompt for report generation
        """
        prompt = "Generate a financial report based on the following data:\n\n"

        # Add website content summaries
        prompt += "News and Analysis:\n"
        for content in website_contents:
            prompt += f"Source: {content['domain']}\n"
            prompt += "Key points from sentiment analysis:\n"
            for sentiment in sentiments:
                prompt += f"- Sentiment: {sentiment['sentiment']}\n"
                prompt += f"- Key points: {', '.join(sentiment['key_points'])}\n"

        prompt += "\nPlease provide a comprehensive analysis including:\n"
        prompt += "1. Market Overview\n"
        prompt += "2. Stock Analysis\n"
        prompt += "3. News Impact Analysis\n"
        prompt += "4. Key Insights and Recommendations\n"

        return prompt


# Example usage
if __name__ == "__main__":
    with tracer:
        generator = FinancialReportGenerator()

        # Example URLs and stock symbols
        urls = [
            "https://money.rediff.com/news/market/rupee-hits-record-low-of-85-83-against-us-dollar/20623520250108",
            "https://indianexpress.com/article/business/banking-and-finance/rbi-asks-credit-bureaus-banks-to-pay-rs-100-compensation-per-day-for-delay-in-data-updation-9765814/",
        ]

        report = generator.generate_report(urls)
        print(report)