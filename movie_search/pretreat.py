import jieba
import csv


punctuation = '，。！？、（）【】<>《》=：+-*—“”…\n\t\r[] \u3000,/·()'
def pretreat():
    with open('baidu_stopwords.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().split('\n')
    with open('movie.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row['id'])
            print(row['片名'])
            seg_list = jieba.cut_for_search(row['简介']+row['导演']+row['编剧']+row['主演']+row['类型']+row['国家/地区']+row['片名'])
            seg_list = [word for word in seg_list if word not in stop_words]
            seg_list = [word for word in seg_list if word not in punctuation]

            seg_list += row['片名'].split(' ')
            seg_list += row['主演'].replace('\r',' ').replace('\n','').replace('[','').replace(']','').replace("'",'').replace(' ','').split('/')
            seg_list += row['类型'].replace(' ','').split('/')
#            seg_list += row['评分'].split(' ')
            seg_list = [word for word in seg_list if word not in punctuation]           
            print(",".join(seg_list))
            with open('movie_pretreat.csv', 'a', newline='', encoding='utf-8-sig') as f:
               csv.DictWriter(f, fieldnames=['id', 'word']).writerow({'id': row['id'], 'word':','.join(seg_list)})
            print(row['id'])
            
with open('movie_pretreat.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['id', 'word']).writeheader()
pretreat()