# coding=gb2312
import csv
import requests
import re
import random
import time
from bs4 import BeautifulSoup
class Movie_Crawler(object):
    status_code=200
    def __init__(self,filename,dest_filename,id_file,url):
        self.filename=filename
        self.dest_filename=dest_filename
        self.id_file=id_file
        self.url=url
    def load_id(self):
        id_list=[]
        with open(self.filename) as csvfile:
            csv_reader=csv.reader(csvfile)
            for row in csv_reader:
                id_list.append(row[0])
        return id_list
    def get_soup(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        cookies={"cookie":"BDUSS_BFESS=XNYSnhUNmgyWkdwRDUxSVI1OUQzVkczTzBtUXhkblRSMXJjclNQa3RvWUs3djFpRVFBQUFBJCQAAAAAAAAAAAEAAAC2~RNzemhlbmfWo7rNyPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAph1mIKYdZiW; BAIDUID_BFESS=38FC810DA13A861B9EC13E501C0C5CFF:FG=1; ZFY=XRQ1CCqlHfVAHJ1xViu4XbXFvjMixhy47aPqVucrCKI:C; ab_sr=1.0.1_NDQ4ODc1OGRiODJhNTQ0MmEzYmM0MWVjY2I3ZjViYWZiOTM3NzBlMjA0Y2Q0MWNhYjcxOWE4MDg0NzE5OTRhOWEwZTI0NjZkZTY0NjhmYmIxNWU1ODIyNmZhMjI3ODMyMmI2Y2JkNWQ5MDAwZDRkZTIzZjk5NzE1OTI1Y2U2N2E3NDIwYjE5OTVhMDE4OWFkZDAzNWQxMmY4OTgyMGRlNWRmMTg0OWE0YzZhMDZkMjg1YmM4NmIzY2Q4MmQ5N2Y2"}
        get_content=requests.get(self.url,headers=headers,cookies=cookies)
        self.status_code=get_content.status_code
        content=get_content.text
        self.soup=BeautifulSoup(content,"html.parser")
        return self.soup
    def file_write_first(self):
        # fieldname=["id","����","����","������","����","������","���ݼ��","���߼��","��������"]
        fieldname=["id","Ƭ��","��ӳ���","����","��������","����","���","����","����","����/����","����","ʱ��","���"]
        with open(self.dest_filename,'w',encoding="utf_8_sig",newline='') as destFile:
            destFile_csv=csv.DictWriter(destFile,fieldnames=fieldname)
            destFile_csv.writeheader()
    def file_write(self):
        info_list=[]
        id_list=self.load_id()
        # fieldname=["id","����","����","������","����","������","���ݼ��","���߼��","��������"]
        fieldname=["id","Ƭ��","��ӳ���","����","��������","����","���","����","����","����/����","����","ʱ��","���"]
        with open(self.id_file,'r') as id_file:
            idnum=int(id_file.read())
        with open(self.dest_filename,'a',encoding="utf_8_sig",newline='') as destFile:
            destFile_csv=csv.DictWriter(destFile,fieldnames=fieldname)
            for i in range(idnum,len(id_list)):
                time.sleep(2)
                self.url="https://movie.douban.com/subject/"+id_list[i]
                print(self.url)
                soup = self.get_soup()
                if(self.status_code!=200):
                    with open(self.id_file,'w') as id_file:
                        id_file.write(str(i))
                        print("\nYour request has been denied\n")
                        return
                # Ƭ��
                name = soup.find(attrs={'property': 'v:itemreviewed'}).text.split(' ')[0]
                # ��ӳ���
                year = soup.find(attrs={'class': 'year'}).text.replace('(','').replace(')','')
                # ����
                score0 = soup.find(attrs={'property': 'v:average'})
                if score0 is None:
                    score = '��'
                else :
                    score = score0.text
                # ��������
                votes0 = soup.find(attrs={'property': 'v:votes'})
                if votes0 is None:
                    votes = '��'
                else:
                    votes = votes0.text
                infos = soup.find(attrs={'id': 'info'}).text.split('\n')[1:11]
                # ����
                director = infos[0].split(': ')[1]
                # ���
                scriptwriter = infos[1].split(': ')[1]
                # ����
                actor = infos[2].split(': ')[1]
                # ����
                filmtype = infos[3].split(': ')[1]
                # ����/����
                area = infos[4].split(': ')[1]
                if '.' in area:
                    area = infos[5].split(': ')[1].split(' / ')[0]
                else:
                    area = infos[4].split(': ')[1].split(' / ')[0]
                # ����
                language = infos[5].split(': ')[1].split(' / ')[0]
                if '��½' in area or '���' in area or '̨��' in area:
                    area = '�й�'
                if '���' in area:
                    area = '����'
                # ʱ��
                times0 = soup.find(attrs={'property': 'v:runtime'})
                if times0 is None:
                    times = '��'
                else:
                    times = re.findall('\d+', times0.text)[0]
                # ���
                summary = soup.find(attrs={'property': 'v:summary'}).text
                info_list.append(str(id_list[i]))
                info_list.append(name)
                info_list.append(year)
                info_list.append(score)
                info_list.append(votes)
                info_list.append(director)
                info_list.append(scriptwriter)
                info_list.append(actor)
                info_list.append(filmtype)
                info_list.append(area)
                info_list.append(language)
                info_list.append(times)
                info_list.append(summary)
                print (i)
                print (info_list)
                destFile_csv.writerow(
                    {
                        "id":info_list[0],
                        "Ƭ��":info_list[1],
                        "��ӳ���":info_list[2],
                        "����":info_list[3],
                        "��������":info_list[4],
                        "����":info_list[5],
                        "���":info_list[6],
                        "����":info_list[7],
                        "����":info_list[8],
                        "����/����":info_list[9],
                        "����":info_list[10],
                        "ʱ��":info_list[11],
                        "���":info_list[12]
                    }
                )
                info_list.clear()
if __name__ =="__main__":
    filename="Movie_id.csv"
    dest_filename="test.csv"
    id_file="id.txt"
    url="https://.douban.com"
    movie=Movie_Crawler(filename=filename,dest_filename=dest_filename,id_file=id_file,url=url)
    flag="y"
    print("Do you want to rewrite the csv file?\tprint[y/n]")
    flag=input()
    if(flag == 'y'):
        movie.file_write_first()
    movie.file_write()
        
    
    
    


