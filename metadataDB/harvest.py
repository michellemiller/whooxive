# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 00:04:42 2016

@author: emarti
"""
import getMetadata
import addArticle
import time
import itertools

def harvest(fromdate, todate):
    start = time.time()
    xmlList = getMetadata.retrieve(getMetadata.constructURL(fromdate, todate))
    
    print type(xmlList)
    if xmlList is not None:
        listArticle = list(itertools.chain.from_iterable([getMetadata.parse(x) for x in xmlList]))
    
        numNewArticle = 0
        for article in listArticle:
            numNewArticle += addArticle.addArticle(article)
    
        final = time.time()
    
        try:
            #        print article
            print 'Total time: %f for %i entries (%f per entry)' % (final - start, len(listArticle), (final-start)/len(listArticle))
        except:
            pass

        return numNewArticle
    else:
        return 0
    
