from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination, CursorPagination
from django.conf import settings

class OnOffPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_page_size(self, request):
        if self.page_size_query_param:
            page_size = min(int(request.query_params.get(self.page_size_query_param, self.page_size)),
                        self.max_page_size)
            if page_size > 0:
                return page_size
            elif page_size == 0:
                return None
            else:
                pass
        return self.page_size


'''
Author: Ashfaque Alam
Date: January 29, 2024
Purpose: As PageNumberPagination or LimitOffsetPagination have their limitations on larger dataset in the database, this custom cursor based pagination class is created to overcome these limitations. Also, it works perfectly in infinite scrolling pagination in fontend.
Usage: For the first time just send `page_size` with some integer value in query params, in the 'next' key of the response there will be a 'cursor' key which needs to be sent in query params in order to goto the subsequent next page. Or, just hit the 'next' page API URL in the response.
Limitations: User will not be able to jump on random pages. They need to goto next or previous page sequentially.
'''
# from rest_framework.pagination import CursorPagination
class OnOffCursorPagination(CursorPagination):
    page_size = 10    # ? Default if no `page_size_query_param` supplied.
    max_page_size = 1000
    page_size_query_param = 'page_size'
    ordering = '-id'    # Any model field will do but it should be unique.
    cursor_query_param = 'cursor'

    def get_page_size(self, request):
        page_size_value_supplied_in_query_params = int(request.query_params.get(self.page_size_query_param, self.page_size))    # If none is supplied, default to `self.page_size`.
        page_size = min(page_size_value_supplied_in_query_params, self.max_page_size)    # Which ever is smaller either `page_size_value_supplied_in_query_params` or `self.max_page_size`.

        if page_size > 0:
            return page_size
        elif page_size == 0:
            return None    # Return all data without pagination.
        else:
            raise ValueError('page_size query parameter should be supplied & its value needs to be greater than or equal to 0.')

''' ENDs Ashfaque '''
