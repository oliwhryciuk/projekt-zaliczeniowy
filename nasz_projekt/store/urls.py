# store/urls.py
from django.urls import path, include
from . import views

app_name = 'store'

urlpatterns = [
    # API Endpoints
    path('api/bags/', views.bags_list, name='api-bags-list'),
    path('api/bags/size/small/', views.bags_small, name='api-bags-small'),
    path('api/bags/size/medium/', views.bags_medium, name='api-bags-medium'),
    path('api/bags/size/big/', views.bags_big, name='api-bags-big'),
    
    path('api/auth/register/', views.register, name='api-register'),
    path('api/auth/login/', views.login_view, name='api-login'),
    path('api/auth/token/', views.get_auth_token, name='api-token'),
    path('api/auth/logout/', views.logout_view, name='api-logout'),
    
    path('api/cart/', views.cart_view, name='api-cart'),
    path('api/order-summary/', views.summary_view, name='api-summary'),
    
    # HTML Views
    path('', views.main_page, name='main-page'),
    path('login-page/', views.login_page, name='login-page'),
    path('register/', views.register_page, name='register-page'),
    path('logout/', views.logout_view, name='logout'),
    
    path('bags/', views.bags_list_html, name='bags-list-html'),
    path('bags/<int:bag_id>/', views.bag_detail_html, name='bag-detail-html'),
    path('bags/size/small/', views.small_bags_page, name='small-bags'),
    path('bags/size/medium/', views.medium_bags_page, name='medium-bags'),
    path('bags/size/big/', views.big_bags_page, name='big-bags'),
    
    path('cart/', views.cart_page, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-summary/', views.go_to_order_summary, name='order-summary'),
]
