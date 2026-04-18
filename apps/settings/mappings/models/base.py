from django.core.exceptions import ValidationError
from django.db import models

from apps.core.common.models import ActivatableModel, AuditUserModel, SortableModel, TimeStampedModel


class PropertyScopedModel(TimeStampedModel, ActivatableModel, AuditUserModel):
    property = models.ForeignKey('propertycore.Property', on_delete=models.CASCADE, related_name='%(class)ss')

    class Meta:
        abstract = True


class MappingGroupBase(PropertyScopedModel, SortableModel):
    code = models.CharField(max_length=60)
    name = models.CharField(max_length=140)
    color = models.CharField(max_length=140, blank=True, null=True)
    icon = models.CharField(max_length=140, blank=True, null=True)
    image = models.ImageField(upload_to="mappings/images/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.code is not None:
            self.code = str(self.code).strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.property.name} / {self.name}'


class MappingCategoryBase(PropertyScopedModel, SortableModel):
    code = models.CharField(max_length=60)
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.code is not None:
            self.code = str(self.code).strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.property.name} / {self.name}'


class SourceMappingBase(PropertyScopedModel, SortableModel):
    source_system = models.ForeignKey('dataopsfiles.SourceSystem', on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)ss')
    code = models.CharField(max_length=80)
    name = models.CharField(max_length=160, blank=True, null=True)
    description = models.CharField(max_length=160, blank=True, null=True)
    # mapped_code = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True, null=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    is_review_required = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        abstract = True

    def clean(self):
        if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
            raise ValidationError({'effective_to': 'Effective end date cannot be before effective start date.'})

    
    def save(self, *args, **kwargs):
        if self.code is not None:
            self.code = str(self.code).strip().upper()
        super().save(*args, **kwargs)
    

