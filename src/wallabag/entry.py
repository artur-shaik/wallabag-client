# -*- coding: utf-8 -*-

import delorean


class Entry:
    entry_id = 0
    title = ""
    content = ""
    url = ""
    read = False
    starred = False
    created_at = None
    reading_time = None
    preview_picture = None
    published_by = []
    tags = []
    annotations = []

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
        if 'created_at' in item:
            self.created_at = delorean.parse(item['created_at'])
        if 'reading_time' in item:
            self.reading_time = item['reading_time']
        if 'preview_picture' in item:
            self.preview_picture = item['preview_picture']
        if 'published_by' in item:
            self.published_by = item['published_by']
        if 'tags' in item:
            self.tags = item['tags']
        if 'annotations' in item:
            self.annotations = item['annotations']

    def get_tags_string(self):
        if not self.tags:
            return None

        def sort(tag):
            return int(tag['id'])

        return " ".join(
                map(
                    lambda tag: tag['label'],
                    sorted(self.tags, key=sort)))

    def create_list(items):
        return [Entry(i) for i in items]
