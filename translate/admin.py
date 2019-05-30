from django.contrib import admin
from translate.models import File
from translate.models import Text

# Register your models here.
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip_address', 'chara_count', 'name', 'created_date', 'modified_date',)  # 一覧に出したい項目
    list_display_links = ('id', 'name',)  # 修正リンクでクリックできる項目
admin.site.register(File, FileAdmin)

class TextAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip_address', 'chara_count', 'created_date', 'modified_date',)  # 一覧に出したい項目
    list_display_links = ('id',)  # 修正リンクでクリックできる項目
admin.site.register(Text, TextAdmin)
