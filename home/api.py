from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.models import Site, Page, Locale
from rest_framework.response import Response
from home.models import SiteBranding 
from django.utils.translation import get_language, activate
from django.shortcuts import redirect

#api entera y nabvar
class CustomPagesAPIViewSet(PagesAPIViewSet):
    def get_queryset(self):
        request = self.request
        url_parts = request.path.split('/')
        supported_languages = Locale.objects.values_list('language_code', flat=True)
        current_url_language = next((part for part in url_parts if part in supported_languages), None)
        current_language = current_url_language or get_language()

        try:
            current_locale = Locale.objects.get(language_code=current_language)
            return super().get_queryset().filter(locale=current_locale)
        except Locale.DoesNotExist:
            return super().get_queryset().filter(locale=Locale.get_default())

    def detail_view(self, request, pk, *args, **kwargs):
        locale_param = request.GET.get('locale')
        supported_languages = Locale.objects.values_list('language_code', flat=True)
        url_parts = request.path.split('/')
        current_url_language = next((part for part in url_parts if part in supported_languages), None)

        if locale_param and locale_param in supported_languages and locale_param != current_url_language:
            try:
                page = Page.objects.live().get(id=pk)
                target_locale = Locale.objects.get(language_code=locale_param)
                translated_page = page.get_translation(target_locale)
                if translated_page:
                    new_path = request.path.replace(f'/{current_url_language}/', f'/{locale_param}/')
                    new_path = new_path.replace(str(pk), str(translated_page.id))
                    new_url = request.build_absolute_uri(new_path)
                    query_dict = request.GET.copy()
                    query_dict.pop('locale')
                    if query_dict:
                        new_url = f"{new_url}?{'&'.join(f'{k}={v}' for k, v in query_dict.items())}"
                    return redirect(new_url)
            except (Page.DoesNotExist, Locale.DoesNotExist):
                pass

        return super().detail_view(request, pk, *args, **kwargs)

    def listing_view(self, request, *args, **kwargs):
        locale_param = request.GET.get('locale')
        supported_languages = Locale.objects.values_list('language_code', flat=True)
        url_parts = request.path.split('/')
        current_url_language = next((part for part in url_parts if part in supported_languages), None)

        if locale_param and locale_param in supported_languages and locale_param != current_url_language:
            new_path = request.path.replace(f'/{current_url_language}/', f'/{locale_param}/')
            new_url = request.build_absolute_uri(new_path)
            query_dict = request.GET.copy()
            query_dict.pop('locale')
            if query_dict:
                new_url = f"{new_url}?{'&'.join(f'{k}={v}' for k, v in query_dict.items())}"
            return redirect(new_url)

        current_language = current_url_language or get_language()
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
            return f"/{current_language}{page.url}" if not page.url.startswith(f'/{current_language}') else page.url

        def build_menu_tree(page):
            translated_page = page.get_translation_or_none(current_locale) or page
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
            for page in root_page.get_children().live().in_menu():
                if menu_item := build_menu_tree(page):
                    menu_items.append(menu_item)

        branding = SiteBranding.for_request(request)
        response.data.update({
            'navbar': menu_items,
            'logo': branding.logo.file.url if branding.logo else None,
            'favicon': branding.favicon.file.url if branding.favicon else None,
            'current_language': current_language
        })
        return response

#footer de la pagina


from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.models import Site, Locale
from rest_framework.response import Response
from home.models import SiteBranding
from django.utils.translation import get_language, activate
from django.shortcuts import redirect

class FooterAPIViewSet(PagesAPIViewSet):
    def listing_view(self, request, *args, **kwargs):
        supported_languages = list(Locale.objects.values_list('language_code', flat=True))
        url_parts = request.path.split('/')
        current_url_language = next((part for part in url_parts if part in supported_languages), None)

        locale_param = request.GET.get('locale')
        if locale_param and locale_param in supported_languages and locale_param != current_url_language:
            new_path = request.path.replace(f'/{current_url_language}/', f'/{locale_param}/')
            new_url = request.build_absolute_uri(new_path)
            query_dict = request.GET.copy()
            query_dict.pop('locale', None)
            if query_dict:
                new_url += f"?{'&'.join(f'{k}={v}' for k, v in query_dict.items())}"
            return redirect(new_url)

        current_language = current_url_language or get_language()
        activate(current_language)

        try:
            current_locale = Locale.objects.get(language_code=current_language)
        except Locale.DoesNotExist:
            current_locale = Locale.get_default()
            current_language = current_locale.language_code

        site = Site.find_for_request(request)
        root_page = site.root_page if site else None

        def get_translated_url(page):
            return f"/{current_language}{page.url}" if not page.url.startswith(f'/{current_language}') else page.url

        footer_items = []

        if root_page:
            translated_root = root_page.get_translation_or_none(current_locale) or root_page
            footer_items.append({
                'id': translated_root.id,
                'title': translated_root.title,
                'url': get_translated_url(translated_root)
            })

            # Agregar hijas directas
            for child in root_page.get_children().live().in_menu():
                translated_child = child.get_translation_or_none(current_locale) or child
                footer_items.append({
                    'id': translated_child.id,
                    'title': translated_child.title,
                    'url': get_translated_url(translated_child)
                })

        branding = SiteBranding.for_request(request)

        return Response({
            'items': footer_items,
            'logo': branding.logo.file.url if branding.logo else None,
            'favicon': branding.favicon.file.url if branding.favicon else None,
            'current_language': current_language
        })
