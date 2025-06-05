

from wagtail.models import Page
from rest_framework.views import APIView
from rest_framework.response import Response
from home.models import SiteBranding
from django.utils.translation import get_language
from wagtail.models import Page, Locale
from django.urls import reverse
from django.utils.translation import activate
from django.utils.translation import check_for_language

class NavbarAPIView(APIView):
    def get(self, request):
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

        root_page = Page.get_first_root_node()
        menu_pages = (
            root_page.get_children()
            .live()
            .in_menu()
            .filter(locale=current_locale)
            .order_by('path')
        )
        
        def build_menu_tree(page):
            translated_page = page.get_translation_or_none(current_locale) or page
            children = (
                page.get_children()
                .live()
                .in_menu()
                .filter(locale=current_locale)
                .order_by('path')
            )
            
            menu_item = {
                "title": translated_page.title,
                "url": f"/{current_language}{translated_page.url}" if not translated_page.url.startswith(f'/{current_language}') else translated_page.url,
                "children": []
            }
            
            if children:
                menu_item["children"] = [build_menu_tree(child) for child in children]
            
            return menu_item

     
        menu = [build_menu_tree(page) for page in menu_pages]
        branding = SiteBranding.for_request(request)
        logo_url = branding.logo.file.url if branding.logo else None
        favicon_url = branding.favicon.file.url if branding.favicon else None

        return Response({
            "navbar": menu,
            "logo": logo_url,
            "favicon": favicon_url,
            "current_language": current_language
        })
