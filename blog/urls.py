from . import views
from django.urls import path

urlpatterns = [
    path('author/<int:author_id>/', views.author_profile, name='author_profile'),
]