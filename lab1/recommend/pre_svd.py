# -*- coding: gbk -*-
import csv

with open('./recommend/rating_movie.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['userId', 'movieId', 'rating', 'timestamp']).writeheader()
    user = []
    movie = []
    with open('./recommend/movie_score.csv', newline='', encoding='utf-8-sig') as csvfile:
        pl = csv.DictReader(csvfile)
        for row in pl:
            # print(row['User'], row['Rate'])
            # ���û�idת��Ϊ1-943�����µ��б���
            if row['User'] not in user:
                user.append(row['User'])
            # ����Ӱidת��Ϊ1-1682�����µ��б���
            if row['Movie'] not in movie:
                movie.append(row['Movie'])
            csv.DictWriter(f, fieldnames=['userId', 'movieId', 'rating', 'timestamp']).writerow({'userId': user.index(row['User'])+1, 'movieId': movie.index(row['Movie'])+1, 'rating':row['Rate'], 'timestamp':row['Time']})
        # print(user)
        # print(movie)
    #�����û�id�͵�Ӱid
    with open('./recommend/user_movie.csv', 'w', newline='', encoding='utf-8-sig') as f:
        csv.DictWriter(f, fieldnames=['userId']).writeheader()
        for i in range(len(user)):
            csv.DictWriter(f, fieldnames=['userId']).writerow({'userId': user[i]})
    with open('./recommend/movie.csv', 'w', newline='', encoding='utf-8-sig') as f:
        csv.DictWriter(f, fieldnames=['movieId']).writeheader()
        for i in range(len(movie)):
            csv.DictWriter(f, fieldnames=['movieId']).writerow({'movieId': movie[i]})



with open('./recommend/rating_book.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['userId', 'bookId', 'rating', 'timestamp']).writeheader()
    user = []
    book = []
    with open('./recommend/book_score.csv', newline='', encoding='utf-8-sig') as csvfile:
        pl = csv.DictReader(csvfile)
        for row in pl:
            # print(row['User'], row['Rate'])
            # ���û�idת��Ϊ1-943�����µ��б���
            if row['User'] not in user:
                user.append(row['User'])
            # ����Ӱidת��Ϊ1-1682�����µ��б���
            if row['Book'] not in book:
                book.append(row['Book'])
            csv.DictWriter(f, fieldnames=['userId', 'bookId', 'rating', 'timestamp']).writerow({'userId': user.index(row['User'])+1, 'bookId': book.index(row['Book'])+1, 'rating':row['Rate'], 'timestamp':row['Time']})
        # print(user)
        # print(movie)
    #�����û�id�͵�Ӱid
    with open('./recommend/user_book.csv', 'w', newline='', encoding='utf-8-sig') as f:
        csv.DictWriter(f, fieldnames=['userId']).writeheader()
        for i in range(len(user)):
            csv.DictWriter(f, fieldnames=['userId']).writerow({'userId': user[i]})
    with open('./recommend/book.csv', 'w', newline='', encoding='utf-8-sig') as f:
        csv.DictWriter(f, fieldnames=['bookId']).writeheader()
        for i in range(len(book)):
            csv.DictWriter(f, fieldnames=['bookId']).writerow({'bookId': book[i]})


      