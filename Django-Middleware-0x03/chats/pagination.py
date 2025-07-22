from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MessagePagination(PageNumberPagination):
    """Custom pagination class for messages.
    """

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Return a paginated response with additional metadata."""

        return Response({
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        })
    
class ConversationPagination(PageNumberPagination):
    """Custom pagination class for conversations.
    """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        """Return a paginated response with additional metadata."""

        return Response({
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        })
