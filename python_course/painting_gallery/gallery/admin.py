from django.contrib import admin
from .models import Style, Artist, Painting


@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    list_display = ('name', 'period', 'artist_count', 'painting_count')
    search_fields = ('name', 'period')
    list_filter = ('period',)

    def artist_count(self, obj):
        return obj.artists.count()
    artist_count.short_description = 'Художников'

    def painting_count(self, obj):
        return obj.paintings.count()
    painting_count.short_description = 'Картин'


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'nationality', 'birth_year', 'death_year', 'style', 'painting_count')
    list_filter = ('nationality', 'style')
    search_fields = ('first_name', 'last_name', 'nationality')
    list_select_related = ('style',)

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Художник'

    def painting_count(self, obj):
        return obj.paintings.count()
    painting_count.short_description = 'Картин'


@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'style', 'year', 'technique', 'museum')
    list_filter = ('technique', 'style', 'year')
    search_fields = ('title', 'artist__first_name', 'artist__last_name', 'museum')
    list_select_related = ('artist', 'style')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'artist', 'style', 'year', 'technique')
        }),
        ('Размеры и место хранения', {
            'fields': ('width_cm', 'height_cm', 'museum')
        }),
        ('Дополнительно', {
            'fields': ('description', 'image_url')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
