#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed Feb 27 04:46:24 2020

@author: Yazid BOUNAB
"""

import random
import sys
import time
from datetime import datetime
import re
import requests

import pickle
from urllib.request import urlopen
from bs4 import BeautifulSoup

from afinn.afinn import Afinn

from googletrans import Translator

BaseLink = 'https://www.vauva.fi/'
Section = 'alue/apua-vanhemmuuteen'

Ontology = {
'parenthood' : ['Vanhemmuus', 'vanhemmuudesta', 'vanhemmuuteen', 'vanhemmuudelta', 'vanhemmuudelle', 'vanhemmuutena', 'vanhemmuudeksi'],
'Mother' : ['Äiti', 'äidistä', 'äitiin', 'äidiltä', 'äidille', 'äitinä', 'äidiksi'],
'Mothers' : ['Äidit', 'äideistä,äiteihin', 'äideiltä', 'äideille', 'äiteinä', 'äideiksi'],
'Father' : ['Isä', 'isästä', 'isään', 'isältä', 'isälle', 'isänä', 'isäksi'],
'Fathers' : ['Isät', 'isistä', 'isiin', 'isiltä', 'isille', 'isinä', 'isiksi'],
'Child' : ['Lapsi', 'lapsesta', 'lapseen', 'lapselta', 'lapselle', 'lapsena', 'lapseksi'],
'Children' : ['Lapset', 'lapsista', 'lapsiin', 'lapsilta', 'lapsille', 'lapsina', 'lapsiksi'],
'Adolescent' : ['Nuori', 'nuoresta', 'nuoreen', 'nuorelta', 'nuorelle', 'nuorena', 'nuoreksi'],
'adolescents' : ['Nuoret', 'nuorista', 'nuoriin', 'nuorilta', 'nuorille', 'nuorina', 'nuoriksi'],
'Childhood' : ['Lapsuus', 'lapsuudesta', 'lapsuuteen', 'lapsuudesta', 'lapsuudelle', 'lapsuutena', 'lapsuudeksi']}

BASE_URL = 'http://www.vauva.fi'
TOPIC_LIST_URL = BASE_URL + '/keskustelu/alue/{subforum}?page={page}'

class ScrapeVauva:
      def __init__(self):
          self.url = BASE_URL
          self.Sections = {}
      
      def getSectins(self):
          soup = BeautifulSoup(urlopen(BaseLink+Section), 'lxml')
          MainMenu = soup.find('nav')
    
          for SubMenu in MainMenu.find('ul', class_='menu').find_all('li'):
              #print(SubMenu,'\n___________________________')
              title = SubMenu.find('a', class_='menu__link').text
              link = SubMenu.find('a', class_='menu__link')['href']
              self.Sections[title] = {'link':link, 'Discussions':{}}
        
      def getDebateMenu(self):
          soup = BeautifulSoup(urlopen('https://www.vauva.fi/keskustelu/alue/aihe_vapaa'), 'lxml')
          MainMenu = soup.find('div', class_='discussion-sections-list')
   
          for SubMenu in MainMenu.find('ul').find_all('li'):
              title = SubMenu.find('a').text
              link = SubMenu.find('a')['href']
              self.Sections[title] = {'link':link, 'Discussions':{}}
        
      def get_page_count(self,url):
          page_number = 1
          while True:
                link = url + '?page=' + str(page_number)
                if requests.get(link).status_code != 200:
                   return page_number
                else:
                    page_number += 1

      def convert_to_soup(html):
          return BeautifulSoup(html, 'html.parser')

      def remove_attributes(soup):
          for tag in soup.findAll(True):
              tag.attrs = {}
          return soup

      def get_sleep_time():
          return random.randrange(100, 221) / 1000

      def fetch_page_as_soup(topic_url, page_number):
          url = topic_url + '?page=' + str(page_number)
          print('fetching ' + url)
          response = requests.get(url)
          if response.status_code == 200:
             return convert_to_soup(response.text)
          return None


class Post:
      def __init__(self, name, age):
          self.name = name
          self.age = age

      def fetch_page_as_soup(topic_url, page_number):
          url = topic_url + '?page=' + str(page_number)
          print('fetching ' + url)
          response = requests.get(url)
          if response.status_code == 200:
             return convert_to_soup(response.text)
          return None
      
      def parse_post_timestamp(self, post_soup):
          container = post_soup.find('div', {'class': 'field-name-post-date'})
          timestamp_str = container.find('div', {'class': 'field-item'}).contents[0]
          return datetime.strptime(timestamp_str, PostParser.VAUVA_DATETIME_FORMAT)

      def remove_quotations(self, post_content):
          for quote in post_content.find_all('blockquote'):
              quote.replaceWith('')
          return post_content

      def remove_linefeeds(self, post_content):
          return post_content.replace('\n', ' ')

      def purify_content(self, post_content_soap):
          post_content_soap = utilities.remove_attributes(post_content_soap)
          post_content_soap = self.remove_quotations(post_content_soap)

          # Replace br-tags with linefeeds
          for br in post_content_soap.find_all('br'):
              br.replace_with('\n')

          post_content = post_content_soap.get_text()
          post_content = self.remove_linefeeds(post_content)

          # Remove multiple whitespaces
          post_content = re.sub('\s+', ' ', post_content).strip()
          return post_content

      def parse_post_content(self, post_soup):
          container = post_soup.find('div', {'class': PostParser.CONTENT_CLASSES})
          if container is None:
             return

          post_content_soap = container.find('div', {'class': 'field-item'})
          post_content = self.purify_content(post_content_soap)
          return post_content

      def parse_posts(self, sanoma_comment_soups):
          posts = []
          for sanoma_comment_soup in sanoma_comment_soups:
              content = self.parse_post_content(sanoma_comment_soup)
              if not content:
                 # No need to store empty posts
                 continue

              post_time = self.parse_post_timestamp(sanoma_comment_soup)
              posts.append({
                'content': content,
                'post_time': post_time,
                })

          return posts

      def parse_topic(self, pages):
          sanoma_comment_soups = []
          for page in pages:
              page_soup = utilities.convert_to_soup(page)
              sanoma_comment_soups += page_soup.find_all('div', {'class': 'sanoma-comment'})
          return self.parse_posts(sanoma_comment_soups)

      def add_topic_id_post_numbers(self, topic_id, posts):
          for i, post in enumerate(posts):
              post['topic_id'] = topic_id
              post['post_number'] = i+1
          return posts

class Topic:
      def __init__(self, url):
          self.url = url
          self.BASE_URL = 'https://www.vauva.fi'
          self.TOPIC_LIST_URL = BASE_URL + '/keskustelu/alue/{subforum}?page={page}'
      
      def get_sleep_time(self):
          return random.randrange(100, 221) / 1000

      def get_Topic_page_count(self, url):
          soup = BeautifulSoup(urlopen(url), 'lxml')
          last_page_bullet = soup.find('li', {'class': 'pager-last last'}).text
          if last_page_bullet is not None:
             return int(last_page_bullet)
          return 1
      
      def GetTopic(self,url):
          soup = BeautifulSoup(urlopen(url), 'lxml')
          html = soup.find('article', class_=re.compile('^node node-discussion-topic'))
          Post = {'title':html.find('h3', class_='comment-title').text.strip()}
          
          S = html.find('div', class_='sanoma-comment')
          Post['user'] = S.find('div', class_='wrapper').text.strip()
          Post['time'] = S.find('div', class_='field-item even').text.strip()
          Post['text'] = S.find('p').get_text().strip()
          
          rate  = S.find('div', class_=re.compile('^rate-node'))
          Post['up'] = rate.find('li', class_='first').find('span', class_='rate-voting-count').text
          Post['down'] = rate.find('li', class_='last').find('span', class_='rate-voting-count').text
          Post['Discussion'] = []
          
          NB_pages = self.get_Topic_page_count(url)
          for page_number in range(1,NB_pages+1):
              print(page_number)
              html = BeautifulSoup(urlopen(url+'?page='+str(page_number)), 'lxml')
              Comments = html.find('div', class_='comments-list-wrapper')
              for article in Comments.find_all('article'):
                  if article.find('blockquote') != None:
                     article.find('blockquote').decompose()
                  Comment = {}
                  Comment['user'] = article.find('div', class_='top').find('span', class_='username-wrapper').text.strip()
                  Time = article.find('div', class_='top').find('div', class_= re.compile('^field field-name-post-date')).text.strip()
                  Comment['time'] = datetime.strptime(Time, 'klo %H:%M | %d.%m.%Y')
                  Comment['text'] = article.find('div', class_='middle clearfix').text.strip()

                  Post['Discussion'].append(Comment)
              time.sleep(self.get_sleep_time())
          return Post
                
      def GetTopics(self,url):
          Posts = []
          soup = BeautifulSoup(urlopen(url), 'lxml')
          Table = soup.find('div', class_='region main').find('div',class_='view-content ds-view-content')
          'title,Votes,Replies,Last'
          for row in Table.find_all('div', class_=re.compile("^row odd" or "^row even")):
              print('\n___________________________')
              link = BASE_URL+row.find('a')['href']
              #title = row.find('span', class_='title').text
              print(link)
              Posts.append(self.GetTopic(self,link))
          return Posts
      
      
      
      def get_topics(page, subforum):
          topic_list_url = TOPIC_LIST_URL.format(subforum=subforum, page=page)
          print('Fetching ' + topic_list_url)
          topic_list_response = requests.get(topic_list_url)

          if topic_list_response.status_code != 200:
             return []

          topics = []
          topic_list_soup = utilities.convert_to_soup(topic_list_response.text)

          for topic in topic_list_soup.find_all('span', {'class': 'title'}):
              topic_url = get_topic_url(topic)
              topics.append({
                      'url': BASE_URL + topic_url,
                      'title': topic.a.contents[-1]
                      })

          return topics

      def get_topic_pages(self):
          pages = []
          first_page_soup = fetch_page_as_soup(self.url, 0)
          if not first_page_soup:
             return []
          content = get_page_content(self, first_page_soup)
          pages.append({'page_number': 0, 'content': content})

          page_count = self.get_page_count(first_page_soup)

          for page_number in range(1, page_count):
              page_soup = fetch_page_as_soup(self.url, page_number)
              if not page_soup:
                 # Content couldn't be fetched
                 return []
              content = get_page_content(page_soup)
              pages.append({'page_number': page_number, 'content': content})
              # Tryin' to be polite
              time.sleep(get_sleep_time())
          return pages
      
def Scraping():
    #T = Topic('https://www.vauva.fi/keskustelu/alue/aihe_vapaa?page=2')
    SV = ScrapeVauva()
    SV.url = 'https://www.vauva.fi/keskustelu/alue/aihe_vapaa'
    #print(SV.get_page_count(SV.url))
    T = Topic('https://www.vauva.fi/keskustelu/alue/aihe_vapaa')
    #Posts = T.GetTopics('https://www.vauva.fi/keskustelu/alue/aihe_vapaa')
    #return Posts
    url = 'https://www.vauva.fi/keskustelu/2911061/typerien-ja-nolojen-kysymysten-ketju-kysy-mita-vain-muut-vastaavat-ilman?changed=1583141686'
    return T.GetTopic(url)
Posts = Scraping()