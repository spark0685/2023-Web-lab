## 实验二 

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

## kg_final.txt的生成

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