import numpy as np
import torch


class Doc2VecService:
    def __init__(self, model_loader):
        self.doc2vec_model = model_loader.doc2vec_model
        self.neural_network = model_loader.neural_network

    def predict(self, text):
        """Get prediction from Doc2Vec"""
        # Generate document embedding
        vector = self.doc2vec_model.infer_vector(text.split())

        # Convert to tensor and predict
        with torch.no_grad():
            tensor = torch.FloatTensor(vector).unsqueeze(0)
            output = self.neural_network(tensor)
            probabilities = torch.softmax(output, dim=1)

        # Convert to numpy
        probs_array = probabilities.numpy()[0]
        predicted_class = int(np.argmax(probs_array))

        return {
            'probabilities': probs_array.tolist(),
            'prediction': predicted_class,
        }