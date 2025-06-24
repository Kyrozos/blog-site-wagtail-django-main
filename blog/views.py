from django.shortcuts import get_object_or_404, render
from .models import Author, BlogPostPage
from wagtail.models import Locale

def author_profile(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    # Get the current locale from the request or the page
    current_locale = Locale.get_active() if hasattr(Locale, "get_active") else None
    posts = BlogPostPage.objects.live().filter(authors=author)
    if current_locale:
        posts = posts.filter(locale=current_locale)
    return render(request, "blog/author_profile.html", {
        "author": author,
        "posts": posts,
    })