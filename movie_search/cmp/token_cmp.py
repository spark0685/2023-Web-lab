import csv
import jieba
import thulac

punctuation = '，。！？、（）【】<>《》=：+-*—“”…\n\t\r[] \u3000,/·()'
thulac1 = thulac.thulac(seg_only=True)
def cmp():
    with open('baidu_stopwords.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().split('\n')
    with open('movie.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for i in punctuation:
                row['简介'] = row['简介'].replace(i, '')
            list_jieba = jieba.cut(row['简介'])

            list_thulac = thulac1.cut(row['简介'])
            list_thulac = [i[0] for i in list_thulac]
            with open('cmp.csv', 'a', newline='', encoding='utf-8-sig') as f:
                csv.DictWriter(f, fieldnames=['id','jieba','thulac']).writerow({'id': row['id'], 'jieba':'/'.join(list_jieba), 'thulac':'/'.join(list_thulac)})
            print(row['id'], list_jieba, list_thulac)

with open('cmp.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['id','jieba','thulac']).writeheader()
cmp()