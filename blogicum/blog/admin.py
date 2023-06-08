from django.contrib import admin

from blog.models import Category, Location, Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('is_published',
                    'created_at',
                    'title',
                    'text',
                    'pub_date',
                    'author',
                    'location',
                    'category',
                    )
    list_editable = ('is_published',
                     )
    search_fields = ('title',
                     'author',
                     'category',
                     )
    list_filter = ('category',
                   'is_published',
                   'created_at',
                   'pub_date',
                   'location',
                   'author',
                   )
    list_display_links = ('title',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'is_published',
        'created_at',
        'title',
        'description',
        'slug',
    )


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'is_published',
        'created_at',
        'name',
    )


admin.site.empty_value_display = 'Не задано'
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Comment)
