# -*- coding: utf-8 -*-

class Entry:
    entry_id = 0
    title = ""
    content = ""
    url = ""
    read = False
    starred = False
    tags = []

    def __init__(self, item):
        self.entry_id = item['id']

        title = item['title']
        title = title.replace("\n", "")
        title = " ".join(title.split())
        self.title = title

        self.content = item['content']
        self.url = item['url']
        self.read = item['is_archived'] == 1
        self.starred = item['is_starred'] == 1
        if 'tags' in item:
            self.tags = item['tags']

    def create_list(items):
        return [Entry(i) for i in items]
