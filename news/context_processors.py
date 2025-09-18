def author_status(request):
    is_not_author = False
    if request.user.is_authenticated:
        is_not_author = not hasattr(request.user, 'author')
    return {
        'is_not_author': is_not_author
    }