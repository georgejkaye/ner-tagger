# Named Entity Recognition in the WSJ - wrapper

print("")
print("--- Named Entity Recognition in the WSJ ---")
print("")

print("Setting up...")
from source import *

corpus = ""

while not corpus == "a" and not corpus == "b" :
    corpus = input("\n1) Do you want to test on the full corpus or subset? \n   a) full \n   b) subset\n   ")

wiki = ""
while not wiki == "a" and not wiki == "b" :
    if corpus == "a" :
        print("\n ***WARNING: using wikification with the full corpus is highly unadvised!***")
    wiki = input("\n2) Do you want to use wikification? \n   a) yay \n   b) nay\n   ")

order = ""
while not order == "a" and not order == "b" and not order == "c" :
    order = input("\n3) Which order of tagging do you want to use?\n   a) name - org - loc \n   b) org - loc - name \n   c) loc - org - name \n   ")

print("\nRunning tests... This may take some time.")

run(corpus, wiki, order)                 
