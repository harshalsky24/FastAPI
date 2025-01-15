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
    #relationships
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='roles')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')

    def __str__(self):
        return f"{self.user.username} - {self.role} in {self.team.name}"
    
class Task(models.Model):
    status_choices =[
        ('not started','Not Started'),
        ('in progress','In Progress'),
        ('in review','In Review'),
        ('reviewed','Reviewed'),
        ('completed','Completed'),
    ]
    set_priority = [('Low','LOW'),('Medium','MEDIUM'),('High','HIGH')]
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=200, choices=status_choices, default='Not Started')
    priority = models.CharField(max_length=200, choices=set_priority, default='Medium')
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