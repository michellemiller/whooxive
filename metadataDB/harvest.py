# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 00:04:42 2016

@author: emarti
"""
import getmetadata
import addArticle
import time
import itertools

def harvest(fromdate, todate):
#    start = time.time()
    totalNewArticles = 0
    for xml in getMetadata.retrieve(getMetadata.constructURL(fromdate, todate)):
        currentNewArticles = 0
        for article in getMetadata.parse(xml):
            currentNewArticles += addArticle.addArticle(article)
        print 'Added %i articles' % currentNewArticles
        totalNewArticles += currentNewArticles
    return totalNewArticles
#    final = time.time()

#    try:
#        #        print article
#        print 'Total time: %f for %i entries (%f per entry)' % (final - start, len(listArticle), (final-start)/len(listArticle))
#    except:
#        pass
#
#        return numNewArticle
#    else:
#        return 0
#    
