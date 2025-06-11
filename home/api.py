from wagtail.api.v2.views import PagesAPIViewSet, BaseAPIViewSet
from wagtail.models import Site, Page, Locale
from rest_framework.response import Response
from home.models import SiteBranding 
from django.utils.translation import get_language, activate, get_language_from_request
from django.shortcuts import redirect
from home.models import NoticiaPage, CategoriaNoticia, NoticiaPageTag
from taggit.models import Tag

#api entera y nabvar
class CustomPagesAPIViewSet(PagesAPIViewSet):
    def get_locale_language(self, request):
        supported_languages = set(Locale.objects.values_list('language_code', flat=True))

        # 1. Revisar parámetro locale en la query string
        locale_param = request.GET.get('locale')
        if locale_param in supported_languages:
            return locale_param

        # 2. Intentar extraer el idioma desde la URL
        path_parts = request.path.strip("/").split("/")
        lang_from_url = next((part for part in path_parts if part in supported_languages), None)
        if lang_from_url:
            return lang_from_url

        # 3. Obtener idioma desde headers del request
        lang_from_request = get_language_from_request(request)
        if lang_from_request in supported_languages:
            return lang_from_request

        # 4. Por defecto, idioma configurado en Locale
        return Locale.get_default().language_code

    def detail_view(self, request, pk, *args, **kwargs):
        supported_languages = set(Locale.objects.values_list('language_code', flat=True))
        locale_param = request.GET.get('locale')

        try:
            page = Page.objects.live().get(id=pk)
            activate(page.locale.language_code)
        except Page.DoesNotExist:
            return Response({"error": f"La página con ID {pk} no existe."}, status=404)

        # Si el locale solicitado es distinto al de la página, intentar redirigir a traducción
        if locale_param in supported_languages and locale_param != page.locale.language_code:
            try:
                target_locale = Locale.objects.get(language_code=locale_param)
                translated_page = page.get_translation(target_locale)
            except Locale.DoesNotExist:
                return Response({"error": f"Locale '{locale_param}' no encontrado."}, status=404)
            except Exception as e:
                return Response({"error": f"Error al obtener la traducción: {e}"}, status=500)

            if translated_page:
                return redirect(request.build_absolute_uri(translated_page.get_url(request)))
            else:
                return Response({"error": "No se encontró traducción para esta página."})

        # Si no, se muestra la vista original
        return super().detail_view(request, pk, *args, **kwargs)

    def listing_view(self, request, *args, **kwargs):
        supported_languages = set(Locale.objects.values_list('language_code', flat=True))
        lang = self.get_locale_language(request)
        locale_param = request.GET.get('locale')

        # Si el locale en query es diferente del calculado, eliminarlo y redirigir
        if locale_param in supported_languages and locale_param != lang:
            query_dict = request.GET.copy()
            query_dict.pop('locale')
            base_url = request.build_absolute_uri(request.path)
            query_string = f"?{'&'.join(f'{k}={v}' for k, v in query_dict.items())}" if query_dict else ""
            return redirect(f"{base_url}{query_string}")

        activate(lang)
        current_locale = Locale.objects.get(language_code=lang)

        page_type = request.GET.get("type")

        # Filtrado especial para NoticiaPage
        if page_type == "home.NoticiaPage":
            categoria_slug = request.GET.get("categoria")
            tag_slug = request.GET.get("tag")

            noticias_queryset = NoticiaPage.objects.live().filter(locale=current_locale)

            if categoria_slug:
                noticias_queryset = noticias_queryset.filter(categoria__slug=categoria_slug)

            if tag_slug:
                noticias_queryset = noticias_queryset.filter(tags__slug=tag_slug)

            paginated_queryset = self.paginate_queryset(noticias_queryset)
            serializer = self.get_serializer_class()(paginated_queryset, many=True, context=self.get_serializer_context())

            categorias = CategoriaNoticia.objects.all()
            categorias_data = [{"slug": c.slug, "nombre": c.nombre} for c in categorias]

            tag_ids = NoticiaPageTag.objects.filter(
                content_object_id__in=noticias_queryset.values_list("id", flat=True)
            ).values_list("tag_id", flat=True)
            tags = Tag.objects.filter(id__in=tag_ids).distinct()
            tags_data = [{"slug": t.slug, "name": t.name} for t in tags]

            return self.get_paginated_response({
                "items": serializer.data,
                "categorias": categorias_data,
                "tags": tags_data,
                "current_categoria": categoria_slug,
                "current_tag": tag_slug,
            })

        # Si no es NoticiaPage, construimos el menú principal
        site = Site.find_for_request(request)
        root_page = site.root_page if site else None

        def build_menu_tree(page):
            translated = page.get_translation_or_none(current_locale) or page
            children = page.get_children().live().in_menu()
            return {
                'title': translated.title,
                'url': translated.url,
                'children': [
                    {
                        'title': child.get_translation_or_none(current_locale).title if child.get_translation_or_none(current_locale) else child.title,
                        'url': child.get_translation_or_none(current_locale).url if child.get_translation_or_none(current_locale) else child.url,
                        'children': []
                    }
                    for child in children
                ]
            }

        menu_items = []
        if root_page:
            root_translated = root_page.get_translation_or_none(current_locale)
            root_item = {
                'title': root_translated.title if root_translated else 'Inicio',
                'url': root_translated.url if root_translated else '/',
                'children': [build_menu_tree(page) for page in root_page.get_children().live().in_menu()]
            }
            menu_items.append(root_item)

        available_languages = [
            {"code": locale.language_code, "display_name": locale.get_display_name()}
            for locale in Locale.objects.all()
        ]

        branding = SiteBranding.for_request(request)
        
        # Obtener la respuesta base (heredada)
        response = super().listing_view(request, *args, **kwargs)
        
        # Agregar datos extra
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
            if page.url.startswith(f'/{current_language}/') or page.url == f'/{current_language}':
                return page.url
            elif page.url == '/':
                return f'/{current_language}/'
            else:
                return f'/{current_language}{page.url}'

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

