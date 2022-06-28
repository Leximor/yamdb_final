import django_filters as filter
from api.mixins import CreateListDestroy
from api.permissions import (AdministratorOrReadOnly,
                             AuthorOrModeratorOrReadOnly, IsAdmin)
from api.serializers import (CategorySerializer, CommentSerializer,
                             CreateUserSerializer, GenreSerializer,
                             ReadTitleSerializer, ReviewSerializer,
                             TitleSerializer, TokenSerializer, UsersSerializer)
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User, UserRole

MAIL_SUBJECT = 'Ваш confirmation code'
BAD_CONFIRMATION_CODE = 'Это поле некорректно'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'


class TitleFilter(filter.FilterSet):
    genre = filter.CharFilter(field_name='genre__slug', lookup_expr='contains')
    category = filter.CharFilter(field_name='category__slug',
                                 lookup_expr='contains')
    name = filter.CharFilter(field_name='name', lookup_expr='contains')
    year = filter.NumberFilter(field_name='year', lookup_expr='exact')

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre')


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (AdministratorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadTitleSerializer
        return TitleSerializer

    def get_queryset(self):
        return Title.objects.annotate(
            rating=Avg('reviews__score')).order_by('year')


class GenreViewSet(CreateListDestroy):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdministratorOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroy):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdministratorOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorOrModeratorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrModeratorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return Comment.objects.filter(title=review.title, review=review)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user,
                        title=title, review=review)


@api_view(['POST'])
def create_user(request):
    """Создаёт нового или получает из базы ранее созданного пользователя и
       высылает код для получения токена на почту.
    """
    serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email', None)
    username = serializer.validated_data.get('username', None)
    user, created = User.objects.get_or_create(
        email=email, username=username)
    user.set_password(BaseUserManager().make_random_password())
    user.save()
    current_site = get_current_site(request).domain
    email_for_user = EmailMessage(MAIL_SUBJECT, user.password,
                                  current_site, [email])
    email_for_user.send()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_token(request):
    """Создаёт токен для пользователя."""
    serializer = TokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    username = serializer.validated_data['username']
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.validated_data['confirmation_code']
    if confirmation_code == user.password:
        token = RefreshToken.for_user(user).access_token
        data = {'token': str(token)}
        return Response(data, status=status.HTTP_200_OK)
    data = {'confirmation_code': BAD_CONFIRMATION_CODE}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def myself(request):
    """Позволяет пользователю получить или изменить информацию о себе."""
    user = request.user
    if request.method == 'GET':
        serializer = UsersSerializer(user)
        return Response(serializer.data)
    serializer = UsersSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if user.role != UserRole.ADMIN.value:
        serializer.save(role=user.role)
    else:
        serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
