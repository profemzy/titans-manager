from typing import TypeVar, Generic, Type, Optional, List

from django.db import transaction

T = TypeVar('T')

class BaseService(Generic[T]):
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    def get_by_id(self, id: int) -> Optional[T]:
        try:
            return self.model_class.objects.get(pk=id)
        except self.model_class.DoesNotExist:
            return None

    def list_all(self) -> List[T]:
        return self.model_class.objects.all()

    @transaction.atomic
    def create(self, **kwargs) -> T:
        instance = self.model_class(**kwargs)
        instance.full_clean()
        instance.save()
        return instance

    @transaction.atomic
    def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.full_clean()
        instance.save()
        return instance

    @transaction.atomic
    def delete(self, instance: T) -> bool:
        instance.delete()
        return True
