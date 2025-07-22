from django.contrib import admin
from .models import BlacklistToken

# Register your models here.
@admin.register(BlacklistToken)
class BlacklistTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'created_at')
    search_fields = ('user', 'token')
    list_filter = ('created_at',)
    ordering = ('-created_at',)