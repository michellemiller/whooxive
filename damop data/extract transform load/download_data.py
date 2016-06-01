from bs4 import BeautifulSoup
import urllib
import itertools
import re
import json

# Get list of DAMOP sessions
website = urllib.urlopen('http://meetings.aps.org/Meeting/DAMOP16/APS_epitome')
soup = BeautifulSoup(website, 'html.parser')
epitome_list = soup.find('div', {'id': 'epitome-all'}).find_all("p", { "class" : "epi" })
session_list = [tag.find('b').text.strip() for tag in epitome_list]

# Convert the session number (e.g., 'H6') to a url with abstracts
def get_address(session):
    return 'http://meetings.aps.org/Meeting/DAMOP16/Session/{}?showAbstract'.format(session)

def download_session(session_number):
    website = urllib.urlopen(get_address(session_number))
    soup = BeautifulSoup(website, 'html.parser')

    # First table has the session name
    # Have to use re twice because the first time it returns the "Session..." part
    myregexp = re.compile("Session {}: (.*)".format(session_number))
    session_name = myregexp.match(soup.find(text=myregexp)).group(1)
    # print session_name

    # Second table has the abstracts.
    abstracts = []

    for x in soup.find_all(href=re.compile('/Meeting/DAMOP16/Session/{}.'.format(session_number))):
        results = re.search('{}.([0-9])*: (.*)'.format(session_number), x.text)
        current_number = results.group(1)
        current_title = results.group(2)
        current_abstract = x.find_next().find('p').text.replace('[Preview Abstract]', '').strip()
    #     print (current_number, current_title, current_abstract)
        abstracts.append({'number': current_number,
                          'title': current_title,
                          'abstract': current_abstract})
    return {'name': session_name,
           'number': session_number,
           'abstracts': abstracts,
          }
          

if __name__ == '__main__':
    data = []
    for session in session_list:
        print session
        data.append(download_session(session))
        # break

    with open("../damop2016.json", "w") as f:
        json.dump(data, f)
    
