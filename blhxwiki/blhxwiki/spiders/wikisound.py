import os
import sys
import time
sys.path.append("../")
from main import save_folder
from main import ship_name
import scrapy
import bs4
from six.moves import urllib
from multiprocessing import Process
from multiprocessing import Pool
import re


class WikisoundSpider(scrapy.Spider):
    name = 'wikisound'
    allowed_domains = ['wiki.biligame.com']
    start_urls = ['https://wiki.biligame.com/blhx/%E8%88%B0%E5%A8%98%E5%9B%BE%E9%89%B4']
    # start_urls = ['https://wiki.biligame.com/blhx/' + ship_name]


    def parse(self, response):
        jp_name, jp_dict = jp_names()
        if ship_name != 'all':
            cb_args = {}
            for sp_name in ship_name:
                if sp_name in jp_name:
                    sp_name = jp_dict.get(sp_name)
                cb_args['sp_name'] = sp_name.upper()
                yield scrapy.Request('https://wiki.biligame.com/blhx/' + sp_name, callback=self.ship_parse, cb_kwargs=cb_args)
        else:
            bs = bs4.BeautifulSoup(response.text,'html.parser')
            out = bs.find_all('div', attrs={"style": "float:left;"})

            ship_set = set()
            for ship in out:
                if '.改' in ship.text:
                    continue
                if ship.text.strip() in jp_name:
                    ship_set.add(jp_dict.get(ship.text.strip()))
                else:
                    ship_set.add(ship.text.strip())
            if not os.path.exists('log.TXT'):
                f = open('log.TXT', 'w')
                f.close()
            with open('log.TXT', 'r') as f:
                ls = f.readlines()
                for i in range(len(ls)):
                    ls[i] = ls[i].strip()
                ship_set = ship_set - set(ls)
            for ship in ship_set:
                cb_args = {}
                cb_args['sp_name'] = ship
                yield scrapy.Request('https://wiki.biligame.com/blhx/' + ship, callback=self.ship_parse, cb_kwargs=cb_args)


    def ship_parse(self, response, sp_name):
        bs = bs4.BeautifulSoup(response.text, 'html.parser')
        out = bs.find_all('table', class_='table-ShipWordsTable')
        dic = {}
        for skin_out in out:
            skin_dic = self.single_skin_sound(skin_out, dic)
            dic.update(skin_dic)

        save_path = os.path.join(save_folder, sp_name)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        pool = Pool()
        iter = []
        for key, value in dic.items():
            ls = [key, value, save_path]
            iter.append(ls)
        pool.map(se2, iter)
        pool.close()
        with open('log.TXT', 'a') as f:
            f.write(sp_name +'\n')


    def single_skin_sound(self, out1, rp_dic):
        i = 0
        for child in out1.children:
            i += 1
            if i == 2:
                src = child.text.strip().split('\n')
                break

        x1 = []
        try:
            for nonblank in src:    # 去除空格后 台词=mp3-1
                if nonblank.strip():
                    x1.append(nonblank)
        except:
            print("undefined bug")
        src = x1

        dic = {}
        for i in range(len(src)):
            if '.mp3' in src[i]:
                sets = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']   # 去除win中无法作为文件名的字符
                for char in src[i-1]:
                    if char in sets:
                        if char == '?':
                            src[i-1] = src[i-1].replace(char, '？')
                        else:
                            src[i-1] = src[i-1].replace(char, '')
                if rp_dic.__contains__(src[i-1]) or dic.__contains__(src[i-1]):     # 同句台词可能出现多次
                    j = 1
                    while rp_dic.__contains__(src[i-1] + '%d' % j) or dic.__contains__(src[i-1] + '%d' % j):
                        j += 1
                    src[i-1] += '%d' % j

                dic[src[i-1]] = src[i]
        return dic


def se2(ls):
    urllib.request.urlretrieve(ls[1], ls[2] + '/' + ls[0].strip() + '.mp3')


def jp_names():
    out = {}
    out1 = []
    with open('./blhxwiki/1.TXT', 'r', encoding='utf-8') as f:
        ls = f.readlines()
        zw = r'[\u4e00-\u9fa5]*'
        zw =r'[^\x00-\xff]*'
        for line in ls:
            p1, p2 = line.split('\t')
            p1_zw = re.findall(zw, p1)
            out1.append(p1_zw[0])
            out[p1_zw[0]] = p2.strip()

    return out1[1:], out