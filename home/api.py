from wagtail.api.v2.views import PagesAPIViewSet, BaseAPIViewSet
from wagtail.models import Site, Page, Locale
from rest_framework.response import Response
from home.models import SiteBranding, NoticiaPage, CategoriaNoticia, NoticiaPageTag,EventoPage, CategoriaEvento, EventoPageTag
from taggit.models import Tag
from django.utils.translation import activate, get_language_from_request
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage

def get_supported_languages():
    return set(Locale.objects.values_list('language_code', flat=True))


def get_current_locale(lang_code):
    return Locale.objects.get(language_code=lang_code)


def build_menu_tree(page, current_locale):
    translated = page.get_translation_or_none(current_locale) or page
    return {
        'title': translated.title,
        'url': translated.url,
        'children': [
            {
                'title': (child.get_translation_or_none(current_locale) or child).title,
                'url': (child.get_translation_or_none(current_locale) or child).url,
                'children': []
            }
            for child in page.get_children().live().in_menu()
        ]
    }


class CustomPagesAPIViewSet(PagesAPIViewSet):
    def get_locale_language(self, request):
        supported = get_supported_languages()
        locale_param = request.GET.get('locale')

        if locale_param in supported:
            return locale_param

        lang_from_url = next((part for part in request.path.strip("/").split("/") if part in supported), None)
        if lang_from_url:
            return lang_from_url

        lang_from_request = get_language_from_request(request)
        return lang_from_request if lang_from_request in supported else Locale.get_default().language_code

    def detail_view(self, request, pk, *args, **kwargs):
        try:
            page = Page.objects.live().get(id=pk)
            activate(page.locale.language_code)
        except Page.DoesNotExist:
            return Response({"error": f"La página con ID {pk} no existe."}, status=404)

        locale_param = request.GET.get('locale')
        if locale_param and locale_param != page.locale.language_code:
            try:
                target_locale = get_current_locale(locale_param)
                translated_page = page.get_translation(target_locale)
                if translated_page:
                    return redirect(request.build_absolute_uri(translated_page.get_url(request)))
                return Response({"error": "No se encontró traducción para esta página."})
            except Locale.DoesNotExist:
                return Response({"error": f"Locale '{locale_param}' no encontrado."}, status=404)
            except Exception as e:
                return Response({"error": f"Error al obtener la traducción: {e}"}, status=500)

        return super().detail_view(request, pk, *args, **kwargs)

    def listing_view(self, request, *args, **kwargs):
        lang = self.get_locale_language(request)
        activate(lang)
        current_locale = get_current_locale(lang)
        page_type = request.GET.get("type")

        if page_type == "home.NoticiasIndexPage":
            categoria_slug = request.GET.get("categoria")
            tag_slug = request.GET.get("tag")
            noticias = NoticiaPage.objects.live().filter(locale=current_locale)

            if categoria_slug:
                noticias = noticias.filter(categoria__slug=categoria_slug)
            if tag_slug:
                noticias = noticias.filter(tags__slug=tag_slug)

            paginated = self.paginate_queryset(noticias)
            serialized = self.get_serializer_class()(paginated, many=True, context=self.get_serializer_context())

            categorias_data = [{"slug": c.slug, "nombre": c.nombre} for c in CategoriaNoticia.objects.all()]
            tag_ids = NoticiaPageTag.objects.filter(content_object_id__in=noticias.values_list("id", flat=True)).values_list("tag_id", flat=True)
            tags_data = [{"slug": t.slug, "name": t.name} for t in Tag.objects.filter(id__in=tag_ids).distinct()]

            response = self.get_paginated_response(serialized.data)
            response.data.update({
                'categorias': categorias_data,
                'tags': tags_data,
                'current_categoria': categoria_slug,
                'current_tag': tag_slug
            })
            return response

        
        site = Site.find_for_request(request)
        root = site.root_page if site else None
        menu_items = []

        if root:
            translated_root = root.get_translation_or_none(current_locale)
            menu_items.append({
                'title': translated_root.title if translated_root else 'Inicio',
                'url': translated_root.url if translated_root else '/',
                'children': [build_menu_tree(child, current_locale) for child in root.get_children().live().in_menu()]
            })

        response = super().listing_view(request, *args, **kwargs)
        return response


class LocalesAPIViewSet(BaseAPIViewSet):
    model = Locale

    def listing_view(self, request, *args, **kwargs):
        return Response([
            {"code": locale.language_code, "display_name": locale.get_display_name()}
            for locale in Locale.objects.all()
        ])

class NavbarAPIViewSet(PagesAPIViewSet):
    model = Page
    def listing_view(self, request, *args, **kwargs):
        lang = CustomPagesAPIViewSet().get_locale_language(request)
        activate(lang)
        current_locale = get_current_locale(lang)
        site = Site.find_for_request(request)
        root = site.root_page if site else None
        menu_items = []

        if root:
            translated_root = root.get_translation_or_none(current_locale)
            menu_items.append({
                'title': translated_root.title if translated_root else 'Inicio',
                'url': translated_root.url if translated_root else '/',
                'children': [build_menu_tree(child, current_locale) for child in root.get_children().live().in_menu()]
            })

        branding = SiteBranding.for_request(request)

        return Response({
            'navbar': menu_items,
            'logo': branding.logo.file.url if branding and branding.logo else None,
            'favicon': branding.favicon.file.url if branding and branding.favicon else None,
            'current_language': lang
        })
