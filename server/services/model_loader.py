import logging
import os
from pathlib import Path
import joblib

import torch
from gensim.models import Doc2Vec
import json
import os

from huggingface_hub import hf_hub_download, snapshot_download
from torch import nn

# Configure logger
logger = logging.getLogger(__name__)

from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_CACHE_DIR = os.getenv('MODEL_CACHE_DIR', 'hf_models')

class ModelLoader:
    def __init__(self):
        self.doc2vec_model = None
        self.neural_network = None
        self.nb_vectorizer = None
        self.nb_model = None
        self.bert_tokenizer = None
        self.bert_model = None

        self.nb_vectorizer_2 = None
        self.nb_model_2 = None
        logger.debug("ModelLoader initialized")

    def load_all_models(self):
        """Load all models at startup"""
        logger.info("Starting model loading process...")

        # Load Model 1: Naive Bayes
        self._load_naivebayes_model('theluantran/cefr-naive-bayes')

        # Load Model 2: Doc2Vec + Neural Network
        self._load_doc2vec_model('theluantran/cefr-doc2vec')

        # Load Model 3: BERT
        self._load_bert_model("theluantran/cefr-bert-classifier")

        logger.info("[OK] All models loaded successfully")

    def _load_naivebayes_model(self, model_id: str = "theluantran/cefr-naive-bayes"):
        """Load Naive Bayes model from HuggingFace Hub"""
        logger.debug(f"Loading Naive Bayes model from HuggingFace")

        current_dir = Path(__file__).resolve().parent
        root_dir = current_dir.parent

        try:
            # Define local directory for this model
            local_dir = os.path.join(root_dir, MODEL_CACHE_DIR, 'nb')
            model_path = os.path.join(local_dir, "model.pkl")
            vectorizer_path = os.path.join(local_dir, "vectorizer.pkl")


            logger.debug(f"Downloading Naive Bayes model to {local_dir}")
            snapshot_download(
                repo_id=model_id,
                local_dir=local_dir,
                local_dir_use_symlinks=False,
                ignore_patterns = [
                    "*.md",  # Skip README
                    ".gitattributes"  # Skip git files
                ]
            )
            logger.debug("Download complete")


            # Load model
            self.nb_model = joblib.load(model_path)
            logger.debug("Model loaded")

            # Load vectorizer
            self.nb_vectorizer = joblib.load(vectorizer_path)
            logger.debug("Vectorizer loaded")

            logger.info(f"[OK] Naive Bayes model downloaded successfully from https://huggingface.co/{model_id}")
        except Exception as e:
            logger.error(f"[ERROR] Error downloading Naive Bayes model: {e}")
            raise

        try:
            # Load model
            self.nb_model = joblib.load(model_path)
            logger.debug("Model loaded")

            # Load vectorizer
            self.nb_vectorizer = joblib.load(vectorizer_path)
            logger.debug("Vectorizer loaded")

            logger.info(f"[OK] Naive Bayes model loaded successfully")
        except Exception as e:
            logger.error(f"[ERROR] Error loading Naive Bayes model: {e}")
            raise


    def _load_doc2vec_model(self, model_id: str = "theluantran/cefr-doc2vec"):
        """Load Doc2Vec and PyTorch neural network"""
        logger.debug(f"Loading Doc2Vec model from HuggingFace")

        current_dir = Path(__file__).resolve().parent
        root_dir = current_dir.parent

        try:
            # Define local directory for this model
            local_dir = os.path.join(root_dir, MODEL_CACHE_DIR, 'doc2vec')
            doc2vec_model_path = os.path.join(local_dir, "doc2vec_model.bin")
            config_path = os.path.join(local_dir, "config.json")
            nn_weights_path = os.path.join(local_dir, "nn_weights.pth")


            logger.debug(f"Downloading Doc2Vec model to {local_dir}")
            snapshot_download(
                repo_id=model_id,
                local_dir=local_dir,
                local_dir_use_symlinks=False,
                allow_patterns=[
                    "doc2vec_model*",  # All doc2vec files
                    "*.json",  # Config files
                    "nn_weights.pth"  # Neural network weights
                ],
                ignore_patterns=[
                    "*.md",  # Skip README
                    ".gitattributes"  # Skip git files
                ]
            )
            logger.debug("Download complete")


            logger.info(f"[OK] Doc2Vec model downloaded successfully from https://huggingface.co/{model_id}")
        except Exception as e:
            logger.error(f"[ERROR] Error downloading Doc2Vec model: {e}")
            raise

        try:
            # Load Doc2Vec
            self.doc2vec_model = Doc2Vec.load(doc2vec_model_path)

            # Load config
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Reconstruct neural network
            self.neural_network = Doc2VecClassifier(
                embedding_dim=config['embedding_dim'],
                hidden_dim=config['hidden_dim'],
                num_classes=config['num_classes'],
                dropout=config['dropout_rate']
            )

            # Load weights
            self.neural_network.load_state_dict(
                torch.load(nn_weights_path)
            )
            self.neural_network.eval()

            logger.info(f"[OK] Doc2Vec model loaded successfully!")
        except Exception as e:
            logger.error(f"[ERROR] Error loading Doc2Vec model: {e}")
            raise

    def _load_bert_model(self, model_id: str = "theluantran/cefr-bert-classifier" ):
        logger.debug(f"Loading BERT model from HuggingFace {model_id}")
        current_dir = Path(__file__).resolve().parent
        root_dir = current_dir.parent
        local_dir = os.path.join(root_dir, MODEL_CACHE_DIR, 'bert')
        try:
            self.bert_tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                cache_dir=local_dir
            )
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(
                model_id,
                cache_dir = local_dir
            )
            self.bert_model.eval()  # Set to evaluation mode

            logger.info(f"[OK] BERT model loaded successfully")
        except Exception as e:
            logger.error(f"[ERROR] Error loading BERT model: {e}")
            raise


class Doc2VecClassifier(nn.Module):
    """Feedforward neural network for CEFR classification (5 classes)."""
    def __init__(self, embedding_dim, hidden_dim=128, num_classes=5, dropout=0.3):
        super().__init__()

        # Store config as attributes for later saving
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes
        self.dropout = dropout

        self.fc1 = nn.Linear(embedding_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, num_classes)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x
