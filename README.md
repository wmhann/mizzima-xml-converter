# mizzima-xml-converter
To convert the magazine file into xml format
# Mizzima XML Converter

This is a lightweight web tool that allows Mizzima editors and journalists to convert plain text articles into XML format used for weekly publishing.

## 🌐 Live App

Once deployed on Render, you can use it here:
`https://your-app-name.onrender.com`

## ✍️ Features

- Converts article text into HTML-wrapped XML
- Outputs `CDATA` format compatible with Mizzima publishing tools
- Dropdowns for category and author
- Clean, responsive UI
- Downloadable `.xml` file

## 📁 Files

- `app.py` — Flask web server
- `requirements.txt` — dependencies
- `README.md` — documentation

## 🚀 How to Deploy on Render

1. Create a free account on [https://render.com](https://render.com)
2. Connect this GitHub repo
3. Choose:
   - **Build Command**: *(leave blank)*
   - **Start Command**: `python app.py`
4. Click **"Deploy"**
