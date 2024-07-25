from . import views
from django.urls import include, path
from rest_framework import routers
# from .views import ProductViewSet, WebsiteViewSet, scrape_and_store
from .views import  scrape_and_store


urlpatterns = [
    path('time/', views.current_time, name='current_time'),
    path('products/', views.product_list, name='product_list'),
    path('search/', views.search_products, name='search_products'),
    # path('api/products/', views.ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='api_product_list'),
    path('api/scrape/', scrape_and_store, name='api_scrape_and_store'),
    # path('api/search/', search_products, name='api_search_products'),
]