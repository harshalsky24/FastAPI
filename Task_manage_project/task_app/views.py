from rest_framework.decorators import api_view,permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegistrationSerializer, LoginSerializer, TeamSerializer
from rest_framework import status
from .models import Team
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

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