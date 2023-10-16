import jieba
import csv


punctuation = '，。！？、（）【】<>《》=：+-*—“”…\n\t\r[]'
def pretreat():
    with open('baidu_stopwords.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().split('\n')
    with open('Book.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row['id'])
            print(row['书名'])
            seg_list = jieba.cut_for_search(row['内容简介'])
            seg_list = [word for word in seg_list if word not in stop_words]
            seg_list = [word for word in seg_list if word not in punctuation]

            seg_list += row['书名'].split(' ')
            seg_list += row['作者'].replace('\r',' ').replace('\n','').replace('[','').replace(']',' ').replace("'",'').split(' ')
            seg_list += row['出版社'].split(' ')
            seg_list += row['译者'].replace('\r',' ').replace('\n','').replace('[','').replace(']',' ').replace("'",'').split(' ')
            seg_list += row['出版年'].split(' ')
            seg_list += row['豆瓣评分'].split(' ')
            seg_list += jieba.cut_for_search(row['作者简介'])
            seg_list = [word for word in seg_list if word not in stop_words]
            seg_list = [word for word in seg_list if word not in punctuation]
            print(",".join(seg_list))
            with open('Book_pretreat.csv', 'a', newline='', encoding='utf-8-sig') as f:
               csv.DictWriter(f, fieldnames=['id', 'word']).writerow({'id': row['id'], 'word': ",".join(seg_list)})
            print(row['id'])
            
with open('Book_pretreat.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['id', 'word']).writeheader()
pretreat()