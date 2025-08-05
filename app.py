from flask import Flask, render_template_string, request, send_file
import html
import io
import re

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mizzima XML Converter</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        textarea { width: 100%; padding: 10px; margin: 5px 0 15px; height: 400px; }
        input[type=submit] { width: auto; background: green; color: white; border: none; padding: 12px 20px; cursor: pointer; }
        label { font-weight: bold; }
        .instructions { background-color: #f0f0f0; padding: 15px; border-left: 5px solid #007bff; margin-bottom: 20px; }
        pre { background-color: #e9ecef; padding: 10px; white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <h2>Mizzima XML Converter - Multiple Articles</h2>
    <div class="instructions">
        <p><strong>အသုံးပြုပုံ:</strong></p>
        <p>အောက်ပါပုံစံအတိုင်း article အများကြီးကို တစ်ပြိုင်နက်တည်း ထည့်သွင်းနိုင်ပါသည်။</p>
        <pre>
### Headline of First Story
## Post Date: DD/MM/YYYY
## Category: Editorial
## Author: Mizzima Weekly
## Source: Mizzima Weekly

Your first story's content goes here. It can have multiple paragraphs.

### Headline of Second Story
## Post Date: DD/MM/YYYY
## Category: Lead Story
## Author: Antonio Graceffo
## Source: Mizzima Weekly

Your second story's content goes here.
        </pre>
        <p><strong>Note:</strong> `###` သည် story အသစ်တစ်ခုကို စတင်ခြင်းဖြစ်ပြီး၊ `##` သည် metadata ကို သတ်မှတ်ခြင်း ဖြစ်သည်။</p>
    </div>
    <form method="post">
        <label>Raw Text:</label>
        <textarea name="rawtext" placeholder="Paste all articles here..." required></textarea>
        <input type="submit" value="Convert and Download XML File">
    </form>
</body>
</html>
'''

def generate_full_xml(rawtext):
    stories_text = re.split(r'\n###\s', rawtext.strip())
    articles_xml = []

    for i, story_text in enumerate(stories_text):
        story_id = i + 1

        # Updated regex to correctly parse your input format
        match = re.search(r'^(.*?)\n##\sPost Date:\s(.*?)\n##\sCategory:\s(.*?)\n##\sAuthor:\s(.*?)\n##\sSource:\s(.*?)\n(.*)', story_text, re.DOTALL)

        if not match:
            print(f"Skipping story {story_id} due to invalid format.")
            continue

        headline, postdate, category, author, source, content = match.groups()

        clean_content = html.escape(content.strip(), quote=False)
        clean_content = clean_content.replace("“", "&ldquo;").replace("”", "&rdquo;").replace("‘", "&lsquo;").replace("’", "&rsquo;")
        
        # Corrected logic to use <p> tags and remove single newlines
        html_body = "<p>" + clean_content.replace("\n\n", "</p><p>").replace("\n", " ") + "</p>"

        single_article_xml = (
            f"\n<storyid>{story_id}</storyid>\n"
            f"<postdate>{postdate.strip()}</postdate>\n"
            f"<headline>{headline.strip()}</headline>\n"
            f"<source>{source.strip()}</source>\n"
            f"<category>{category.strip()}</category>\n"
            f"<author>{author.strip()}</author>\n"
            "<CONTENT><![CDATA[\n"
            f"{html_body}\n"
            "]]>\n</CONTENT>\n"
        )
        articles_xml.append(single_article_xml)

    full_xml_output = "<article>\n" + "\n".join(articles_xml) + "\n</article>"
    return full_xml_output

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        rawtext = request.form.get('rawtext')
        if rawtext:
            xml = generate_full_xml(rawtext)
            return send_file(io.BytesIO(xml.encode('utf-8')), mimetype='text/xml',
                             as_attachment=True, download_name='mizzima_articles.xml')
    return render_template_string(HTML_FORM)
