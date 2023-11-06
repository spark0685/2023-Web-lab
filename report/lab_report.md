# 豆瓣书籍爬虫

## 爬取方法

本实验使用python语言，采用requests包将豆瓣网页html文本爬取下来，并用BeautifulSoup解析器和re正则表达式来解析爬取内容。

## 爬取过程

### 爬取豆瓣图书html文本

先从csv文件读取书籍的id号，得到书籍的url地址，再用url地址获得网页html文本内容。爬取时需要加入headers和cookies信息来模仿普通人访问网页的行为，以避免被豆瓣网站禁止访问。

```python
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
        soup=BeautifulSoup(content,"html.parser")
        return soup
```

### 内容解析

得到爬取下列的html文本后，用BeautifulSoup解析书名和基本信息：

```python
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
```

由于豆瓣图书的html文本对作者、出版社、译者等信息没有加入特殊标签，所以使用BeautifulSoup较难将这些信息分类解析出来，所以这里使用正则表达式来解析作者、出版社、译者、出版年。

```python
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
```

书籍简介和作者简介则依然使用BeautifulSoup来解析，解析时用迭代来把所有相关信息（包括点开更多后的信息）提取出来：

```python
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
                    if(info_string.string is None):
                        continue
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
                        if(intro_string.string is None):
                            continue
                        ans+=intro_string.string
        if(len(ans)==0):
            return "无"
        else:
            return ans
    def get_rating(self):
        soup=self.get_soup()
        #<strong class="ll rating_num " property="v:average"> 8.6 </strong>
        rating=soup.findAll("strong",attrs={"property":"v:average"})
        if(rating is None):
            return "无"
        else:
            if(len(rating)==0):
                return "无"
            return rating[0].string
```

### 输出csv文件

本实验用csv库，用字典按列写入csv文件：

```python
    def file_write(self):
        info_list=[]
        id_list=self.load_id()
        fieldname=["id","书名","作者","出版社","译者","出版年","内容简介","作者简介","豆瓣评分"]
        with open(self.id_file,'r') as id_file:
            idnum=int(id_file.read())
        with open(self.dest_filename,'a',encoding="utf_8_sig",newline='') as destFile:
            destFile_csv=csv.DictWriter(destFile,fieldnames=fieldname)
            for i in range(idnum,len(id_list)):
                if(self.status_code!=200):
                    with open(self.id_file,'w') as id_file:
                        id_file.write(str(i))
                        print("\nYour request has been denied\n")
                        return
                self.url="https://book.douban.com/subject/"+id_list[i]
                info_list.append(str(id_list[i]))
                info_list.append(self.get_book_name())
                info_list.append(self.get_author_name())
                info_list.append(self.get_translator_name())
                info_list.append(self.get_pub_year())
                info_list.append(self.get_press_name())
                info_list.append(self.get_book_intro())
                info_list.append(self.get_author_intro())
                info_list.append(self.get_rating())
                destFile_csv.writerow(
                    {
                        "id":info_list[0],
                        "书名":info_list[1],
                        "作者":info_list[2],			
                        "译者":info_list[3],
                        "出版年":info_list[4],
                          "出版社":info_list[5],
                        "内容简介":info_list[6],
                        "作者简介":info_list[7],
                        "豆瓣评分":info_list[8]
                    }
                )
                info_list.clear()
```

### 爬取效果

除了少数几个网页无法访问外，其他豆瓣书籍均能将信息完整爬取和解析出来。爬取示例：(由于该书籍简介有展开全部，所以一些内容有重复，考虑到后面倒排表构建不考虑词频，所以此处无影响)

