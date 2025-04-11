from transformers import T5Tokenizer, T5ForConditionalGeneration
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load pre-trained T5 model and tokenizer
tokenizer = T5Tokenizer.from_pretrained("t5-small", legacy=True)
model = T5ForConditionalGeneration.from_pretrained("t5-small")

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment_label(summary):
    """
    Returns a sentiment label with emoji for a given text.
    """
    score = analyzer.polarity_scores(summary)
    compound = score['compound']

    if compound >= 0.05:
        return "📈 Sentiment: Positive"
    elif compound <= -0.05:
        return "🔻 Sentiment: Negative"
    else:
        return "⚖️ Sentiment: Neutral"

def summarize_text(text, max_length=60, min_length=20):
    """
    Summarizes the input text using T5 and adds sentiment analysis.
    :param text: The long text to be summarized
    :return: Dict with summary and sentiment
    """
    input_text = "summarize: " + text
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

    summary_ids = model.generate(input_ids, max_length=max_length, min_length=min_length, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    sentiment = get_sentiment_label(summary)

    return {
        "summary": summary,
        "sentiment": sentiment
    }

# Test the summarizer with sentiment
if __name__ == "__main__":
    long_text = """
    India won the final match of the Cricket World Cup after a thrilling contest against Australia.
    The game went down to the last over, where India successfully defended a total of 280 runs.
    This marks India's third World Cup victory, and celebrations erupted across the country.
    Fans across the globe congratulated the Indian team for their outstanding performance.
    """

    result = summarize_text(long_text)

    print("\n📝 Summarized News:\n")
    print(result["summary"])
    print("\n" + result["sentiment"])
