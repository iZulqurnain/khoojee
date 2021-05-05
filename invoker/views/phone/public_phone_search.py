from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

from invoker.models import SearchedPhoneNumberModel


class PublicPhoneSearch(BaseDatatableView):
    model = SearchedPhoneNumberModel
    columns = ['phone_number', 'details_found', 'is_search_completed']

    order_columns = ['phone_number', 'details_found', 'is_search_completed', '', '']

    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'user':
            # escape HTML for security reasons
            return escape('{0} {1}'.format(row.customer_firstname, row.customer_lastname))
        else:
            return super(PublicPhoneSearch, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(name__istartswith=search)

        # more advanced example using extra parameters
        filter_customer = self.request.GET.get('customer', None)

        if filter_customer:
            customer_parts = filter_customer.split(' ')
            qs_params = None
            for part in customer_parts:
                q = Q(customer_firstname__istartswith=part) | Q(customer_lastname__istartswith=part)
                qs_params = qs_params | q if qs_params else q
            qs = qs.filter(qs_params)
        return qs
