import records
from amazon_models import AmazonKeywords


db = records.Database('sqlite:///AmazonData.db')

unique_keywords = []

r1 = db.query('select DISTINCT(one_word_keyword_1) from amazonnodescraper')
r2 = db.query('select DISTINCT(one_word_keyword_2) from amazonnodescraper')
r3 = db.query('select DISTINCT(one_word_keyword_3) from amazonnodescraper')
r4 = db.query('select DISTINCT(two_word_keyword_1) from amazonnodescraper')
r5 = db.query('select DISTINCT(two_word_keyword_2) from amazonnodescraper')
r6 = db.query('select DISTINCT(two_word_keyword_3) from amazonnodescraper')
r7 = db.query('select DISTINCT(three_word_keyword_1) from amazonnodescraper')
r8 = db.query('select DISTINCT(three_word_keyword_2) from amazonnodescraper')
r9 = db.query('select DISTINCT(three_word_keyword_3) from amazonnodescraper')
for i in r1, r2, r3, r4, r5, r6, r7, r8, r9:
    r = i[0]
    print(r[0])
    if r[0] not in unique_keywords:
        unique_keywords.append(r[0])

db.close()

for i in unique_keywords:
    q = AmazonKeywords.insert(keyword_name=i)
    q.execute()
