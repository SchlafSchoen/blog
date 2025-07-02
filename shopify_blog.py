import os
import openai
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
BLOG_ID = os.getenv("BLOG_ID")

def generate_topic():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": "Erstelle einen kurzen, interessanten Blogartikel-Titel auf Deutsch für eine Matratzenmarke namens 'Schlaf Schön®'."
        }]
    )
    return response.choices[0].message["content"].strip()

def generate_blog_content(topic):
    prompt = f"""
Schreibe einen SEO-optimierten Blogartikel auf Deutsch zum Thema: '{topic}'.
Der Artikel soll mindestens 300 Wörter lang sein, relevante Keywords enthalten und gut strukturiert sein (mit Absätzen, Zwischenüberschriften).
Zielgruppe sind Menschen, die eine hochwertige Matratze kaufen möchten.
Der Artikel soll von der Matratzenmarke 'Schlaf Schön®' stammen und den Leser direkt ansprechen.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": prompt.strip()
        }]
    )
    return response.choices[0].message["content"].strip()

def generate_image(topic):
    response = openai.Image.create(
        prompt=f"{topic}, stilisiertes modernes Produktfoto für eine Matratzenmarke",
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']

def post_to_shopify(title, content_html, image_url):
    full_html = f'<img src="{image_url}" alt="{title}" style="max-width:100%; height:auto;"><br><br>{content_html.replace("\n", "<br>")}'
    url = f"https://{SHOPIFY_STORE}/admin/api/2023-07/blogs/{BLOG_ID}/articles.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    data = {
        "article": {
            "title": title,
            "body_html": full_html
        }
    }
    response = requests.post(url, headers=headers, json=data)
    print("Shopify response:", response.status_code)
    print(response.json())

if __name__ == "__main__":
    topic = generate_topic()
    content = generate_blog_content(topic)
    image_url = generate_image(topic)
    post_to_shopify(topic, content, image_url)
