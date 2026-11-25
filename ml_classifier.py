"""Small illustrative scikit-learn text classifier for issue-category prediction."""
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class IssueClassifier:
    def __init__(self):
        self.ready = False
        if SKLEARN_AVAILABLE:
            samples = [
                ("line exceeds character limit style formatting", "Style"),
                ("trailing spaces whitespace formatting", "Style"),
                ("unused import module imported not used", "Style"),
                ("function missing docstring documentation", "Documentation"),
                ("class missing documentation docstring", "Documentation"),
                ("function too long many lines maintainability", "Maintainability"),
                ("too many parameters function arguments", "Maintainability"),
                ("deep nested conditions complexity", "Maintainability"),
                ("duplicate repeated code", "Maintainability"),
                ("empty except block exception handling", "Error Handling"),
                ("bare except catches all errors", "Error Handling"),
                ("function name should snake case naming", "Naming"),
                ("class name should pascal case naming", "Naming"),
            ]
            x, y = zip(*samples)
            self.vectorizer = TfidfVectorizer()
            self.model = MultinomialNB()
            self.model.fit(self.vectorizer.fit_transform(x), y)
            self.ready = True

    def predict(self, text):
        if not self.ready:
            return "Rule-based"
        return str(self.model.predict(self.vectorizer.transform([text]))[0])
