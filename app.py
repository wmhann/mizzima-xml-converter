from flask import Flask, render_template_string, request, jsonify, send_file
import html
import io
import re
from datetime import datetime

app = Flask(__name__)

# Helper function to handle smart characters
def replace_smart_characters(text):
    text = text.replace('—', '&mdash;')
    text = text.replace('–', '&ndash;')
    text = text.replace('…', '&hellip;')
    text = text.replace('’', '&rsquo;')
    text = text.replace('‘', '&lsquo;')
    text = text.replace('”', '&rdquo;')
    text = text.replace('“', '&ldquo;')
    return text

# New HTML form with a step-by-step UI
HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mizzima XML Converter</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 900px; margin: auto; padding: 20px; }
        .story-form { border: 1px solid #ccc; padding: 20px; margin-bottom: 20px; border-radius: 8px; }
        .story-form h4 { border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], textarea, select { 
        width: 100%; 
        padding: 8px; 
        box-sizing: border-box; 
        border: 1px solid #ccc; 
        border-radius: 4px; 
        }
        input[type="date"] {
        width: 250px; 
        padding: 8px; 
        box-sizing: border-box; 
        border: 1px solid #ccc; 
        border-radius: 4px; 
        }
        textarea { height: 150px; }
        .btn { padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; color: white; transition: background-color 0.2s ease, transform 0.12s ease; }
        .btn-primary { background-color: #007bff; }
        .btn-secondary { background-color: #6c757d; }
        .btn-success { background-color: #28a745; }
        .btn-danger { background-color: #dc3545; }

        /* Hover states for buttons (anchors with .btn class will be affected too) */
        .btn:hover,
        button.btn:hover,
        a.btn:hover {
            transform: translateY(-2px);
            filter: brightness(0.95);
        }

        .btn-primary:hover { background-color: #005f95; }
        .btn-secondary:hover { background-color: #5a6268; }
        .btn-success:hover { background-color: #218838; }
        .btn-danger:hover { background-color: #c82333; }
        .xml-preview { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 4px; margin-top: 20px; white-space: pre-wrap; word-wrap: break-word; }
        #buttons-container button { margin-right: 10px; }
        #filename-group { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Mizzima XML Converter - Developed by Wai Min Han</h2>
        
        <div id="stories-container">
            </div>

        <div id="buttons-container">
            <button id="add-story-btn" class="btn btn-primary">Add New Story</button>
            <button id="start-over-btn" class="btn btn-danger">Start Over</button>
        </div>

        <div id="filename-group" class="form-group" style="display:none;">
            <label for="filename">Filename for Download:</label>
            <input type="text" id="filename" name="filename" value="mizzima_articles" required>
        </div>

        <div id="output-buttons-container" style="display:none; margin-top: 20px;">
            <button id="preview-btn" class="btn btn-secondary">Preview XML</button>
            <button id="download-btn" class="btn btn-success">Download XML</button>
        </div>

        <div id="xml-preview-container" class="xml-preview" style="display:none;">
            <h4>XML Output Preview</h4>
            <pre id="xml-output"></pre>
        </div>
    </div>

    <script>
        const storyFormTemplate = (storyCount) => `
            <div class="story-form" id="story-${storyCount}">
                <h4>Story #${storyCount}</h4>
                <div class="form-group">
                    <label for="headline-${storyCount}">Headline:</label>
                    <input type="text" id="headline-${storyCount}" name="headline-${storyCount}" required>
                </div>
                <div class="form-group">
                    <label for="postdate-${storyCount}">Post Date:</label>
                    <input type="date" id="postdate-${storyCount}" name="postdate-${storyCount}" required>
                </div>
                <div class="form-group">
                    <label for="category-${storyCount}">Category:</label>
                    <input list="categories" id="category-${storyCount}" name="category-${storyCount}" value="" required>
                    <datalist id="categories">
                        <option value="Editorial">
                        <option value="Lead Story">
                        <option value="Core Developments">
                        <option value="Analysis">
                        <option value="Business">
                        <option value="On The Ground in Myanmar">
                        <option value="International Affairs">
                        <option value="Podcast">
                        <option value="Junta Watch">
                        <option value="Social Watch">
                        <option value="Myanmar News">
                        <option value="International News">
                    </datalist>
                </div>
                <div class="form-group">
                    <label for="author-${storyCount}">Author:</label>
                    <input list="authors" id="author-${storyCount}" name="author-${storyCount}" value="Mizzima Weekly" required>
                    <datalist id="authors">
                        <option value="Mizzima Weekly">
                        <option value="Insight Myanmar">
                        <option value="Mizzima News">
                    </datalist>
                </div>
                <div class="form-group">
                    <label for="source-${storyCount}">Source:</label>
                    <input list="sources" id="source-${storyCount}" name="source-${storyCount}" value="Mizzima Weekly" required>
                    <datalist id="sources">
                        <option value="Mizzima Weekly">
                        <option value="Mizzima News">
                    </datalist>
                </div>
                <div class="form-group">
                    <label for="content-${storyCount}">Content:</label>
                    <textarea id="content-${storyCount}" name="content-${storyCount}" required></textarea>
                </div>
            </div>
        `;

        let storyCount = 0;

        function addStoryForm() {
            storyCount++;
            const container = document.getElementById('stories-container');
            container.insertAdjacentHTML('beforeend', storyFormTemplate(storyCount));
            
            // Show the filename and output buttons after the first story is added
            document.getElementById('filename-group').style.display = 'block';
            document.getElementById('output-buttons-container').style.display = 'block';
            if (storyCount > 1) {
            const firstStoryDate = document.getElementById('postdate-1').value;
        
        if (firstStoryDate) {
            document.getElementById(`postdate-${storyCount}`).value = firstStoryDate;
            }
        }
    }
        function collectFormData() {
            const stories = [];
            for (let i = 1; i <= storyCount; i++) {
                const headline = document.getElementById(`headline-${i}`).value;
                const postdate = document.getElementById(`postdate-${i}`).value;
                const category = document.getElementById(`category-${i}`).value;
                const author = document.getElementById(`author-${i}`).value;
                const source = document.getElementById(`source-${i}`).value;
                const content = document.getElementById(`content-${i}`).value;

                if (headline && postdate && category && author && source && content) {
                    stories.push({ headline, postdate, category, author, source, content });
                }
            }
            return stories;
        }

        async function handlePreview() {
            const stories = collectFormData();
            if (stories.length === 0) {
                alert('Please fill in at least one story.');
                return;
            }

            try {
                const response = await fetch('/api/preview', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ stories })
                });

                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('xml-output').textContent = data.xml_output;
                    document.getElementById('xml-preview-container').style.display = 'block';
                } else {
                    const errorData = await response.json();
                    alert('Error: ' + errorData.error);
                }
            } catch (error) {
                console.error('Fetch error:', error);
                alert('An error occurred. Please check the console for details.');
            }
        }

        async function handleDownload() {
            const stories = collectFormData();
            if (stories.length === 0) {
                alert('Please fill in at least one story.');
                return;
            }

            const filename = document.getElementById('filename').value || 'mizzima_articles';
            const fullFilename = filename.endsWith('.xml') ? filename : `${filename}.xml`;

            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ stories, filename: fullFilename })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = fullFilename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    const errorData = await response.json();
                    alert('Error: ' + errorData.error);
                }
            } catch (error) {
                console.error('Fetch error:', error);
                alert('An error occurred. Please check the console for details.');
            }
        }
        
        function handleStartOver() {
            if (confirm('Are you sure you want to start over? All entered data will be lost.')) {
                storyCount = 0;
                document.getElementById('stories-container').innerHTML = '';
                document.getElementById('xml-preview-container').style.display = 'none';
                document.getElementById('filename-group').style.display = 'none';
                document.getElementById('output-buttons-container').style.display = 'none';
                document.getElementById('filename').value = 'mizzima_articles';
                addStoryForm();
            }
        }

        window.onload = function() {
            handleStartOver(); // Start with one form on page load
            document.getElementById('add-story-btn').addEventListener('click', addStoryForm);
            document.getElementById('start-over-btn').addEventListener('click', handleStartOver);
            document.getElementById('preview-btn').addEventListener('click', handlePreview);
            document.getElementById('download-btn').addEventListener('click', handleDownload);
        };
    </script>
</body>
</html>
'''

def generate_full_xml(stories_data):
    """
    Generates a single XML file from a list of story data.
    """
    articles_xml = []
    
    for i, story in enumerate(stories_data):
        try:
            # Reformat the date from YYYY-MM-DD to DD/MM/YYYY
            postdate_obj = datetime.strptime(story['postdate'], '%Y-%m-%d')
            formatted_postdate = postdate_obj.strftime('%d/%m/%Y')
        except ValueError:
            # Handle invalid date format if necessary
            formatted_postdate = story['postdate']

        headline = story['headline']
        category = story['category']
        author = story['author']
        source = story['source']
        content = story['content']
        
        # Split content into paragraphs and wrap with <p> tags
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        html_body = ""

        for p in paragraphs:
            # Handle line breaks within paragraphs
            p_cleaned = p.replace('\n', ' ')
            p_final = replace_smart_characters(p_cleaned)
            html_body += f"<p>{html.escape(p_final)}</p>\n"

        # Build the XML for this single story
        single_article_xml = (
            f"<storyid>{i + 1}</storyid>\n"
            f"<postdate>{html.escape(formatted_postdate)}</postdate>\n"
            f"<headline>{html.escape(headline)}</headline>\n"
            f"<source>{html.escape(source)}</source>\n"
            f"<category>{html.escape(category)}</category>\n"
            f"<author>{html.escape(author)}</author>\n"
            f"<CONTENT><![CDATA[\n{html_body}]]></CONTENT>"
        )
        articles_xml.append(single_article_xml)

    full_xml_output = "<article>\n" + "\n\n".join(articles_xml) + "\n</article>"
    return full_xml_output

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_FORM)

@app.route('/api/preview', methods=['POST'])
def preview_xml():
    data = request.json
    if not data or 'stories' not in data:
        return jsonify({'error': 'Invalid request body'}), 400
    
    xml = generate_full_xml(data['stories'])
    return jsonify({'xml_output': xml})

@app.route('/api/download', methods=['POST'])
def download_xml():
    data = request.json
    if not data or 'stories' not in data or 'filename' not in data:
        return jsonify({'error': 'Invalid request body'}), 400
        
    xml = generate_full_xml(data['stories'])
    filename = data['filename']
    return send_file(io.BytesIO(xml.encode('utf-8')), mimetype='text/xml',
                     as_attachment=True, download_name=filename)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
