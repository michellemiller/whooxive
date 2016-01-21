from datetime import date
import dateutil.parser
import urllib2
from lxml import etree
from time import sleep

def constructURL(fromdate, todate):
    baseURL = 'http://export.arxiv.org/oai2?verb=ListRecords&set=%s&from=%s&until=%s&metadataPrefix=arXiv'
#    fromdate = date(2014, 1, 1)
#    todate = date(2014, 2, 1)
    category = 'physics'
    return baseURL % (category, fromdate, todate)

def resume_retrieve(token):
    return 'http://export.arxiv.org/oai2?verb=ListRecords&resumptionToken=%s' % token


def retrieve_one_page(url):
    opener = urllib2.build_opener()    
    #opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    maxTries = 2
    tryNumber = 0
    gotdata = False
    
    while not(gotdata) and (tryNumber < maxTries):
        
        try:
            tryNumber += 1
            response = opener.open(url)
        except urllib2.HTTPError as e:
            print e
            sleep(30)
        except urllib2.URLError as e:
            print 'Could not reach server.'
            break
        else:
            xml = response.read()
            response.close()
            
            # Check if there's a resumption token.
            e = etree.fromstring(xml)
            e1 = e.find('.//{http://www.openarchives.org/OAI/2.0/}resumptionToken')
            
            return (xml, e1)
    return None
    # Two main complications: retry after a fixed time and resumption tokens.
    # If the list is too long, it can pass a resumptionToken. This requires
    # waiting and submitting another request a minute (or so) later.
    
def retrieve(url):
    out = retrieve_one_page(url)
    if out is None:
        return None
    if out[1] is None:
        return [out[0]]
    else:
        xmlList = [out[0]]
        e1 = out[1]
        while e1.text is not None:
            print 'xml is long... at %s / %s.' % (e1.attrib['cursor'], e1.attrib['completeListSize'])
            sleep(30)
            (xml, e1) = retrieve_one_page(resume_retrieve(e1.text))
            xmlList.append(xml)
        return xmlList 

def parse(text):
    e = etree.fromstring(text)
    result = []
    stupidPrefix1 = '{http://www.openarchives.org/OAI/2.0/}'
    stupidPrefix2 = '{http://arxiv.org/OAI/arXiv/}'

    for item in e.iterfind('.//' + stupidPrefix1 + 'record'):   
        keywords = ['id',
                    'created',
                    'updated',
                    'title',
                    'categories',
                    'comments',
                    'doi',
                    'abstract',
                    'journal-ref']
        
        currentDict = {}
        currentDict['OAI_datestamp'] = item.find('.//' + stupidPrefix1 + 'datestamp').text
        currentDict['OAI_identifier'] = item.find('.//' + stupidPrefix1 + 'identifier').text
        for key in keywords:
            try:
                currentDict[key.replace('-','_')] = item.find('.//' + stupidPrefix2 + key).text
            except:
                currentDict[key.replace('-','_')] = None
                
        currentDict['authors'] = []
        for author in item.find('.//' + stupidPrefix2 + 'authors').getchildren():
            keyname = author.find(stupidPrefix2 + 'keyname').text
            # This doesn't handle multiple affiliations or forenames correctly!!
            try:
                forenames = author.find(stupidPrefix2 + 'forenames').text
            except:
                forenames = ''
            try: 
                affiliation = author.find(stupidPrefix2 + 'affiliation').text
            except:
                affiliation = None

            currentAuthor = {'name': forenames + ' ' + keyname,
                             'affiliation': affiliation}

            currentDict['authors'].append(currentAuthor)

        currentDict['categories'] = currentDict['categories'].split(' ')
        
        result.append(currentDict)
        #break
    return result