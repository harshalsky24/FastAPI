from rest_framework.decorators import api_view,permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegistrationSerializer, LoginSerializer, TeamSerializer, TaskSerializer
from rest_framework import status
from .models import Team, Role, TeamMembership, Task
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
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

        if not request.user.is_staff:
            raise PermissionDenied('only admin can create team')
        
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

    def permisssion(self, user, team):
        try:
            membership = TeamMembership.objects.get(user=user, team=team)
            return membership.role.name in ['admin','manager']
        except TeamMembership.DoesNotExist:
            return False
        
    def post(self, request, team_id):
        team =Team.objects.get(id=team_id)
        
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
            
        # Validate and retrieve the user and role
        user = User.objects.get(id=user_id)
        role = Role.objects.get(id=role_id)
            
        if TeamMembership.objects.filter(user=user, team=team).exists():
            return Response({'error': 'User is already a member of the team'}, status=status.HTTP_400_BAD_REQUEST)
            
        team.members.add(user)
        TeamMembership.objects.create(user=user, team=team, role=role)
            
        return Response({'message': 'User added to team successfully'}, status=status.HTTP_200_OK)
    
    def delete(self, request, team_id): 
        team = Team.objects.get(id=team_id)

        user_id = request.data.get('user_id')
            
        user = User.objects.get(id=user_id)

        member =TeamMembership.objects.filter(user=user, team=team)
            
        if not member.exists():
            return Response({'error': 'User is not a member of the team'}, status=status.HTTP_400_BAD_REQUEST)
            
        team.members.remove(user)
        member.delete()
            
        return Response({'message': 'User removed from team successfully'}, status=status.HTTP_200_OK)

class TaskCreateView(APIView):
    def post(self, request):
        user = request.user  # Creator
        
        
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