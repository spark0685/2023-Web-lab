#coding=utf-8

# '''
# Ŀ�꣺�����򵥵�Ӱ�Ƽ�ϵͳ����������ABCDE 5��ͬѧ�������Ӱ֮�����������
#     move1 move2 move3 mov4  mov5
# A   5      5      5     1    5
# B   5      5      3     4    5
# C   4      3      2     1    5
# D   4      4      3     2    5
# E   4      4      3     2    4
# F   3      4      3     2    5

# ����֪Gͬѧ�ĶԵ�Ӱ����������(5,5,0,0,5) 0��ʾû�п����ĵ�Ӱ

# �Ƽ�����:
#     �����û����ҵ���G��ζ��ͬ�������û����������û��Ŀ����ĵ�Ӱ�Ƽ���
#     ������Ʒ������G���ڿ�move2,�㷢��move7��move8��movie2�Ƚ����ƣ�������G��move2���԰�movie7��8Ҳ�Ƽ���G

#     ʵ���Ƽ����������������Խ�ϵģ�

# ������Ҫʵ�ֻ����û��Ŀ�ζ���Ƽ����ԣ��������������淴ӳ�û������ƶȣ�

# ���巽����
#     1.����SVD�ֽ���󣬽��ͼ����Ѷȷֽ�õ�U���󣬶ԽǾ�֤��VT����
#     2.���ӻ�U����VT����
#     3.����Gͬѧ�����ֵõ���U�����е�����
#     4.�ƻ�U�������������û������ƶ�
#     5.�����û�������Gû�п����ĵ�Ӱ�Ƽ���G

# �������ռ���:
#     1.SVD����ֽ�
#     2.���ƶȼ���
#     3.matplotlib ���ݿ��ӻ� ��ɢ��ͼ���
#     4.�����ȡ

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

#��֪Gͬѧ�Ŀ����ĵ�Ӱ�б�ƽ�ɣ�0��ʾû�п���
G=np.array([5,5,0,0,5])

#������ʶ��
def cos_similar(A,B):
    fz = float(A*B.T)
    fm = np.linalg.norm(A)*np.linalg.norm(B)
    return float(fz/fm)


#�Ծ����������ֵ�ֽ�
U,S,VT=np.linalg.svd(USER_SCRORE)

#������Ҫ������ֵ���� ������ֵ����Ϊ3ʱ�ܱ���ԭ����97%����Ϣ
loss = sum(S[:3])/sum(S)

#��ʱ
U = U[:,0:3]
S = np.array([
    [S[0],0,0],
    [0,S[1],0],
    [0,0,S[2]]
])
VT=VT[0:3,:].T


#���ӻ�U,VT
fig = plt.figure(figsize=(4,4))  #����8*2.54=20����  ��:8*2.54=20����
ax = fig.add_subplot(111,projection='3d')

#�û�����
for m in range(U.shape[0]):
    ax.scatter(U[m,0],U[m,1],U[m,2], color='blue', alpha=0.5)
    ax.text(U[m,0],U[m,1],U[m,2], '%s' % (str(m)), size=20, zorder=1,color='k')


#��Ӱ����
for m in range(VT.shape[0]):
    ax.scatter(VT[m,0],VT[m,1],VT[m,2], color='red', alpha=0.5)
    ax.text(VT[m,0],VT[m,1],VT[m,2], '%s' % (str(m)), size=20, zorder=1,color='k')


ax.text(1,2,3,'3', size=20, zorder=1,color='k')

#plt.show()

#����Gͬѧ��λ��
G = np.mat(G)

G_P= G*VT*(np.mat(S).I)
m=0
ax.scatter(G_P[m,0],G_P[m,1],G_P[m,2], color='green', alpha=0.5)
ax.text(G_P[m,0],G_P[m,1],G_P[m,2], 'G', size=20, zorder=1,color='k')
plt.show()


#������ÿ���û�����ʶ��
#G_P = G_P.getA()
#G_P = G_P[0,:]

paris=[]
for i in range(U.shape[0]):
    similar_rate = cos_similar(G_P,np.array([U[i,:]]))
    #print i+1,'similar is ',similar_rate
    paris.append([similar_rate,i])
#paris = np.mat(paris)
paris.sort(key=lambda x: x[0],reverse=True)
paris = np.mat(paris)  #�ҵ������û��������ƶȴ�С��������

'''
print "################################"

for i in range(USER_SCRORE.shape[0]):
    print i + 1, 'similar is ', cos_similar(G, np.array([USER_SCRORE[i, :]]))
'''

#ȡǰ���������û�
paris = paris[0:3,1]
G = G.A
G = G[0,:]

#�ҵ������û������Ķ�G�û�û�п�����
result=[]
for i in range(paris.shape[0]):
    index = int(paris[i,0])
    similar_user_movies = USER_SCRORE[index,:]
    for j in range(len(similar_user_movies)):
        user_movie = similar_user_movies[j]
        if user_movie>0  and G[j]==0:
            result.append(j)

result = list(set(result))

#��������Ƽ����
print ('the recommend movie is ',result)