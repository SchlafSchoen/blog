import os
import openai
import requests
import re

openai.api_key = os.getenv("OPENAI_API_KEY")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
BLOG_ID = os.getenv("BLOG_ID")

def clean_title(title):
    return re.sub(r'^"|"$', '', title.strip())

def generate_topic():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": (
                "Du bist ein SEO-Experte und Content-Prompt-Ingenieur. Erstelle einen monatlich planbaren, SEO-freundlichen Blog-Titel "
                "auf Deutsch zum Thema Schlaf, Matratzen, Schlafhygiene oder Erholung. Vermeide direkte Werbung. Ziel ist ein Blogartikel, "
                "der bei Google gut gelistet wird. Verwende keine Anführungszeichen im Titel."
            )
        }]
    )
    return clean_title(response.choices[0].message["content"].strip())

def generate_faq(topic):
    faq_prompt = f"Du bist ein SEO-Texter. Erstelle 5 häufig gestellte Fragen mit kurzen prägnanten Antworten zum Thema '{topic}'."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": faq_prompt }]
    )
    return response.choices[0].message["content"].strip()

def generate_blog_content(topic):
    prompt = (
        f"Du bist ein professioneller SEO-Texter mit Fokus auf organische Sichtbarkeit. "
        f"Schreibe einen strukturierten Blogartikel auf Deutsch über folgendes Thema: {topic}.\n"
        "Verwende <h1> für den Haupttitel, <h2> für Zwischenüberschriften, nutze klare Absätze. "
        "Integriere relevante Keywords für Google-Indexierung. Erwähne die Marke 'Schlaf Schön®' nur einmal und subtil, "
        "ohne Werbung. Der Artikel soll mindestens 400 Wörter umfassen. Zielgruppe sind Menschen mit Schlafproblemen "
        "oder dem Wunsch nach besserer Schlafqualität."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": prompt }]
    )
    return response.choices[0].message["content"].strip()

def generate_tags(topic):
    tag_prompt = f"Erstelle 3 passende SEO-Tags auf Deutsch für das Thema '{topic}', ohne Hashtags oder Anführungszeichen."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": tag_prompt }]
    )
    tags = response.choices[0].message["content"].strip().split("\n")
    return [tag.strip() for tag in tags if tag.strip()]

def generate_image(topic):
    image_prompt = f"{topic}. Symbolische Darstellung: schlafendes Kind, ruhige Stimmung, wenig sichtbare Matratze, keine Marke. Minimalistisch, natürliches Licht."
    response = openai.Image.create(
        prompt=image_prompt,
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']

def post_to_shopify(title, content_html, image_url, tags):
    faq = generate_faq(title)
    faq_html = '<h2>Häufige Fragen</h2><ul>' + ''.join(f'<li>{line}</li>' for line in faq.split("\n") if line.strip()) + '</ul>'
    converted_content = content_html.replace("\n", "<br>")
    full_html = f'<img src="{image_url}" alt="{title}" style="max-width:100%; height:auto;"><br><br>{converted_content}<br><br>{faq_html}'

    url = f"https://{SHOPIFY_STORE}/admin/api/2023-07/blogs/{BLOG_ID}/articles.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    data = {
        "article": {
            "title": title,
            "body_html": full_html,
            "tags": ', '.join(tags),
            "image": {
                "src": image_url,
                "alt": title
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    print("Shopify response:", response.status_code)
    print(response.json())

if __name__ == "__main__":
    topic = generate_topic()
    content = generate_blog_content(topic)
    image_url = generate_image(topic)
    tags = generate_tags(topic)
    post_to_shopify(topic, content, image_url, tags)
