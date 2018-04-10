
# coding: utf-8

# In[ ]:


from nltk import word_tokenize
import random
import io
import re
import string
import json
import operator
import bisect
from unidecode import unidecode
from nltk import sent_tokenize


# In[ ]:


filename = "dataset/GOT.txt"

sequenceLength = 2
BEGIN = "___BEGIN__"
END = "___END__"


# In[ ]:


wordList = []
tempMapping = {}
mapping = {}
begin_cumdist= None
begin_choices = None


# In[ ]:


def sentence_split(text):
    potential_end_pat = re.compile(r"".join([
        r"([\w\.'’&\]\)]+[\.\?!])", # A word that ends with punctuation
        r"([‘’“”'\"\)\]]*)", # Followed by optional quote/parens/etc
        r"(\s+(?![a-z\-–—]))", # Followed by whitespace + non-(lowercase or dash)
        ]), re.U)
    dot_iter = re.finditer(potential_end_pat, text)
    end_indices = [ (x.start() + len(x.group(1)) + len(x.group(2)))
        for x in dot_iter]
        #if is_sentence_ender(x.group(1)) ]
    spans = zip([None] + end_indices, end_indices + [None])
    sentences = [ text[start:end].strip() for start, end in spans ]
    return sentences


# In[ ]:



word_split_pattern = re.compile(r"\s+")
def word_split(sentence):
    return re.split(word_split_pattern, sentence)


# In[ ]:


def test_sentence_input(sentence):
    if len(sentence.strip()) == 0: return False
    reject_pat = re.compile(r"(^')|('$)|\s'|'\s|[\"(\(\)\[\])]")
    # Decode unicode, mainly to normalize fancy quotation marks
    if sentence.__class__.__name__ == "str": # pragma: no cover
        decoded = sentence
    else: # pragma: no cover
        decoded = unidecode(sentence)
    # Sentence shouldn't contain problematic characters
    if re.search(reject_pat, decoded): 
        return False
    return True


# In[ ]:


def generate_corpus(text):
    if isinstance(text, str):
        sentences = sentence_split(text)
    else:
        sentences = []
        for line in text:
            sentences += sentence_split(line)
    passing = filter(test_sentence_input, sentences)
    
    runs = map(word_split, passing)
    print(len(runs))
    return runs


# In[ ]:


with io.open(filename, 'r', encoding="utf8") as f:
    rawText = f.read().lower()

sentence_list = sent_tokenize(rawText)

wordList = generate_corpus(sentence_list)
print(len(wordList))


# In[ ]:


def build():
    print(len(wordList))
    for run in wordList:
        #print("run",run)
        items = ([ BEGIN ] * sequenceLength) + run + [ END ]
        print(items)
        for i in range(len(run) + 1):
            state = tuple(items[i:i+sequenceLength])
            follow = items[i+sequenceLength]
            if state not in tempMapping:
                tempMapping[state] = {}
            if follow not in tempMapping[state]:
                tempMapping[state][follow] = 0

            tempMapping[state][follow] += 1
    return tempMapping    
build() 
#print(tempMapping)


# In[ ]:


def accumulate(iterable, func=operator.add):
    """
    Cumulative calculations. (Summation, by default.)
    Via: https://docs.python.org/3/library/itertools.html#itertools.accumulate
    """
    it = iter(iterable)
    total = next(it)
    yield total
    for element in it:
        total = func(total, element)
        yield total


# In[ ]:


#def precompute_begin_state():
#print(tempMapping)
begin_state = tuple([ BEGIN ] * sequenceLength)
#print("begin state",begin_state)
#print(tempMapping)
choices, weights = zip(*tempMapping[begin_state].items())
#print("choices",choices)
#print("weights",weights)
cumdist = list(accumulate(weights))
#print("cumdist",cumdist)
begin_cumdist = cumdist
begin_choices = choices
#print("$$$$",begin_cumdist)
#precompute_begin_state()


# In[ ]:


def move(state):
    if state == tuple([ BEGIN ] * sequenceLength):
       # print("if")
        choices = begin_choices
        cumdist = begin_cumdist
    else:
        choices, weights = zip(*tempMapping[state].items())
        cumdist = list(accumulate(weights))
    #print(cumdist)
    r = random.random() * cumdist[-1]
    selection = choices[bisect.bisect(cumdist, r)]
    return selection
#move((BEGIN,) * sequenceLength)


# In[ ]:


def gen(init_state=None):
    state = init_state or (BEGIN,) * sequenceLength
    while True:
        next_word = move(state)
        if next_word == END: break
        #print("next word",next_word)
        yield next_word
        state = tuple(state[1:]) + (next_word,)
op = gen(None)
result=" "
for w in op:
    result = result + w + " "
print(result)

