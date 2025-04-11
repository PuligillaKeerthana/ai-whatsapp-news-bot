# 📰 AI WhatsApp News Bot

An AI-powered WhatsApp bot that delivers summarized real-time news using T5 (Hugging Face), VADER, and Green API.

## 🔧 Tools Used
- Python, Flask, Hugging Face (T5)
- Green API (WhatsApp)
- VADER Sentiment Analysis
- APScheduler

## 📷 Demo Screenshot

![image](https://github.com/user-attachments/assets/d287e76e-7b7e-49ba-aa98-1b46181d1111)
![image](https://github.com/user-attachments/assets/3de612f3-d20d-4152-b36b-04ac6212dd6b)
![image](https://github.com/user-attachments/assets/f10520e1-1935-448b-85c1-7e1a94dae20d)

## 📁 Files
- `app.py` → Flask app
- `news_fetcher.py` → Fetches & cleans news
- `summarizer.py` → Summarizes text
- `requirements.txt` → List of libraries

## 📦 How to Run
1. `python -m venv venv`
2. `venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python app.py`
