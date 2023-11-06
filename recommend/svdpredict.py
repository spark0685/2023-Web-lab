#coding=utf-8

# '''
# 目标：构建简单电影推荐系统，假设现有ABCDE 5个同学，看完电影之后的评价如下
#     move1 move2 move3 mov4  mov5
# A   5      5      5     1    5
# B   5      5      3     4    5
# C   4      3      2     1    5
# D   4      4      3     2    5
# E   4      4      3     2    4
# F   3      4      3     2    5

# 先已知G同学的对电影的评价如下(5,5,0,0,5) 0表示没有看过改电影

# 推荐策略:
#     基于用户：找到跟G口味相同的所有用户，把相似用户的看过的电影推荐给
#     基于商品：比如G正在看move2,你发现move7，move8跟movie2比较相似，所以在G看move2可以吧movie7，8也推荐给G

#     实际推荐策略是这两个策略结合的：

# 本文主要实现基于用户的口味的推荐策略：（从评分来侧面反映用户的相似度）

# 具体方案：
#     1.采用SVD分解矩阵，降低计算难度分解得到U矩阵，对角举证，VT矩阵
#     2.可视化U矩阵，VT矩阵
#     3.根据G同学的评分得到在U矩阵中的向量
#     4.计划U矩阵中与其他用户的相似度
#     5.相似用户看过的G没有看过的电影推荐给G

# 所需掌握技术:
#     1.SVD矩阵分解
#     2.相似度计算
#     3.matplotlib 数据可视化 及散点图标记
#     4.矩阵截取

# '''

import  numpy as np
from matplotlib import  pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch

np.set_printoptions(suppress=True)

USER_SCRORE=np.array(
    [
        [5,5,5,1,5],
        [5,5,3,4,5],
        [5,5,3,3,5],
        [4,4,3,2,8],
        [4,4,3,2,4],
        [3,4,3,2,5],
    ]
)

#已知G同学的看过的电影列表平飞，0表示没有看过
G=np.array([5,5,0,0,5])

#余玄相识度
def cos_similar(A,B):
    fz = float(A*B.T)
    fm = np.linalg.norm(A)*np.linalg.norm(B)
    return float(fz/fm)


#对矩阵进行奇异值分解
U,S,VT=np.linalg.svd(USER_SCRORE)

#计算需要的奇异值个数 ，奇异值个数为3时能保留原矩阵97%的信息
loss = sum(S[:3])/sum(S)

#此时
U = U[:,0:3]
S = np.array([
    [S[0],0,0],
    [0,S[1],0],
    [0,0,S[2]]
])
VT=VT[0:3,:].T


#可视化U,VT
fig = plt.figure(figsize=(4,4))  #长：8*2.54=20厘米  宽:8*2.54=20厘米
ax = fig.add_subplot(111,projection='3d')

#用户特征
for m in range(U.shape[0]):
    ax.scatter(U[m,0],U[m,1],U[m,2], color='blue', alpha=0.5)
    ax.text(U[m,0],U[m,1],U[m,2], '%s' % (str(m)), size=20, zorder=1,color='k')


#电影特征
for m in range(VT.shape[0]):
    ax.scatter(VT[m,0],VT[m,1],VT[m,2], color='red', alpha=0.5)
    ax.text(VT[m,0],VT[m,1],VT[m,2], '%s' % (str(m)), size=20, zorder=1,color='k')


ax.text(1,2,3,'3', size=20, zorder=1,color='k')

#plt.show()

#计算G同学的位置
G = np.mat(G)

G_P= G*VT*(np.mat(S).I)
m=0
ax.scatter(G_P[m,0],G_P[m,1],G_P[m,2], color='green', alpha=0.5)
ax.text(G_P[m,0],G_P[m,1],G_P[m,2], 'G', size=20, zorder=1,color='k')
plt.show()


#计算与每个用户的相识度
#G_P = G_P.getA()
#G_P = G_P[0,:]

paris=[]
for i in range(U.shape[0]):
    similar_rate = cos_similar(G_P,np.array([U[i,:]]))
    #print i+1,'similar is ',similar_rate
    paris.append([similar_rate,i])
#paris = np.mat(paris)
paris.sort(key=lambda x: x[0],reverse=True)
paris = np.mat(paris)  #找到相似用户，按相似度从小到大排序

'''
print "################################"

for i in range(USER_SCRORE.shape[0]):
    print i + 1, 'similar is ', cos_similar(G, np.array([USER_SCRORE[i, :]]))
'''

#取前三个相似用户
paris = paris[0:3,1]
G = G.A
G = G[0,:]

#找到相似用户看过的而G用户没有看过的
result=[]
for i in range(paris.shape[0]):
    index = int(paris[i,0])
    similar_user_movies = USER_SCRORE[index,:]
    for j in range(len(similar_user_movies)):
        user_movie = similar_user_movies[j]
        if user_movie>0  and G[j]==0:
            result.append(j)

result = list(set(result))

#输出最终推荐结果
print ('the recommend movie is ',result)