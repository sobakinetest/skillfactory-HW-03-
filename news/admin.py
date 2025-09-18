from django.contrib import admin
from .models import Post, Comment, Category, Author

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_categories', 'author', 'rating', 'post_type', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('categories', 'post_type', 'author')

    def display_categories(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])

    display_categories.short_description = 'Категории'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'display_category', 'user', 'rating', 'created_at')
    search_fields = ('text',)
    list_filter = ('user',)

    def display_category(self, obj):
        first_cat = obj.post.categories.first()
        return first_cat.name if first_cat else None

    display_category.short_description = 'Категория поста'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')
    readonly_fields = ('rating',)
    fields = ('user', 'rating')


admin.site.register(Category)

