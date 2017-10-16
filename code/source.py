# Named Entity Recognition in the WSJ - main code

# imports
import nltk
import re

from os import listdir
from os.path import isfile, join, abspath

from nltk.corpus.reader import WordListCorpusReader
from nltk.corpus import treebank
from nltk.tokenize import word_tokenize
from nltk.tag import *

from wiki import *

path = abspath('..')
path = path.replace('\\', '/')
corpora = path + '/corpora'

# path to supplied named entities corpora
nepath = corpora + '/ne_corpora'

# getting training copora
onlyfilestraining   = [f for f in listdir(corpora + '/wsj_training') if isfile(join(corpora + '/wsj_training', f))]
onlyfilesuntagged   = [f for f in listdir(corpora + '/wsj_untagged') if isfile(join(corpora + '/wsj_untagged', f))]
trainingcorpus =  nltk.corpus.reader.plaintext.PlaintextCorpusReader(corpora + '/wsj_training', onlyfilestraining)
untaggedcorpus =  nltk.corpus.reader.plaintext.PlaintextCorpusReader(corpora + '/wsj_untagged', onlyfilesuntagged)

# the entire test corpus
onlyfilestesting   = [f for f in listdir(corpora + '/golden_test') if isfile(join(corpora + '/golden_test', f))]
onlyfilestagged    = [f for f in listdir(corpora + '/golden_tagged') if isfile(join(corpora + '/golden_tagged', f))]
testcorpus =  nltk.corpus.reader.plaintext.PlaintextCorpusReader(corpora + '/golden_test', onlyfilestesting)
taggedcorpus =  nltk.corpus.reader.plaintext.PlaintextCorpusReader(corpora + '/golden_tagged', onlyfilestagged)

# subset of the test data (necessary to facilitate quicker tests)
onlyfilessbsa1 = [f for f in listdir(corpora + '/golden_test_subset_a') if isfile(join(corpora + '/golden_test_subset_a', f))]
onlyfilessbsa2   = [f for f in listdir(corpora + '/golden_tagged_subset_a') if isfile(join(corpora + '/golden_tagged_subset_a', f))]
testc =  nltk.corpus.reader.plaintext.PlaintextCorpusReader(corpora + '/golden_test_subset_a', onlyfilessbsa1)
tagdc =  nltk.corpus.reader.plaintext.PlaintextCorpusReader(corpora + '/golden_tagged_subset_a', onlyfilessbsa2)

# getting named entity corpora

names = WordListCorpusReader(nepath, ['male.txt', 'female.txt', 'family.txt'])  # list of names, from canvas
titles = WordListCorpusReader(nepath, ['titles.txt'])                           # list of common titles
orgsuffs = WordListCorpusReader(nepath, ['orgsuff.txt'])                        # list of organisation suffixes
daymonths = WordListCorpusReader(nepath, ['daymonths.txt'])                     # list of days and months

# extracting named entities from tagged data
# regex patterns to match each tag
pattern1 = '<ENAMEX TYPE="PERSON">(.*?)<\/ENAMEX>'
pattern2 = '<ENAMEX TYPE="LOCATION">(.*?)<\/ENAMEX>'
pattern3 = '<ENAMEX TYPE="ORGANIZATION">(.*?)<\/ENAMEX>'

# finding every example in the data, storing in sets
people = set(re.findall(pattern1,trainingcorpus.raw()))
locs = set(re.findall(pattern2,trainingcorpus.raw()))
orgs = set(re.findall(pattern3,trainingcorpus.raw()))

# writing the tagged entities to text files
file = open(nepath + "\\names.txt", "w")
for p in people :
	file.write(p + "\n")
file.close()
	
file = open(nepath + "\\locs.txt", "w")
for l in locs :
	file.write(l + "\n")
file.close()

file = open(nepath + "\\orgs.txt", "w")
for o in orgs :
	file.write(o + "\n")
file.close()

# extracting the new data into corpora
fullnames = WordListCorpusReader(nepath, ['names.txt'])
locs = WordListCorpusReader(nepath, ['locs.txt'])
orgs = WordListCorpusReader(nepath, ['orgs.txt'])

