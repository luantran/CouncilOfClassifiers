import {useState} from 'react'
import './App.css'

const CLASSES = ['A1', 'A2', 'B1', 'B2', 'C1/C2']

function App() {
    const [text, setText] = useState('')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({text}),
            })

            if (!response.ok) {
                throw new Error('Prediction failed')
            }

            const data = await response.json()
            setResult(data)
        } catch (err) {
            setError(err.message || 'An error occurred while getting predictions')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="container">
            <header>
                <h1>Council of Classifiers</h1>
                <p className="subtitle">CEFR Text Classification Ensemble</p>
                <div className="app-description">
                    <p>
                        This tool classifies English text by proficiency level using the Common European Framework of Reference (CEFR).
                        Simply paste your text below and get predictions from three different machine learning models working together:
                    </p>
                    <ul>
                        <li><strong>Naive Bayes</strong> with TF-IDF features</li>
                        <li><strong>Doc2Vec</strong> with neural network classifier</li>
                        <li><strong>Fine-tuned RoBERTa</strong> transformer model</li>
                    </ul>
                    <p>
                        The ensemble combines all three predictions to give you both a <strong>majority vote</strong> result
                        and <strong>averaged probabilities</strong> across all CEFR levels (A1, A2, B1, B2, C1/C2).
                    </p>
                </div>
            </header>

            {/* Flash Messages */}
            {error && (
                <div className="alert alert-error">{error}</div>
            )}

            {/* Input Form */}
            <div className="input-section">
                <form onSubmit={handleSubmit}>
            <textarea
                  name="text"
                  rows="6"
                  placeholder="Enter your text here..."
                  required
                  value={text}
                  onChange={(e) => setText(e.target.value)}
            />
                    <button type="submit" disabled={loading}>
                        {loading ? 'Getting Prediction...' : 'Get Prediction'}
                    </button>
                </form>
            </div>

            {/* Results */}
            {result && (
                <div className="results">
                    {/* Ensemble Summary */}
                    <div className="result-card highlight">
                        <h2>Results</h2>
                        <div className="results-two-column">
                            {/* Majority Vote Column */}
                            <div className="ensemble-summary">
                                <h3>Majority Vote</h3>
                                <div className="result-item">
                                    <span className="label">Predicted Level</span>
                                    <span className="value">
                                        <span className="class-badge">
                                            {CLASSES[result.majority_vote]}
                                        </span>
                                    </span>
                                </div>
                                <div className="result-item">
                                    <span className="label">Confidence</span>
                                    <span className="value">
                                        {Math.round(result.confidence * 100)}%
                                    </span>
                                </div>
                                <div className="result-item">
                                    <span className="label">Agreement</span>
                                    <span className="value">
                                        {result.stats.agreement_count}/{result.stats.num_models} models
                                        {result.stats.all_agree && (
                                            <span className="agree-badge">✓ Unanimous</span>
                                        )}
                                    </span>
                                </div>
                            </div>

                            {/* Mean Probabilities Column */}
                            <div className="ensemble-summary">
                                <h3>Mean Probabilities</h3>
                                <div className="result-item">
                                    <span className="label">Predicted Level</span>
                                    <span className="value">
                                        <span className="class-badge">
                                            {CLASSES[result.mean_pred]}
                                        </span>
                                    </span>
                                </div>
                                <div className="result-item">
                                    <span className="label">Probability</span>
                                    <span className="value">
                                        {Math.round(result.mean_pred_proba * 100)}%
                                            <span
                                                className={`agree-badge ${
                                                    result.mean_pred_proba >= 0.90
                                                        ? "high"
                                                        : result.mean_pred_proba >= 0.70
                                                            ? "medium"
                                                            : "low"
                                                }`}
                                            >
                                                {result.mean_pred_proba >= 0.90
                                                    ? "High Confidence"
                                                    : result.mean_pred_proba >= 0.70
                                                        ? "Confident"
                                                        : "Low Confidence"}
                                            </span>
                                        </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Mean Probabilities */}
                    <div className="result-card">
                        <h3>Mean Probabilities</h3>
                        <div className="probability-bars">
                            {result.mean_probabilities.map((prob, idx) => (
                                <div key={idx} className="prob-row">
                                    <span className="prob-label">{CLASSES[idx]}</span>
                                    <div className="prob-bar-container">
                                        <div
                                            className="prob-bar"
                                            style={{width: `${prob * 100}%`}}
                                        />
                                        <span className="prob-value">
                      {(prob * 100).toFixed(1)}%
                    </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="result-card">
                        <h3>Individual Model Predictions</h3>
                        <div className="models-grid">
                            {Object.entries(result.predictions).map(([modelName, pred]) => (
                                <div key={modelName} className="model-card">
                                    <h4>{modelName.replace('model', 'Model ')}</h4>
                                    <div className="model-prediction">
                                        <span className="class-badge">{CLASSES[pred]}</span>
                                    </div>
                                    <div className="model-probs">
                                        {result.probabilities[modelName].map((prob, idx) => (
                                            <div key={idx} className="prob-row-indiv">
                                                <div className="prob-bar-container-indiv">
                                                    <span className="prob-label-indiv">{CLASSES[idx]}</span>
                                                    <div
                                                        className="prob-bar-indiv"
                                                        style={{width: `${prob * 100}%`}}
                                                    />
                                                    <span className="prob-value-indiv">
                                                        {(prob * 100).toFixed(1)}%
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default App