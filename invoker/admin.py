from django.contrib import admin

# Register your models here.
import invoker.models

admin.site.register(invoker.models.SearchedPhoneNumberModel)