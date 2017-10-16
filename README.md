# Named Entity Recognition in the WSJ

## Tagging 
### Parsing Training Data
The training data  is read by the system and, using regular expressions  (looking for the ```<ENAMEX = “”>``` tags, the named entities are extracted and stored in three text files: ```names.txt```, ```locs.txt``` and ```orgs.txt```. This means that any entities recognised at this stage will be stored for future use (beyond the WSJ test set, for example). Three ```WordListCorpusReader``` objects are then created to house these data for use later on in the code.

### Other Corpora
As well as corpora gathered from the training data, several other corpora are supplied with the code: the names corpora ```male```, ```female``` and ```family```, which were provided via Canvas. Three other corpora have been self-defined: ```titles```, a list of common name titles (such as Mr and Mrs), ```orgsuffs```, a list of organisation suffixes (such as plc and Ltd.), and ```daymonths```, a list of days and months (which are often erroneously tagged during the process). All of these corpora are used during the tagging process.

### POS Taggers and Extracting Named Entites
The inbuilt nltk POS tagger  is used to tag the words appropriately. Once the words are all tagged, the program iterates through the new wordlist and adds every word tagged with ```NNP``` (i.e. proper nouns) to a list. If the program finds two proper nouns next to each other, they are joined together to form one entity. This is effectively a simple (albeit rather naïve) chunker.

### Classifying the Named Entities
Now that the program has a list of (what it believes) to be all the named entities in the text, it attempts to classify them. It iterates through every item in the entities list, skipping them if they have already been tagged (there are often duplicates in the text and tagging each one would be time-wasting).

One area to note is that days of the week and months are also tagged as named entities (not illogical), despite not having an appropriate tag to map them to. To counter this, anything in the ```daymonths``` corpus is simply ignored. Unfortunately, this means that names such as May and June are not tagged as names but since these names are much less common than usage of months and days, it is fairly acceptable at this early stage.

### Names
Names are the easiest named entity to classify as the program has lots of data to use. There are the aforementioned names corpora and the names extracted from the training data. We can also use the ```titles``` corpus to tag any entity beginning with a title. Initially the program checks the entire extracted entity against the names extracted from the training data as a preliminary sweep. 

If that does not succeed, it checks each part of the entity in turn. If it finds a title, the entity must be a name and so is tagged as such. All subsequent parts are added to the ```names``` corpus if they are not present – one example from the first set of test data was *Mr. Vinken* – *Vinken* was not initially in the ```names``` corpus but *Mr.* was immediately picked up and subsequent uses of Vinken were then tagged appropriately.

If it finds something in the ```names``` corpus, it is temporarily tagged as a name, but if subsequent parts are not names it will be tagged as not a name (this avoids tagging some organisations or locations as names, such as Harvard University: Harvard is in the names corpus but the entity is clearly not a name).

### Organisations
Organisations are slightly harder than names in that they have a less limited set of words. However, there are some words (such as *Inc* or *Ltd*) which immediately flag up an organisation, similar to the name titles. These are dealt with in the same way as titles with names, and the entities are also checked against the extracted entities from the training data.

### Locations
Locations are the hardest entity to tag since there are very few ways to identify them without knowledge of the real world, which the program does not have. All that can be done at the first stage is check against the training data: several common locations like *USA* and *UK* are contained within it.

### Wikification
Clearly this naïve method of tagging provides nowhere near enough accuracy for a useful system. Therefore, after the first process, untagged entities are checked against Wikipedia articles (using a modified version of the Wikification code provided on Canvas ). 

Rather than the search results as was initially suggested, the method has been modified to take wiki markup  from the page. Using regular expressions, the ```{{Infobox}}``` template code is lifted from it. Often the title of the infobox template will contain exactly what the program needs (e.g. Infobox UK place ), and if not there will normally be fields further down which will help decide which tag is appropriate (e.g. born for a person). The template is checked against a selection of buzzwords and if an appropriate match is found this is returned to the main program.

One flaw in this process is that when more than one Wikipedia page exists for a query (common with place names ), Wikipedia will sometimes redirect to a disambiguation page. The program detects this by checking for the phrase *may refer to* in the markup, which seems to be common to all disambiguation pages. Then it searches for the first link on the page (again not the most accurate of methods but acceptable).

## Evaluation
To evaluate the tagging, the tagged version of the data is parsed and any elements surrounded in ```<ENAMEX>``` tags is recorded in tuples, much like how the tagging process stored elements. These two lists are then compared: elements in both lists are noted as true positives, elements tagged but not found as false positives, and elements found but not tagged as false negatives. An accuracy score is then calculated using F1 score  (precision * recall / precision + recall).

![Name first, no wiki](/eval/nowiki.jpg) ![Name first, wiki](/eval/wiki.jpg)
![Org first, name last, no wiki](/eval/orgsfirst.jpg) ![Loc first, name last, no wiki](/eval/locsfirst.jpg)

Four sets of evaluation results can be seen above. The data on the top uses the initial configuration of the system, tagging names first. As can be seen, there is in fact a very small (just over 2%) increase between the set with wikification and without, despite it increasing the time taken drastically (larger sets were more likely to time out than tag completely).

Both sets of data still suggest a disappointingly low accuracy rate. This can be attributed to different reasons depending on which tag is being assigned. Names are tagged overenthusiastically (with a large amount of false positives): this is because of its highest place in the tagging process, and how many organisations and locations can also be tagged as names (for example, the state of Georgia).  Conversely, there are also many false negatives: potentially less common names not contained in the names corpora. Locations and organisations are much more weighted towards a large number of false negatives: this is either because they have been mistagged as names, or because wikification has failed (perhaps the entity in question is not prolific enough to warrant a page).

To test the effects of the tagging order, two more tests were run. Names was relegated to last in order, and the other two tags switched around. The results were actually more accurate than even wikification: locations in particular showed a drastic increase of almost 20% when in first position.

To actually get a suitably accurate result, context would have to be taken into account. With the current process (simply analysing each named entity independent of location), it is impossible to distinguish between the different meanings of words (seen in the wikification process), which is why the order of tagging has such a large effect on the result. This means that although many words are indeed tagged as named entities, they are tagged as the incorrect type, resulting in a false positive still being flagged.

