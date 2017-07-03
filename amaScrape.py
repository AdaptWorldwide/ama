from random import choice
from collections import Counter
import csv
from time import sleep

import requests
from bs4 import BeautifulSoup
from lxml.html.clean import Cleaner
from nltk.util import ngrams
from nltk import word_tokenize
from amazon_models import AmazonPages
from retrying import retry


def stop_word_list(txt_file):
    stop_list = []
    with open(txt_file, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            stop_list.append(line.strip())
    return stop_list


class AmazonNodeScraper(AmazonPages):

    def __init__(self, url, txt_file):

        self.url = url.strip()
        self.stop_words = None
        self.text_content = None

        self.parent_nodes = []
        self.parent_node_urls = []

        self.nodes = []

        self.failed = False

        self.frequent_keywords = []
        self.stop_words = stop_word_list(txt_file)

        self.h1 = None

    def __random_headers(self):
        desktop_agents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
        return {'User-Agent': choice(desktop_agents),'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

    @retry((Exception),3, 45, 1.5)
    def __get_page(self):
        r = requests.get(self.url)
        r.raise_for_status()
        print(r.text)
        return r.url, r.text, r.status_code

    def __make_soup(self, html, status):
        if status != 200:
            self.failed = True
            soup = None
        else:
            soup = BeautifulSoup(html, 'html.parser')
        return soup

    def __get_parents(self, soup):

        parents = soup.find_all('li',attrs={'class':'shoppingEngineExpand'})
        for parent in parents:
            self.parent_nodes.append(parent.get_text().strip())
            parent_url = parent.find('a',href=True)
            if parent_url:
                self.parent_node_urls.append(parent_url['href'])

    def __get_children(self, soup):

        children = soup.find_all('span', {'class': 'refinementLink'})
        children = children[0:4]

        for i in children:
            temp_list = []
            try:
                print(i.get_text().strip())
                temp_list.append(i.get_text())
            except:
                pass
            if len(temp_list) > 0:
                if temp_list[0] in ('Ship to United Kingdom', 'Subscribe & Save Eligible','Free Shipping by Amazon'):
                    self.nodes.append('None')
                else:
                    for i in temp_list:
                        self.nodes.append(i)
            else:
                self.nodes.append('None')

    def __get_clean_html(self, html):
        cleaner = Cleaner()
        cleaner.javascript = True
        cleaner.style = True
        new_html = cleaner.clean_html(html)
        soup = BeautifulSoup(new_html, 'html.parser')
        h1 = soup.find('h1')
        if h1:
            self.h1 = h1.get_text()
        body = soup.find('div', attrs={'id': 'merchandised-content'}).get_text()
        new_text = body.lower()
        words = word_tokenize(new_text)
        new_words = []
        for word in words:
            if word not in self.stop_words:
                new_words.append(word)
        new_text = ' '.join(new_words)
        self.text_content = new_text

    def __get_ngrams(self, text, n):
        n_grams = ngrams(word_tokenize(text), n)
        return [' '.join(grams) for grams in n_grams]

    def __get_multi_ngrams(self, text):
        one_word_list = []
        two_word_list = []
        three_word_list = []
        for i in [1,2,3]:
            our_list = self.__get_ngrams(self.text_content,i)
            for word in our_list:
                if i == 1:
                    one_word_list.append(word)
                if i == 2:
                    two_word_list.append(word)
                if i == 3:
                    three_word_list.append(word)
        return one_word_list, two_word_list, three_word_list

    def __count_keywords(self, list1, list2, list3):
        count1 = Counter(list1).most_common(3)
        count2 = Counter(list2).most_common(3)
        count3 = Counter(list3).most_common(3)
        out_list = count1 + count2 + count3
        return out_list

    def __write_to_database(self, url):
        self.make_table()

        try:
            parent_1_node = self.parent_nodes[0] if self.parent_nodes[0] else 'None'
            parent_1_url = self.parent_node_urls[0] if self.parent_node_urls[0] else 'None'
        except:
            parent_1_node = 'None'
            parent_1_url = 'None'
        try:
            parent_2_node = self.parent_nodes[1] if self.parent_nodes[1] else 'None'
            parent_2_url = self.parent_node_urls[1] if self.parent_node_urls[1] else 'None'
        except:
            parent_2_node = 'None'
            parent_2_url = 'None'
        try:
            parent_3_node = self.parent_nodes[2] if self.parent_nodes[2] else 'None'
            parent_3_url = self.parent_node_urls[2] if self.parent_node_urls[2] else 'None'
        except:
            parent_3_node = 'None'
            parent_3_url = 'None'

        q = self.insert(NodeURL=url, one_word_keyword_1=self.frequent_keywords[0][0],
                        child_nodes=','.join(self.nodes),
                        one_word_keyword_2=self.frequent_keywords[1][0],
                        one_word_keyword_3=self.frequent_keywords[2][0],
                        two_word_keyword_1=self.frequent_keywords[3][0],
                        two_word_keyword_2=self.frequent_keywords[4][0],
                        two_word_keyword_3=self.frequent_keywords[5][0],
                        three_word_keyword_1=self.frequent_keywords[6][0],
                        three_word_keyword_2=self.frequent_keywords[7][0],
                        three_word_keyword_3=self.frequent_keywords[8][0],
                        primary_parent=parent_1_node,
                        primary_parent_url=parent_1_url,
                        secondary_parent=parent_2_node,
                        secondary_parent_url=parent_2_url,
                        tertiary_parent=parent_3_node,
                        tertiary_parent_url=parent_3_url,
                        current_h1=self.h1)
        q.execute()


    def page_parser(self):
        url, html, status_code = self.__get_page()
        print(status_code)
        self.__get_clean_html(html)
        n, g, h = self.__get_multi_ngrams(self.text_content)
        self.frequent_keywords = self.__count_keywords(n,g,h)
        soup = self.__make_soup(html, status_code)
        self.__get_parents(soup)
        self.__get_children(soup)
        self.__write_to_database(url)
        print(type(self.frequent_keywords[0]))



with open('urls.txt','r', encoding='utf-8') as outputfile:
    for line in outputfile:
        line = line.strip()
        try:
            a = AmazonNodeScraper(line, 'stoplist.txt')
            a.page_parser()
            sleep(10)
        except:
            print(line)
