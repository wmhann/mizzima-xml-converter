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
    """
    Parses the raw text and generates a properly formatted XML string with <p> tags.
    """
    pattern = re.compile(
        r"### (.+?)\n"
        r"## Post Date: (.+?)\n"
        r"## Category: (.+?)\n"
        r"## Author: (.+?)\n"
        r"## Source: (.+?)\n\n"
        r"(.+)",
        re.DOTALL
    )
    
    match = re.search(pattern, rawtext)
    
    if not match:
        return "Invalid input format."

    # Correctly extract and clean data
    headline_raw, postdate, category, author, source, content = match.groups()

    # The content text might have a mix of \n and \r\n line endings. We normalize it to \n.
    normalized_content = content.replace('\r\n', '\n')
    
    # Split content by double newlines to get separate paragraphs
    paragraphs = [p.strip() for p in normalized_content.split('\n\n') if p.strip()]

    # Format the paragraphs with <p> tags
    html_body = ""
    for paragraph in paragraphs:
        # Replace single newlines within a paragraph with a space to keep it as one block of text
        clean_paragraph = paragraph.replace('\n', ' ')
        html_body += f"<p>{html.escape(clean_paragraph)}</p>\n"

    # Assemble the final XML output
    full_xml_output = (
        f'<storyid>1</storyid>\n'
        f'<postdate>{html.escape(postdate)}</postdate>\n'
        f'<headline>{html.escape(headline_raw)}</headline>\n'
        f'<source>{html.escape(source)}</source>\n'
        f'<category>{html.escape(category)}</category>\n'
        f'<author>{html.escape(author)}</author>\n'
        f'<CONTENT><![CDATA[\n{html_body}]]></CONTENT>'
    )
    
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
