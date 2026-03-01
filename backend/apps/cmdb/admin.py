from django.contrib import admin
from .models import Host, IDC, City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(IDC)
class IDCAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city')
    search_fields = ('name',)
    list_filter = ('city',)


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('id', 'hostname', 'city', 'idc', 'ip', 'is_active')
    search_fields = ('hostname', 'ip_address')
    list_filter = ('city', 'idc', 'is_active')
