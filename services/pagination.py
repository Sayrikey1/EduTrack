# common/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from typing import Type, List, Any, Dict

class ServicePaginationMixin:
    """
    Mixin to give any service a self.paginate(...) helper.
    """
    page_size: int = None       # optional override
    pagination_class = PageNumberPagination

    def paginate(
        self,
        queryset,
        serializer_class: Type,
        request: Request,
    ) -> List[Dict[str, Any]]:
        paginator = self.pagination_class()
        if self.page_size is not None:
            paginator.page_size = self.page_size

        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serialized = serializer_class(page, many=True).data
            # returns the raw .data dict with links, counts, etc.
            return paginator.get_paginated_response(serialized).data

        return serializer_class(queryset, many=True).data
