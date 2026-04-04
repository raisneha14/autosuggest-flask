from flask import Flask, render_template, request
import  pandas as pd
import numpy as np
import textdistance
from collections import Counter
import re
import os

app = Flask(__name__)


words = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data.txt")

with open(file_path, "r", encoding="utf-8") as f:
    data = f.read(
  data = f.read()
  data = data.lower()
  word = re.findall(r'\w+', data)
  words = words+word

  print(words[0:25])
  len(words)
  vocab = set(words)
  new_len = len(vocab)
  word_count_dict = Counter(words)
print(word_count_dict)
word_count_dict.most_common(20)
counts = (word_count_dict.values())
print(counts)
total_sum = sum(counts)
print(total_sum)
new_dict = {}
for k in word_count_dict.keys():
    prob = word_count_dict[k]/total_sum
    new_dict[k] = prob


print(new_dict)

@app.route('/')    
def index():
        return render_template('index.html', suggestion = None, keyword ="")
    
@app.route('/suggest',methods=['POST'])
def suggest():
        keyword = request.form['keyword'].strip().lower()
        if not keyword:
            return render_template('index.html', suggestion = None, keyword ="")
        if len(keyword)<3:
         return render_template('index.html', suggestion = ["Enter Valid Word"], keyword = keyword)
           similarities = [1-(textdistance.Jaccard(qval=2)).distance(w, keyword)for w in word_count_dict.keys()]
           df = pd.DataFrame.from_dict(new_dict, orient='index').reset_index()
           df.columns = ['Words', 'Prob']
           df['Similarity'] = similarities
           df['Similarity'] = df['Similarity'].round(2)
           df = df[df['Similarity'>0.2]]
           df = df[abs(df['Words'].str.len()-len(keyword)) <=3]
           if df.empty:
              suggestions_list = ["No meaning"]
           else:
              suggestions = df.sort_values(['Similarity','Prob'], ascending = False)[['Words', 'Similarity']].head
              suggestions_list = suggestions.to_dict('records')
        return render_template('index.html', suggestion = suggestions_list, keyword = keyword)
        
if __name__ == '__main__':
    app.run(debug = True)
