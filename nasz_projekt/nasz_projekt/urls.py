"""
URL configuration for nasz_projekt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from biblioteka import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bags/small-bags', views.small_bags_page, name='small_bags_page'),
    path('bags/medium-bags', views.medium_bags_page, name='medium_bags_page'),
    path('bags/big-bags', views.big_bags_page, name='big_bags_page'),
    path('bags/', views.bags_list, name='bags_list'),
    path('bags/<int:bag_id>/', views.bag_detail, name='bag_detail'),
    path('login', views.login_view, name='login'),
    path('get-token/', views.get_auth_token, name='get_auth_token'),
    path('register/', views.register, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('cart', views.cart_page, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('summary', views.summary_view, name='summary'),
    path('order-summary/', views.go_to_order_summary, name='go_to_order_summary'),
    path('login-page', views.login_page, name='login_page'),
    path('', views.main_page, name='main_page'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

