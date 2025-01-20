from rest_framework.decorators import api_view,permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegistrationSerializer, LoginSerializer, TeamSerializer, TaskSerializer,TaskUpdationSerializer, TeamMemberSerializer 
from rest_framework import status
from .models import Team, Role, TeamMembership, Task
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied

class RegisterView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            confirm_password = serializer.validated_data.get('confirm_password')

            if User.objects.filter(username=username).exists():
                return Response({"message": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
    
            if password != confirm_password:
                return Response({"message": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            return Response({"message": "User registered successfully."},status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        print("Running login")
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username = request.data.get('username')
            password = request.data.get('password')

            user = User.objects.filter(username=username).first()

            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }, status=status.HTTP_200_OK)

            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
class TeamCreateView(APIView):
    def post(self, request):
        
        team_name = request.data.get("name")
        if Team.objects.filter(name=team_name).exists():
            return Response({'error':'Team with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Team Created Successfully','team':serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AddRemoveTeamMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        team =Team.objects.get(id=team_id)
        print(team)
        user_role = TeamMembership.objects.filter(team = team, user = request.user).first()

        if user_role is None or user_role.role.role not in ['admin','manager']:
            return Response({"error": "You do not have permission to add or create task to this team."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        print(user_id)
        role_id = request.data.get('role_id')
        print(role_id)
            
        # validate and retrieve the user and role
        user = User.objects.get(id=user_id)
        role = Role.objects.get(id=role_id)
            
        if TeamMembership.objects.filter(user=user, team=team).exists():
            return Response({'error': 'User is already a member of the team'}, status=status.HTTP_400_BAD_REQUEST)
            
        team.members.add(user)
        TeamMembership.objects.create(user=user, team=team, role=role)
            
        return Response({'message': 'User added to team successfully'}, status=status.HTTP_200_OK)
    
    def delete(self, request, team_id): 
        team = Team.objects.get(id=team_id)
        user_role = TeamMembership.objects.filter(team = team, user = request.user).first()

        if user_role is None or user_role.role.role not in ['admin','manager']:
            return Response({"error": "You do not have permission to delete task."}, 
                            status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
            
        user = User.objects.get(id=user_id)

        member =TeamMembership.objects.filter(user=user, team=team)
            
        if not member.exists():
            return Response({'error': 'User is not a member of the team'}, status=status.HTTP_400_BAD_REQUEST)
            
        team.members.remove(user)
        member.delete()
            
        return Response({'message': 'User removed from team successfully'}, status=status.HTTP_200_OK)

class TaskCreateView(APIView):

    def post(self, request,team_id):
        try:
            team = Team.objects.get(id = team_id)
            user_role = TeamMembership.objects.filter(team = team, user = request.user).first()

            if user_role is None or user_role.role.role not in ['admin','manager']:
                return Response({"error": "You do not have permission to add or create task to this team."}, status=status.HTTP_403_FORBIDDEN)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
           
            title = serializer.validated_data["title"]
            print(title)
            if Task.objects.filter(title=title).exists():
                return Response({"error": "Task with this title already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
            task = serializer.save()
            return Response({
                "message": "Task created successfully!",
                "task": TaskSerializer(task).data  
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        task_id = request.data.get('task_id')
        try:
            task = Task.objects.get(id=task_id)
            
            # Validate team membership
            team = Team.objects.get(id=team_id)
            if task.team != team:
                return Response(
                    {"error": "The task does not belong to the specified team."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            team_membership = TeamMembership.objects.filter(team=team, user=request.user).first()
            if not team_membership:
                return Response(
                    {"error": "You are not a member of this team."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if not (request.user == task.assignee or request.user == task.creator or 
                team_membership.role.role.lower() == 'manager'):
                return Response(
                    {"error": "You do not have permission to edit this task."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = TaskUpdationSerializer(data=request.data)
            if serializer.is_valid():
                description = serializer.validated_data.get('description', task.description)
                priority = serializer.validated_data.get('priority', task.priority)
                assignee_id = serializer.validated_data.get('assignee')
                assignee = User.objects.get(id=assignee_id) if assignee_id else task.assignee

                # Update the task
                task.description = description
                task.priority = priority
                task.assignee = assignee
                task.save()

                return Response({
                        "message": "Task updated successfully.",
                        "task": TaskSerializer(task).data,
                },status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        except Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

        except User.DoesNotExist:
            return Response({"error": "Assignee not found."}, status=status.HTTP_404_NOT_FOUND)

class DeleteTaskView(APIView):
    def delete(self, request, team_id):
        task_id = request.data.get('task_id')
        try:
            team = Team.objects.get(id=team_id)
            task = Task.objects.get(id=task_id)
            user_role = TeamMembership.objects.filter(team=team, user=request.user).first()

            if user_role is None or user_role.role.role not in ['admin','manager']:
                return Response({"error": "You do not have permission to delete task."}, status=status.HTTP_403_FORBIDDEN)
            task.delete()
            return Response({"message":"Task deleted successfully"},status=status.HTTP_200_OK)
        
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status==status.HTTP_404_NOT_FOUND)
        except Task.DoesNotExist:
            return Response({"error": "Task not Found"}, status=status.HTTP_404_NOT_FOUND)

class UserDashboardview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        print(user)

        tasks = Task.objects.filter(assignee=user)
        print(tasks)
        task_data = [{"id":task.id, "title": task.title, "status": task.status, "deadline": task.deadline}
                     for task in tasks]
        
        response = {
            "user":user.username,
            "task":task_data,
            "task_count": tasks.count()
        }
        return Response(response,status=status.HTTP_200_OK)
