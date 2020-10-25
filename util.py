from sqlalchemy import create_engine
import os

engine = create_engine(os.getenv("DATABASE_URL"))
db = engine.connect()

def getCategories(table):
    """Get all available game categories from SQL enum"""
    
    query = f"SELECT COLUMN_TYPE AS game_category_names FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='u5b3cy05kem78z1q' AND TABLE_NAME='{table}' AND COLUMN_NAME='game_category'"
    allcatquery = str(db.execute(query).fetchone()[0])
    allcat = []
    cat = ""
    for i in range(6, len(allcatquery)):
        if allcatquery[i] in ',)':
            allcat.append(cat)
            cat = ""
        elif allcatquery[i]=="'":
            continue
        else:
            cat += allcatquery[i]
    return allcatquery, allcat
