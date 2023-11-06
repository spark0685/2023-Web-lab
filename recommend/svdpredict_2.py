# -*- coding: gbk -*-


from surprise import SVD
from surprise import Dataset
from surprise.model_selection import cross_validate
from surprise import Reader
from surprise import accuracy
from surprise.model_selection import KFold
import pandas as pd
import time
import csv
import random

time1=time.time()

# ���ݶ�ȡ
reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)
data = Dataset.load_from_file('./recommend/rate.csv', reader=reader)

# �����������
raw_ratings = data.raw_ratings
random.shuffle(raw_ratings)

# �����ݷֳ������֣�һ��ѵ����һ����ԣ�
threshold = int(0.5 * len(raw_ratings))
train_raw_ratings = raw_ratings[:threshold]
test_raw_ratings = raw_ratings[threshold:]
# �޸Ĳ������ݸ�ʽ�Խ������û�ID����ƷID��ʵ������
modified_test_raw_ratings = [(uid, iid, r_ui) for (uid, iid, r_ui, timestamp) in test_raw_ratings]

# �����������
with open('./recommend/modified_test_raw_ratings.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['user', 'Movie', 'Rate']).writeheader()
    for uid, iid, r_ui in modified_test_raw_ratings:
        csv.DictWriter(f, fieldnames=['user', 'Movie', 'Rate']).writerow({'user': uid, 'Movie': iid, 'Rate': r_ui})



# ����ѵ�����Ͳ��Լ�
data.raw_ratings = train_raw_ratings  # ��ʹ��һ���������Ϊѵ����
trainset = data.build_full_trainset()
# train_set = data.build_full_trainset()

# ʹ��funkSVD
algo = SVD(biased=False)#����Ĭ����True��ʹ�õ���biasSVD

# �洢���Լ���Ԥ����
all_predictions = []

# ѵ����Ԥ��
algo.fit(trainset)
predictions = algo.test(modified_test_raw_ratings)
all_predictions.append(predictions)

# ������Խ��
with open('./recommend/svd_test.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['user', 'Movie', 'Rate']).writeheader()
    for uid, iid, r_ui, est, _ in predictions:
        csv.DictWriter(f, fieldnames=['user', 'Movie', 'Rate']).writerow({'user': uid, 'Movie': iid, 'Rate': est})

# ����RMSE
rmse = accuracy.rmse(predictions, verbose=True)
print(f"RMSE on the other half of the data: {rmse}")

# # ����K�۽�����֤��������K=3
# kf = KFold(n_splits=3)
# for trainset, testset in kf.split(data):
#     # ѵ����Ԥ��
#     algo.fit(trainset)
#     predictions = algo.test(testset)
#     # ����RMSE
#     accuracy.rmse(predictions, verbose=True)

# uid = str(196)
# iid = str(302)
# # ���uid��iid��Ԥ����
# pred = algo.predict(uid, iid, r_ui=4, verbose=True)

with open ('./recommend/user.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    user = []
    for row in reader:
        user.append(row['userId'])

with open ('./recommend/movie.csv', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    movie = []
    for row in reader:
        movie.append(row['movieId'])


# ����predictions���ļ��У�������ʵֵ��Ԥ��ֵ��
with open('./recommend/svd_predict.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.DictWriter(f, fieldnames=['user', 'Movie', 'Rate'])
    csv_writer.writeheader()  # д�������
    for uid, iid, r_ui, est, _ in predictions:
        user_id = user[int(uid)-1]
        movie_id = movie[int(iid)-1]
        csv_writer.writerow({'user': user_id, 'Movie': movie_id, 'Rate': est})



# # ��������û���Ԥ����
# with open ('./recommend/knn_predict.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
#     #User,Movie,Rate,Time,Tag
#     csv.DictWriter(csvfile, fieldnames=['user', 'Movie', 'Rate']).writeheader()
#     for uid in range(len(user)):
#         for iid in range(len(movie)):
#             pred = algo.predict(user[uid], movie[iid], r_ui=4, verbose=True)
#             csv.DictWriter(csvfile, fieldnames=['user', 'Movie', 'Rate']).writerow({'user': uid, 'Movie': iid, 'Rate': pred.est})
#