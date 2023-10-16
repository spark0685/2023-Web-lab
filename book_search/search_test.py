import csv



input = input("请输入搜索内容：")
with open('pl.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if input == row['term']:
#            print(row[' docID'])
            doc = row[' docID'].split('/')
            with open('Book.csv', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['id'] in doc:
#                        print(row['id'])
                        print(row['书名'])
                        # print(row['作者'])
#                        print(row['出版社'])
#                        print(row['译者'])
#                        print(row['出版年'])
#                        print(row['豆瓣评分'])
#                        print(row['内容简介'])
#                        print(row['作者简介'])
            break
    