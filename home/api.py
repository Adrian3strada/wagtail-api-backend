from wagtail.api.v2.views import PagesAPIViewSet, BaseAPIViewSet
from wagtail.models import Site, Page, Locale
from rest_framework.response import Response
from home.models import SiteBranding 
from django.utils.translation import get_language, activate, get_language_from_request
from django.shortcuts import redirect

#api entera y nabvar
class CustomPagesAPIViewSet(PagesAPIViewSet):
    def get_locale_language(self, request):
        supported_languages = set(Locale.objects.values_list('language_code', flat=True))

        locale_param = request.GET.get('locale')
        if locale_param and locale_param in supported_languages:
            return locale_param

        path_parts = request.path.strip("/").split("/")
        lang_from_url = next((part for part in path_parts if part in supported_languages), None)
        if lang_from_url:
            return lang_from_url

        lang_from_request = get_language_from_request(request)
        if lang_from_request and lang_from_request in supported_languages:
            return lang_from_request

        default_lang = Locale.get_default().language_code
        return default_lang



    def detail_view(self, request, pk, *args, **kwargs):
        supported_languages = set(Locale.objects.values_list('language_code', flat=True))
        locale_param = request.GET.get('locale')

        try:
            page = Page.objects.live().get(id=pk)
            lang = page.locale.language_code
            activate(lang)

        except Page.DoesNotExist:
            return Response({"error": f"La página con ID {pk} no existe."}, status=404)

        if locale_param and locale_param in supported_languages and locale_param != lang:
            try:
                target_locale = Locale.objects.get(language_code=locale_param)
            except Locale.DoesNotExist:
                return Response({"error": f"Locale '{locale_param}' no encontrado."}, status=404)

            try:
                translated_page = page.get_translation(target_locale)
            except Exception as e:
                return Response({"error": f"Error al obtener la traducción: {e}"}, status=500)

            if translated_page:
                new_url = request.build_absolute_uri(translated_page.get_url(request))
                return redirect(new_url)
            else:
                return Response({"error": "No se encontró traducción para esta página."})
        return super().detail_view(request, pk, *args, **kwargs)
            

    def listing_view(self, request, *args, **kwargs):
        lang = self.get_locale_language(request)
        locale_param = request.GET.get('locale')
        supported_languages = set(Locale.objects.values_list('language_code', flat=True))

      
        if locale_param and locale_param in supported_languages and locale_param != lang:
            new_url = request.build_absolute_uri(request.path)
            query_dict = request.GET.copy()
            query_dict.pop('locale')
            if query_dict:
                new_url += f"?{'&'.join(f'{k}={v}' for k, v in query_dict.items())}"
            return redirect(new_url)

        activate(lang)
        current_locale = Locale.objects.get(language_code=lang)

        response = super().listing_view(request, *args, **kwargs)

        site = Site.find_for_request(request)
        root_page = site.root_page if site else None

        def get_translated_url(page):
            return page.url  

        def build_menu_tree(page):
            translated = page.get_translation_or_none(current_locale) or page
            children = page.get_children().live().in_menu()
            return {
                'title': translated.title,
                'url': get_translated_url(translated),
                'children': [
                    {
                        'title': child.get_translation_or_none(current_locale).title if child.get_translation_or_none(current_locale) else child.title,
                        'url': get_translated_url(child),
                        'children': []
                    }
                    for child in children
                ]
            }

        menu_items = []
        if root_page:
            root_item = {
                'title': root_page.get_translation_or_none(current_locale).title if root_page.get_translation_or_none(current_locale) else 'Inicio',
                'url': root_page.get_translation_or_none(current_locale).url if root_page.get_translation_or_none(current_locale) else '/',
                'children': []
            }
            for page in root_page.get_children().live().in_menu():
                root_item['children'].append(build_menu_tree(page))
            menu_items.append(root_item)

        locales = Locale.objects.all()
        available_languages = [
        {
            "code": locale.language_code,
            "display_name": locale.get_display_name()
        }
        for locale in locales 
        ]

        branding = SiteBranding.for_request(request)
        response.data.update({
            'navbar': menu_items,
            'logo': branding.logo.file.url if branding and branding.logo else None,
            'favicon': branding.favicon.file.url if branding and branding.favicon else None,
            'current_language': lang,
            'available_languages': available_languages
        })
        return response


class FooterAPIViewSet(PagesAPIViewSet):
    def listing_view(self, request, *args, **kwargs):
        locale_param = request.GET.get('locale')
        if locale_param and Locale.objects.filter(language_code=locale_param).exists():
            current_language = locale_param
        else:
            current_language = get_language()

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
            'logo': branding.logo.file.url if branding and branding.logo else None,
            'favicon': branding.favicon.file.url if branding and branding.favicon else None,
            'current_language': current_language
        })



class LocalesAPIViewSet(BaseAPIViewSet):
    model = Locale

    def listing_view(self, request, *args, **kwargs):
        locales = Locale.objects.all()
        data = [
            {
                "code": locale.language_code,
                "display_name": locale.get_display_name()
            }
            for locale in locales
        ]
        return Response(data)
