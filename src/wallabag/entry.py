"""
Wallabag entry.
"""


class Entry:
    """
    The entry class.
    """
    entry_id = 0
    title = ""
    content = ""
    url = ""
    read = False
    starred = False

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

    def entrylist(items):
        """
        Creates Entry instances of multiple items and returns an Entry-list.
        """
        ret = list()
        for item in items:
            ret.append(Entry(item))
        return ret
