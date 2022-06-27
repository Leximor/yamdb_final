import datetime as dt

from rest_framework import serializers

from users.models import User
from reviews.models import (Genre, Category, Title,
                            Review, Comment)

CHANGE_USERNAME = 'Нельзя создать пользователя с username = "me"'
MESSAGE_DUBPLICATE_REVIEW = 'От Вас уже есть отзыв на это произведение.'
MESSAGE_WRONG_SCORE = 'Оценка произведения должна быть в диапазоне от 1 до 10'
MESSAGE_NO_COMMENTS = 'Неверно указано произведение и отзыв.'
CHECK_YEAR = 'Год выпуска превышает текущий.'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Category


class ReadTitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Category.objects.all(),
                                            slug_field='slug')
    genre = serializers.SlugRelatedField(many=True,
                                         queryset=Genre.objects.all(),
                                         slug_field='slug')

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        year = dt.datetime.now().year
        if year < value:
            raise serializers.ValidationError(CHECK_YEAR)
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'title', 'author')
        model = Review

    def validate(self, data):
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            user = self.context['request'].user
            if Review.objects.filter(title=title_id, author=user).exists():
                raise serializers.ValidationError(MESSAGE_DUBPLICATE_REVIEW)
        return data

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError(MESSAGE_WRONG_SCORE)
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date')
        read_only_fields = ('id', 'title', 'author', 'review', 'pub_date')
        model = Comment


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(CHANGE_USERNAME)
        return value


class UsersSerializer(CreateUserSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
