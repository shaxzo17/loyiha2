from django.urls import path
from .views import *

app_name = "blog"

urlpatterns = [
    path('', home_page, name='home'),
    path('detail/<post_id>/', detail, name='detail'),
    path('rating/<value>/<post_id>/', set_rating, name='set_rating'),
    path("<category_slug>/posts/", category_list, name='category_list'),
    path("search/", search, name="search"),
    path('contact/', contact, name='contact'),
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update-profile'),
    path('about/' , about , name='about'),
    

]
