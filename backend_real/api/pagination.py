"""Custom pagination classes for API views."""
from rest_framework.pagination import PageNumberPagination

from foodgram_backend.constants import DEFAULT_PAGE_SIZE


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results."""
    
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
    page_query_param = 'page'
