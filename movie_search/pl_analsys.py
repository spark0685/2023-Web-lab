import csv



if __name__ == '__main__':

    with open('movie_pl.csv', newline='', encoding='utf-8-sig') as csvfile:
        num = [0] * 100
        pl = csv.DictReader(csvfile)
        for row in pl:
            doc = row[' docID']

            s = doc.strip('[]')
            id_list = s.split(', ')

            id_list = [id.strip("'") for id in id_list]
            if(len(id_list) >= 100):
                num[99] = num[99] + 1
            else:
                num[len(id_list)] = num[len(id_list)] + 1
    print(num)

