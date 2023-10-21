import csv
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
if __name__ =="__main__":
	zip_interval("pl.csv","interval.csv")
	Recode(srcfile="interval.csv",destfile="plzip.csv")					
	unzip(srcfile="plzip.csv",destfile="pl_unzip.csv")