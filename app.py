import gradio as gr
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from transformers import pipeline

# Initialize the summarization pipeline
summarizer = pipeline("summarization", model="google/flan-t5-small")

def fetch_bbc_news():
    bbc_url = "https://www.bbc.com/news"
    response = requests.get(bbc_url)
    
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a", href=True)
    article_links = [link for link in links if "/news/articles/" in link["href"]]

    articles = []
    
    for link in article_links[:10]:
        article_url = "https://www.bbc.com" + link["href"]
        
        try:
            article_response = requests.get(article_url, timeout=10)
            article_soup = BeautifulSoup(article_response.content, "html.parser")
            
            title = article_soup.find("h1").get_text() if article_soup.find("h1") else "Untitled"
            
            paragraphs = article_soup.find_all("p")
            article_text = " ".join([p.get_text() for p in paragraphs])
            
            if not article_text:
                article_text = "No content available."
            
            summary = summarizer(article_text, max_length=200, min_length=50, do_sample=False)[0]["summary_text"]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            articles.append({
                "title": title,
                "summary": summary,
                "link": article_url,
                "timestamp": timestamp
            })
        except Exception as e:
            print(f"Error fetching article from {article_url}: {e}")
            continue
    
    return articles

def display_articles():
    articles = fetch_bbc_news()
    if not articles:
        return """<h3 style="text-align: center; color: red;">No articles found. Please try again later.</h3>"""
    
    html_header = """<div style="text-align: center; padding: 20px; background-color: #f0f2f5; border-radius: 10px;">
                        <h1 style="font-size: 2.2em; margin-bottom: 10px; color: #1a73e8;">BBC News Summaries</h1>
                    </div>"""
    
    html_content = []
    html_content.append(html_header)
    
    for article in articles:
        article_card = f"""
        <div style="background-color: white; border-radius: 10px; padding: 20px; margin: 10px auto; 
                    max-width: 800px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #1a73e8; font-size: 1.3em; margin-bottom: 15px;">{article['title']}</h3>
            <p style="color: #4a5568; font-size: 0.95em; margin-bottom: 15px;">{article['summary']}</p>
            <div style="color: #94a3b8; font-size: 0.85em; margin-bottom: 12px;">
                <strong>Published:</strong> {article['timestamp']}
            </div>
            <a href="{article['link']}" target="_blank" style="background-color: #1a73e8; color: white; 
              padding: 8px 18px; text-decoration: none; border-radius: 5px; font-weight: 500; 
              transition: background-color 0.3s ease; display: block; margin-top: 10px;">
                Read More →
            </a>
        </div>"""
        html_content.append(article_card)
    
    return ''.join(html_content)

demo = gr.Interface(
    fn=display_articles,
    inputs=None,
    outputs=gr.HTML(),
    live=True,
    title="📰 BBC News Summarizer",
    description="Get the latest BBC News articles with AI-generated summaries."
)

if __name__ == "__main__":
    demo.launch()