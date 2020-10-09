from django.contrib import admin
from .models import (ClientAccount, CustomUser,
                    Notification,File, ManagerAccount,
                    Saloon, Style, Rating, SaloonService,
                     Appointment,)
# Register your models here.


class ManagerAccountAdmin(admin.ModelAdmin):
    list_display = ['owner']


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['origin', 'destination', 'seen', 'date']
    search_fields = ['date', 'origin__first_name', ' destination__first_name']


class ClientAccountAdmin(admin.ModelAdmin):
    list_display = ['owner']
    search_fields = ['owner__first_name']


class SaloonAdmin(admin.ModelAdmin):
    list_display = ['owner', 'saloon_name', 'address', 'opening_hours', 'closing_hours', 'approved']
    search_fields = ('saloon_name', 'owner__first_name')


class StyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'service']
    search_fields = ['name']


class SaloonServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'saloon']
    search_fields = ['name', 'saloon__saloon_name']


class AppointMentAdmin(admin.ModelAdmin):
    list_display = ['time', 'client', 'saloon', 'approved']
    search_fields = ['time', 'client__owner__first_name', 'saloon__saloon_name']


admin.site.register(Appointment, AppointMentAdmin)
admin.site.register(SaloonService, SaloonServiceAdmin)
admin.site.register(ManagerAccount, ManagerAccountAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(ClientAccount, ClientAccountAdmin)
admin.site.register(Saloon, SaloonAdmin)
admin.site.register(Style, StyleAdmin)
admin.site.register(Rating)
admin.site.register(File)
admin.site.register(CustomUser)