# get the words from the named entity corpora created earlier
names = names.words()
titles = titles.words()
fullnames = fullnames.words()
locations = locs.words()
organisations = orgs.words()
orgsuffs = orgsuffs.words()
daymonths = daymonths.words()

# extracting named entities (proper nouns)
# if a proper noun is found, add it to the list
# adjacent proper nouns are joined together
def findPropers (words):
    propers = []
    last = False
    
    for (word, tag) in nltk.pos_tag(words):
        if (tag == 'NNP') :
            if last :
                propers = propers[0:(len(propers)-1)] + [(propers[len(propers)-1] + " " + word)]
            else :
                propers = propers + [word]
                last = True
        else :
            last = False
    return propers

# when a title (mr, mrs etc) is seen, all words after are added to names
def addNamesTitle(words):
    for piece in words[1:]:
        # check that we're not adding initials or duplicate names
        if piece not in names and not len(piece) == 1 and not piece[1] == '.':
            names.append(piece)

# check if a given named entity is a name
def nameCheck(entity):
    name = False

    # check if the entire entity is in the name corpus
    if entity in fullnames or entity in names:
        name = True
    else:
        # to ensure lone titles are not tagged as names
        if entity in titles or entity in daymonths:
            name = False
        else:
            # split the entity into its component pieces
            splentity = entity.split()

            # any entity starting with a title must be a name
            if splentity[0] in titles:
                name = True
                addNamesTitle(entity)
            else :
                for piece in splentity :
                    if piece in names :
                        name = True
                    else :
                        name = False
    
    return name
                

# check if a given named entity is an organisation
def organisationCheck(entity):
    organisation = False

    # check if we already have the organisation in the corpus
    if entity in organisations :
        organisation = True

    # make sure that just organisation suffixes are not accepted
    if entity in orgsuffs or entity in daymonths:
        organisation = False
    else :
        splentity = entity.split()
    
        # if the entity contains an organisation suffix (plc, ltd etc) we know it's a company
        for piece in splentity :
            if piece in orgsuffs :
                organisation = True

    return organisation

# check if a given named entity is a location
def locationCheck(entity):
    location = False
    if entity in daymonths :
        location = False
    elif entity in locations :
        location = True
    return location

def recordEntity(entity, ident, results, entities):

    code = ''
    
    if ident == 0 :
        code = 'N'
    elif ident == 1 :
        code = 'O'
    elif ident == 2 :
        code = 'L'
    else :
        return
        
    entities.append((entity, code))


# tag a corpus
def tagUntagged(corpus, wiki, order) :
    words = word_tokenize(corpus.raw())
    propers = findPropers(words)

    nameCount = 0
    orgCount = 0
    locCount = 0

    entities = []
    done = []

    nt = open(path + "/results/tagged-names.txt", "w")
    ot = open(path + "/results/tagged-orgs.txt", "w")
    lt = open(path + "/results/tagged-locs.txt", "w")

    
    for entity in propers :
        if entity not in daymonths and entity not in orgsuffs and entity not in titles and entity not in done :

            # different orders lead to different results
            if order == "a":
                
                if nameCheck(entity) :
                    nameCount += 1
                    entities.append((entity, 'N'))
                    nt.write("\n" + entity)
                elif organisationCheck(entity) :
                    orgCount += 1
                    entities.append((entity, 'O'))
                    ot.write("\n" + entity)
                elif locationCheck(entity) :
                    locCount += 1
                    entities.append((entity, 'L'))
                    lt.write("\n" + entity)

            elif order == "b":
                
                if organisationCheck(entity) :
                    orgCount += 1
                    entities.append((entity, 'O'))
                    ot.write("\n" + entity)
                elif locationCheck(entity) :
                    locCount += 1
                    entities.append((entity, 'L'))
                    lt.write("\n" + entity)
                elif nameCheck(entity) :
                    nameCount += 1
                    entities.append((entity, 'N'))
                    nt.write("\n" + entity)

            elif order == "c":
                
                if locationCheck(entity) :
                    locCount += 1
                    entities.append((entity, 'L'))
                    lt.write("\n" + entity)
                elif organisationCheck(entity) :
                    orgCount += 1
                    entities.append((entity, 'O'))
                    ot.write("\n" + entity)
                elif nameCheck(entity) :
                    nameCount += 1
                    entities.append((entity, 'N'))
                    nt.write("\n" + entity)

            # wikification step
            else :
                if wiki == "a" :
                    num = wiki(entity, 0)

                    if num == 0 :
                        nameCount += 1
                        entities.append((entity, 'N'))
                        nt.write("\n" + entity)
                    elif num == 1 :
                        orgCount += 1
                        entities.append((entity, 'O'))
                        ot.write("\n" + entity)
                    elif num == 2 :
                        locCount += 1
                        entities.append((entity, 'L'))
                        lt.write("\n" + entity)

            done.append(entity)
            
    lt.close()
    ot.close()
    nt.close()
    
    print("---tagged entities--- \nnames: " + str(nameCount) + "\norganisations: " + str(orgCount) + "\nlocations: " + str(locCount)) 
    
    return entities

