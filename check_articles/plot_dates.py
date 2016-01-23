#Need to add parent directoy to sys.path to find 'metadataDB'
import sys
sys.path.append('../')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date
import numpy as np
from metadataDB.declareDatabase import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///../arXiv_metadata.db", echo=False)
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()

result = session.query(Article.oai_datestamp).order_by(Article.oai_datestamp).all()

print len(result)
#datestamps = np.array([x.oai_datestamp for x in result[100000:101000]], dtype=np.datetime64)
datestamps = [x.oai_datestamp.toordinal() for x in result]
bins = [date(x, y, 1).toordinal() for x in range(2007,2016) for y in range(1,13,1)]

session.close_all()

plt.figure(figsize=(12,6))
plt.hist(datestamps,bins=bins)
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y.%m'))
plt.show()