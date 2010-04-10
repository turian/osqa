
class RequestUtils(object):
    def __init__(self):
        self.request = None

    def set_sort_method(self, sort):
        self.request.session['questions_sort_method'] = sort

    def sort_method(self, default):
        sort = self.request.REQUEST.get('sort', None)
        if sort is None:
            return self.request.session.get('questions_sort_method', default)
        else:
            self.set_sort_method(sort)
            return sort

    def page_size(self, default):
        pagesize = self.request.REQUEST.get('pagesize', None)
        if pagesize is None:
            return int(self.request.session.get('questions_pagesize', default))
        else:
            self.request.session['questions_pagesize'] = pagesize
            return int(pagesize)

    def process_request(self, request):
        self.request = request
        request.utils = self
        return None