# check a tagged corpus for entities
def checkTagged(corpus) :

    taggedNames = set(re.findall(pattern1,corpus.raw()))
    taggedLocs = set(re.findall(pattern2,corpus.raw()))
    taggedOrgs = set(re.findall(pattern3,corpus.raw()))

    entities = []

    nf = open(path + "/results/found-names.txt", "w")
    of = open(path + "/results/found-orgs.txt", "w")
    lf = open(path + "/results/found-locs.txt", "w")
    
    for i in taggedNames :
        entities.append((i, 'N'))
        nf.write("\n" + i)
    for i in taggedLocs :
        entities.append((i, 'L'))
        lf.write("\n" + i)
    for i in taggedOrgs :
        entities.append((i, 'O'))
        of.write("\n" + i)

    nf.close()
    of.close()
    lf.close()
    
    print("---found entities--- \nnames: " + str(len(taggedNames)) + "\norganisations: " + str(len(taggedOrgs)) + "\nlocations: " + str(len(taggedLocs))) 

    return entities

# functions related to accuracy (uses F1 score)

def calcPrecision (tp, fp) :
    return len(tp)/(len(tp) + len(fp))

def calcRecall (tp, fn) :
    return len(tp)/(len(tp) + len(fn))

def effone (tp, fp, fn) :

    precision = calcPrecision(tp, fp)
    recall = calcRecall(tp, fn)

    score = 2 * (precision * recall) / (precision + recall)

    print("\nscore: " + str(score))
    return score

def calcScore (found, tagged) :

    tp = []
    fp = []
    fn = []
    
    for item in tagged :
        if item in found :
            tp.append(item)
        else :
            fp.append(item)

    for item in found :
        if item not in tagged :
            fn.append(item)

    print("true positives: " + str(len(tp)))
    print("false positives: " + str(len(fp)))
    print("false negatives: " + str(len(fn)))
    
    return effone(tp, fp, fn)

# evaluates the tagger, comparing tagged data with the program's tagged version 
def evaluate (tagged, untagged, wiki, order) :
    
    print("")
    true = checkTagged(tagged)

    foundlocs = []
    foundnames = []
    foundorgs = []

    for (ent, tag) in true :
        if tag == 'N' :
            foundnames.append(ent)
        elif tag == 'O' :
            foundorgs.append(ent)
        elif tag == 'L' :
            foundlocs.append(ent)

    print("")
    positives = tagUntagged(untagged, wiki, order)

    taggedlocs = []
    taggednames = []
    taggedorgs = []

    for (ent, tag) in positives :
        if tag == 'N' :
            taggednames.append(ent)
        elif tag == 'O' :
            taggedorgs.append(ent)
        elif tag == 'L' :
            taggedlocs.append(ent)

    print("\n---names---")
    nameScore = calcScore(foundnames, taggednames)
    print("\n---organisations---")
    orgScore = calcScore(foundorgs, taggedorgs)
    print("\n---locations---")
    locScore = calcScore(foundlocs, taggedlocs)

    print("\n---stats---")
    print("average: " + str((nameScore + orgScore + locScore)/3))

def run (corpus, wiki, order):
    
    if corpus == "a" :
        evaluate(taggedcorpus, testcorpus, wiki, order)
    else:
        evaluate(tagdc, testc, wiki, order)
    
