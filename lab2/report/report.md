# 2023-Web-lab2 



## 小组成员

- [王润泽](https://github.com//spark0685)

- [马彬](https://github.com//souracid)

- [卢昶宇](https://github.com//Lucy8179)



## 实验分工

- 卢昶宇：stage1图谱数据挖掘
- 王润泽：stage2代码补全
- 马彬：stage2模型训练与预测

## 实验内容简介

- #### stage1

  - 第一跳子图的生成
  - 第二跳子图的生成

- #### **stage2**

  - kg_final.txt的生成
  - loader_Embedding_based.py补全
  - Embedding_based.py补全
  - 模型训练与预测

  

## 实验内容介绍

### 第一跳子图的生成

我们先建立所给的电影的id和电影实体名称的映射，并创建和初始化第一跳子图三元组的集合Graph：

```python
movie_entity = {}
with open('douban2fb.txt', 'rb') as f:
    for line in f:
        line = line.strip()
        list = line.decode().split('\t')
        movie_entity[list[1]] = list[0]

Graph=pd.DataFrame({"head_entity":[],"relation":[],"tail_entity":[]})
```

然后读取freebase的数据集，将头实体是电影实体的三元组加进Graph中，同时确保三元组的每个实体都以"http://rdf.freebase.com/ns/"字符串开头，来保证图谱的质量：

```python
with gzip.open('freebase_douban.gz', 'rb') as f:
    for line in tqdm(f):
        line = line.strip()
        list = line.decode().split('\t')[:3]
        if(cons_str not in list[0]) or (cons_str not in list[2]):
            continue
        head = list[0][len(cons_str):].strip('>')
        if head in movie_entity.keys():
            Graph.loc[len(Graph)]=list
```

由于第一跳实体符合上述条件的不多，故可以直接在循环中用

```python
Graph.loc[len(Graph)]=list
```

直接添加到Graph中。但后面第二跳子图不能，因为符合条件的太多且该操作非常耗时。

初步得到第一跳子图后，分别对头尾实体和关系进行计数：

```python
delete_line=[]
head_count=Graph["head_entity"].value_counts()
tail_count=Graph["tail_entity"].value_counts()
relation_count=Graph["relation"].value_counts()
```

然后采取20核的设置，筛掉出现次数不超过50次的头实体和尾实体：

```python
line_index=0
for head_entity in Graph["head_entity"]: 
    if head_entity in head_count:
        head_num=head_count[head_entity]
    else:
        head_num=0
    if head_entity in tail_count:
        tail_num=tail_count[head_entity]
    else:
        tail_num=0
    total_num=head_num+tail_num
    if(total_num<20):
        if(line_index not in delete_line):
            delete_line.append(line_index)
    line_index=line_index+1

line_index = 0
for tail_entity in Graph["tail_entity"]: 
    if tail_entity in head_count:
        head_num=head_count[tail_entity]
    else:
        head_num=0
    if tail_entity in tail_count:
        tail_num=tail_count[tail_entity]
    else:
        tail_num=0
    total_num=head_num+tail_num
    if(total_num<20):
        if(line_index not in delete_line):
            delete_line.append(line_index)
    line_index=line_index+1
```

然后删掉出现次数小于50次的关系，重置索引值。

```python
line_index=0
for relation in Graph["relation"]: 
    total_num=relation_count[relation]
    if(total_num<50):
        if(line_index not in delete_line):
            delete_line.append(line_index)
    line_index=line_index+1

Graph.drop(index=delete_line,axis=0,inplace=True)
Graph.reset_index(drop=True, inplace=True)

```

### 第二跳子图的生成

先得到第一跳生成子图的尾实体集合：

```python
tail=Graph['tail_entity'].value_counts()
```

然后按照类似第一跳的方式初步得到第二条子图：

```python
Graph_2jump=pd.DataFrame({"head_entity":[],"relation":[],"tail_entity":[]})
i=0
Graph_2jump.to_csv("secondjump.gz",mode='w',compression="gzip")
with gzip.open('freebase_douban.gz', 'rb') as f:
    with gzip.open('secondjump.gz','ab') as fgz:
        for line in tqdm(f):
            wline=line
            line = line.strip()
            list = line.decode().split('\t')[:3]
            if(cons_str not in list[0]) or (cons_str not in list[2]):
                continue
            head = list[0]
            # print(head)
            if(head in tail):
                #print("find!")
                fgz.write(wline)
```

注意这里符合条件(即头实体是第一跳子图的尾实体)的三元组的数量太多，如果直接使用

```python
Graph_2jump.loc[len(Graph)]=list
```

会很慢(甚至可能一年也难跑完)，所以只能先以压缩的形式存到一个中间文件。然后先过滤掉出现超过 2w 次的实体和出现少于 50 次的关系：

```python
Graph_2jump=pd.DataFrame({"head_entity":[],"relation":[],"tail_entity":[]})
entity={}
relation={}
i=0
with gzip.open('secondjump.gz','rb') as f:
    for line in tqdm(f):
        i=i+1
        if(i==1):
            continue
        line = line.strip()
        list = line.decode().split('\t')[:3]
        if(list[0] in entity):
            entity[list[0]]=entity[list[0]]+1
        else:
            entity[list[0]]=1
        if(list[1] in relation):
            relation[list[1]]=relation[list[1]]+1
        else:
            relation[list[1]]=1
        if(list[2] in entity):
            entity[list[2]]=entity[list[2]]+1
        else:
            entity[list[2]]=1

delete_entity=[]
delete_relation=[]
# 对两跳子图的处理：先过滤掉出现超过 2w 次的实体和出现少于 50 次的关系；
for ett in entity:
    if(entity[ett]>20000):
        delete_entity.append(ett)
        
for rel in relation:
    if(relation[rel]<50):
        delete_relation.append(rel)
```

然后再采样 15 核的设置，同时只保留出现大于50次的关系，对两跳子图进行清洗：

```python
with gzip.open('secondjump.gz','rb') as f:
    for line in tqdm(f):
        i=i+1
        if(i==1):
            continue
        line = line.strip()
        list = line.decode().split('\t')[:3]
        if(list[0] in delete_entity or list[2] in delete_entity or list[1] in delete_relation):
            continue
        if(list[0] in entity):
            entity[list[0]]=entity[list[0]]+1
        else:
            entity[list[0]]=1
        if(list[1] in relation):
            relation[list[1]]=relation[list[1]]+1
        else:
            relation[list[1]]=1
        if(list[2] in entity):
            entity[list[2]]=entity[list[2]]+1
        else:
            entity[list[2]]=1
        
# 然后再采样 15 核的设置，同时只保留出现大于50次的关系，对两跳子图进行清洗
need_entity=[]
need_relation=[]
for ett in entity:
    if(entity[ett]>=15):
        need_entity.append(ett)
        
for rel in relation:
    if(relation[rel]>50):
        need_relation.append(rel)

```

最后根据根据筛选的实体和关系取出三元组，并加到之前的Graph.csv中。

```python
i=0
count = 0
Graph_2jump=pd.DataFrame({"head_entity":[],"relation":[],"tail_entity":[]})
with gzip.open('secondjump.gz','rb') as f:
    for line in tqdm(f):
        i=i+1
        if(i==1):
            continue
        line = line.strip()
        list = line.decode().split('\t')[:3]
        if not(list[1] in need_relation):
            continue
        if(list[0] in need_entity==False or list[2] in need_entity==False):
            continue
        else:
            #print(count)
            Graph_2jump.loc[len(Graph_2jump)] = list
            count=count+1
Graph_2jump.to_csv("Graph.csv",mode='a',header=False,index=False)
```

### kg_final.txt的生成

先分别得到电影实体到id，id到映射id的字典：

```python
with open('movie_id_map.txt','r') as f:
    for line in f:
        line = line.strip()
        list = line.split('\t')
        movie_id[list[0]] = list[1]
with open('douban2fb.txt', 'r') as f:
    for line in f:
        line=line.strip()
        list = line.split('\t')
        movie_entity[list[1]]=movie_id[list[0]]
```

然后先对Graph.csv生成对应的kg_final.txt:

```python
Graph=pd.read_csv(filepath_or_buffer="Graph.csv",usecols=['head_entity','relation','tail_entity'])
cons_str=r"<http://rdf.freebase.com/ns/"
writeline=""
other_entity={}
relation_map={}
with open("kg_final.txt",'w') as f:
    for index,row in Graph.iterrows():
        writeline=""
        head_entity=row.iloc[0][len(cons_str):].strip('>')
        relation=row.iloc[1]
        tail_entity=row.iloc[2][len(cons_str):].strip('>')
        
        if head_entity in movie_entity:
            writeline=writeline+str(movie_entity[head_entity])
        else:
            if head_entity in other_entity:
                writeline=writeline+str(other_entity[head_entity])
            else:
                val=len(other_entity)+len(movie_entity)
                other_entity[head_entity]=val
                writeline=writeline+str(other_entity[head_entity])
        
        writeline=writeline+" "
        if relation in relation_map:
            writeline=writeline+str(relation_map[relation])
        else:
            val=len(relation_map)
            relation_map[relation]=val
            writeline=writeline+str(relation_map[relation])
        
        writeline=writeline+" "
        if tail_entity in movie_entity:
            writeline=writeline+str(movie_entity[tail_entity])
        else:
            if tail_entity in other_entity:
                writeline=writeline+str(other_entity[tail_entity])
            else:
                val=len(other_entity)+len(movie_entity)
                other_entity[tail_entity]=val
                writeline=writeline+str(other_entity[tail_entity])
        
        writeline=writeline+"\n"
        f.write(writeline)
```

然后加上助教提供的tag信息：

```python
tag_Graph=pd.DataFrame({"head_entity":[],"relation":[],"tail_entity":[]})
write_list=[]
i=0
with open("Movie_tag.csv",encoding='utf-8') as f:
    for line in f:
        line = line.strip('"')
        list = line.split(',',1)
        #print(list)
        if list[0] in movie_id:
            write_list.append(list[0])
            write_list.append("tag")
            write_list.append(list[1])
            tag_Graph.loc[len(tag_Graph)]=write_list
            write_list.clear()
```

并在之前的kg_final.txt基础上追加tag信息：

```python
with open("kg_final.txt",'a') as f:
    for index,row in tag_Graph.iterrows():
        writeline=""
        head_entity=row.iloc[0]
        relation=row.iloc[1]
        tail_entity=row.iloc[2]
        writeline=writeline+str(movie_id[head_entity])
        writeline=writeline+" "
        if relation in relation_map:
            writeline=writeline+str(relation_map[relation])
        else:
            val=len(relation_map)
            relation_map[relation]=val
            writeline=writeline+str(relation_map[relation])
        
        writeline=writeline+" "
        if tail_entity in other_entity:
            writeline=writeline+str(other_entity[tail_entity])
        else:
            val=len(other_entity)+len(movie_entity)
            other_entity[tail_entity]=val
            writeline=writeline+str(other_entity[tail_entity])
        
        writeline=writeline+"\n"
        f.write(writeline)
```

生成对应的部分信息如下：

```tex
577 23 978
349 23 1233
456 23 1234
6 23 1235
453 23 1236
449 23 970
441 23 1237
442 23 1238
462 23 1239
2 23 1240
0 23 1241
334 23 1242
439 23 1243
1 23 1244
```

可以看到tag关系的映射为23。

### loader_Embedding_based.py补全

```python
import os
import random
import collections

import torch
import numpy as np
import pandas as pd

from data_loader.loader_base import DataLoaderBase


class DataLoader(DataLoaderBase):

    def __init__(self, args, logging):
        super().__init__(args, logging)

        self.cf_batch_size = args.cf_batch_size
        self.kg_batch_size = args.kg_batch_size
        self.test_batch_size = args.test_batch_size

        kg_data = self.load_kg(self.kg_file)
        self.construct_data(kg_data)
        self.print_info(logging)


    def construct_data(self, kg_data):
        '''
            kg_data 为 DataFrame 类型
        '''
        # 1. 为KG添加逆向三元组，即对于KG中任意三元组(h, r, t)，添加逆向三元组 (t, r+n_relations, h)，
        #    并将原三元组和逆向三元组拼接为新的DataFrame，保存在 self.kg_data 中。
        relations = len(kg_data['r'].unique())
        inverse_kg_data = kg_data.copy()
        inverse_kg_data['r'] += relations
        inverse_kg_data = inverse_kg_data[['t', 'r', 'h']]
        self.kg_data = pd.concat([kg_data, inverse_kg_data], ignore_index=True)

        # 2. 计算关系数，实体数和三元组的数量
        self.n_relations = len(self.kg_data['r'].unique())
        self.n_entities = len(set(kg_data['h']).union(set(kg_data['t'])))
        self.n_kg_data = len(self.kg_data)

        # 3. 根据 self.kg_data 构建字典 self.kg_dict ，其中key为h, value为tuple(t, r)，
        #    和字典 self.relation_dict，其中key为r, value为tuple(h, t)。
        self.kg_dict = collections.defaultdict(list)
        self.relation_dict = collections.defaultdict(list)
        for h, r, t in self.kg_data.values:
            self.kg_dict[h].append((t, r))
            self.relation_dict[r].append((h, t))
        

    def print_info(self, logging):
        logging.info('n_users:      %d' % self.n_users)
        logging.info('n_items:      %d' % self.n_items)
        logging.info('n_entities:   %d' % self.n_entities)
        logging.info('n_relations:  %d' % self.n_relations)

        logging.info('n_cf_train:   %d' % self.n_cf_train)
        logging.info('n_cf_test:    %d' % self.n_cf_test)

        logging.info('n_kg_data:    %d' % self.n_kg_data)
```

这段代码是一个数据加载器，用于加载知识图谱（Knowledge Graph，KG）数据和构建相应的字典。以下是对代码的中文介绍：

1. **初始化方法 (`__init__`)：**
   - 初始化数据加载器，继承自 `DataLoaderBase` 类。
   - 设置协同过滤（Collaborative Filtering，CF）和知识图谱（KG）的批处理大小，以及测试集的批处理大小。
   - 载入知识图谱数据，并调用 `construct_data` 和 `print_info` 方法。

2. **构建数据方法 (`construct_data`)：**
   - 为知识图谱数据添加逆向三元组，即对于每个三元组 $(h, r, t)$，添加逆向三元组 $(t, r + \text{relations}, h)$，其中 $\text{relations}$ 是关系的数量。
   - 将原始知识图谱数据和逆向知识图谱数据合并为新的数据框（DataFrame），保存在 `self.kg_data` 中。
   - 计算关系数量 (`self.n_relations`)，实体数量 (`self.n_entities`)，以及三元组的数量 (`self.n_kg_data`)。
   - 构建两个字典：`self.kg_dict`，其中键为头实体 `h`，值为包含尾实体 `t` 和关系 `r` 的元组；`self.relation_dict`，其中键为关系 `r`，值为包含头实体 `h` 和尾实体 `t` 的元组。

3. **打印信息方法 (`print_info`)：**
   - 输出数据的基本信息，包括用户数、物品数、实体数、关系数、训练集和测试集的大小以及知识图谱数据的数量。

这段代码主要用于数据的预处理，特别是对知识图谱数据的处理和构建相应的数据结构，以便在推荐系统中使用。通过逆向三元组的添加和字典的构建，它为推荐模型提供了关于实体和关系的丰富信息。

### Embedding_based.py补全

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


def _L2_loss_mean(x):
    return torch.mean(torch.sum(torch.pow(x, 2), dim=1, keepdim=False) / 2.)


class Embedding_based(nn.Module):

    def __init__(self, args, n_users, n_items, n_entities, n_relations):

        super(Embedding_based, self).__init__()
        self.use_pretrain = args.use_pretrain

        self.n_users = n_users
        self.n_items = n_items
        self.n_entities = n_entities
        self.n_relations = n_relations

        self.KG_embedding_type = args.KG_embedding_type

        self.embed_dim = args.embed_dim
        self.relation_dim = args.relation_dim

        self.cf_l2loss_lambda = args.cf_l2loss_lambda
        self.kg_l2loss_lambda = args.kg_l2loss_lambda

        self.user_embed = nn.Embedding(self.n_users, self.embed_dim)
        self.item_embed = nn.Embedding(self.n_items, self.embed_dim)
        nn.init.xavier_uniform_(self.user_embed.weight)
        nn.init.xavier_uniform_(self.item_embed.weight)

        self.entity_embed = nn.Embedding(self.n_entities, self.embed_dim)
        self.relation_embed = nn.Embedding(self.n_relations, self.relation_dim)
        nn.init.xavier_uniform_(self.entity_embed.weight)
        nn.init.xavier_uniform_(self.relation_embed.weight)

        # TransR 
        self.trans_M = nn.Parameter(torch.Tensor(self.n_relations, self.embed_dim, self.relation_dim))
        nn.init.xavier_uniform_(self.trans_M)


    def calc_kg_loss_TransR(self, h, r, pos_t, neg_t):
        """
        h:      (kg_batch_size)
        r:      (kg_batch_size)
        pos_t:  (kg_batch_size)
        neg_t:  (kg_batch_size)
        """
        r_embed = self.relation_embed(r)                                                # (kg_batch_size, relation_dim)
        W_r = self.trans_M[r]                                                           # (kg_batch_size, embed_dim, relation_dim)

        h_embed = self.entity_embed(h)                                                  # (kg_batch_size, embed_dim)
        pos_t_embed = self.entity_embed(pos_t)                                          # (kg_batch_size, embed_dim)
        neg_t_embed = self.entity_embed(neg_t)                                          # (kg_batch_size, embed_dim)

        # 1. 计算头实体，尾实体和负采样的尾实体在对应关系空间中的投影嵌入
        r_mul_h = torch.matmul(h_embed.unsqueeze(1), W_r).squeeze()                                                           # (kg_batch_size, relation_dim)
        r_mul_pos_t = torch.matmul(pos_t_embed.unsqueeze(1), W_r).squeeze()                                                                  # (kg_batch_size, relation_dim)
        r_mul_neg_t = torch.matmul(neg_t_embed.unsqueeze(1), W_r).squeeze()                                                            # (kg_batch_size, relation_dim)

        # 2. 对关系嵌入，头实体嵌入，尾实体嵌入，负采样的尾实体嵌入进行L2范数归一化
        r_embed = F.normalize(r_embed, p=2, dim=1)                                      # (kg_batch_size, relation_dim)
        r_mul_h = F.normalize(r_mul_h, p=2, dim=1)                                      # (kg_batch_size, relation_dim)
        r_mul_pos_t = F.normalize(r_mul_pos_t, p=2, dim=1)                              # (kg_batch_size, relation_dim)
        r_mul_neg_t = F.normalize(r_mul_neg_t, p=2, dim=1)                              # (kg_batch_size, relation_dim)

        # 3. 分别计算正样本三元组 (h_embed, r_embed, pos_t_embed) 和负样本三元组 (h_embed, r_embed, neg_t_embed) 的得分
        pos_score = torch.sum(r_embed * h_embed * pos_t_embed, dim=-1)                                                             # (kg_batch_size)
        neg_score = torch.sum(r_embed * h_embed * neg_t_embed, dim=-1)                                                                   # (kg_batch_size)

        # 4. 使用 BPR Loss 进行优化，尽可能使负样本的得分大于正样本的得分
        kg_loss =  -torch.mean(torch.log(torch.sigmoid(pos_score - neg_score)))

        l2_loss = _L2_loss_mean(r_mul_h) + _L2_loss_mean(r_embed) + _L2_loss_mean(r_mul_pos_t) + _L2_loss_mean(r_mul_neg_t)
        loss = kg_loss + self.kg_l2loss_lambda * l2_loss
        return loss


    def calc_kg_loss_TransE(self, h, r, pos_t, neg_t):
        """
        h:      (kg_batch_size)
        r:      (kg_batch_size)
        pos_t:  (kg_batch_size)
        neg_t:  (kg_batch_size)
        """
        r_embed = self.relation_embed(r)                                                # (kg_batch_size, relation_dim)
        
        h_embed = self.entity_embed(h)                                                  # (kg_batch_size, embed_dim)
        pos_t_embed = self.entity_embed(pos_t)                                          # (kg_batch_size, embed_dim)
        neg_t_embed = self.entity_embed(neg_t)                                          # (kg_batch_size, embed_dim)

        # 5. 对关系嵌入，头实体嵌入，尾实体嵌入，负采样的尾实体嵌入进行L2范数归一化
        r_embed = F.normalize(r_embed, p=2, dim=1)                                      # (kg_batch_size, relation_dim)
        h_embed = F.normalize(h_embed, p=2, dim=1)                                      # (kg_batch_size, embed_dim)
        pos_t_embed = F.normalize(pos_t_embed, p=2, dim=1)                              # (kg_batch_size, embed_dim)
        neg_t_embed = F.normalize(neg_t_embed, p=2, dim=1)                              # (kg_batch_size, embed_dim)

        # 6. 分别计算正样本三元组 (h_embed, r_embed, pos_t_embed) 和负样本三元组 (h_embed, r_embed, neg_t_embed) 的得分
        pos_score = -torch.norm(h_embed + r_embed - pos_t_embed, dim=-1)                                                                     # (kg_batch_size)
        neg_score = -torch.norm(h_embed + r_embed - neg_t_embed, dim=-1)                                                                     # (kg_batch_size)

        # 7. 使用 BPR Loss 进行优化，尽可能使负样本的得分大于正样本的得分
        kg_loss = -torch.mean(torch.log(torch.sigmoid(pos_score - neg_score)))

        l2_loss = _L2_loss_mean(h_embed) + _L2_loss_mean(r_embed) + _L2_loss_mean(pos_t_embed) + _L2_loss_mean(neg_t_embed)
        loss = kg_loss + self.kg_l2loss_lambda * l2_loss
        return loss


    def calc_cf_loss(self, user_ids, item_pos_ids, item_neg_ids):
        """
        user_ids:       (cf_batch_size)
        item_pos_ids:   (cf_batch_size)
        item_neg_ids:   (cf_batch_size)
        """
        user_embed = self.user_embed(user_ids)                                          # (cf_batch_size, embed_dim)
        item_pos_embed = self.item_embed(item_pos_ids)                                  # (cf_batch_size, embed_dim)
        item_neg_embed = self.item_embed(item_neg_ids)                                  # (cf_batch_size, embed_dim)

        item_pos_kg_embed = self.entity_embed(item_pos_ids)                             # (cf_batch_size, embed_dim)
        item_neg_kg_embed = self.entity_embed(item_neg_ids)                             # (cf_batch_size, embed_dim)
        
        # 8. 为 物品嵌入 注入 实体嵌入的语义信息
        item_pos_cf_embed =  item_pos_embed + item_pos_kg_embed                                                            # (cf_batch_size, embed_dim)
        item_neg_cf_embed =  item_neg_embed + item_neg_kg_embed                                                           # (cf_batch_size, embed_dim)

        pos_score = torch.sum(user_embed * item_pos_cf_embed, dim=1)                    # (cf_batch_size)
        neg_score = torch.sum(user_embed * item_neg_cf_embed, dim=1)                    # (cf_batch_size)

        cf_loss = (-1.0) * torch.log(1e-10 + F.sigmoid(pos_score - neg_score))
        cf_loss = torch.mean(cf_loss)

        l2_loss = _L2_loss_mean(user_embed) + _L2_loss_mean(item_pos_cf_embed) + _L2_loss_mean(item_neg_cf_embed)
        loss = cf_loss + self.cf_l2loss_lambda * l2_loss
        return loss


    def calc_loss(self, user_ids, item_pos_ids, item_neg_ids, h, r, pos_t, neg_t):
        """
        user_ids:       (cf_batch_size)
        item_pos_ids:   (cf_batch_size)
        item_neg_ids:   (cf_batch_size)

        h:              (kg_batch_size)
        r:              (kg_batch_size)
        pos_t:          (kg_batch_size)
        neg_t:          (kg_batch_size)
        """
        if self.KG_embedding_type == 'TransR':
            calc_kg_loss = self.calc_kg_loss_TransR
        elif self.KG_embedding_type == 'TransE':
            calc_kg_loss = self.calc_kg_loss_TransE
        
        kg_loss = calc_kg_loss(h, r, pos_t, neg_t)
        cf_loss = self.calc_cf_loss(user_ids, item_pos_ids, item_neg_ids)
        
        loss = kg_loss + cf_loss
        return loss


    def calc_score(self, user_ids, item_ids):
        """
        user_ids:  (n_users)
        item_ids:  (n_items)
        """
        user_embed = self.user_embed(user_ids)                                          # (n_users, embed_dim)

        item_embed = self.item_embed(item_ids)                                          # (n_items, embed_dim)
        item_kg_embed = self.entity_embed(item_ids)                                     # (n_items, embed_dim)

        # 9. 为 物品嵌入 注入 实体嵌入的语义信息
        item_cf_embed = item_embed + item_kg_embed                                                               # (n_items, embed_dim)

        cf_score = torch.matmul(user_embed, item_cf_embed.transpose(0, 1))              # (n_users, n_items)
        
        return cf_score


    def forward(self, *input, is_train):
        if is_train:
            return self.calc_loss(*input)
        else:
            return self.calc_score(*input)

```

这段代码定义了一个继承自 `nn.Module` 的推荐模型类 `Embedding_based`，其中包含了基于嵌入的推荐算法。以下是代码的中文介绍：

1. **初始化方法 (`__init__`)：**
   - 初始化推荐模型，包括用户、物品、实体和关系的数量等参数。
   - 定义了各种超参数，如嵌入维度、关系维度、损失函数权重等。
   - 创建了用户、物品、实体和关系的嵌入层，其中用户和物品使用标准的嵌入层，而实体和关系使用了额外的初始化和处理（如 TransR 中的 `trans_M` 参数）。

2. **TransR 算法损失计算方法 (`calc_kg_loss_TransR`)：**
   - 计算 TransR 算法中的知识图谱损失。
   - 根据模型参数和输入，计算正样本和负样本的得分。
   - 使用 BPR Loss 进行优化，最大化正样本得分与负样本得分之间的差异。
   - 包含 L2 范数归一化项，用于控制参数的大小。

3. **TransE 算法损失计算方法 (`calc_kg_loss_TransE`)：**
   - 类似于 TransR，但是计算方式稍有不同，通过计算向量范数来度量正样本和负样本的距离。

4. **协同过滤损失计算方法 (`calc_cf_loss`)：**
   - 计算协同过滤损失，包括正负样本的得分计算和 BPR Loss 的应用。
   - 将物品的嵌入与对应实体的嵌入相加，为物品嵌入注入了实体嵌入的语义信息。

5. **总体损失计算方法 (`calc_loss`)：**
   - 在训练阶段，同时计算知识图谱损失和协同过滤损失。

6. **得分计算方法 (`calc_score`)：**
   - 在预测阶段，计算用户与物品之间的得分，用于推荐。

7. **前向传播方法 (`forward`)：**
   - 根据是否为训练阶段选择调用 `calc_loss` 或 `calc_score` 方法。

这段代码实现了一个嵌入-based 的推荐模型，支持 TransR 和 TransE 两种知识图谱嵌入算法，以及协同过滤推荐。在训练阶段，同时优化知识图谱和协同过滤损失，而在预测阶段，通过计算用户和物品之间的得分来进行推荐。

### 模型训练与预测

#### baseline模型

我们配置了cuda相关工具，使用以下命令用gpu训练模型:

```shell
python -u "c:\Users\promise\Desktop\workspace\2023-Web-lab\lab2\stage2\main_KG_free.py" --cuda
```

训练结果如下：

![1](C:\Users\promise\Desktop\workspace\2023-Web-lab\lab2\report\fig\1.png)

#### 图谱嵌入模型

我们配置了cuda相关工具，使用以下命令用gpu训练模型:

```shell
python -u "c:\Users\promise\Desktop\workspace\2023-Web-lab\lab2\stage2\main_Embedding_based.py" --cuda
```

训练结果如下：

![2](C:\Users\promise\Desktop\workspace\2023-Web-lab\lab2\report\fig\2.png)

#### 预测结果分析

baseline模型

![1](C:\Users\promise\Desktop\workspace\2023-Web-lab\lab2\report\fig\1.png)

图谱嵌入模型![3](C:\Users\promise\Desktop\workspace\2023-Web-lab\lab2\report\fig\3.jpg)

|              | Recall@5 | Recall@10 | NDCG@5 | NDCG@10 |
| ------------ | -------- | --------- | ------ | ------- |
| baseline模型 | 0.0477   | 0.0857    | 0.2230 | 0.2149  |
| 图谱嵌入模型 | 0.0653   | 0.1128    | 0.3183 | 0.2915  |

根据表格的内容，图谱嵌入模型相较于基线模型在Recall@5、Recall@10、NDCG@5和NDCG@10这几个指标上都取得了更好的性能。这表明图谱嵌入模型在推荐任务上具有更好的效果，能够更准确地捕捉用户和物品之间的关系，提高了推荐的准确性和质量。

#### 现象解释

1. **更丰富的信息表示：** 图谱嵌入模型能够从知识图谱中学到更丰富的信息，包括实体和关系之间的语义关联。这使得模型能够更好地捕捉用户和物品之间的复杂关系，提高了推荐的准确性。
2. **关联性建模：** 图谱嵌入模型能够学到实体和关系之间的嵌入表示，从而更好地理解它们之间的关联性。这对于推荐系统来说是关键的，因为用户对物品的兴趣往往是通过它们在知识图谱中的关联来建模的。
3. **解决冷启动问题：** 知识图谱中的信息可以帮助解决冷启动问题，即对于新物品或新用户缺乏历史行为数据的情况。通过利用图谱中的相关信息，模型可以更好地推断出新物品或新用户的特性和兴趣。
4. **更好的泛化能力：** 图谱嵌入模型可能具有更好的泛化能力，能够在训练数据之外的数据上表现良好。这有助于提高推荐系统的实用性和适用性。
5. **对稀疏性的鲁棒性：** 知识图谱嵌入模型在处理稀疏数据时可能更为鲁棒，因为它们能够从相似实体或关系中获取有用的信息，从而降低了对完整数据的依赖性。