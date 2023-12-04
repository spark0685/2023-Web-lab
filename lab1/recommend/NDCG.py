import pandas as pd
import math

def compute_DCG(rel_list):
    dcg = 0.0
    for i in range(len(rel_list)):
        dcg += (2 ** rel_list[i] - 1) / math.log2(i + 2)
    return dcg

def compute_NDCG(predictions, targets):
    ndcg = []
    for i in range(len(predictions)):
        pred = predictions[i]
        target = targets[i]

        # 根据评分对预测结果进行排序
        sorted_pred = [x for _, x in sorted(zip(target, pred), reverse=True)]
        # 计算预测结果的DCG
        dcg_pred = compute_DCG(sorted_pred)
        # 计算真实结果的DCG
        dcg_target = compute_DCG(target)

        # 如果DCG_target为0，则NDCG为0
        if dcg_target == 0:
            ndcg.append(0)
        else:
            # 计算NDCG
            ndcg.append(dcg_pred / dcg_target)
    return ndcg

def compute_mse(predictions, targets):
    mse = []
    for i in range(len(predictions)):
        pred = predictions[i]
        target = targets[i]

        # 计算预测结果和真实结果的均方误差
        mse.append(sum([(pred[i] - target[i]) ** 2 for i in range(len(pred))]) / len(pred))
    return mse

# 读取预测文件和测试文件的CSV文件
predictions_df = pd.read_csv('predict.csv')
targets_df = pd.read_csv('test.csv')

# 获取用户和评分列的数据
users_pred = predictions_df['User'].tolist()
ratings_pred = predictions_df['Rate'].tolist()
users_target = targets_df['User'].tolist()
ratings_target = targets_df['Rate'].tolist()

# 将用户和评分列的数据按照用户进行分组
users_pred_grouped = predictions_df.groupby('User')
users_target_grouped = targets_df.groupby('User')

# 用于存储每个用户的预测评分和真实评分
predictions = []
targets = []

# 遍历每个用户
for user in users_pred_grouped.groups.keys():
    # 获取该用户的预测评分
    user_pred_ratings = users_pred_grouped.get_group(user)['Rate'].tolist()
    # 获取该用户的真实评分
    user_target_ratings = users_target_grouped.get_group(user)['Rate'].tolist()

    # 将该用户的预测评分和真实评分添加到列表中
    predictions.append(user_pred_ratings)
    targets.append(user_target_ratings)

# 计算NDCG
ndcg = compute_NDCG(predictions, targets)

print('NDCG:', sum(ndcg) / len(ndcg)) #运行结果为NDCG: 0.791167190117562

# 计算MSE
mse = compute_mse(predictions, targets)
print('MSE:', sum(mse) / len(mse)) # 运行结果为MSE: 1.1141054372146006 
# 运行这个程序需要一定的时间，请耐心等待。 by mb