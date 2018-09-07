from scrapy import Spider
from scrapy import Request
from bdwm.items import BdwmItem
import re


class bdwm(Spider):
    name = 'bdwm'
    allow_domains = ['bbs.pku.edu.cn']
    base_url = 'https://bbs.pku.edu.cn/v2/'

    def start_requests(self):
        yield Request(self.base_url + 'zone.php', callback=self.parse_board)

    def parse_board(self, response):
        urls = response.xpath('//*[@id="boards-list"]/div/a/@href').extract()
        for url in urls[1:]:
            board_url = self.base_url + url
            yield Request(board_url, callback=self.parse_thread)

    def parse_thread(self, response):
        urls = response.xpath('//*[@id="page-board"]/div[3]/div/div[2]/div[2]/div/div/a/@href').extract()
        for url in urls:
            thread_url = self.base_url + url
            yield Request(thread_url, callback=self.parse_post_lst)

    def parse_post_lst(self, response):
        board_name = response.xpath('/html/head/title/text()').extract()[0].replace(' - 北大未名BBS', '')
        page_num = int(
            re.findall(r'\d+', response.xpath('//*[@id="board-body"]/div[3]/div[not(@class)]/text()').extract()[0])[0])
        page_base = 'https://bbs.pku.edu.cn' + response.xpath('//*[@id="page-thread"]/div[1]/a[4]/@href').extract()[0]
        pages = []
        for i in range(1, page_num + 1):
            pages.append(page_base + '&mode=topic&page=' + str(i))
        for page in pages:
            yield Request(page, callback=self.parse_post_page, meta={'board_name': board_name})

    def parse_post_page(self, response):
        board_name = response.meta['board_name']
        pages = response.xpath('//*[@id="list-content"]/div/a/@href').extract()
        page_base = 'https://bbs.pku.edu.cn/v2/'
        for page in pages:
            yield Request(page_base + page, callback=self.parse_post, meta={'board_name': board_name})

    def parse_post(self, response):
        board_name = response.meta['board_name']
        page_num = int(
            re.findall(r'\d+', response.xpath('//*[@id="post-read"]/div[3]/div[not(@class)]/text()').extract()[0])[0])
        page_base = 'https://bbs.pku.edu.cn' + response.xpath('//*[@id="page-post"]/div[1]/a[5]/@href').extract()[0]
        pages = []
        for i in range(1, page_num + 1):
            page = page_base + '&page=' + str(i)
            pages.append(page)
            yield Request(page, callback=self.parse, meta={'board_name': board_name, 'page': i})

    def parse(self, response):
        board_name = response.meta['board_name']
        page = response.meta['page']
        texts = response.xpath('//*[@id="post-read"]/div[2]/div/div[3]/div[1]/div[1]/p[not(@class)]/text()').extract()
        title = response.xpath('//*[@id="post-read"]/header/h3/text()').extract()[0]
        text = ''
        for t in texts:
            text += t.strip() + '\n'
        item = BdwmItem()
        item['board_name'] = board_name.strip().replace('\\', '-').replace(' ', '').replace('/', '-')
        item['text'] = text
        item['title'] = title.strip().replace('\\', '-').replace(' ', '').replace('/', '-')
        path = '/Users/yanjin/PycharmProjects/scrapyspider/bdwm/archive/' + board_name + '/' + title + '/'
        filename = title + '-' + str(page) + '.txt'
        item['path'] = path
        item['filename'] = filename.strip().replace('\\', '-').replace(' ', '').replace('/', '-')
        yield item
