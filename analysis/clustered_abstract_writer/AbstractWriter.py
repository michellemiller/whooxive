import random
import re

class AbstractWriter:
    '''This class will take a specific n-gram and learn to write abstracts from a few words.'''
    _data = dict()
    _data_specialized = dict()
    _abstracts = []
    _abstracts_specialized = []
    _specialized_weight = 0.8
    
    def __init__(self, ngram, randomize=False, seed=None, maxWords=200):
        self.ngram = ngram
        self.randomize = randomize
        self.seed = seed
        self.maxWords = maxWords
        if seed is not None:
            random.seed(seed)

    
    def transform(self, train):
        data_list = []
        abstracts = []
        for item in train:
            ind = 0
            textlist = self.__cleanup_text(item)
            abstracts.append(' '.join(textlist))
            while ind + self.ngram - 1 < len(textlist):
                currentTuple = tuple(textlist[ind:(ind+self.ngram-1)])
                nextWord = textlist[ind+self.ngram-1]
                data_list.append((tuple(textlist[ind:(ind+self.ngram-1)]),
                                        textlist[ind+self.ngram-1]))
                ind += 1
        data_list.sort()
        
        # Now that the list is sorted, convert it into a dictionary.
        # Since the list is sorted, each subsuquent entry is either new or a continuation of the previous one.
        data = dict()
        previousKey = None
        for val in data_list:
            currentKey = val[0]
            if currentKey == previousKey:
                data[currentKey].append(val[1])
            else:
                data[currentKey] = [val[1]]
            previousKey = val[0]
        return (data, abstracts)
    
    def fit(self, train):
        data, self._abstracts = self.transform(train)
        self._data.update(data)
    
    def fit_specialized(self, train):
        data_specialized, self._abstracts_specialized = self.transform(train)
        self._data_specialized.update(data_specialized)

    def find_next_word(self, phrase):
        '''phrase is a tuple of (typ. 3) words. Returns the next word.'''
        # We would prefer to have a word from our specialized vocabulary, so we will weigh those more heavily. Fortunately, if a word is missing, it will always be able to use the 'normal' vocabulary. 
        
        # If the phrase is not in the specialized vocabulary, use the large
        # (general) vocabulary. 
        soln_general = self._data.get(phrase,[])
        soln_specialized = self._data_specialized.get(phrase,[])
        
        if len(soln_general) + len(soln_specialized) == 0:
            return None
        
        # if phrase in self._data_specialized.keys():
        #     soln_specialized = self._data_specialized[phrase]
        # elif phrase in self._data.keys():
        #     return random.choice(self._data[phrase])
        # else:
        #     return None
        #
        # # It seems highly unlikely that a phrase shows up in the specialized
        # # vocabulary but not the general one.
        # if phrase in self._data.keys():
        #     soln_general = self._data[phrase]
        # else:
        #     return random.choice(soln_specialized)
        
        # Whether I use the specialized or general vocabulary is weighted by how
        # many choices are in each and by the weight self._specialized_weight
        ratio = len(soln_specialized)*self._specialized_weight / \
                (len(soln_specialized)*self._specialized_weight + \
                  len(soln_general)*(1.-self._specialized_weight) )
        # print ratio
        # random_number = random.random()
        # print random_number
        if ratio > random.random():
            # print 'specialized'
            return random.choice(soln_specialized)
        else:
            # print 'general'
            return random.choice(soln_general)

        
    def write_abstract(self, beginning=None):
        if beginning:
            beginning_tuple = tuple(beginning.split())
        else:
            if self._abstracts_specialized:
                beginning_tuple = random.choice(self._abstracts_specialized).split()[0:(self.ngram-1)]
            else:
                beginning_tuple = random.choice(self._abstracts).split()[0:(self.ngram-1)]
        abstract = list(beginning_tuple)
        nextWord = ''
        ind = len(beginning_tuple) - self.ngram + 1
        while (nextWord is not None) and (ind < self.maxWords):
            nextWord = self.find_next_word(tuple(abstract[ind:(ind+self.ngram)]))
            if nextWord is None:
                break
            else:
                abstract.append(nextWord)
                ind += 1
        return ' '.join(abstract)
    
    def find_similar(self, abstract):
        '''Have I accidentally plagiarized one of the articles?
        With too few choices, we will likely just copy an existing article.
        Returns the longest chunk highlighted in an existing article.'''
        first = 0
        last = 1
        abort = False
        longestChunk = ''
        longestChunkLength = 0

        totalLength = len(abstract.split())
        while first + longestChunkLength < totalLength:
            chunk = ' '.join(abstract.split()[first:last])
            if any(x for x in self._abstracts if chunk in x):
                if last - first + 1 > longestChunkLength:
                    longestChunk = chunk
                    longestChunkLength = last - first + 1
                last += 1
            else:
                first += 1
                last = first + 1
        
        best_abstract = (x for x in self._abstracts if longestChunk in x).next()
        return re.sub('(' + longestChunk + ')', '[[[' + longestChunk + ']]]', best_abstract)


    def __cleanup_text(self, text):
        # re from kaggle https://www.kaggle.com/c/word2vec-nlp-tutorial/details/part-1-for-beginners-bag-of-wordsi
        # Remove punctuation. Keep periods.
        # 
        # New trick: replace numbers with ##, which we will later replace with different numbers.
        pattern1 = re.compile("[0-9]")
        pattern2 = re.compile("[^a-zA-Z#.]")
        # The previous pattern could make multiple spaces. Turn multiple spaces into a single space.
        pattern3 = re.compile("(\s{2,})")
        return pattern3.sub(" ",
                    pattern2.sub(" ",
                            pattern1.sub("#",
                                    text.lstrip().rstrip()))).split(' ')

def WriteAbstract(ngram):
    writer = AbstractWriter(ngram=ngram, randomize=True, seed=42)
    writer.fit(abstract_train)
    for i in range(0,5):
        phrase = random.choice(writer._abstracts).split()[0:(ngram-1)]
        currentAbstract = writer.write_abstract(tuple(phrase))
        print 'New abstract: ' + currentAbstract
        print ''
        print 'Existing abstract: ' + writer.find_similar(currentAbstract)
        print ''
    return writer