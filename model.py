import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# Loading the corpus.csv file
corpus_df = pd.read_csv('corpus.csv')

# Function to count the number of sentences
def count_sentences(text):
    sentences = re.split(r'[.!?]+', text)
    return len(sentences)

# Function to count the number of words
def count_words(text):
    words = text.split()
    return len(words)

# Function to estimate the number of syllables in a word
def estimate_syllables(word):
    vowels = "aeiouy"
    word = word.lower()
    count = 0

    if word[0] in vowels:
        count += 1

    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1

    if word.endswith("e"):
        count -= 1

    return count if count > 0 else 1

# Computing total words, total sentences, and total syllables
corpus_df['total_sentences'] = corpus_df['content'].apply(count_sentences)
corpus_df['total_words'] = corpus_df['content'].apply(count_words)
corpus_df['total_syllables'] = corpus_df['content'].apply(lambda text: sum(estimate_syllables(word) for word in text.split()))

# Computing Flesch-Kincaid grade level
corpus_df['flesch_kincaid_grade'] = 0.39 * (corpus_df['total_words'] / corpus_df['total_sentences']) \
                                  + 11.8 * (corpus_df['total_syllables'] / corpus_df['total_words']) \
                                  - 15.59

# Preparinng data for logistic regression
# Labeling the data based on an arbitrary threshold (median)
threshold = corpus_df['flesch_kincaid_grade'].median()
corpus_df['readability_label'] = (corpus_df['flesch_kincaid_grade'] > threshold).astype(int)

# Features (X) and target variable (y)
X = corpus_df['flesch_kincaid_grade'].values.reshape(-1, 1)
y = corpus_df['readability_label']

# Spliting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Training the logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Predicting and evaluating the model
predictions = model.predict(X_test)
report = classification_report(y_test, predictions, target_names=['simple', 'difficult'])

# Printing the classification report
print(report)

# Creating a figure and axis to plot the text
fig, ax = plt.subplots(figsize=(8, 4))  # Adjust the figure size as needed
ax.text(0.5, 0.5, report, horizontalalignment='center', verticalalignment='center', fontsize=12, family='monospace')
plt.axis('off')

# Saving the figure in a BytesIO object
buf = BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)

# Opening the image and save it
img = Image.open(buf)
img.save('classification_report.png') 

# Closing the buffer and figure
buf.close()
plt.close(fig)
