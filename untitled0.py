# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1eTA8-n98WJqQCeF5o2AtmOH1VKiWuctg
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

df_fixs = pd.read_csv('/content/sample_data/text.csv')

df_fixs = df_fixs.sample(n=20000, random_state=42)

label_encoder = LabelEncoder()
df_fixs['label'] = label_encoder.fit_transform(df_fixs['label'])

df_fixs.head()

print(df_fixs)

train_texts, test_texts, train_labels, test_labels = train_test_split(df_fixs['text'], df_fixs['label'], test_size=0.2, random_state=42)

tokenizer = Tokenizer(num_words=10000, oov_token='<OOV>')
tokenizer.fit_on_texts(train_texts)

train_sequences = tokenizer.texts_to_sequences(train_texts)
test_sequences = tokenizer.texts_to_sequences(test_texts)

max_sequence_length = max([len(sequence) for sequence in train_sequences])

train_padded = pad_sequences(train_sequences, maxlen=max_sequence_length, padding='post', truncating='post')
test_padded = pad_sequences(test_sequences, maxlen=max_sequence_length, padding='post', truncating='post')

class_counts = np.bincount(train_labels)
total_samples = np.sum(class_counts)
class_weights = {class_label: total_samples / (len(class_counts) * class_count) for class_label, class_count in enumerate(class_counts)}

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=10000, output_dim=16, input_length=max_sequence_length),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(6, activation='softmax')
])

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

checkpoint = ModelCheckpoint('best_model.h5', monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')
early_stopping = EarlyStopping(monitor='val_accuracy', patience=3, verbose=1, mode='max', restore_best_weights=True)

history = model.fit(train_padded, train_labels, epochs=20, batch_size=32,
                    validation_data=(test_padded, test_labels),
                    class_weight=class_weights, callbacks=[checkpoint, early_stopping])

test_loss, test_accuracy = model.evaluate(test_padded, test_labels)
print(f'Test Accuracy: {test_accuracy}')

import matplotlib.pyplot as plt
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='accuracy')
plt.plot(history.history['val_accuracy'], label='val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.show()

random_tweets = [
    "I'm feeling really happy today!",
    "Today, I went to school and learn the subject that I love"
]

random_sequences = tokenizer.texts_to_sequences(random_tweets)
random_padded = pad_sequences(random_sequences, maxlen=max_sequence_length, padding='post', truncating='post')

sentiment_labels = ['sadness', 'joy', 'love', 'anger', 'fear', 'surprise']
predictions = model.predict(random_padded)
for i, prediction in enumerate(predictions):
    predicted_label = sentiment_labels[np.argmax(prediction)]
    print(f"Random Tweet {i+1}: {random_tweets[i]} - Predicted Sentiment: {predicted_label}")