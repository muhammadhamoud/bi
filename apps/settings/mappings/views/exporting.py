import csv
from django.http import HttpResponse


class CsvExportMixin:
    export_param = 'export'

    def should_export(self):
        return self.request.GET.get(self.export_param) == 'csv'

    def get_export_filename(self):
        return 'export.csv'

    def get_export_headers(self):
        """
        Return a list of tuples:
        [
            ('Column Header', callable_or_attr_name),
        ]
        """
        return []

    def get_export_rows(self, queryset):
        headers = self.get_export_headers()
        for obj in queryset:
            row = []
            for _, accessor in headers:
                if callable(accessor):
                    value = accessor(obj)
                else:
                    value = getattr(obj, accessor, '')
                row.append('' if value is None else str(value))
            yield row

    def render_to_csv_response(self, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_export_filename()}"'

        writer = csv.writer(response)
        headers = self.get_export_headers()
        writer.writerow([label for label, _ in headers])

        for row in self.get_export_rows(queryset):
            writer.writerow(row)

        return response
    

    