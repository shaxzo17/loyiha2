from django.urls import path
from .views import *

app_name = "blog"

urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('send-code/', send_verification_code, name='send_code'),
    path('signup/', signup, name='signup'),
    path('verify-code/', verify_code, name='verify_code'),
    path('', blog_home, name='home'),
    path('detail/<post_id>/', detail, name='detail'),
    path('rating/<value>/<post_id>/', set_rating, name='set_rating'),
    path("<category_slug>/posts/", category_list, name='category_list'),
    path("search/", search, name="search"),
    path('contact/', contact, name='contact'),
]
