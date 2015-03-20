from os import listdir
from ast import literal_eval
from numpy import array
from scipy import stats
import csv

subjecta = raw_input("Subject Number: ")
subjectb = raw_input("Subject Number: ")
subjectc = raw_input("Subject Number: ")

rankingsa = "Subject %s/rankings.txt"%subjecta

rankingsb = "Subject %s/rankings.txt"%subjectb

rankingsc = "Subject %s/rankings.txt"%subjectc



with open(rankingsa) as f:
	data1 = f.read()
	data1 = data1.split('\n')
	data1 = [literal_eval(line) for line in data1]
	ranking1 = sorted(data1, key=lambda pair: pair[0:2])
	ordinal1 = [int(x[2]) for x in (ranking1)]
	rankA = array(ordinal1,ndmin=1)


with open(rankingsb) as f:
	data2 = f.read()
	data2 = data2.split('\n')
	data2 = [literal_eval(line) for line in data2]
	ranking2 = sorted(data2, key=lambda pair: pair[0:2])
	ordinal2 = [int(x[2]) for x in (ranking2)]
	rankB = array(ordinal2, ndmin=1)


with open(rankingsc) as f:
	data3 = f.read()
	data3 = data3.split('\n')
	data3 = [literal_eval(line) for line in data3]
	ranking3 = sorted(data3, key=lambda pair: pair[0:2])
	ordinal3 = [int(x[2]) for x in (ranking3)]
	print len(ordinal3)
	rankC = array(ordinal3, ndmin=1)

"""ranks = open("rankings.csv", 'wb')
writer = csv.writer(ranks, delimiter='\t')

for item in ranking1:
	writer.writerow(list(item[2]))


for item in ranking2:
	writer.writerow(list(item[2]))


for item in ranking3:
	writer.writerow(list(item[2]))

ranks.close()"""

rankings =[]
for ranking1,ranking2 in zip(ordinal1, ordinal2):
	ranking = abs(ranking1-ranking2)
	rankings.append(ranking)
print rankings

print stats.spearmanr(ordinal1,ordinal2)