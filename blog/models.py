from django.db import models
from wagtail.models import Page, Orderable, Locale
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from datetime import date
from modelcluster.models import ParentalKey, ParentalManyToManyField
from wagtail.snippets.models import register_snippet
from django import forms
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.search import index
from django.utils.translation import get_language
from taggit.models import Tag, TaggedItemBase

class BlogIndexPage(Page):
    description = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [FieldPanel("description")]
    def get_context(self, request):
        context = super().get_context(request)
        blogposts = self.get_children().live().order_by("-first_published_at")
        context["blogposts"] = blogposts
        
        return context

class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey("BlogPostPage", related_name="tagged_items",
                                 on_delete=models.CASCADE)

class BlogPostPage(Page):
    date = models.DateField("Post Date", default=date.today)
    intro = RichTextField(blank=True, max_length=500, help_text="A short summary of the post, displayed on the index page.")
    body = RichTextField(blank=True)
    authors = ParentalManyToManyField("blog.Author", blank=True)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    featured = models.BooleanField(default=False, help_text="Check this box to feature this post on the homepage.")
    categories = ParentalManyToManyField("blog.Category", blank=True, related_name="blog_posts")
    def main_image(self):
        thumbnail_image = self.image_gallery.first()
        if thumbnail_image:
            return thumbnail_image.image
        else:
            return None
 
    def get_related_posts(self, count=3):
        # Get the current locale for the page
        current_locale = self.locale
        # Get posts that share at least one tag, excluding self, and in the same locale
        related = BlogPostPage.objects.live().public().filter(
            tags__in=self.tags.all(),
            locale=current_locale
        ).exclude(id=self.id).distinct().order_by('-first_published_at')[:count]
        return related
    
    def get_featured_posts(self, count=3):
        # Get featured posts in the same locale
        current_locale = self.locale
        featued = BlogPostPage.objects.live().public().filter(
            featured=True,
            locale=current_locale
        ).exclude(id=self.id).distinct().order_by('-first_published_at')[:count]
        return featued
    
    # @property
    # def word_count(self):
    #     # Count words in the body field
    #     import re
    #     text = re.sub('<[^<]+?>', '', self.body or "")
    #     return len(text.split())

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("authors", widget=forms.CheckboxSelectMultiple),
        FieldPanel("intro"),
        FieldPanel("body"),
        InlinePanel("image_gallery", label="gallery images"),
        FieldPanel("tags"),
        FieldPanel("featured", widget=forms.CheckboxInput),
        FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
        # FieldPanel("word_count", read_only=True),
    ]

    search_fields = Page.search_fields + [index.SearchField("body"), index.SearchField("intro")]


class BlogPageImageGallery(Orderable):
    page = ParentalKey(BlogPostPage, related_name="image_gallery",
                       on_delete=models.CASCADE)
    image = models.ForeignKey("wagtailimages.Image", related_name="+",
                              on_delete=models.CASCADE)
    caption = models.CharField(max_length=255, blank=True)
    panels = [FieldPanel("image"), FieldPanel("caption")]

@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    description = RichTextField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
    ]

    def safe(self):
        if not self.slug:
            return self.name.lower().replace(" ", "-")
        return self.slug

    def get_absolute_url(self):
        return f"/categories/{self.safe()}/"
    
    def __str__(self):
        return self.name

@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=255)
    # slug = models.SlugField(max_length=500, unique=True, blank=True)
    bio = RichTextField(blank=True)
    author_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    # Add more social fields as needed

    panels = [
        FieldPanel("name"),
        FieldPanel("bio"),
        FieldPanel("author_image"),
        FieldPanel("twitter"),
        FieldPanel("linkedin"),
        FieldPanel("github"),
    ]

    # def safe(self):
    #     if not self.slug:
    #         return self.name.lower().replace(" ", "-")
    #     return self.slug

    # def get_absolute_url(self):
    #     return f"/authors/{self.safe()}/"
    
    def __str__(self):
        return self.name

class AuthorProfilePage(Page):
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="profile_pages"
    )

    content_panels = Page.content_panels + [
        FieldPanel("author"),
    ]

    # List all posts by this author
    def get_context(self, request):
        context = super().get_context(request)
        context["posts"] = BlogPostPage.objects.live().filter(authors=self.author)
        return context

class TagIndexPage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        tag = request.GET.get("tag")
        blogposts = BlogPostPage.objects.live()

        # Filter by current locale
        current_language = get_language()
        try:
            current_locale = Locale.objects.get(language_code=current_language)
            blogposts = blogposts.filter(locale=current_locale)
        except Locale.DoesNotExist:
            pass

        if tag:
            blogposts = blogposts.filter(tags__name=tag)
            context["selected_tag"] = tag

        context["blogposts"] = blogposts
        #Show only tags used in the current locale
        used_tag_ids = blogposts.values_list('tags', flat=True).distinct()
        context["all_tags"] = Tag.objects.filter(id__in=used_tag_ids)
        return context






