from django.contrib import admin

from blog.models import Category, Comment, Location, Post


@admin.register(Post)
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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'is_published',
        'created_at',
        'title',
        'description',
        'slug',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'is_published',
        'created_at',
        'name',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('is_published',
                    'created_at',
                    'text',
                    'author',
                    )
    list_editable = ('text',
                     )
    list_display_links = ('is_published',)


admin.site.empty_value_display = 'Не задано'