| id      | 书名       | 作者          | 出版社         | 译者   | 出版年 | 内容简介                                                     | 作者简介                                                     | 豆瓣评分 |
| ------- | ---------- | ------------- | -------------- | ------ | ------ | ------------------------------------------------------------ | ------------------------------------------------------------ | -------- |
| 1046265 | 挪威的森林 | [日] 村上春树 | 上海译文出版社 | 林少华 | 2001-2 | 这是一部动人心弦的、平缓舒雅的、略带感伤的恋爱小说。小说主人公渡边以第一人称展开他同两个女孩间的爱情纠葛。渡边的第一个恋人直子原是他高中要好同学木月的女友，后来木月自杀了。一年后渡边同直子不期而遇并开始交往。此时的直子已变得娴静腼腆，美丽晶莹的眸子里不时掠过一丝难以捕捉的阴翳。两人只是日复一日地在落叶飘零的东京街头漫无目标地或前或后或并肩行走不止。直子20岁生日的晚上两人发生了性关系，不料第二天直子便不知去向。几个月后直子来信说她住进一家远在深山里的精神疗养院。渡边前去探望时发现直子开始带有成熟女性的丰腴与娇美。晚间两人虽同处一室，但渡边约束了自己，分手前表示永远等待直子。返校不久，由于一次偶然相遇，渡边开始与低年级的绿子交往。绿子同内向的直子截然相反，“简直就像迎着春天的晨光蹦跳到世界上来的一头小鹿”。这期间，渡边内心十分苦闷彷徨。一方面念念不忘直...(展开全部)这是一部动人心弦的、平缓舒雅的、略带感伤的恋爱小说。小说主人公渡边以第一人称展开他同两个女孩间的爱情纠葛。渡边的第一个恋人直子原是他高中要好同学木月的女友，后来木月自杀了。一年后渡边同直子不期而遇并开始交往。此时的直子已变得娴静腼腆，美丽晶莹的眸子里不时掠过一丝难以捕捉的阴翳。两人只是日复一日地在落叶飘零的东京街头漫无目标地或前或后或并肩行走不止。直子20岁生日的晚上两人发生了性关系，不料第二天直子便不知去向。几个月后直子来信说她住进一家远在深山里的精神疗养院。渡边前去探望时发现直子开始带有成熟女性的丰腴与娇美。晚间两人虽同处一室，但渡边约束了自己，分手前表示永远等待直子。返校不久，由于一次偶然相遇，渡边开始与低年级的绿子交往。绿子同内向的直子截然相反，“简直就像迎着春天的晨光蹦跳到世界上来的一头小鹿”。这期间，渡边内心十分苦闷彷徨。一方面念念不忘直子缠绵的病情与柔情，一方面又难以抗拒绿子大胆的表白和迷人的活力。不久传来直子自杀的噩耗，渡边失魂魄地四处徒步旅行。最后，在直子同房病友玲子的鼓励下，开始摸索此后的人生。 | 村上春树（1949-  ），日本小说家。曾在早稻田大学文学部戏剧科就读。1979年，他的第一部小说《听风之歌》问世后，即被搬上了银幕。随后，他的优秀作品《1973年的弹子球》、《寻羊冒险记》、《挪威的森林》等相继发表。他的创作不受传统拘束，构思新奇，行文潇洒自在，而又不流于庸俗浅薄。尤其是在刻画人的孤独无奈方面更有特色，他没有把这种情绪写成负的东西，而是通过内心的心智性操作使之升华为一种优雅的格调，一种乐在其中的境界，以此来为读者，尤其是生活在城市里的人们提供了一种生活模式或生命的体验。 | 8.1      |

# 索引压缩

### 压缩方法

本实验采用前端编码的方式来压缩索引(文档id)，先将文档ID转化为文档之间的间隔，即相邻两个文档ID之差，再使用前端编码的方式进行压缩。

### 压缩过程

先得到文档间距的中间文件：

```python
def zip_interval(srcfile,destfile):
    #按照文档id间距压缩
	with open(file=srcfile, mode='r',encoding="utf_8_sig") as src:
		reader=csv.reader(src)
		result=list(reader)
		with open(file=destfile, mode='w',encoding="utf_8_sig",newline='') as dest:
			writer=csv.writer(dest)
			write_list=[]
			for i in range(1,len(result)):
				pl_row=result[i]
				write_list.append(pl_row[0])
				id_list=pl_row[1].strip('[').strip(']').split(',')
				for j in range(0,len(id_list)):
					if j==0:
						write_list.append(eval(id_list[j]))
					else:
						id_num=int(eval(id_list[j]))-int(eval(id_list[j-1]))
						write_list.append(str(id_num))
				writer.writerow(write_list)
				write_list.clear()
```

再进行前端编码压缩。注意到csv文件是unicode编码，而unicode编码最小单位是16位，这里将ID数字拆成以12位(4095)为单位，第16位设置为延续位。比如数字5000的二进制位：0001001110001000，以12位为单元分割为：

