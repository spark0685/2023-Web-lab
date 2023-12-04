import csv
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import pandas as pd

# 量化阶段
loaded_data = pd.read_csv("data\\book_score.csv")
All_Tag = []
maxlen = 0
Tag1_list = []
Tag2_list = []
Tag3_list = []
Tag4_list = []
Time_hour = []
User_list = []
User_id = []
item_list = []
item_id = []
with open(file="data\\book_score.csv", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    result = list(reader)
    for i in range(1, len(result)):
        row = result[i]
        tag_list = list(row[4].split(","))
        time = str(row[3])
        Time_hour.append(int(time[11:13]))
        if (row[0] in User_list) is False:
            User_list.append(row[0])
        User_id.append(User_list.index(row[0]))
        if (row[1] in User_list) is False:
            item_list.append(row[1])
        item_id.append(item_list.index(row[1]))
        if len(tag_list) == 0:
            continue
        if len(tag_list) > maxlen:
            maxlen = len(tag_list)
        for tag in tag_list:
            if (tag in All_Tag) is False:
                All_Tag.append(tag)
        if len(tag_list) == 0:
            Tag1_list.append(0)
            Tag2_list.append(0)
            Tag3_list.append(0)
            Tag4_list.append(0)
        if len(tag_list) == 1:
            Tag1_list.append(All_Tag.index(tag_list[0]))
            Tag2_list.append(0)
            Tag3_list.append(0)
            Tag4_list.append(0)
        if len(tag_list) == 2:
            Tag1_list.append(All_Tag.index(tag_list[0]))
            Tag2_list.append(All_Tag.index(tag_list[1]))
            Tag3_list.append(0)
            Tag4_list.append(0)
        if len(tag_list) == 3:
            Tag1_list.append(All_Tag.index(tag_list[0]))
            Tag2_list.append(All_Tag.index(tag_list[1]))
            Tag3_list.append(All_Tag.index(tag_list[2]))
            Tag4_list.append(0)
        if len(tag_list) >= 4:
            Tag1_list.append(All_Tag.index(tag_list[0]))
            Tag2_list.append(All_Tag.index(tag_list[1]))
            Tag3_list.append(All_Tag.index(tag_list[2]))
            Tag4_list.append(All_Tag.index(tag_list[3]))
loaded_data["Tag1"] = Tag1_list
loaded_data["Tag2"] = Tag2_list
loaded_data["Tag3"] = Tag3_list
loaded_data["Tag4"] = Tag4_list
loaded_data["Time_hour"] = Time_hour
loaded_data["User_id"] = User_id
loaded_data["item_id"] = item_id
loaded_data.to_csv("pretreat.csv")

# 分割数据集
loaded_data = pd.read_csv("pretreat.csv")
standardscaler = StandardScaler()
# loaded_data[["User","Book","Tag1","Tag2","Time_hour"]]=standardscaler.fit_transform(loaded_data[["User","Book","Tag1","Tag2","Time_hour"]])
# loaded_data.drop(labels=loaded_data[(loaded_data.Rate==0)].index,inplace=True,axis=0)
train_data, test_data = train_test_split(
    loaded_data, test_size=0.5, random_state=42, shuffle=True
)
# train_data.drop(labels=train_data[(train_data.Rate!=0)].index,inplace=True,axis=0)
# test_data.drop(test_data[test_data.Rate!=0].index,axis=0,inplace=True)
# test_data=test_data.sort_index(axis=0)
# test_data=pd.DataFrame(test_data,columns=["User","Book","Rate","Time","Tag","Tag1","Tag2","Tag3","Tag4","Time_hour","User_id","item_id"])
test_data = pd.DataFrame(test_data)
test_data.sort_values(by=["User", "Rate"], ascending=[True, False], inplace=True)
test_data.to_csv("test.csv", index=False)

# 训练
train = train_data[["User", "Tag1", "Tag2", "Time_hour"]]
# train=standardscaler.fit(train)
# test_data=standardscaler.transform(test_data)
target = train_data["Rate"]
knn = KNeighborsClassifier(
    n_neighbors=20, weights="distance", algorithm="auto", leaf_size=30
)

knn.fit(train, target)

# 预测
x_test = test_data[["User", "Tag1", "Tag2", "Time_hour"]]
# x_test=standardscaler.fit(x_test)
y_test = test_data["Rate"]
y_predict = knn.predict(x_test)
test_data["Rate"] = y_predict
test_data.sort_values(by=["User", "Rate"], ascending=[True, False], inplace=True)
test_data.to_csv("predict.csv", index=False)
print(accuracy_score(y_test, y_predict))
