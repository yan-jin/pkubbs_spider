# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os


def mkdir_(path):
    if not os.path.isdir(path):
        mkdir_(os.path.split(path)[0])
    else:
        return
    if not os.path.exists(path):
        os.mkdir(path)


class BdwmPipeline(object):
    def process_item(self, item, spider):
        path = item['path']
        text = item['text']
        filename = item['filename']
        if not os.path.exists(path):
            mkdir_(path)
        with open(path + filename, 'w') as f:
            f.write(text)
        return item
