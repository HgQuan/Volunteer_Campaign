from rest_framework import pagination

class ProductPaginator(pagination.PageNumberPagination):
    page_size = 8

class ReviewPaginator(pagination.PageNumberPagination):
    page_size = 2

class OrderPaginator(pagination.PageNumberPagination):
    page_size = 5