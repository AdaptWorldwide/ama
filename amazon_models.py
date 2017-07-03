from peewee import *
import datetime


class AmazonPages(Model):

    NodeURL = CharField()
    current_h1 = CharField()

    child_nodes = CharField()

    one_word_keyword_1 = CharField()
    one_word_keyword_1_volume = IntegerField(null=True)
    one_word_keyword_2 = CharField()
    one_word_keyword_2_volume = IntegerField(null=True)
    one_word_keyword_3 = CharField()
    one_word_keyword_3_volume = IntegerField(null=True)

    two_word_keyword_1 = CharField()
    two_word_keyword_1_volume = IntegerField(null=True)
    two_word_keyword_2 = CharField()
    two_word_keyword_2_volume = IntegerField(null=True)
    two_word_keyword_3 = CharField()
    two_word_keyword_3_volume = IntegerField(null=True)

    three_word_keyword_1 = CharField()
    three_word_keyword_1_volume = IntegerField(null=True)
    three_word_keyword_2 = CharField()
    three_word_keyword_2_volume = IntegerField(null=True)
    three_word_keyword_3 = CharField()
    three_word_keyword_3_volume = IntegerField(null=True)

    primary_parent = CharField()
    primary_parent_url = CharField()

    secondary_parent = CharField()
    secondary_parent_url = CharField()

    tertiary_parent = CharField()
    tertiary_parent_url = CharField()

    def make_table(self):
        self.create_table(fail_silently=True)

    class Meta:
        database = SqliteDatabase('AmazonData.db')

class AmazonKeywords(Model):

    keyword_name = CharField()
    keyword_volume = IntegerField(null=True)
    date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = SqliteDatabase('AmazonData.db')

if __name__ == '__main__':
    AmazonKeywords.create_table()