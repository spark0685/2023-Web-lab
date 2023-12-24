import pandas as pd
from tqdm import *
movie_id={}
movie_entity = {}
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
        
Graph=pd.read_csv(filepath_or_buffer="Graph.csv",usecols=['head_entity','relation','tail_entity'])
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

        
