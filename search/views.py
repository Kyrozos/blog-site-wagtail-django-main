from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from wagtail.models import Page, Locale
from django.utils.translation import get_language

def search(request):
    search_query = request.GET.get("query", None)
    page_number = request.GET.get("page", 1)

    current_language = get_language()

    try:
        current_locale = Locale.objects.get(language_code=current_language)
    except Locale.DoesNotExist:
        current_locale = None

    # ✅ Apply locale filter before calling `.search()`
    base_qs = Page.objects.live()
    if current_locale:
        base_qs = base_qs.filter(locale=current_locale)

    if search_query:
        search_results = base_qs.search(search_query)
    else:
        search_results = base_qs.none()

    paginator = Paginator(search_results, 10)
    try:
        paginated_results = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_results = paginator.page(1)
    except EmptyPage:
        paginated_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": paginated_results,
        },
    )
