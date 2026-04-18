from django import forms


class StyledFormMixin:
    input_classes = 'mt-1 block w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-blue-400 dark:focus:ring-blue-950'
    select_classes = input_classes
    textarea_classes = input_classes + ' min-h-[110px]'
    checkbox_classes = 'h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styles()

    def _apply_styles(self):
        for field in self.fields.values():
            widget = field.widget
            css_class = self.input_classes
            if isinstance(widget, forms.CheckboxInput):
                css_class = self.checkbox_classes
            elif isinstance(widget, forms.Textarea):
                css_class = self.textarea_classes
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_class = self.select_classes
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing} {css_class}'.strip()
            if isinstance(widget, forms.DateInput):
                widget.input_type = 'date'
            if isinstance(widget, forms.DateTimeInput):
                widget.input_type = 'datetime-local'
