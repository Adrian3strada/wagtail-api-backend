from wagtail.api.v2.views import PagesAPIViewSet, BaseAPIViewSet
from wagtail.models import Site, Page, Locale
from rest_framework.response import Response
from home.models import FooterLink, SiteBranding 
from .models import CustomPage
from django.utils.translation import get_language, activate
from django.utils.translation import check_for_language


class CustomPagesAPIViewSet(PagesAPIViewSet):

    def listing_view(self, request, *args, **kwargs):
        current_language = None
        
        lang_param = request.GET.get('locale') or request.GET.get('lang')
        if lang_param and check_for_language(lang_param):
            current_language = lang_param
        if not current_language:
            accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
            if accept_language:
                for language in accept_language.split(','):
                    lang_code = language.split(';')[0].strip().lower()[:2]
                    if check_for_language(lang_code):
                        current_language = lang_code
                        break

        if not current_language:
            current_language = get_language()

        activate(current_language)
        
        try:
            current_locale = Locale.objects.get(language_code=current_language)
        except Locale.DoesNotExist:
            current_locale = Locale.get_default()
            current_language = current_locale.language_code

        
        response = super().listing_view(request, *args, **kwargs)

        site = Site.find_for_request(request)
        root_page = site.root_page if site else None

        def get_translated_url(page):
    
            if page.url.startswith(f'/{current_language}'):
                return page.url
            return f"/{current_language}{page.url}"

        def build_menu_tree(page):
            translated_page = page.get_translation_or_none(current_locale) or pag
            children = page.get_children().live().in_menu()
            
            item = {
                'title': translated_page.title,
                'url': get_translated_url(translated_page),
                'children': []
            }
            
 
            for child in children:
                child_translated = child.get_translation_or_none(current_locale) or child
                child_item = build_menu_tree(child)
                if child_item: 
                    item['children'].append(child_item)
            
            return item

        menu_items = []
        if root_page:
    
            first_level_pages = root_page.get_children().live().in_menu()
            
            for page in first_level_pages:
                menu_item = build_menu_tree(page)
                if menu_item:
                    menu_items.append(menu_item)
        branding = SiteBranding.for_request(request)
        logo_url = branding.logo.file.url if branding.logo else None
        favicon_url = branding.favicon.file.url if branding.favicon else None
        response.data['navbar'] = menu_items
        response.data['logo'] = logo_url
        response.data['favicon'] = favicon_url
        response.data['current_language'] = current_language

        return response


class FooterAPIViewSet(BaseAPIViewSet):
    model = FooterLink
    meta_fields = ['id']
    listing_default_fields = ['titulo', 'url']
