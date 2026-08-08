# Neural Machine Translation using Seq2Seq LSTM

## Project Introduction
This is a complete Flask-based Mini Project demonstrating Neural Machine Translation (NMT) using a Sequence-to-Sequence (Encoder-Decoder LSTM) model in TensorFlow/Keras. It translates simple English sentences into French.

## Features
- **Encoder-Decoder Architecture:** Implemented using TensorFlow/Keras.
- **Web Interface:** Modern, minimalistic, light-themed UI built with Flask, HTML5, CSS3, and JavaScript.
- **Real-time Translation:** AJAX-based predictions displaying translation time and handling unknown words gracefully.
- **Lightweight Dataset:** Comes with a pre-configured 4-sentence toy dataset for instant local training.

## Folder Structure
```text
Neural_Translator/
├── app.py
├── train_model.py
├── translator.py
├── requirements.txt
├── README.md
├── model/
│   ├── seq2seq_model.keras
│   ├── english_vocab.pkl
│   ├── french_vocab.pkl
│   ├── reverse_french_vocab.pkl
│   └── max_len.pkl
├── templates/
│   ├── index.html
│   └── about.html
├── static/
│   ├── css/
│   │     style.css
│   ├── js/
│   │     script.js
│   └── images/
│         logo.png
└── dataset/
      dataset.py
```

## Installation

1. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the Model:**
   ```bash
   python train_model.py
   ```
   *(This takes only a few seconds and generates the `.keras` and `.pkl` files in the `model/` folder.)*

4. **Run the Flask App:**
   ```bash
   python app.py
   ```

5. **Open Browser:**
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Screenshots
*(Add your screenshots here)*

## Future Scope
- Train on a much larger corpus (e.g., Europarl or WMT) for realistic translations.
- Implement Attention Mechanism for better long-sentence translation.
- Use pre-trained embeddings (Word2Vec, GloVe).
