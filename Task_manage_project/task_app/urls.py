from . import views
from django.urls import path
urlpatterns = [
     path('register/', views.RegisterView.as_view(), name='register'),
     path('login/', views.LoginView.as_view(), name='login'),
     path('team-create/', views.TeamCreateView.as_view(), name='team_create'),
     path('teams/add-remove-member/<int:team_id>/', views.AddRemoveTeamMemberView.as_view(), name='add-remove-member'),
     path('task-create/<int:team_id>/', views.TaskCreateView.as_view(), name="create_task"),
     path('task-update/<int:team_id>/', views.TaskUpdateView.as_view(), name="task_update"),
     path('task-delete/<int:team_id>/', views.DeleteTaskView.as_view(), name="task-delete"),
     path('user-dashboard/',views.UserDashboardview.as_view(), name="user_dashboard"),
]