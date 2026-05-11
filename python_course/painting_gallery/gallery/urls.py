from django.urls import path
from . import views

urlpatterns = [
    # Картины
    path('', views.painting_list, name='painting_list'),
    path('painting/<int:pk>/', views.painting_detail, name='painting_detail'),
    path('painting/add/', views.painting_add, name='painting_add'),
    path('painting/<int:pk>/edit/', views.painting_edit, name='painting_edit'),
    path('painting/<int:pk>/delete/', views.painting_delete, name='painting_delete'),

    # Художники
    path('artists/', views.artist_list, name='artist_list'),
    path('artist/<int:pk>/', views.artist_detail, name='artist_detail'),
    path('artist/add/', views.artist_add, name='artist_add'),
    path('artist/<int:pk>/edit/', views.artist_edit, name='artist_edit'),

    # Стили
    path('styles/', views.style_list, name='style_list'),
    path('style/add/', views.style_add, name='style_add'),
    path('style/<int:pk>/edit/', views.style_edit, name='style_edit'),
]