0001，0001 1100 0100

设置延续位(标黑)：

 0000 0000 0000 0001，**1**000 0001 1100 0100

这样将一个数字字符串转化为2个unicode字符。

压缩编码代码为：

```python
def encode(num,base=32):
    #前端编码
    #编码方式为Unicode
    string=""
    while(num>4095):
        low7bits=num%4096 #取num的低12位
        string=string+chr(4096+low7bits+base)
        num=num>>12
    if num<=4095:
        return string+chr(num+base)
def Recode(srcfile,destfile):
    #对间隔id进行前端编码
	with open(file=srcfile, mode='r',encoding="utf_8_sig") as src:
		reader=csv.reader(src)
		result=list(reader)
		with open(file=destfile, mode='w',encoding="utf_8_sig",newline='') as dest:
			writer=csv.writer(dest)
			write_list=[]
			for i in range(0,len(result)):
				src_row=result[i]
				write_list.append(src_row[0])
				for j in range(1,len(src_row)):
					write_list.append(encode(int(src_row[j]),base=32))
				writer.writerow(write_list)
				write_list.clear()
```

注意到Unicode前面32位字符为控制字符，不利于输出和后面的解码，所以加了base，编码从base开始进行，这也是为什么取12位为单位而非15位的原因。

解码则是根据unicode字符数值对文档ID进行还原：

```python
def decode(string,base=32):
	num=0
	for i in range(0,len(string)):
		charnum=ord(string[i])-base
		#print("charnum is "+str(charnum)+"\n")
		if(charnum>4095):
			num+=(charnum-4096)*(4096**i)
		else:
			num+=(charnum)*(4096**i)
	return num
def unzip(srcfile,destfile):
    #解压回原文件
	header=["term"," docID"]
	with open(file=srcfile, mode='r',encoding="utf_8_sig") as src:
		reader=csv.reader(src)
		result=list(reader)
		with open(file=destfile, mode='w',encoding="utf_8_sig",newline='') as dest:
			writer=csv.writer(dest)
			writer.writerow(header)
			write_list=[]
			for src_row in result:
				write_list.append(src_row[0])
				write_string=""
				num=0
				for i in range(1,len(src_row)):
					num+=decode(src_row[i],base=32)
					write_string+="\'"+str(num)+"\'"
					if i==1:
						write_string="["+write_string
					if i==len(src_row)-1:
						write_string=write_string+"]"
					else:
						write_string=write_string+", "
				write_list.append(write_string)
				writer.writerow(write_list)
				write_list.clear()
```

### 压缩效果

以豆瓣图书倒排表为例,压缩前：

![](..\fig\屏幕截图 2023-11-04 112621.png)

生成的文档间距文件interval.csv和压缩文件plzip.csv：

![](..\fig\屏幕截图 2023-11-04 112837.png)

可以得到压缩率为:
$$
\frac{1435KB}{2735KB}\times100\%=52.468\%
$$
比较解压后的文件plunzip.csv和原文件pl.csv，可得两者文件完全相同：

![](..\fig\屏幕截图 2023-11-04 113308.png)

# 豆瓣推荐

## K-近邻算法预测评分

### 算法原理

- 1, 计算训练样本和测试样本中每个样本点的距离（常见的距离度量有欧式距离，马氏距离等）；
-  2, 对上面所有的距离值进行排序；
-  3, 选前k个最小距离的样本；
-  4, 根据这k个样本的标签进行投票，得到最后的分类类别；

## 预测过程

### 预处理数据

由于K-近邻算法基于计算样本点之间的距离，所以样本数据必须为数字，不能包含字符串等其他格式。

这里，我们只采用book_score.csv或movie_score.csv文件的信息，包含：

- 用户ID
- 书籍/电影ID
- 评分
- 时间
- Tag

进行预处理时，考虑到不同用户对同一类物品的差距可能很大，为了反应这一差距，直接将用户ID数字串转换为数字。同理，对于书籍ID也进行类似操作。对于时间，只取小时部分。而对于评论的标签，考虑到同一评论的Tag相似，直接按照顺序进行映射。由于大多数用户评论的tag较少，只取用户评论的前4个Tag，如下为预处理数据的过程：

