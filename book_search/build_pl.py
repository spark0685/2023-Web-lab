import csv
word_map = {}
with open('Book_pretreat.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for word in row['word'].split(','):
            if word not in word_map:
                word_map[word] = row['id']
            else:
                word_map[word] += '/' + row['id']
with open('pl.csv', 'a', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['term', ' docID']).writeheader()
    for word in word_map:
        csv.DictWriter(f, fieldnames=['term', 'docID']).writerow({'term': word, 'docID': word_map[word]})
        print(word, word_map[word])
