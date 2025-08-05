from flask import Flask, render_template_string, request, send_file
import html
import io

app = Flask(__name__)

CATEGORIES = [
    "Editorial", "Lead Story", "Core Developments",
    "On The Ground in Myanmar", "Analysis", "Business", "World"
]

AUTHORS = [
    "Mizzima Weekly", "Antonio Graceffo", "Mizzima Business Team", "Mizzima Correspondent"
]

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mizzima XML Converter</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        input, select, textarea { width: 100%%; padding: 10px; margin: 5px 0 15px; }
        textarea { height: 250px; }
        input[type=submit] { width: auto; background: green; color: white; border: none; padding: 12px 20px; cursor: pointer; }
        label { font-weight: bold; }
    </style>
</head>
<body>
    <h2>Mizzima XML Converter</h2>
    <form method="post">
        <label>Story ID:</label><input name="storyid" required>

        <label>Post Date (DD/MM/YYYY):</label><input name="postdate" required>

        <label>Headline:</label><input name="headline" required>

        <label>Category:</label>
        <select name="category">
            %s
        </select>

        <label>Author:</label>
        <select name="author">
            %s
        </select>

        <label>Source:</label><input name="source" value="Mizzima Weekly" required>

        <label>Raw Text:</label>
        <textarea name="rawtext" placeholder="Paste article here..." required></textarea>

        <input type="submit" value="Convert and Download XML">
    </form>
</body>
</html>
''' % (
    "\n".join([f'<option value="{c}">{c}</option>' for c in CATEGORIES]),
    "\n".join([f'<option value="{a}">{a}</option>' for a in AUTHORS])
)

def generate_xml(data):
    raw = html.escape(data['rawtext'], quote=False)
    raw = raw.replace("“", "&ldquo;").replace("”", "&rdquo;").replace("‘", "&lsquo;").replace("’", "&rsquo;")
    html_body = "<p>" + raw.replace("\n", "<br />") + "</p>"

    xml_output = (
        "<article>\n\n"
        f"<storyid>{data['storyid']}</storyid>\n"
        f"<postdate>{data['postdate']}</postdate>\n"
        f"<headline>{data['headline']}</headline>\n"
        f"<source>{data['source']}</source>\n"
        f"<category>{data['category']}</category>\n"
        f"<author>{data['author']}</author>\n"
        "<CONTENT><![CDATA[\n"
        f"{html_body}\n"
        "]]>\n</CONTENT>\n\n</article>\n"
    )

    return xml_output

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        xml = generate_xml(request.form)
        return send_file(io.BytesIO(xml.encode('utf-8')), mimetype='text/xml',
                         as_attachment=True, download_name='article.xml')
    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
