# This program goes on to demonstrate additional text
# processing capabilities of Python. Here we gather up
# text from 297 blog pages dealing with web analytics,
# creating a single corpus for analysis. We imagine
# that we want to assess the overall sentiment about Google.

# let's make our program compatible with Python 3.0/1/2/3
# from __future__ import division, print_function
# from future_builtins import ascii, filter, hex, map, oct, zip

search_word = 'America'  # one-word string for this program
q_dir = "../../Output-BofA/"

import os  # operating system commands
import re  # regular expressions
import nltk  # draw on the Python natural language toolkit
from nltk.corpus import PlaintextCorpusReader
from numpy import *  # for array calculations

# create lists of positive and negative words using Hu and Liu (2004) lists
my_directory = '../twitter'
positive_list = PlaintextCorpusReader(my_directory, 'Hu_Liu_positive_word_list.txt')
negative_list = PlaintextCorpusReader(my_directory, 'Hu_Liu_negative_word_list.txt')
positive_words = positive_list.words()
negative_words = negative_list.words()
# define bag-of-words dictionaries 
def bag_of_words(words, value):
    return dict([(word, value) for word in words])
positive_scoring = bag_of_words(positive_words, 1)
negative_scoring = bag_of_words(negative_words, -1)
# scoring_dictionary = dict(positive_scoring.items() + negative_scoring.items())
scoring_dictionary = positive_scoring.copy()
scoring_dictionary.update(negative_scoring)
# Previous work provided a directory called results
# with text files from the web analytics blogs.

# identify all of the file names 
file_names =  os.listdir(q_dir)

nfiles = len(file_names)  # nfiles should be 297

# Create a single blog corpus by combining the files.
# Use ten divider words between the files. Our reason
# for doing this will become clear as we move to the 
# sentiment analysis portion of this program.
textdivider = 10 * 'xxxxxxxx '  
blogstring = textdivider  # initialize corpus as string of words

for ifile in range(len(file_names)):
    this_file_name = q_dir + file_names[ifile]
    with open(this_file_name, 'rt') as f:
        this_file_text = f.read()
    blogstring = blogstring + this_file_text + textdivider

# Because our interest is sentiment about Google Analytics,
# let's see how often the search_word appears in the corpus.
blogstring.count(search_word)  

blogcorpus = blogstring.split()

# see how many words are in the corpus 
# subtracting the number of textdivider words 
len(blogcorpus) - blogstring.count('xxxxxxxx')

# list for assigning a score to every word in the blogcorpus
# scores are -1 if in negative word list, +1 if in positive word list
# and zero otherwise. We use a dictionary for scoring.
blogscore = [0] * len(blogcorpus)  # initialize scoring list

for iword in range(len(blogcorpus)):
    if blogcorpus[iword] in scoring_dictionary:
        blogscore[iword] = scoring_dictionary[blogcorpus[iword]]
        
# report the norm sentiment score for the words in the corpus
print('Corpus Average Sentiment Score:')
print(round(sum(blogscore) / (len(blogcorpus) - blogstring.count('xxxxxxxx')), 3))        

# Read the blogcorpus from beginning to end
# identifying all the places where the search_word occurs.
# We arbitrarily identify search-string-relevant words
# to be those within three words of the search string.
blogrelevant = [0] * len(blogcorpus)  # initialize blog-relevnat indicator
blogrelevantgroup = [0] * len(blogcorpus)
groupcount = 0  

for iword in range(len(blogcorpus)):
    if blogcorpus[iword] == search_word:
        groupcount = groupcount + 1
        for index in range(max(0,(iword - 4)),min((iword + 4), len(blogcorpus))):
            blogrelevant[index] = 1
            blogrelevantgroup[index] = groupcount

# Compute the average sentiment score for the words nearby the search term.
print('Average Sentiment Score Around Search Term')
print(round(sum((array(blogrelevant) * array(blogscore))) / sum(array(blogrelevant)),3))
                
print('RUN COMPLETE')                