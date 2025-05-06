import requests
import random

from core.config import GCS_API_KEY, GCS_CX

def search_web_snippets(llm_response, num_results=5):
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GCS_API_KEY,
            "cx": GCS_CX,
            "q": llm_response,
            "num": num_results,
        }
        
        response = requests.get(url, params=params).json()
        results = []
        
        for item in response.get("items", []):
            title   = item.get("title", "No Title")
            link    = item.get("link", "")
            snippet = item.get("snippet", "")

            results.append({
                "title" : title, 
                "link"  : link, 
                "snippet"   : snippet
            })

        num_to_return = random.randint(1, min(5, len(results)))
        link_result = [link['link'] for link in random.sample(results, num_to_return)]
        return link_result
    
    except Exception as e:
        return []