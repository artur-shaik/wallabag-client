# -*- coding: utf-8 -*-


class TagsParam():

    def _validate_tags(self):
        if self.tags is not None:
            used = set()
            self.tags = ",".join([x.strip() for x in self.tags.split(',')
                                  if x.strip() and x not in used and
                                  (used.add(x) or True)])
            if not self.tags:
                return False, 'tags value is empty'
        return True, None
