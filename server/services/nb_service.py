class NaiveBayesService:
    def __init__(self, model_loader):
        self.vectorizer = model_loader.nb_vectorizer
        self.model = model_loader.nb_model

    def predict(self, text):
        """Get prediction from Naive Bayes"""

        # 1. Vectorize text
        features = self.vectorizer.transform([text])

        # 2. Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]

        return {
            'prediction': int(prediction),
            'probabilities': probabilities.tolist()
        }