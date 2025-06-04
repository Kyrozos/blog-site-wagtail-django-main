from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.models import TranslatableMixin
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
)

from wagtail.fields import RichTextField
# import AbstractEmailForm and AbstractFormField:
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField

# import FormSubmissionsPanel:
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)
from wagtail.snippets.models import register_snippet
from wagtailcaptcha.models import WagtailCaptchaEmailForm

@register_setting
class NavigationSettings(BaseGenericSetting):
    linkedin_url = models.URLField(verbose_name="LinkedIn URL", blank=True)
    github_url = models.URLField(verbose_name="GitHub URL", blank=True)
    mastodon_url = models.URLField(verbose_name="Mastodon URL", blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("linkedin_url"),
                FieldPanel("github_url"),
                FieldPanel("mastodon_url"),
            ],
            "Social settings",
        )
    ]
class FormField(TranslatableMixin, AbstractFormField):
    page = ParentalKey('FormPage', on_delete=models.CASCADE, related_name='form_fields')


class FormPage(WagtailCaptchaEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('intro'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address'),
                FieldPanel('to_address'),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]

    def process_form_submission(self, form):
        super().process_form_submission(form)
        email = form.cleaned_data.get('email')
        name = form.cleaned_data.get('name')
        if email:
            Subscriber.objects.get_or_create(email=email, defaults={'name': name or ''})


@register_snippet
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True) 
    subscribed_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("email", help_text="The email address of the subscriber."),
        FieldPanel("name", help_text="The full name of the subscriber (optional)."),
        FieldPanel("subscribed_at", read_only=True),
    ]

    def __str__(self):
        return self.email