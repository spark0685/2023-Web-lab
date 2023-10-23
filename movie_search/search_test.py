import csv

def search_id(term):
    with open('movie_pl.csv', newline='', encoding='utf-8-sig') as csvfile:
        pl = csv.DictReader(csvfile)
        doc = []
        id_list = []
        for row in pl:
            if term == row['term']:
                #print(row[' docID'])
                doc = row[' docID']
                # 去除方括号并按逗号分隔字符串
                s = doc.strip('[]')
                id_list = s.split(', ')
                # 去除每个 id 号的引号
                id_list = [id.strip("'") for id in id_list]
                break
    return id_list
def Not(id_not):
    ID_not = []
    with open('movie.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['id'] not in id_not:
                ID_not.append(row['id'])
    #print(ID_not)
    # sort ID_not
    ID_not.sort()
    return ID_not
def And(id_and):
    ID_and = []
    if(len(id_and) == 0):
        return ID_and
    for i in range(len(id_and)):
        if i == 0:
            ID_and = id_and[i]
            #print("ID_and:", ID_and)
        else:
            if(len(id_and[i]) == 0):
                ID_and = []
                break
            m = 0
            n = 0
            while(m < len(ID_and) and n < len(id_and[i])):
                # print("m:", m, "n:", n)
                # print("ID_and[m]:", ID_and[m], "id_and[i][n]:", id_and[i][n])
                if ID_and[m] == id_and[i][n]:
                    m += 1
                    n += 1
                elif ID_and[m] < id_and[i][n]:
                    ID_and.pop(m)
                else:
                    n += 1
                # print("ID_and:", ID_and)
            if m < len(ID_and):
                for j in range(m, len(ID_and)):
                    ID_and.pop(m)
                # print("ID_and:", ID_and)
    return ID_and

def Or(id_or):
    ID_or = []
    if(len(id_or) == 0):
        return ID_or
    for i in range(len(id_or)):
        if i == 0:
            ID_or = id_or[i]
            #print("ID_or:", ID_or)
        else:
            if(len(id_or[i]) == 0):
                continue
            m = 0
            n = 0
            while(m < len(ID_or) and n < len(id_or[i])):
                if ID_or[m] == id_or[i][n]:
                    m += 1
                    n += 1
                elif ID_or[m] < id_or[i][n]:
                    m += 1
                else:
                    ID_or.insert(m, id_or[i][n])
                    m += 1
                    n += 1
            if n < len(id_or[i]):
                for j in range(n, len(id_or[i])):
                    ID_or.append(id_or[i][j])
    #print("ID_or:", ID_or)
    return ID_or
if __name__ =="__main__":
    input = input("请输入搜索内容：")
    term_and = input.split('|')
    # 得出and项的ID
    id_or = []
    for item_and in term_and:
        id_and = []
        term = item_and.split('&')
        #print(term)
        for item in term:
            #print(item)
            tag_not = 0
            if item[0] == '!' or item[0] == '！':
                tag_not = 1
                item = item[1:]
            id = search_id(item)
            if tag_not == 1:
                id = Not(id)
                #print("item:", item, "id:", id)
            id_and.append(id)
            #print(item, ":", id)
        #print(id_and)
        ID_and = And(id_and)
        #print(ID_and)
        id_or.append(ID_and)
    # 合并andx项ID日本&柯南&！魔术
    id_final = Or(id_or)
    # print(id_final)
    # 输出结果
    with open('movie.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        flag = 0
        num = 0
        for row in reader:
            if row['id'] in id_final:
                flag = 1
                num += 1
    #            print(row['id'])
                print("第", num, "条结果：")
                print(row['片名'])
                #print(row['作者'])
    #            print(row['出版社'])
    #            print(row['译者'])
    #            print(row['出版年'])
    #            print(row['豆瓣评分'])
    #            print(row['内容简介'])
    #            print(row['作者简介'])
        if flag == 0:
            print("无结果")