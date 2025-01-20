from django.db import models
from django.contrib.auth.models import User

#class User-built in field like "username","pass"
class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #relationship
    members = models.ManyToManyField(User, related_name='teams')

    def __str__(self):
        return self.name
    
class Role(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),#(value,label)
        ('manager', 'Manager'),
        ('member', 'Member'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.role}"
    
class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'

        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=200, choices=Status, default='Not Started')
    priority = models.CharField(max_length=200, choices=Priority, default='Medium')
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #relationships
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_tasks', null=True, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return f"{self.title}"
    
class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} - {self.team.name}'