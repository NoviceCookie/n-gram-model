from collections import Counter
import re

def segment(line,pos,word_list,tokens,maxLen):
    #求每个位置可能的分词
    if pos >=len(line):
        return
    last=pos
    if pos+maxLen>=len(line):
        last=len(line)
    else:
        last=pos+maxLen
    ok = False
    for i in range(pos,last+1)[:0:-1]:
        if line[pos:i] in tokens and i not in word_list[pos]:
            word_list[pos].append(i)
            segment(line,i,word_list,tokens,maxLen)
            ok=True
    if not ok and (pos+1) not in word_list[pos]:
        word_list[pos].append(pos+1)
        segment(line,pos+1,word_list,tokens,maxLen)

def cal_pro(word_a,word_b,wordlist,length=1,sum=1):
    #计算P(B|A)
    p=0
    if wordlist[word_a]==0:
        p=(wordlist[word_b]+1)/(sum+length)
    else:
        p=(wordlist[word_a+word_b]+1)/(wordlist[word_a]+length)
    return p
	
def foward(line,word_list,wordlist,length,sum,list_prob):
    #pos位置,通过词line[j,i]到达的概率[i,p,j]
    list_prob[0].append([0,1,-1])
    for i in range(len(line))[:]:#每个可能产生单词的位置，计算后一个单词结尾位置的概率
        if len(word_list[i]):
            for nextPos in word_list[i]:#i位置后的每个单词
                p=[i,0,0]
                for x in list_prob[i]:#计算P(a|b)概率，可能有多条路径,求其最大的路径概率
                    pro=x[1]*cal_pro(line[x[0]:i],line[i:nextPos],wordlist,length,sum)
                    if p[1]<pro:
                        p[1]=pro
                        p[2]=x[0]
                list_prob[nextPos].append(p)

def lineTowords(line,wordlist,tokens,maxLen,sum):
    #转换句子为单词序列
    word_list=[[]for _ in range(len(line))]
    list_prob=[[] for _ in range(len(line)+1)]
    segment(line,0,word_list,tokens,maxLen)
    foward(line,word_list,wordlist,len(tokens),sum,list_prob)
    x=[0,0,-1]
    for i in list_prob[len(line)]:#求最大概率
        if x[1]<=i[1]:
            x=i
    y=len(line)
    words = []
    while y>0:
        words.insert(0,line[x[0]:y])
        for m in list_prob[x[0]]:
            if m[0]==x[2]:
                y=x[0]
                x=m
                break
    return words

def lineTowords_2(line,wordlist,tokens,puns=[],maxLen=1,all_word=1):
    sentence = ''
    words=[]
    for w in line:
        if w in puns:
            if len(sentence):
                sub_words = lineTowords(sentence, wordlist, tokens, maxLen, all_word)
                words.extend(sub_words)
                words.append(w)
                sentence = ''
        else:
            sentence += w
    if len(sentence):
        sub_words = lineTowords(sentence, wordlist, tokens, maxLen, all_word)
        words.extend(sub_words)
    return words

wordlist = Counter()
with open('./北大(人民日报)语料库199801.txt','r',encoding='utf-8') as f:
    wordlines=[] #单词行
    puns=[]      #标点符号
    #记录每个单词的频率
    rex = r'./w'
    for line in f.readlines():
        line = line.strip()
        if line:
           words = [x.split('/')[0].strip('[]') for x in line.split('  ')[1:]]
           pun = [x.split('/')[0].strip('[]') for x in line.split('  ')[1:] if re.match(rex,x)]
           puns=list(set(pun).union(puns))
           wordlines.append(words)
           wordlist.update(words)
    #tokaens: 单词列表
    #all_word: 所有单词频率
    #maxLen: 最大单词长度
    tokens = list(wordlist.keys())
    all_word = sum(wordlist.values())
    maxLen = len(max(tokens, key=len))
    #计算近邻词的组合词频
    for line in wordlines:
        for i in range(len(line)-1):
            word = [line[i]+line[i+1]]
            wordlist.update(word)

    with open('./test.txt','r',encoding='utf-8') as t:
        with open('./result.txt','w',encoding='utf-8') as r:
            for line in t.readlines():
                words = lineTowords_2(line.strip(),wordlist,tokens,puns,maxLen,all_word)
                for i in words:
                    r.write(str(i)+' ')
                r.write('\n')