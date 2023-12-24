import gzip
import pandas as pd
import pickle
from tqdm import *

#movie_id to movie_entity
movie_entity = {}
with open('douban2fb.txt', 'rb') as f:
    for line in f:
        line = line.strip()
        list = line.decode().split('\t')
        movie_entity[list[1]] = list[0]

Graph=pd.DataFrame({"head_entity":[],"relation":[],"tail_entity":[]})

#first jump
# debug=0
cons_str=r"<http://rdf.freebase.com/ns/"
with gzip.open('freebase_douban.gz', 'rb') as f:
    for line in tqdm(f):
        # debug = debug +1
        #print(debug)
        line = line.strip()
        list = line.decode().split('\t')[:3]
        if(cons_str not in list[0]) or (cons_str not in list[2]):
            continue
        head = list[0][len(cons_str):].strip('>')
        if head in movie_entity.keys():
            #print("Find one!")
            Graph.loc[len(Graph)]=list
        # if(debug == 10000000):
        #     break
delete_line=[]
head_count=Graph["head_entity"].value_counts()
tail_count=Graph["tail_entity"].value_counts()
relation_count=Graph["relation"].value_counts()

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
    
line_index=0
for relation in Graph["relation"]: 
    total_num=relation_count[relation]
    if(total_num<50):
        if(line_index not in delete_line):
            delete_line.append(line_index)
    line_index=line_index+1

Graph.drop(index=delete_line,axis=0,inplace=True)
Graph.reset_index(drop=True, inplace=True)

Graph.to_csv("firstjump.csv")
cons_str=r"<http://rdf.freebase.com/ns/"

Graph=pd.read_csv(filepath_or_buffer="firstjump.csv",usecols=["head_entity","relation","tail_entity"])
#second jump

tail=Graph['tail_entity'].value_counts()
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
# 然后再采样 15 核的设置，同时只保留出现大于50次的关系，对两跳子图进行清洗
for ett in entity:
    if(entity[ett]>20000):
        delete_entity.append(ett)
        
for rel in relation:
    if(relation[rel]<50):
        delete_relation.append(rel)

#print(len(relation),len(delete_relation))
print(len(entity),len(delete_entity))
        
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
        #print("hello")
        
# 然后再采样 20 核的设置，同时只保留出现大于50次的关系，对两跳子图进行清洗
need_entity=[]
need_relation=[]
for ett in entity:
    if(entity[ett]>=20):
        need_entity.append(ett)
        
for rel in relation:
    if(relation[rel]>50):
        need_relation.append(rel)

print(len(entity),len(need_entity),len(relation),len(need_relation))

with open("need_ett","wb") as tf:
    pickle.dump(need_entity, tf)
    
with open("need_rel","wb") as tf:
    pickle.dump(need_relation, tf)
    
with open("need_ett","rb") as tf:
    need_entity=pickle.load(tf)

with open("need_rel","rb") as tf:
    need_relation=pickle.load(tf)
    
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
Graph_2jump.to_csv("secondjump.csv",mode='w')
#print(count)

Graph_2jump=pd.read_csv(filepath_or_buffer="secondjump.csv")
Graph_2jump.to_csv("Graph.csv",mode='a',header=False,index=False)
