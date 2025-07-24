from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # URLs pour la gestion des congés des employés
    path('request-leave/', views.request_leave_view, name='request_leave'),
    path('my-leaves/', views.my_leaves_view, name='my_leaves'),

    # URLs pour l'approbation des congés par les responsables
    path('leaves-to-approve/', views.leaves_to_approve_view, name='leaves_to_approve'),
    path('leave/<int:pk>/manage/', views.manage_leave_view, name='manage_leave'),

    # URL pour afficher tous les congés des employés
    path('all-employees-leaves/', views.all_employees_leaves_view, name='all_employees_leaves'),

    # Nouvelles URLs pour la modification et la suppression (pour les responsables)
    path('leave/<int:pk>/edit/', views.edit_leave_view, name='edit_leave'),
    path('leave/<int:pk>/delete/', views.delete_leave_view, name='delete_leave'),
]
