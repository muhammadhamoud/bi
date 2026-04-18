from django import forms
from django.utils.text import slugify

from apps.properties.core.models import Property


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'organization',
            'name',
            'code',
            'resort',
            'property_type',
            'city',
            'country',
            'currency',
            'timezone',
            'total_rooms',
            'is_active',
        ]
        widgets = {
            'organization': forms.Select(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100',
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100',
                'placeholder': 'Property name',
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100',
                'placeholder': 'Property code',
            }),
            'resort': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100',
                'placeholder': 'Resort code',
            }),
            'property_type': forms.Select(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100',
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100',
                'placeholder': 'City',
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100',
                'placeholder': 'Country',
            }),
            'currency': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm uppercase text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100',
                'placeholder': 'AED',
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100',
                'placeholder': 'Asia/Dubai',
            }),
            'total_rooms': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100',
                'min': '0',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        organization = cleaned_data.get('organization')
        name = cleaned_data.get('name')

        if organization and name:
            slug = slugify(f'{organization.code}-{name}')
            qs = Property.objects.filter(slug=slug)

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error(
                    'name',
                    f'A property with this generated slug already exists: "{slug}". Please change the property name.'
                )

        return cleaned_data