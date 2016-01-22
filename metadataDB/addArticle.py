from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from declareDatabase import Base, Article, Author, Author_Name, Article_Author_Name, Category, Article_Category
from dateutil import parser

def addArticle(articleDict, update=False):
    """articleDict is a dictionary.
    
    update=False skips identical arXiv IDs """
    
    engine = create_engine("sqlite:///../arXiv_metadata.db", echo=False)
    Base.metadata.bind = engine
    DBsession = sessionmaker(bind=engine)
    session = DBsession()
    
    # Is the article in the database already?
    # FUTURE CHANGES: Currently skips rather than updates
    
    result = session.query(Article.id).filter(Article.arxiv_id == articleDict['id']).first()
    
    if update or (result is None):   
        # parser.parse(): NEED TO HANDLE 'NONE' CASES
        try:
            created = parser.parse(articleDict['created'])
        except:
            created = None
        try:
            updated = parser.parse(articleDict['updated'])
        except:
            updated = None
        try:
            oai_datestamp = parser.parse(articleDict['OAI_datestamp'])
        except:
            oai_datestamp = None

        new_article = Article(arxiv_id=      articleDict['id'],
                              oai_id=        articleDict['OAI_identifier'],
                              oai_datestamp= oai_datestamp,
                              created=       created,
                              updated=       updated,
                              title=         articleDict['title'],
                              abstract=      articleDict['abstract'],
                              comments=      articleDict['comments'],
                              journal_ref=   articleDict['journal_ref'],
                              doi=           articleDict['doi'],
                              )
        
        new_author_list = []
        new_author_name_list = []
        new_article_author_name_list = []
        new_category_list = []
        new_article_category_list = []
        
        # Authors are a dictionary with keys 'name' and 'affiliation'
        for auth in articleDict['authors']:
            # Check if the author_name already exists.
            # If so, the article to it.
            result = session.query(Author_Name).filter(Author_Name.name == auth['name']).first()

            if result is None:
                new_author = Author()
                new_author_name = Author_Name(name=auth['name'],
                                              affiliation=auth['affiliation'],
                                              author=new_author)
                new_author_list.append(new_author)
                new_author_name_list.append(new_author_name)
            else:
                new_author_name = result

            new_article_author_name = Article_Author_Name(article=new_article,
                                                          author_name=new_author_name)

            new_article_author_name_list.append(new_article_author_name)
#            break
                                                
         # Categories come as a list
        for current_category in articleDict['categories']:
            result = session.query(Category).filter(Category.name == current_category).first()
            
            if result is None:
                new_category = Category(name=current_category)
                new_category_list.append(new_category)
            else:
                new_category = result
            
            new_article_category = Article_Category(article=new_article,
                                                    category=new_category)
            
            new_article_category_list.append(new_article_category)
        
        session.add(new_article)
        session.add_all(new_author_list)
        session.add_all(new_author_name_list)
        session.add_all(new_category_list)
        session.add_all(new_article_category_list)
        session.commit()
        
        #If we add a new article, add 1
        return 1
    else:
        return 0
