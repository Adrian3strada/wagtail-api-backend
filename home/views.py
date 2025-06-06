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
      
        locale_param = request.GET.get('locale')
        
        
        if locale_param and check_for_language(locale_param):
            current_language = locale_param
            activate(current_language)
        else:
            current_language = get_language()
    
        try:
            current_locale = Locale.objects.get(language_code=current_language)
        except Locale.DoesNotExist:
            current_locale = Locale.get_default()
            current_language = current_locale.language_code
            activate(current_language)

   
        root_page = Page.get_first_root_node()
        menu_pages = (
            root_page.get_children()
            .live()
            .in_menu()
            .filter(locale=current_locale)
            .specific()
            .order_by('path')
        )
        
        def build_menu_tree(page):
        
            translated_page = page.get_translation_or_none(current_locale) or page
            children = (
                page.get_children()
                .live()
                .in_menu()
                .filter(locale=current_locale)
                .specific()
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
        
        return Response({
            "navbar": menu,
            "logo": branding.logo.file.url if branding and branding.logo else None,
            "favicon": branding.favicon.file.url if branding and branding.favicon else None,
            "current_language": current_language
        })
