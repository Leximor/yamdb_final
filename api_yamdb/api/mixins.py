from rest_framework import mixins, viewsets


class CreateListDestroy(mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Класс для получения списка объектов, создания или удаления объекта."""
    pass
