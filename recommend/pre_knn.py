# -*- coding: gbk -*-
import csv

with open('./recommend/rating.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['userId', 'movieId', 'rating', 'timestamp']).writeheader()
    user = []
    movie = []
    with open('./recommend/movie_score.csv', newline='', encoding='utf-8-sig') as csvfile:
        pl = csv.DictReader(csvfile)
        for row in pl:
            # print(row['User'], row['Rate'])
            # 将用户id转换为1-943存入新的列表中
            if row['User'] not in user:
                user.append(row['User'])
            # 将电影id转换为1-1682存入新的列表中
            if row['Movie'] not in movie:
                movie.append(row['Movie'])
            csv.DictWriter(f, fieldnames=['userId', 'movieId', 'rating', 'timestamp']).writerow({'userId': user.index(row['User'])+1, 'movieId': movie.index(row['Movie'])+1, 'rating':row['Rate'], 'timestamp':row['Time']})
        # print(user)
        # print(movie)
    #保存用户id和电影id
    with open('./recommend/user.csv', 'w', newline='', encoding='utf-8-sig') as f:
        csv.DictWriter(f, fieldnames=['userId']).writeheader()
        for i in range(len(user)):
            csv.DictWriter(f, fieldnames=['userId']).writerow({'userId': user[i]})
    with open('./recommend/movie.csv', 'w', newline='', encoding='utf-8-sig') as f:
        csv.DictWriter(f, fieldnames=['movieId']).writeheader()
        for i in range(len(movie)):
            csv.DictWriter(f, fieldnames=['movieId']).writerow({'movieId': movie[i]})


        