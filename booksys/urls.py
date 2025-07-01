from django.urls import path
from .views import *

urlpatterns = [
    path('genres/', GenreListView.as_view(), name='genre-list'),
    path('authors/', AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('books/', BookListView.as_view(), name='author-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('copies/', CopyListView.as_view(), name='copy-list'),
    path('copies/<int:pk>/', CopyDetailView.as_view(), name='copy-detail'),
]