import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Embedding
from dataset.dataset import data

# Ensure model directory exists
if not os.path.exists('model'):
    os.makedirs('model')

# 1. Preprocess data
eng_sentences = []
fre_sentences = []

for eng, fre in data:
    eng_sentences.append(eng.lower().split())
    # Add start and end tokens to French sentences
    fre_sentences.append(['<START>'] + fre.lower().split() + ['<END>'])

# 2. Build Vocabulary
eng_vocab = set()
fre_vocab = set()

for eng in eng_sentences:
    eng_vocab.update(eng)
for fre in fre_sentences:
    fre_vocab.update(fre)

eng_vocab = ['<PAD>'] + list(eng_vocab)
fre_vocab = ['<PAD>'] + list(fre_vocab)

# Create mapping dictionaries
eng_word2idx = {word: idx for idx, word in enumerate(eng_vocab)}
fre_word2idx = {word: idx for idx, word in enumerate(fre_vocab)}
fre_idx2word = {idx: word for idx, word in enumerate(fre_vocab)}

# Determine maximum sequence lengths
max_eng_len = max([len(seq) for seq in eng_sentences])
max_fre_len = max([len(seq) for seq in fre_sentences])

print(f"English Vocab Size: {len(eng_vocab)}")
print(f"French Vocab Size: {len(fre_vocab)}")
print(f"Max English Length: {max_eng_len}")
print(f"Max French Length: {max_fre_len}")

# 3. Convert sentences to sequences and pad them
num_samples = len(data)

# Encoder input data
encoder_input_data = np.zeros((num_samples, max_eng_len), dtype='float32')
# Decoder input data (teacher forcing)
decoder_input_data = np.zeros((num_samples, max_fre_len), dtype='float32')
# Decoder target data (shifted by one)
decoder_target_data = np.zeros((num_samples, max_fre_len, len(fre_vocab)), dtype='float32')

for i, (eng, fre) in enumerate(zip(eng_sentences, fre_sentences)):
    for t, word in enumerate(eng):
        encoder_input_data[i, t] = eng_word2idx[word]
        
    for t, word in enumerate(fre):
        decoder_input_data[i, t] = fre_word2idx[word]
        # decoder target is ahead by one timestep and one-hot encoded
        if t > 0:
            decoder_target_data[i, t - 1, fre_word2idx[word]] = 1.0

# 4. Build Seq2Seq Model

latent_dim = 256
embedding_dim = 100

# ENCODER
encoder_inputs = Input(shape=(None,), name='encoder_inputs')
encoder_embedding = Embedding(len(eng_vocab), embedding_dim, name='encoder_embedding')(encoder_inputs)
encoder_lstm = LSTM(latent_dim, return_state=True, name='encoder_lstm')
encoder_outputs, state_h, state_c = encoder_lstm(encoder_embedding)
encoder_states = [state_h, state_c]

# DECODER
decoder_inputs = Input(shape=(None,), name='decoder_inputs')
decoder_embedding = Embedding(len(fre_vocab), embedding_dim, name='decoder_embedding')
decoder_embedding_outputs = decoder_embedding(decoder_inputs)
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True, name='decoder_lstm')
decoder_outputs, _, _ = decoder_lstm(decoder_embedding_outputs, initial_state=encoder_states)
decoder_dense = Dense(len(fre_vocab), activation='softmax', name='decoder_dense')
decoder_outputs = decoder_dense(decoder_outputs)

# Define Model
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

# 5. Compile and Train Model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("Training model...")
model.fit(
    [encoder_input_data, decoder_input_data],
    decoder_target_data,
    batch_size=2,
    epochs=150
)
print("Training completed.")

# 6. Save the model and vocabularies
model.save('model/seq2seq_model.keras')

with open('model/english_vocab.pkl', 'wb') as f:
    pickle.dump(eng_word2idx, f)
    
with open('model/french_vocab.pkl', 'wb') as f:
    pickle.dump(fre_word2idx, f)
    
with open('model/reverse_french_vocab.pkl', 'wb') as f:
    pickle.dump(fre_idx2word, f)

with open('model/max_len.pkl', 'wb') as f:
    pickle.dump((max_eng_len, max_fre_len), f)

print("Model and vocabularies saved successfully to model/ folder.")
