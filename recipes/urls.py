from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('add/', views.add_recipe, name='add_recipe'),
    path('upload/', views.upload_file, name='upload_file'),
    path('search/', views.search_recipes, name='search_recipes'),
    path('edit/<int:pk>/', views.edit_recipe, name='edit_recipe'),
    path('delete/<int:pk>/', views.delete_recipe, name='delete_recipe'),
]
