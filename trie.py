'''
Created on Nov 13, 2013
@author: Vivek
'''
from collections import defaultdict

class _Node(object):

    def __init__(self):
        self.__docMap = defaultdict(int)
        self.__child = dict()
        self.offset = 0

    def children(self):
        return self.__child

    def addDocID(self,docID):
        self.__docMap[docID]+=1

    def getDocMap(self):
        return self.__docMap

    def __repr__(self):
        return self.__child.__str__()+' List: '+self.__docMap.__str__()+'Offset: '+self.offset.__str__()


class Trie(object):

    _end = '_end_' #indicates a terminating character or word end.

    def __init__(self):
        self.__root = _Node()
        self.__size=0

    def root(self):
        return self.__root

    def size(self):
        return self.__size

    def __repr__(self):
        return self.root().__str__()

    def insert(self,docID,words):
        offset=0
        for word in words:
            offset+=1
            self.__insert(docID,word,offset)

    def __insert(self,docID,word,offset):
        active = self.__root
        for char in word:
            active = active.children().setdefault(char,_Node())
        active.addDocID(docID)
        active.offset=offset
        if not active.children().has_key(self._end):
            active = active.children().setdefault(self._end,None)
            self.__size+=1

    def getFrequency(self,word):
        return sum(self.getDocMap(word).values())

    def getDocFrequency(self,word):
        return len(self.getDocMap(word))

    def isPresent(self,word):
        active=self.root()
        for char in word:
            if char in active.children():
                active = active.children()[char]
            else:
                return False
        if active.children().has_key(self._end):
            return True
        return False

    def getDocMap(self,word):
        active=self.root()
        for char in word:
            if char in active.children():
                active = active.children()[char]
            else:
                return {}
        if active.children().has_key(self._end):
            return active.getDocMap()
        return {}