class FooterAPIViewSet(PagesAPIViewSet):
    model = Page

    def listing_view(self, request, *args, **kwargs):
        lang = request.GET.get('locale') or Locale.get_default().language_code
        activate(lang)
        current_locale = get_current_locale(lang)
        site = Site.find_for_request(request)
        root = site.root_page if site else None
        footer_items = []

        if root:
            translated_root = root.get_translation_or_none(current_locale) or root
            footer_items.append({'id': translated_root.id, 'title': translated_root.title, 'url': translated_root.url})

            for child in root.get_children().live().in_menu():
                translated_child = child.get_translation_or_none(current_locale) or child
                footer_items.append({
                    'id': translated_child.id,
                    'title': translated_child.title,
                    'url': translated_child.url
                })

        branding = SiteBranding.for_request(request)

        return Response({
            'items': footer_items,
            'logo': branding.logo.file.url if branding and branding.logo else None,
            'favicon': branding.favicon.file.url if branding and branding.favicon else None,
            'current_language': lang
        })


class NoticiasAPIViewSet(PagesAPIViewSet):
    model = NoticiaPage

    def listing_view(self, request, *args, **kwargs):
        lang = CustomPagesAPIViewSet().get_locale_language(request)
        activate(lang)
        current_locale = get_current_locale(lang)

        categoria_slug = request.GET.get("categoria")
        tag_slug = request.GET.get("tag")

        noticias = NoticiaPage.objects.live().filter(locale=current_locale)

        if categoria_slug and tag_slug:
            noticias = noticias.filter(
                categoria__slug=categoria_slug,
                tags__slug=tag_slug
            ).distinct()
        elif categoria_slug:
            noticias = noticias.filter(categoria__slug=categoria_slug)
        elif tag_slug:
            noticias = noticias.filter(tags__slug=tag_slug)

        page_number = request.GET.get("page", 1)
        paginator = Paginator(noticias, 6)

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        noticias_data = [{
            'id': n.id,
            'title': n.title,
            'url': n.url,
            'categoria': n.categoria.nombre if n.categoria else None,
            'tags': [tag.name for tag in n.tags.all()],
            'date': n.first_published_at,
        } for n in page_obj]

        categorias_data = [{"slug": c.slug, "nombre": c.nombre} for c in CategoriaNoticia.objects.all()]
        tag_ids = NoticiaPageTag.objects.filter(
            content_object_id__in=noticias.values_list("id", flat=True)
        ).values_list("tag_id", flat=True)
        tags_data = [{"slug": t.slug, "name": t.name} for t in Tag.objects.filter(id__in=tag_ids).distinct()]

        return Response({
            "noticias": noticias_data,
            "categorias": categorias_data,
            "tags": tags_data,
            "current_categoria": categoria_slug,
            "current_tag": tag_slug,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "total_items": paginator.count,
            }
        })


class EventosAPIViewSet(PagesAPIViewSet):
    model = EventoPage

    def listing_view(self, request, *args, **kwargs):
        lang = CustomPagesAPIViewSet().get_locale_language(request)
        activate(lang)
        current_locale = get_current_locale(lang)

        categoria_slug = request.GET.get("categoria")
        tag_slug = request.GET.get("tag")

        eventos = EventoPage.objects.live().filter(locale=current_locale)

        if categoria_slug and tag_slug:
            eventos = eventos.filter(
                categoria__slug=categoria_slug,
                tags__slug=tag_slug
            ).distinct()
        elif categoria_slug:
            eventos = eventos.filter(categoria__slug=categoria_slug)
        elif tag_slug:
            eventos = eventos.filter(tags__slug=tag_slug)

        page_number = request.GET.get("page", 1)
        paginator = Paginator(eventos, 6)

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        eventos_data = [{
            'id': e.id,
            'title': e.title,
            'url': e.url,
            'categoria': e.categoria.nombre if e.categoria else None,
            'tags': [tag.name for tag in e.tags.all()],
            'date': e.first_published_at,
        } for e in page_obj]

        categorias_data = [{"slug": c.slug, "nombre": c.nombre} for c in CategoriaEvento.objects.all()]
        tag_ids = EventoPageTag.objects.filter(
            content_object_id__in=eventos.values_list("id", flat=True)
        ).values_list("tag_id", flat=True)
        tags_data = [{"slug": t.slug, "name": t.name} for t in Tag.objects.filter(id__in=tag_ids).distinct()]

        return Response({
            "eventos": eventos_data,
            "categorias": categorias_data,
            "tags": tags_data,
            "current_categoria": categoria_slug,
            "current_tag": tag_slug,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "total_items": paginator.count,
            }
        })
