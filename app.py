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
        .instructions-toggle { margin-bottom: 20px; }
        #instructions-content { background-color: #f0f0f0; padding: 15px; border-left: 5px solid #007bff; margin-bottom: 20px; }
        pre { background-color: #e9ecef; padding: 10px; white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <h2>Mizzima XML Converter - Multiple Articles</h2>
    
    <div class="instructions-toggle">
        <button class="btn btn-secondary" onclick="toggleInstructions()">အသုံးပြုပုံ</button>
    </div>

    <div id="instructions-content" style="display:none;">
        <h5 class="mt-3">သတိပြုရန်အချက်များ</h5>
        <ul>
            <li>Story အသစ်တစ်ခု စတင်ရန် <code>###</code> ဖြင့် Headline ကို စတင်ပါ။</li>
            <li>Metadata (<code>Post Date</code>, <code>Category</code>, <code>Author</code>, <code>Source</code>) တို့ကို <code>##</code> ဖြင့် စတင်ပါ။</li>
            <li>Metadata နှင့် Content ကြားတွင် လိုင်းအလွတ် (Enter နှစ်ချက်) တစ်ကြောင်း ခြားပါ။</li>
            <li>Content အတွင်း စာပိုဒ်ခွဲရန် လိုင်းအလွတ် (Enter နှစ်ချက်) တစ်ကြောင်း ခြားပါ။</li>
            <li><code>###</code> သို့မဟုတ် <code>##</code> ကို စာသားထဲတွင် အလွဲသုံးစားမပြုလုပ်ပါနှင့်။</li>
        </ul>
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
    </div>

    <form method="post">
        <label>Raw Text:</label>
        <textarea name="rawtext" placeholder="Paste all articles here..." required></textarea>
        <input type="submit" value="Convert and Download XML File">
    </form>

    <script>
        function toggleInstructions() {
            var content = document.getElementById("instructions-content");
            if (content.style.display === "none") {
                content.style.display = "block";
            } else {
                content.style.display = "none";
            }
        }
    </script>

</body>
</html>
'''

# This helper function must be defined outside of the main function
def replace_smart_characters(text):
    text = text.replace('—', '&mdash;')  # Em dash
    text = text.replace('–', '&ndash;')  # En dash
    text = text.replace('…', '&hellip;') # Ellipsis
    text = text.replace('’', '&rsquo;')  # Smart single quote
    text = text.replace('‘', '&lsquo;')  # Smart single quote
    text = text.replace('”', '&rdquo;')  # Smart double quote
    text = text.replace('“', '&ldquo;')  # Smart double quote
    return text

def generate_full_xml(rawtext):
    """
    Parses multiple stories from raw text and generates a single XML file.
    """
    articles_xml = []
    
    # Normalize line endings to be consistent (e.g., from \r\n to \n)
    normalized_text = rawtext.replace('\r\n', '\n')
    
    # Split the text by '###' to get individual stories
    stories = re.split(r'\n###\s', normalized_text)
    
    # Pattern to find metadata and content within each story
    story_pattern = re.compile(
        r"## Post Date: (.+?)\n"
        r"## Category: (.+?)\n"
        r"## Author: (.+?)\n"
        r"## Source: (.+?)\n\n"
        r"(.+)", 
        re.DOTALL
    )

    for i, story_text in enumerate(stories):
        if not story_text.strip():
            continue  # Skip any empty parts from the split

        # The first line is the headline
        headline_and_rest = story_text.split('\n', 1)
        
        if len(headline_and_rest) < 2:
            continue # Skip if no content after headline

        headline = headline_and_rest[0].strip()
        rest_of_story = headline_and_rest[1].strip()

        match = re.search(story_pattern, rest_of_story)

        if not match:
            print(f"Skipping story {i+1} due to invalid format.")
            continue

        # Extract data from the matched groups
        postdate, category, author, source, content = match.groups()

        # Split content into paragraphs and wrap with <p> tags
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        html_body = ""

        for p in paragraphs:
            p_cleaned = p.replace('\n', ' ')
            p_final = replace_smart_characters(p_cleaned)
            html_body += f"<p>{html.escape(p_final)}</p>\n"

        # Build the XML for this single story
        single_article_xml = (
            f"<storyid>{i + 1}</storyid>\n"
            f"<postdate>{html.escape(postdate)}</postdate>\n"
            f"<headline>{html.escape(headline)}</headline>\n"
            f"<source>{html.escape(source)}</source>\n"
            f"<category>{html.escape(category)}</category>\n"
            f"<author>{html.escape(author)}</author>\n"
            f"<CONTENT><![CDATA[\n{html_body}]]></CONTENT>"
        )
        articles_xml.append(single_article_xml)

    full_xml_output = "<article>\n" + "\n\n".join(articles_xml) + "\n</article>"
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
