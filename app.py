from flask import Flask, render_template_string, request, send_file
import html
import io

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head><title>Mizzima XML Converter</title></head>
<body>
<h2>Mizzima XML Converter</h2>
<form method="post">
    Story ID: <input name="storyid"><br><br>
    Post Date (DD/MM/YYYY): <input name="postdate"><br><br>
    Headline: <input name="headline"><br><br>
    Category: <input name="category"><br><br>
    Author: <input name="author"><br><br>
    Source: <input name="source"><br><br>
    <textarea name="rawtext" rows="20" cols="100" placeholder="Paste article text here..."></textarea><br><br>
    <input type="submit" value="Convert and Download XML">
</form>
</body>
</html>
'''

def generate_xml(data):
    raw = html.escape(data['rawtext'], quote=False)
    raw = raw.replace("“", "&ldquo;").replace("”", "&rdquo;").replace("‘", "&lsquo;").replace("’", "&rsquo;")
    html_body = "<p>" + raw.replace("\n", "<br />") + "</p>"
    return f"""<article>

<storyid>{data['storyid']}</storyid>
<postdate>{data['postdate']}</postdate>
<headline>{data['headline']}</headline>
<source>{data['source']}</source>
<category>{data['category']}</category>
<author>{data['author']}</author>
<CONTENT><![CDATA[
{html_body}
]]>
</CONTENT>

</article>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        xml = generate_xml(request.form)
        return send_file(io.BytesIO(xml.encode('utf-8')), mimetype='text/xml',
                         as_attachment=True, download_name='article.xml')
    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
