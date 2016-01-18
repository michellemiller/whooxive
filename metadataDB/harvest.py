# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 00:04:42 2016

@author: emarti
"""
import getmetadata
import addArticle
import time
import itertools

def harvest():
    start = time.time()
    xmlList = getmetadata.download(getmetadata.constructURL())
    
    listArticle = list(itertools.chain.from_iterable([getmetadata.parse(x) for x in xmlList]))

    for article in listArticle:
        addArticle.addArticle(article)
    final = time.time()
    print 'Total time: %f for %i entries (%f per entry)' % (final - start, len(listArticle), (final-start)/len(listArticle))

