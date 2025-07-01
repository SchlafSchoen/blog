import os
import openai
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
BLOG_ID = os.getenv("BLOG_ID")

def generate_topic():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": "Erstelle einen kurzen, interessanten Blogartikel-Titel auf Deutsch für eine Matratzenmarke namens 'Schlaf Schön®'."
        }]
    )
    return response.choices[0].message["content"].strip()

def generate_blog_content(topic):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"Schreibe einen SEO-freundlichen, informativen Blogartikel auf Deutsch mit dem Titel '{topic}'. Der Text sollte ca. 300 Wörter lang sein und direkt die Kunden einer Matratzenmarke namens 'Schlaf Schön®' ansprechen."
        }]
    )
    return response.choices[0].message["content"].strip()

def post_to_shopify(title, content_html):
    url = f"https://{SHOPIFY_STORE}/admin/api/2023-07/blogs/{BLOG_ID}/articles.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    data = {
        "article": {
            "title": title,
            "body_html": content_html.replace("\n", "<br>")
        }
    }
    response = requests.post(url, headers=headers, json=data)
    print("Shopify response:", response.status_code)
    print(response.json())

if __name__ == "__main__":
    topic = generate_topic()
    content = generate_blog_content(topic)
    post_to_shopify(topic, content)
