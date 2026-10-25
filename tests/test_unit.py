import pytest
from app.model import SentimentClassifier

def test_sentiment_positive():
    clf = SentimentClassifier()
    res = clf.predict("The product is amazing and fast!")
    assert res["sentiment"] == "positive"
    assert res["confidence"] > 0.8

def test_sentiment_negative():
    clf = SentimentClassifier()
    res = clf.predict("This item is broken and terrible.")
    assert res["sentiment"] == "negative"
    assert res["confidence"] > 0.8

def test_sentiment_empty():
    clf = SentimentClassifier()
    with pytest.raises(ValueError):
        clf.predict("   ")
