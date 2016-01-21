from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key = True)
    arxiv_id = Column(String())
    oai_id = Column(String())
    oai_datestamp = Column(Date)
    created = Column(Date)
    updated = Column(Date)
    title = Column(String())
    comments = Column(String())
    journal_ref = Column(String())
    doi = Column(String())

class Author(Base):
    """Author is an table of unique authors, referenced as an id without 
    current affiliation or name. Author_Name contains a (non-unique) 
    spelling and affiliation."""
    __tablename__ = 'author'
    id = Column(Integer, primary_key = True)
    
class Author_Name(Base):
    """Author_Name is an table of non-unique author names and affiliations.
    Names are a single string, '<firstname> <lastname>'"""
    __tablename__ = 'author_name'
    id = Column(Integer, primary_key = True)
    name = Column(String())
    affiliation = Column(String())
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship(Author)
    
class Category(Base):
    """arXiv category (e.g., physics:cond-mat/quant-gas)"""
    __tablename__ = 'category'
    id = Column(Integer, primary_key = True)
    name = Column(String())

class Article_Author_Name(Base):
    """Handles the many-to-many relationship between articles and author names.
    Since it's important to keep affiliations for articles, the links are to
    the table of non-unique author names."""
    __tablename__ = 'article_author_name'
    id = Column(Integer, primary_key = True)
    article_id = Column(Integer, ForeignKey('article.id'))
    author_name_id = Column(Integer, ForeignKey('author_name.id'))
    article = relationship(Article)
    author_name = relationship(Author_Name)

class Article_Category(Base):
    """Handles the many-to-many relationship between articles and arXiv
    categories."""
    __tablename__ = 'article_category'
    id = Column(Integer, primary_key = True)
    article_id = Column(Integer, ForeignKey('article.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    article = relationship(Article)
    category = relationship(Category)

# Create database
engine = create_engine("sqlite:///arXiv_metadata.db", echo=False)
#conn = db.connect()
Base.metadata.create_all(engine)

##So I don't duplicate entires, delete everything in the table.
#conn.execute(article.delete())
#conn.execute(author.delete())
#conn.execute(author_name.delete())
#conn.execute(category.delete())
#conn.execute(article_author.delete())
#conn.execute(article_category.delete())
#
#if __name__ ==  '__main__':
#    tic = datetime.datetime.now()
#    createDatabase()
#    toc = datetime.datetime.now()
#    print (toc-tic).total_seconds()