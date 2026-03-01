# =============================================================================
# SeconiqueStockAPI | pagination.py
# =============================================================================
# Custom LimitOffsetPagination that detects Swagger UI requests via User-Agent
# and Referer headers, applying a 1000-record default for Swagger and unlimited
# results for other clients (e.g. Postman). Supports limit=all/unlimited.
# =============================================================================

#Get Rest Framework pagination class
from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Custom pagination class that:
    - Defaults to 1000 records when accessed from Swagger UI
    - Defaults to unlimited when accessed from Postman or other clients
    - Allows 'limit' query parameter to override (including unlimited)
    - Allows 'offset' query parameter for pagination
    """
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = None  # Allow unlimited results if explicitly requested

    def is_swagger_request(self, request):
        """Detect whether the request originates from Swagger UI.

        Args:
            request (HttpRequest): The incoming DRF request.

        Returns:
            bool: True if the User-Agent or Referer header indicates a Swagger
                UI origin (checks for 'swagger', '/api/docs/', or '/swagger'
                in the respective headers). False otherwise.
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        referer = request.META.get('HTTP_REFERER', '').lower()

        is_swagger = (
            'swagger' in user_agent or
            'swagger' in referer or
            '/api/docs/' in referer or
            '/swagger' in referer
        )

        return is_swagger

    def get_limit(self, request):
        """Determine the page size for the current request.

        Args:
            request (HttpRequest): The incoming DRF request, which may include
                a 'limit' query parameter.

        Returns:
            int: The number of records to return per page when an explicit
                positive integer limit is provided via the query string.
            None: When no limit is set and the client is not Swagger UI
                (unlimited), or when 'limit' is set to 'all', 'unlimited',
                'none', or a non-positive integer.

        Contract:
            - If 'limit' is provided and is a valid positive integer it is
              honoured regardless of client type.
            - If 'limit' is 'all', 'unlimited', 'none', or <= 0, all records
              are returned with no paging.
            - If no 'limit' is supplied, Swagger UI requests default to 1000
              records; all other clients default to unlimited.
        """
        if self.limit_query_param:
            limit = request.query_params.get(self.limit_query_param)
            if limit is not None:
                if str(limit).lower() in ['all', 'unlimited', 'none']:
                    return None
                try:
                    limit = int(limit)
                    if limit <= 0:
                        return None
                    return limit
                except (TypeError, ValueError):
                    pass

        if self.is_swagger_request(request):
            return 1000
        else:
            return None
