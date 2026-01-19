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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bags/', views.bags_list, name='bags_list'),
    path('bags/small-bags', views.bags_small, name='bags_small'),
    path('bags/medium-bags', views.bags_medium, name='bags_medium'),
    path('bags/big-bags', views.bags_big, name='bags_big'),
    path('login', views.login_view, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('cart', views.cart_view, name='cart'),
    path('summary', views.summary_view, name='summary'),
    path('order-summary/', views.go_to_order_summary, name='go_to_order_summary'),
    path('login-page', views.login_page, name='login_page'),
    path('', views.main_page, name='main_page'),
]

