from flask import Flask, render_template, request
import pandas as pd
import textdistance
from collections import Counter
import re
import os

app = Flask(__name__)

# ------------------ LOAD DATA ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data.txt")

words = []

try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read().lower()
        words = re.findall(r'\w+', data)
except FileNotFoundError:
    print("❌ data.txt file not found")
    words = []

# ------------------ PROCESS DATA ------------------
word_count_dict = Counter(words)

total_sum = sum(word_count_dict.values())

# Avoid division by zero
new_dict = {}
if total_sum > 0:
    for k in word_count_dict.keys():
        new_dict[k] = word_count_dict[k] / total_sum

# ------------------ ROUTES ------------------
@app.route('/')
def index():
    return render_template('index.html', suggestion=None, keyword="")

@app.route('/suggest', methods=['POST'])
def suggest():
    keyword = request.form.get('keyword', '').strip().lower()

    # Input validation
    if not keyword:
        return render_template('index.html', suggestion=None, keyword="")

    if len(keyword) < 3:
        return render_template('index.html',
                               suggestion=[{"Words": "Enter valid word", "Similarity": 0}],
                               keyword=keyword)

    if not word_count_dict:
        return render_template('index.html',
                               suggestion=[{"Words": "No data available", "Similarity": 0}],
                               keyword=keyword)

    # ------------------ SIMILARITY ------------------
    similarities = [
        1 - textdistance.Jaccard(qval=2).distance(w, keyword)
        for w in word_count_dict.keys()
    ]

    # Safety check
    if len(similarities) != len(word_count_dict):
        return render_template('index.html',
                               suggestion=[{"Words": "Error in processing", "Similarity": 0}],
                               keyword=keyword)

    # ------------------ DATAFRAME ------------------
    df = pd.DataFrame({
        'Words': list(word_count_dict.keys()),
        'Prob': list(new_dict.values())
    })

    df['Similarity'] = similarities
    df['Similarity'] = df['Similarity'].round(2)

    # Filters
    df = df[df['Similarity'] > 0.2]
    df = df[abs(df['Words'].str.len() - len(keyword)) <= 3]

    # ------------------ OUTPUT ------------------
    if df.empty:
        suggestions_list = [{"Words": "No similar words", "Similarity": 0}]
    else:
        suggestions = df.sort_values(['Similarity', 'Prob'], ascending=False)
        suggestions_list = suggestions.head(10).to_dict('records')

    return render_template('index.html',
                           suggestion=suggestions_list,
                           keyword=keyword)

# ------------------ RUN APP ------------------
if __name__ == '__main__':
    app.run(debug=True)



