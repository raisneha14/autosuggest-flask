from flask import Flask, render_template, request
import pandas as pd
import textdistance
from collections import Counter
import re
import os

app = Flask(__name__)


words = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, r"C:\Users\JP COMPUTER\OneDrive\Documents\data.txt")

try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read().lower()
        words = re.findall(r'\w+', data)
except FileNotFoundError:
    print("data.txt file not found")
    words = []


word_count_dict = Counter(words)

total_sum = sum(word_count_dict.values())

new_dict = {}

if total_sum != 0:
    for k in word_count_dict.keys():
        new_dict[k] = word_count_dict[k] / total_sum



@app.route('/')
def index():
    return render_template('index.html', suggestion=None, keyword="", corrected=None)


@app.route('/suggest', methods=['POST'])
def suggest():

    keyword = request.form['keyword'].strip().lower()

    
    if not keyword:
        return render_template('index.html', suggestion=None, keyword="", corrected=None)

    
    if len(keyword) < 3:
        return render_template(
            'index.html',
            suggestion=[{"Words": "Enter valid word", "Similarity": 0}],
            keyword=keyword,
            corrected=None
        )

    
    if not word_count_dict:
        return render_template(
            'index.html',
            suggestion=[{"Words": "No data available", "Similarity": 0}],
            keyword=keyword,
            corrected=None
        )

    
    similarities = [
        1 - textdistance.Jaccard(qval=2).distance(w, keyword)
        for w in word_count_dict.keys()
    ]

    #
    if len(similarities) != len(word_count_dict):
        return render_template(
            'indexhtml',
            suggestion=[{"Words": "Error in processing", "Similarity": 0}],
            keyword=keyword,
            corrected=None
        )

    
    df = pd.DataFrame({
        'Words': list(word_count_dict.keys()),
        'Prob': list(new_dict.values()),
        'Similarity': similarities
    })

    df['Similarity'] = df['Similarity'].round(2)
    print("Debug Output:")
    print(df.sort_values('Similarity', ascending=False).head(10))   
    df = df[df['Similarity'] > 0.02]
    df = df[abs(df['Words'].str.len() - len(keyword)) <= 3]


    if df.empty:
        suggestions_list = [{"Words": "No similar words", "Similarity": 0}]
        corrected_word = None
    else:
        df = df.sort_values(['Similarity', 'Prob'], ascending=False)

        
        corrected_word = df.iloc[0]['Words']

        
        if df.iloc[0]['Similarity'] < 0.3:
            suggestion_list = [{"Words":"No Similar words", "Similarity":0}]
            corrected_word = None
        else   

            suggestions_list = df[['Words', 'Similarity']].head(5).to_dict('records')
    return render_template(
        'index.html',
        suggestion=suggestions_list,
        keyword=keyword,
        corrected=corrected_word
    )


if __name__ == '__main__':
    app.run(debug=True)



