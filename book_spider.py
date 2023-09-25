import csv
import requests
import re
import random
from bs4 import BeautifulSoup
class Book_Crawler:
	def __init__(self,filename,dest_filename,url):
		self.filename=filename
		self.dest_filename=dest_filename
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
		content=requests.get(self.url,headers=headers,cookies=cookies).text
		soup=BeautifulSoup(content,"html.parser")
		return soup
	def get_book_name(self):
		soup=self.get_soup()
		all_book_name=soup.findAll("span",attrs={"property":"v:itemreviewed"})
		if(len(all_book_name)==0):
			return "Not find"
		else:
			return all_book_name[0].string
	def get_basic_info(self):
		soup=self.get_soup()
		basic_info=str(soup.findAll("div",attrs={"id":"info"})).strip()
		return basic_info
	def get_author_name(self):
		book_info=self.get_basic_info()
		author_index=re.compile(r'.*?作者.*?<a.*?href.*?">(.*?)<',re.S)
		author=re.findall(author_index,book_info)
		if(len(author)==0):
			return "无"
		else:
			return author[0]
	def get_press_name(self):
		book_info=self.get_basic_info()
		press_index=re.compile(r'.*?出版社.*?<a.*?href.*?">(.*?)<',re.S)
		press=re.findall(press_index,book_info)
		if(len(press)==0):
			return "无"
		else:
			return press[0]
	def get_translator_name(self):
		book_info=self.get_basic_info()
		translator_index=re.compile(r'.*?译者.*?<a.*?href.*?">(.*?)<',re.S)
		translator=re.findall(translator_index,book_info)
		if(len(translator)==0):
			return "无"
		else:
			return translator[0]
	def get_pub_year(self):
		book_info=self.get_basic_info()
		pub_index=re.compile(r'.*?出版年.*?pan>(.*?)<b',re.S)
		pub_year=re.findall(pub_index,book_info)
		if(len(pub_year)==0):
			return "无"
		else:
			return pub_year[0]
	def get_related_info(self):
		soup=self.get_soup()
		related_info=str(soup.findAll("div",attrs={"class":"related_info"})).strip()
		return related_info
	def get_book_intro(self):
		soup=self.get_soup()
		book_info=soup.findAll("div",attrs={"class":"indent","id":"link-report"})
		ans=""
		if(book_info is None):
			return "无"
		for index in book_info:
			book_intro=index.findAll("p")
			if(book_intro is None):
				continue
			for info_string in book_intro:
				if((info_string is None)==False):
					ans+=info_string.string
		if(len(ans)==0):
			return "无"
		else:
			return ans
	def get_author_intro(self):
		soup=self.get_soup()
		book_info=soup.findAll("div",attrs={"class":"indent","id":""})
		ans=""
		for index in book_info:
			info=index.findAll("div",attrs={"class":"intro"})
			if(info is None):
				continue
			for info_string in info:
				intro=info_string.findAll("p")
				if(intro is None):
					continue
				else:
					for intro_string in intro:
						ans+=intro_string.string
		if(len(ans)==0):
			return "无"
		else:
			return ans
	def file_write(self):
		info_list=[]
		id_list=self.load_id()
		fieldname=["书名","作者","出版社","译者","出版年","内容简介","作者简介"]
		with open(self.dest_filename,'w',encoding="utf_8_sig",newline='') as destFile:
			destFile_csv=csv.DictWriter(destFile,fieldnames=fieldname)
			destFile_csv.writeheader()
			rand=random.randint(1,300)
			for i in range(rand,rand+2):
				self.url="https://book.douban.com/subject/"+id_list[i]
				info_list.append(self.get_book_name())
				info_list.append(self.get_author_name())
				info_list.append(self.get_translator_name())
				info_list.append(self.get_pub_year())
				info_list.append(self.get_press_name())
				info_list.append(self.get_book_intro())
				info_list.append(self.get_author_intro())
				destFile_csv.writerow(
					{
						"书名":info_list[0],
						"作者":info_list[1],			
						"译者":info_list[2],
						"出版年":info_list[3],
      					"出版社":info_list[4],
						"内容简介":info_list[5],
						"作者简介":info_list[6]
					}
				)
				info_list.clear()
if __name__ =="__main__":
    s = requests.Session()
    filename="Book_id.csv"
    dest_filename="test.csv"
    url="https://book.douban.com"
    book=Book_Crawler(filename=filename,dest_filename=dest_filename,url=url)
    book.file_write()
        
    
	
    


