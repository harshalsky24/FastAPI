from . import views
from django.urls import path
urlpatterns = [
     path('register/', views.RegisterView.as_view(), name='register'),
     path('login/', views.LoginView.as_view(), name='login'),
     path('team_create/',views.TeamCreateView.as_view(), name='Team_create'),
     path('teams/add-remove-member/<int:team_id>/', views.AddRemoveTeamMemberView.as_view(), name='add-remove-member'),
     path('create_task/',views.TaskCreateView.as_view(), name="create_task"),
]