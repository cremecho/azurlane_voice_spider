from scrapy import cmdline

ship_name = ['拉菲','标枪','Z23','绫波']
save_folder = 'C:/Quadratic/azurlane'


if __name__ == '__main__':
    cmdline.execute(['scrapy', 'crawl', 'wikisound'])