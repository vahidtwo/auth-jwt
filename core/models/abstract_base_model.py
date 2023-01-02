from django.db import models
from django.db.models import QuerySet, Q
from django.utils import timezone


class SoftQuerySet(QuerySet):
    def delete(self):
        return self.update(deleted=True, deleted_at=timezone.now())

    def un_delete(self):
        return self.update(deleted=False)

    def all_with_deleted(self):
        qs = super(SoftQuerySet, self).all()
        qs.__class__ = SoftQuerySet
        return qs


class SoftDeleteObjectsManager(models.Manager):
    def _base_queryset(self):
        return super(SoftDeleteObjectsManager, self).get_queryset()

    def get_queryset(self):
        qs = (
            super(SoftDeleteObjectsManager, self)
            .get_queryset()
            .filter(Q(deleted=False) | Q(deleted__isnull=True))
        )

        if not issubclass(qs.__class__, SoftQuerySet):
            qs.__class__ = SoftQuerySet
        return qs

    def all_with_deleted(self, prt=False):
        if hasattr(self, "core_filters"):  # it's a RelatedManager
            qs = self._base_queryset().filter(**self.core_filters)
        else:
            qs = self._base_queryset()
        return qs


class DeletedObjectsManager(models.Manager):
    def get_queryset(self):
        return super(DeletedObjectsManager, self).get_queryset().filter(deleted=True)


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False, null=True, blank=True, db_index=True)

    all_objects = models.Manager()
    objects = SoftDeleteObjectsManager()

    class Meta:
        abstract = True
        ordering = ["-id"]
        default_manager_name = "objects"

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save(*args, **kwargs)

    def un_delete(self, *args, **kwargs):
        self.deleted = False
        self.save(*args, **kwargs)
