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

# 数据读取
reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)
data = Dataset.load_from_file('./recommend/rate.csv', reader=reader)

# 随机打乱数据
raw_ratings = data.raw_ratings
random.shuffle(raw_ratings)

# 将数据分成两部分（一半训练，一半测试）
threshold = int(0.5 * len(raw_ratings))
train_raw_ratings = raw_ratings[:threshold]
test_raw_ratings = raw_ratings[threshold:]
# 修改测试数据格式以仅包含用户ID、物品ID和实际评分
modified_test_raw_ratings = [(uid, iid, r_ui) for (uid, iid, r_ui, timestamp) in test_raw_ratings]

# 输出打乱数据
with open('./recommend/modified_test_raw_ratings.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['user', 'Movie', 'Rate']).writeheader()
    for uid, iid, r_ui in modified_test_raw_ratings:
        csv.DictWriter(f, fieldnames=['user', 'Movie', 'Rate']).writerow({'user': uid, 'Movie': iid, 'Rate': r_ui})



# 构建训练集和测试集
data.raw_ratings = train_raw_ratings  # 仅使用一半的数据作为训练集
trainset = data.build_full_trainset()
# train_set = data.build_full_trainset()

# 使用funkSVD
algo = SVD(biased=False)#这里默认是True，使用的是biasSVD

# 存储测试集的预测结果
all_predictions = []

# 训练并预测
algo.fit(trainset)
predictions = algo.test(modified_test_raw_ratings)
all_predictions.append(predictions)

# 输出测试结果
with open('./recommend/svd_test.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv.DictWriter(f, fieldnames=['user', 'Movie', 'Rate']).writeheader()
    for uid, iid, r_ui, est, _ in predictions:
        csv.DictWriter(f, fieldnames=['user', 'Movie', 'Rate']).writerow({'user': uid, 'Movie': iid, 'Rate': est})

# 计算RMSE
rmse = accuracy.rmse(predictions, verbose=True)
print(f"RMSE on the other half of the data: {rmse}")

# # 定义K折交叉验证迭代器，K=3
# kf = KFold(n_splits=3)
# for trainset, testset in kf.split(data):
#     # 训练并预测
#     algo.fit(trainset)
#     predictions = algo.test(testset)
#     # 计算RMSE
#     accuracy.rmse(predictions, verbose=True)

# uid = str(196)
# iid = str(302)
# # 输出uid对iid的预测结果
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


# 保存predictions到文件中（保存真实值和预测值）
with open('./recommend/svd_predict.csv', 'w', newline='', encoding='utf-8-sig') as f:
    csv_writer = csv.DictWriter(f, fieldnames=['user', 'Movie', 'Rate'])
    csv_writer.writeheader()  # 写入标题行
    for uid, iid, r_ui, est, _ in predictions:
        user_id = user[int(uid)-1]
        movie_id = movie[int(iid)-1]
        csv_writer.writerow({'user': user_id, 'Movie': movie_id, 'Rate': est})



# # 输出所有用户的预测结果
# with open ('./recommend/knn_predict.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
#     #User,Movie,Rate,Time,Tag
#     csv.DictWriter(csvfile, fieldnames=['user', 'Movie', 'Rate']).writeheader()
#     for uid in range(len(user)):
#         for iid in range(len(movie)):
#             pred = algo.predict(user[uid], movie[iid], r_ui=4, verbose=True)
#             csv.DictWriter(csvfile, fieldnames=['user', 'Movie', 'Rate']).writerow({'user': uid, 'Movie': iid, 'Rate': pred.est})
#