```python
#预处理阶段
loaded_data=pd.read_csv('data\\book_score.csv')
All_Tag=[]
maxlen=0
Tag1_list=[]
Tag2_list=[]
Tag3_list=[]
Tag4_list=[]
Time_hour=[]
User_list=[]
User_id=[]
item_list=[]
item_id=[]
with open(file="data\\book_score.csv",encoding="utf-8-sig") as f:
    reader=csv.reader(f)
    result=list(reader)
    for i in range(1,len(result)):
        row=result[i]
        tag_list=list(row[4].split(","))
        time=str(row[3])
        Time_hour.append(int(time[11:13]))
        if(row[0] in User_list) is False:
            User_list.append(row[0])
        User_id.append(User_list.index(row[0]))
        if(row[1] in User_list) is False:
            item_list.append(row[1])
        item_id.append(item_list.index(row[1]))
        if(len(tag_list)==0):
            continue
        if(len(tag_list)>maxlen):
            maxlen=len(tag_list)
        for tag in tag_list:
            if((tag in All_Tag) is False):
                All_Tag.append(tag)
        if(len(tag_list)==0):
            Tag1_list.append(0)
            Tag2_list.append(0)
            Tag3_list.append(0)
            Tag4_list.append(0)
        if len(tag_list)==1:
            Tag1_list.append(All_Tag.index(tag_list[0]))
            Tag2_list.append(0)
            Tag3_list.append(0)
            Tag4_list.append(0)
        if len(tag_list)==2:
            Tag1_list.append(All_Tag.index(tag_list[0]))
            Tag2_list.append(All_Tag.index(tag_list[1]))
            Tag3_list.append(0)
            Tag4_list.append(0)
        if len(tag_list)==3:
            Tag1_list.append(All_Tag.index(tag_list[0]))
            Tag2_list.append(All_Tag.index(tag_list[1]))
            Tag3_list.append(All_Tag.index(tag_list[2]))
            Tag4_list.append(0)
        if len(tag_list)>=4:
            Tag1_list.append(All_Tag.index(tag_list[0]))
            Tag2_list.append(All_Tag.index(tag_list[1]))
            Tag3_list.append(All_Tag.index(tag_list[2]))
            Tag4_list.append(All_Tag.index(tag_list[3]))
loaded_data["Tag1"]=Tag1_list
loaded_data["Tag2"]=Tag2_list
loaded_data["Tag3"]=Tag3_list
loaded_data["Tag4"]=Tag4_list
loaded_data["Time_hour"]=Time_hour
loaded_data["User_id"]=User_id
loaded_data["item_id"]=item_id
loaded_data.to_csv("pretreat.csv")

```

### 数据集划分

使用train_test_split()函数，将源文件随机打乱，训练集和测试集大小均为50%。

```python
#分割数据集
loaded_data=pd.read_csv('pretreat.csv')
train_data, test_data = train_test_split(loaded_data, test_size=0.5, random_state=42,shuffle=True)
test_data=pd.DataFrame(test_data)
test_data.sort_values(by=["User","Rate"],ascending=[True,False],inplace=True)
test_data.to_csv("test.csv",index=False)
```

### 训练和预测

使用sklearn的**KNeighborsClassifier**模型进行训练和预测，并使用accuracy_score()进行简单评估。

```python
#训练
train=train_data[["User","Tag1","Tag2","Tag3","Tag4","Time_hour"]]
target=train_data["Rate"]
knn=KNeighborsClassifier(n_neighbors=20,weights="distance",algorithm="auto",leaf_size=30)
knn.fit(train,target)
#预测
x_test=test_data[["User","Tag1","Tag2","Tag3","Tag4","Time_hour"]]
y_test=test_data["Rate"]
y_predict=knn.predict(x_test)
test_data["Rate"]=y_predict
test_data.sort_values(by=["User","Rate"],ascending=[True,False],inplace=True)
test_data.to_csv("predict.csv",index=False)
print(accuracy_score(y_test,y_predict)) #简单评估预测准确率
```

我们发现，如果同时使用User和Book的ID信息，得到的预测分数只有0.39。但如果去掉Book这一列信息，预测分数会显著增加到0.57。但是当去掉其他列信息，得到的分数不仅不会显著增加，反而可能减少。猜测原因是，对于同一本书，不同的用户预测分数可能有很大差异，所以最终使用：

- 用户ID
- 时间
- Tag(前4项)
- 评分

这些信息。
