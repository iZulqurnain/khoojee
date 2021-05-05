from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from .views import home_page_view, domain_page_view, phone_page_view
from .views.phone.phone_page import sim_details_page_view
from .views.phone.public_phone_search import PublicPhoneSearch

urlpatterns = [
    path('', home_page_view, name="home_page"),
    path('domain', domain_page_view, name="domain_page"),
    path('phone', phone_page_view, name="phone_page"),
    url(r'^sim_details/$', sim_details_page_view, name="sim_details"),
    url(r'^sim_dt_details/data/$', PublicPhoneSearch.as_view(), name='recent_record_list_json'),

]
