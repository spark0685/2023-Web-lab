import csv


word_map = {}
with open('movie_pretreat.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for word in row['word'].split(','):
            if word not in word_map:
                word_map[word] = [row['id']]
            else:
                if row['id'] not in word_map[word]:
                    word_map[word].append(row['id'])  
for word in word_map:
    word_map[word].sort()
with open('movie_pl.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['term', ' docID']).writeheader()
    for word in word_map:
        csv.DictWriter(f, fieldnames=['term', 'docID']).writerow({'term': word, 'docID': word_map[word]})
        print(word, word_map[word])
