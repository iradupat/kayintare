from django.contrib import admin
from .models import (ClientAccount, CustomUser,
                    Notification,File, ManagerAccount,
                    Saloon, Style, Rating,)
# Register your models here.

admin.site.register(ManagerAccount)
admin.site.register(Notification)
admin.site.register(ClientAccount)
admin.site.register(Saloon)
admin.site.register(Style)
admin.site.register(Rating)
admin.site.register(File)
admin.site.register(CustomUser)

