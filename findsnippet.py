'''
Created on Nov 13, 2013
@author: Vivek
'''
import re, string,math,operator
from trie import Trie

class makeSnippet(object):

    def __init__(self):
        self.wordMap = dict()
        self.trie = Trie()
        self.queryWordList = list()
        self.rawSentences = None

    def buildTokens(self,document):
        docID=0
        self.rawSentences = self.clean(document)
        for sentence in self.rawSentences:
            words = self.tokenize(sentence)
            docID+=1
            self.wordMap[docID] = words

    def tokenize(self,sentence):
        return [word for word in re.compile(r'(\W)').split(re.compile('[%s]' % re.escape(string.punctuation)).sub('',sentence).lower()) if len(word.strip())>0]

    def clean(self,document):
        return [sentence for sentence in tuple(re.compile(r'[.!?\n\r]').split(document)) if sentence]

    def tf(self,word,docID):
        return (self.trie.getDocMap(word)[docID] / float(self.wordCount(docID)))

    def findidf(self,word):
        n= len(self.wordMap)
        df= self.trie.getDocFrequency(word)
        if df == 0:
            df=1
        if n<df:
            return 0.0
        return math.log(n/float(df))

    def tfidf(self,word,docID):
        return self.tf(word,docID)*self.findidf(word)

    def wordCount(self,docID):
        return len(self.wordMap[docID])

    def avgDocLen(self):
        su = sum(len(values) for values in self.wordMap.values())
        return su/float(len(self.wordMap))

    def getCosineSimilarity(self,docId,q):
        vec1 = self.convertToVector(docId)
        vec2 = self.makeQueryVector(q)
        intersection = set(vec1.keys()) & set(vec2.keys())
#         numerator = sum([vec1[x] * vec2[x] for x in intersection])
        numerator = sum(vec1[x]*vec2[y] for x,y in zip(vec1.keys(),vec2.keys()))
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    def getOkapiRelevance(self,docId,q):
        vec2 = self.makeQueryVector(q)
        return sum([self.idfokapi(word)*self.termOkapi(word,docId) for word in vec2.keys()])

    def idfokapi(self,word):
        queryFreq = self.queryWordList.count(word)+0.5
        if len(self.queryWordList) == 1:
            return 1.0
        idf = math.log((float(len(self.queryWordList))-queryFreq)/queryFreq)
        if idf < 0:
            idf=1.0 # we apply this smoothing to trim common terms.
        return idf

    def termOkapi(self,word,docId):
        term = 0.0
        k1 = 1.5
        b = 0.75
        if docId in self.trie.getDocMap(word):
            numerator = self.trie.getDocMap(word)[docId]*(k1+1)
            denominator = self.trie.getDocMap(word)[docId]+(k1*(1-b+(b*(float(self.wordCount(docId))/self.avgDocLen()))))
            term = numerator/denominator
        return term

    def getBayesRelevance(self,docId,q):
        pass

    def convertToVector(self,docId):
        vec = dict()
        for word in self.wordMap[docId]:
            vec[word]=self.tfidf(word,docId)
        return vec

    def makeQueryVector(self,query):
        self.queryWordList = self.tokenize(query)
        vec = dict()
        for word in self.queryWordList:
            vec[word]=self.querytfidf(word)
        return vec

    def querytfidf(self,word):
        return (0.5 +(self.queryWordList.count(word)*0.5 / float(len(self.queryWordList))))*self.findidf(word)

def highlight_doc(document,query,measure='COS'):
    snippetMaker = makeSnippet()
    measureDict = {
    'COS' : snippetMaker.getCosineSimilarity,
    'OKA' : snippetMaker.getOkapiRelevance,
    'BAY' : snippetMaker.getBayesRelevance
    }
    relevanceScores = dict()
    snippetMaker.buildTokens(document)
    for k,v in snippetMaker.wordMap.iteritems():
        snippetMaker.trie.insert(k,v)
    for key in snippetMaker.wordMap.keys():
        relevanceScores[key]=measureDict.get(measure,snippetMaker.getCosineSimilarity)(key,query)
    relevanceScores = sorted(relevanceScores.iteritems(), key=operator.itemgetter(1),reverse=True)
    print relevanceScores
    del relevanceScores[3:] #Retain the first 3 sentences alone.
    print relevanceScores
    snippet = ''.join([snippetMaker.rawSentences[key-1]+'..' for key,v in relevanceScores])
    for k in snippetMaker.queryWordList:
        snippet = re.compile(k, re.IGNORECASE).sub(' [[HIGHLIGHT]'+k+'[[ENDHIGHLIGHT] ',snippet)
    return snippet

def main():
    document = 'I love Pizza. I don#t like Deep Dish pizza though. Just the thin crust.The deep dish crust was pretty poor. I loved the pizza crust though.'
    query = 'crust'
    '''
    Values for relevance measure:
    'COS' : Cosine Similarity (Default)
    'OKA' : Okapi Relevance Score
    'BAY' : Bayes Language Model Relevance Score
    '''
    measure = 'COS'
    print highlight_doc(document,query,measure)


if  __name__ =='__main__':main()