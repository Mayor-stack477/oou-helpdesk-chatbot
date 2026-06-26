from django.contrib import admin
from .models import Chat, Document, Rating

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message_preview', 'response_preview', 'rating', 'created_at')
    list_filter = ('created_at', 'rating')
    search_fields = ('message', 'response')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def message_preview(self, obj):
        return obj.message[:50] + '…' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
    
    def response_preview(self, obj):
        return obj.response[:50] + '…' if len(obj.response) > 50 else obj.response
    response_preview.short_description = 'Response'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'uploaded_at', 'description')
    list_filter = ('uploaded_at',)
    search_fields = ('user__username', 'description')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('chat', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('chat__message',)