import os
import time
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Input

print("Loading trained model and vocabularies...")

MODEL_PATH = 'model/seq2seq_model.keras'

# Ensure model exists
if not os.path.exists(MODEL_PATH):
    print("Model not found! Please run 'python train_model.py' first.")
    # Initialize empty variables to prevent import errors before training
    model = None
    eng_word2idx = {}
    fre_word2idx = {}
    fre_idx2word = {}
    max_eng_len, max_fre_len = 0, 0
    encoder_model = None
    decoder_model = None
else:
    # Load entire model
    model = load_model(MODEL_PATH)
    
    # Load vocabularies
    with open('model/english_vocab.pkl', 'rb') as f:
        eng_word2idx = pickle.load(f)
    with open('model/french_vocab.pkl', 'rb') as f:
        fre_word2idx = pickle.load(f)
    with open('model/reverse_french_vocab.pkl', 'rb') as f:
        fre_idx2word = pickle.load(f)
    with open('model/max_len.pkl', 'rb') as f:
        max_eng_len, max_fre_len = pickle.load(f)
        
    # Build Inference Models
    
    # Encoder Model
    encoder_inputs = model.input[0]
    encoder_lstm = model.get_layer('encoder_lstm')
    _, state_h_enc, state_c_enc = encoder_lstm.output
    encoder_states = [state_h_enc, state_c_enc]
    encoder_model = Model(encoder_inputs, encoder_states)
    
    # Decoder Model
    decoder_inputs = model.input[1]
    decoder_state_input_h = Input(shape=(256,), name='input_h')
    decoder_state_input_c = Input(shape=(256,), name='input_c')
    decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
    
    decoder_embedding_layer = model.get_layer('decoder_embedding')
    decoder_embedding = decoder_embedding_layer(decoder_inputs)
    
    decoder_lstm_layer = model.get_layer('decoder_lstm')
    decoder_outputs, state_h_dec, state_c_dec = decoder_lstm_layer(
        decoder_embedding, initial_state=decoder_states_inputs
    )
    decoder_states = [state_h_dec, state_c_dec]
    
    decoder_dense_layer = model.get_layer('decoder_dense')
    decoder_outputs = decoder_dense_layer(decoder_outputs)
    
    decoder_model = Model(
        [decoder_inputs] + decoder_states_inputs,
        [decoder_outputs] + decoder_states
    )
    print("Model loaded successfully.")

def get_model_info():
    """Returns information about the loaded model."""
    return {
        'model_type': 'Seq2Seq Encoder-Decoder LSTM',
        'framework': 'TensorFlow/Keras',
        'training_samples': 4,
        'eng_vocab_size': len(eng_word2idx) if eng_word2idx else 0,
        'fre_vocab_size': len(fre_word2idx) if fre_word2idx else 0,
        'max_eng_len': max_eng_len,
        'max_fre_len': max_fre_len
    }

def translate(sentence):
    """
    Translates an English sentence to French.
    Returns: (translated_sentence, unknown_words_list, success_status, translation_time_ms)
    """
    if model is None:
        return "", [], False, 0
        
    start_time = time.time()
    
    words = sentence.lower().split()
    
    if len(words) > max_eng_len:
        return "Sentence exceeds maximum supported length.", [], False, 0
        
    unknown_words = []
    input_seq = np.zeros((1, max_eng_len), dtype='float32')
    
    for t, word in enumerate(words):
        if word in eng_word2idx:
            input_seq[0, t] = eng_word2idx[word]
        else:
            unknown_words.append(word)
            # Use <PAD> or simply ignore for this basic model
            input_seq[0, t] = eng_word2idx.get('<PAD>', 0)
            
    # Encode the input as state vectors
    states_value = encoder_model.predict(input_seq, verbose=0)
    
    # Generate empty target sequence of length 1
    target_seq = np.zeros((1, 1), dtype='float32')
    # Populate the first character of target sequence with the start character
    if '<START>' in fre_word2idx:
        target_seq[0, 0] = fre_word2idx['<START>']
        
    stop_condition = False
    decoded_sentence = ""
    
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value, verbose=0
        )
        
        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_word = fre_idx2word.get(sampled_token_index, '')
        
        if sampled_word != '<END>':
            decoded_sentence += sampled_word + " "
            
        # Exit condition: either hit max length or find stop character
        if sampled_word == '<END>' or len(decoded_sentence.split()) > max_fre_len:
            stop_condition = True
            
        # Update the target sequence (of length 1)
        target_seq = np.zeros((1, 1), dtype='float32')
        target_seq[0, 0] = sampled_token_index
        
        # Update states
        states_value = [h, c]
        
    end_time = time.time()
    translation_time_ms = int((end_time - start_time) * 1000)
    
    status = True
    if unknown_words:
        status = False
        
    return decoded_sentence.strip(), unknown_words, status, translation_time_ms
