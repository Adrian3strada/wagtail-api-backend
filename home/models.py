import datetime
from datetime import date
from django import forms
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.rich_text import RichText
from wagtail.blocks import ChoiceBlock, ListBlock, RichTextBlock, StructBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail.snippets.models import register_snippet
from wagtail_localize.models import TranslatableMixin
from ckeditor.widgets import CKEditorWidget
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from taggit.models import Tag



@register_snippet
class NavItem(models.Model):
    title = models.CharField(max_length=255)
    page = models.ForeignKey(Page, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.IntegerField(default=0)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

@register_setting
class SiteBranding(BaseSiteSetting):
    logo = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    favicon = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    panels = [
        FieldPanel("logo"),
        FieldPanel("favicon"),
    ]

@register_snippet
class FooterLink(models.Model):
    titulo = models.CharField(max_length=255)
    url = models.URLField("Enlace", blank=True, null=True)

    panels = [
        FieldPanel("titulo"),
        FieldPanel("url"),
    ]

    api_fields = [
        APIField("titulo"),
        APIField("url"),
    ]

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Elemento del Footer"
        verbose_name_plural = "Footer"


@register_snippet
class CategoriaEvento(models.Model):
    nombre = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    panels = [
        FieldPanel('nombre'),
        FieldPanel('slug'),
    ]

    def __str__(self):
        return self.nombre

@register_snippet
class CategoriaNoticia(models.Model):
    nombre = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    panels = [
        FieldPanel("nombre"),
        FieldPanel("slug"),
    ]

    def __str__(self):
        return self.nombre

#etiquetas
class NoticiaPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'NoticiaPage',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )

class EventoPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'home.EventoPage',  
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )


# apis para imagen

class CustomImageBlock(ImageChooserBlock):
    def get_api_representation(self, value, context=None):
        if not value:
            return None
        return {
            "id": value.id,
            "title": value.title,
            "url": value.file.url,

        }

class CustomPage(Page):
    show_in_footer = models.BooleanField(default=False)  


    menu_children = APIField('menu_children')
    show_in_footer_api = APIField('show_in_footer')  

    def get_menu_children(self):
        return [
            {
                'title': child.title,
                'url': child.url,
            }
            for child in self.get_children().live().in_menu()
        ]

    @property
    def menu_children(self):
        return self.get_menu_children()

    content_panels = Page.content_panels  

    promote_panels = Page.promote_panels + [ 
        FieldPanel('show_in_footer'),
    ]
#quasar 

QUASAR_COLOR_CHOICES = [
    ('primary', 'Primary'),
    ('secondary', 'Secondary'),
    ('accent', 'Accent'),
    ('dark', 'Dark'),
    ('positive', 'Positive'),
    ('negative', 'Negative'),
    ('info', 'Info'),
    ('warning', 'Warning'),
]




#bloques

class ButtonBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, help_text="Texto del botón")
    url = blocks.URLBlock(required=True, help_text="Enlace del botón")
    style = blocks.ChoiceBlock(
        choices=[
            ('primary', 'Primary'),
            ('secondary', 'Secondary'),
            ('success', 'Success'),
            ('danger', 'Danger'),
            ('warning', 'Warning'),
        ],
        default='primary',
        required=False,
        help_text="Estilo del botón"
    )

    class Meta:
        template = 'blocks/button_block.html'
        icon = 'placeholder'
        label = 'Botón'

class CardBlock(blocks.StructBlock):
    imagen = CustomImageBlock(required=False, label="Imagen")
    titulo = blocks.CharBlock(required=True, label="Título")
    descripcion = blocks.TextBlock(required=False, label="Descripción")
    enlace = blocks.URLBlock(required=False, label="Enlace")

    class Meta:
        icon = "placeholder"
        label = "Tarjeta"
        template = "blocks/card_block.html"

    def get_api_representation(self, value, context=None):
        imagen = value.get("imagen")
        return {
            "titulo": value["titulo"],
            "descripcion": value["descripcion"],
            "enlace": value.get("enlace"),
            "imagen": {
                 "url": imagen.get_rendition("fill-800x450-c100").url if imagen else None,
                "title": imagen.title if imagen else None
            } if imagen else None
        }




class CardsBlock(blocks.StructBlock):
    tarjetas = blocks.ListBlock(CardBlock(), label="tarjeta de noticias")

    class Meta:
        icon = "placeholder"
        label = "Grupo de tarjetas"
        template = "blocks/cards_block.html"


class CardEDBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True, label="Título")
    descripcion = blocks.TextBlock(required=False, label="Descripción")
    textos_adicionales = blocks.ListBlock(blocks.RichTextBlock(), required=False, label="Textos adicionales")
    enlace = ButtonBlock(required=False, label="Botón de enlace")

    class Meta:
        icon = "placeholder"
        label = "Tarjeta ED"
        template = "blocks/cardED_block.html"

    def get_api_representation(self, value, context=None):
        return {
            "titulo": value["titulo"],
            "descripcion": value["descripcion"],
            "textos_adicionales": [
                str(texto) for texto in value.get("textos_adicionales", [])
            ],
            "enlace": value.get("enlace"),
        }

        
class CardsEDBlock(blocks.StructBlock):
    tarjetas = blocks.ListBlock(CardEDBlock(), label="tarjetas ED")

    class Meta:
        icon = "placeholder"
        label = "Grupo de tarjetas ED"
        template = "blocks/cardsED_block.html"

class TestimonioBlock(blocks.StructBlock):
    nombre = blocks.CharBlock(required=True, label="Nombre")
    organizacion = blocks.CharBlock(required=False, label="Organización")
    comentario = blocks.TextBlock(required=True, label="Comentario")
    imagen = CustomImageBlock(required=False, label="Imagen principal")
    fondo = CustomImageBlock(required=False, label="Imagen de fondo")

    class Meta:
        icon = "user"
        label = "Testimonio"

    def get_api_representation(self, value, context=None):
        imagen = value.get("imagen")
        fondo = value.get("fondo")
        return {
            "nombre": value["nombre"],
            "comentario": value["comentario"],
            "organizacion": value["organizacion"],
            "imagen": {
                "url": imagen.get_rendition("original").url if imagen else None,
                "title": imagen.title if imagen else None
            } if imagen else None,
            "fondo": {
                "url": fondo.get_rendition("fill-1600x600-c100").url if fondo else None,
                "title": fondo.title if fondo else None
            } if fondo else None
        }


class TestimoniosBlock(blocks.StructBlock):
    testimonios = blocks.ListBlock(TestimonioBlock(), label="Lista de testimonios")

    class Meta:
        template = "blocks/testimonios_carrusel.html"  
        icon = "group"
        label = "Testimonios Carrusel"

class PactoVerdeBlock(blocks.StructBlock):
    imagen = CustomImageBlock(required=False, label="Imagen")
    titulo = blocks.CharBlock(required=True, label="Título")
    descripcion = blocks.TextBlock(required=False, label="Descripción")

    class Meta:
        icon = "placeholder"
        label = "Pacto-verde"
        template = "blocks/pactoverde_block.html"

    def get_api_representation(self, value, context=None):
        imagen = value.get("imagen")
        return {
            "titulo": value["titulo"],
            "descripcion": value["descripcion"],
            "imagen": {
                 "url": imagen.get_rendition("fill-800x450-c100").url if imagen else None,
                "title": imagen.title if imagen else None
            } if imagen else None
        }




class ModuloCertiffyBlock(blocks.StructBlock):
    tipo_contenido = blocks.ChoiceBlock(
        choices=[
            ('video', 'Video'),
            ('imagen', 'Imagen'),
        ],
        label="Tipo de contenido principal",
        default='video'
    )
    video_url = blocks.URLBlock(
        required=False,
        label="URL del video (YouTube, Vimeo, etc.)"
    )
    video_caption = blocks.CharBlock(
        required=False,
        label="Descripción del video (abajo del reproductor)"
    )
    imagen_principal = ImageChooserBlock(
        required=False,
        label="Imagen principal"
    )
    imagen = ImageChooserBlock(
        required=False,
        label="Imagen banner"
    )
    titulo = blocks.CharBlock(required=True, label="Título")
    descripcion = blocks.TextBlock(required=True, label="Descripción")
    botones = blocks.ListBlock(ButtonBlock(), label="Módulos disponibles")

    def get_api_representation(self, value, context=None):
        contenido_principal = None
        if value.get("tipo_contenido") == "video":
            contenido_principal = {
                "tipo": "video",
                "video_url": value.get("video_url"),
                "video_caption": value.get("video_caption")
            }
        elif value.get("tipo_contenido") == "imagen" and value.get("imagen_principal"):
            contenido_principal = {
                "tipo": "imagen",
                "imagen_url": value["imagen_principal"].get_rendition("original").url,
                "imagen_title": value["imagen_principal"].title,
            }

        return {
            "contenido_principal": contenido_principal,
            "imagen": {
                "url": value["imagen"].get_rendition("original").url,
                "title": value["imagen"].title,
            } if value.get("imagen") else None,
            "titulo": value.get("titulo"),
            "descripcion": value.get("descripcion"),
            "botones": [
                {
                    "text": b["text"],
                    "url": b["url"],
                    "style": b.get("style", "primary")
                } for b in value["botones"]
            ]
        }

    class Meta:
        icon = "media"
        label = "Bloque Módulo CERTIFFY"
        template = "blocks/modulo_certiffy_block.html"


class CarouselImageBlock(blocks.StructBlock):
    image = CustomImageBlock(required=True, label="Imagen")
    caption = blocks.CharBlock(required=False, label="Texto opcional", max_length=250)

    class Meta:
        icon = "image"
        label = "Imagen del Carrusel"
    
    def get_api_representation(self, value, context=None):
        return {
            "caption": value.get("caption"),
            "image": {
                "url": value["image"].get_rendition("original").url,
                "title": value["image"].title
            }   
        }

class CarouselBlock(blocks.StructBlock):
    images = blocks.ListBlock(CarouselImageBlock(), label="Imágenes")
    
 
    teaser_video_url = blocks.URLBlock(
        required=False, label="Video de muestra (URL de YouTube o Vimeo)"
    )
    

    main_video_url = blocks.URLBlock(
        required=False, label="Video principal (URL de YouTube o Vimeo)"
    )
    
    mostrar_video = blocks.BooleanBlock(
        required=False, default=True, label="Mostrar video"
    )

    class Meta:
        icon = "image"
        label = "Carrusel con video"
        template = "blocks/carrusel_block.html"

    def get_api_representation(self, value, context=None):
        return {
            "images": [
                CarouselImageBlock().get_api_representation(img, context)
                for img in value.get("images", [])
            ],
            "teaser_video_url": value.get("teaser_video_url"),
            "main_video_url": value.get("main_video_url"),
            "mostrar_video": value.get("mostrar_video"),
        }


class HoverImageBlock(blocks.StructBlock):
    image = CustomImageBlock(required=True, label="Imagen")
    texto_overlay = blocks.CharBlock(required=False, label="Texto sobre la imagen")
    color_overlay = blocks.ChoiceBlock(
        choices=QUASAR_COLOR_CHOICES,
        label="Color del overlay (Quasar)",
        required=False,
        help_text="Color que se verá al pasar el mouse"
    )

    class Meta:
        template = "blocks/hover_image_block.html"
        icon = "image"
        label = "Imagen con Hover"

    def get_api_representation(self, value, context=None):
        return {
            "texto_overlay": value["texto_overlay"],
            "color_overlay": value["color_overlay"],
            "image": {
                "url": value["image"].get_rendition("original").url,
                "title": value["image"].title
            }
        }


class MisionBlock(blocks.StructBlock):
    imagen_hover = HoverImageBlock(required=True, label="Imagen con overlay")

    class Meta:
        template = "blocks/mision_block.html"
        icon = "doc-full"
        label = "Bloque Misión"

    def get_api_representation(self, value, context=None):
        return {
            "imagen_hover": self.child_blocks["imagen_hover"].get_api_representation(
                value["imagen_hover"], context=context
            )
        }

class PlataformBlock(blocks.StructBlock):
    imagen = ImageChooserBlock(required=True, label="Imagen")
    titulo = blocks.CharBlock(required=True, label="Titular")
    descripcion = blocks.TextBlock(required=True, label="Texto largo")
    botones = blocks.ListBlock(ButtonBlock(), required=False, label="Botones")

    class Meta:
        template = "blocks/PlataformBlock.html"
        icon = "image"
        label = "Contenido con Imagen"

    def get_api_representation(self, value, context=None):
        imagen = value.get('imagen')
        return {
            "imagen": {
                "id": imagen.id,
                "url": imagen.get_rendition("original").url,
                "title": imagen.title,
            } if imagen else None,
            "titulo": value.get('titulo', ''),
            "descripcion": value.get('descripcion', ''),
            "botones": [
                {
                    "texto": boton.get('texto', ''),
                    "url": boton.get('url', ''),
                }
                for boton in value.get('botones', [])
            ],
        }
    
class ParrafoConAlineacionBlock(blocks.StructBlock):
    alineacion = blocks.ChoiceBlock(
        choices=[
            ('left', 'Izquierda'),
            ('center', 'Centrado'),
            ('right', 'Derecha'),
            ('justify', 'Justificado'), 
        ],
        default='left',
        label='Alineación del texto'
    )
    texto = blocks.RichTextBlock(label="Texto enriquecido")

    def get_api_representation(self, value, context=None, **kwargs):
        return {
            'alineacion': value['alineacion'],
            'texto': value['texto'].source,  
        }

    class Meta:
        icon = 'doc-full'
        label = 'Párrafo con alineación'

class ImagenConTextoBlock(blocks.StructBlock):
    titulo = RichTextBlock(required=False)
    texto = ParrafoConAlineacionBlock()  
    posicion_imagen = ChoiceBlock(choices=[
        ('fondo', 'Fondo'),
        ('izquierda', 'Izquierda'),
        ('derecha', 'Derecha'),
        ('abajo', 'Abajo'),
        ('galeria', 'Galería'),
    ])
    imagen = ImageChooserBlock(required=False)
    galeria = ListBlock(ImageChooserBlock(), required=False)

    def get_api_representation(self, value, context=None):
        imagen = value.get("imagen")
        galeria = value.get("galeria", [])
        texto_struct = value.get("texto")
        alineacion = texto_struct.get("alineacion")
        texto_html = str(texto_struct.get("texto"))

        return {
            "titulo": str(value.get("titulo")) if value.get("titulo") else "",
            "texto": texto_html,
            "alineacion_texto": alineacion,
            "posicion_imagen": value.get("posicion_imagen"),
            "imagen": {
                "id": imagen.id,
                "url": imagen.get_rendition("original").url,
                "title": imagen.title
            } if imagen else None,
            "galeria": [
                {
                    "id": img.id,
                    "url": img.get_rendition("original").url,
                    "title": img.title
                } for img in galeria if img is not None
            ]
        }

    class Meta:
        icon = 'image'
        label = 'Bloque de Imagen y Texto'
        template = 'blocks/texto_imagen_block.html'

class GalleryImageBlock(blocks.StructBlock):
    image = CustomImageBlock(required=True, label="Imagen")
    caption = blocks.CharBlock(required=False, label="Texto opcional", max_length=250)

    class Meta:
        icon = "image"
        label = "Imagen de galería"

    def get_api_representation(self, value, context=None):
        return {
            "caption": value.get("caption"),
            "image": {
                "url": value["image"].get_rendition("original").url,
                "title": value["image"].title
            }
        }


class GalleryBlock(blocks.StructBlock):
    images = blocks.ListBlock(GalleryImageBlock(), label="Imágenes")

    class Meta:
        icon = "image"
        label = "Galería de imágenes"
        template = "blocks/gallery_block.html"



class VideoBlock(blocks.StructBlock):
    video_url = blocks.URLBlock(label="URL del video (YouTube o Vimeo)")

    class Meta:
        icon = "media"
        label = "Video embebido"
        template = "blocks/video_block.html"




class DocumentBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True, label="Título del documento")
    documento = DocumentChooserBlock(required=True, label="Documento")

    class Meta:
        template = "blocks/documento_block.html"
        icon = "doc-full"
        label = "Documento"

    def get_api_representation(self, value, context=None):
  
        documento = value.get('documento')
        return {
            "titulo": value.get("titulo"),
            "documento": {
                "id": documento.id,
                "title": documento.title,
                "url": documento.url,
                "filename": documento.filename,
                "file_size": documento.file.size,
                "file_extension": documento.file_extension,
            } if documento else None,
        }


class IframeBlock(blocks.StructBlock):
    iframe_url = blocks.URLBlock(label="URL del contenido embebido")
    height = blocks.IntegerBlock(default=400, label="Altura (px)")

    class Meta:
        icon = "code"
        label = "Contenido embebido (iframe)"
        template = "blocks/iframe_block.html"


class LogoConURLBlock(blocks.StructBlock):
    logo = ImageChooserBlock(required=True, label="Logo")
    url = blocks.URLBlock(required=False, label="Enlace (opcional)")

    def get_api_representation(self, value, context=None):
        return {
            
            'url': value.get('url', ''),
            'logo_url': value['logo'].file.url if value.get('logo') else None,
        }

    class Meta:
        icon = "image"
        label = "Logo con URL"
        template = "blocks/logo_con_url.html"

class DocumentoItemBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True, label="Título del documento")
    archivo = DocumentChooserBlock(required=True, label="Archivo")

    class Meta:
        icon = "doc-full"
        label = "Documento"

class TextoYDocumentosBlock(blocks.StructBlock):
    texto = blocks.RichTextBlock(label="Texto explicativo")
    documentos = blocks.ListBlock(DocumentoItemBlock(), label="Lista de documentos")

    class Meta:
        icon = "folder-open-inverse"
        label = "Texto con múltiples documentos"

class ListaDeLogosBlock(blocks.StructBlock):
    titulo = blocks.CharBlock(required=True, label="Título general")
    logos = blocks.ListBlock(LogoConURLBlock(), label="Logos")

    def get_api_representation(self, value, context=None):
        return {
            'titulo': value['titulo'],
            'logos': [
                {
                    'imagen': {
                        'id': logo['logo'].id,
                        'url': logo['logo'].get_rendition("original").url,
                        'title': logo['logo'].title,
                    } if logo.get('logo') else None,
                    'url': logo.get('url')
                }
                for logo in value.get('logos', []) if logo.get('logo') is not None
            ]
        }

    class Meta:
        icon = "list-ul"
        label = "Lista de Logos"
        template = "blocks/ListaDeLogosBlock.html"

class CKEditorBlock(blocks.FieldBlock):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.field = forms.CharField(widget=CKEditorWidget(config_name='default'))

    class Meta:
        icon = "doc-full"
        label = "Texto Avanzado"





class TarjetaSimpleFondoBlock(blocks.StructBlock):
    imagen = ImageChooserBlock(label="Imagen")
    descripcion = blocks.RichTextBlock(label="Descripción")
    url = blocks.URLBlock(required=False, label="URL (al hacer clic en la tarjeta)")
    categoria = SnippetChooserBlock(required=False, target_model="home.CategoriaNoticia", label="Categoría")

    class Meta:
        icon = "image"
        label = "Tarjeta clicable (imagen + descripción + URL)"
        template = "blocks/tarjeta_simple_fondo.html"



class GrupoDeTarjetasFondoBlock(blocks.StructBlock):
    titulo_apartado = blocks.CharBlock(required=True, label="Título del apartado")
    tarjetas = blocks.ListBlock(TarjetaSimpleFondoBlock(), label="Tarjetas")

    def get_api_representation(self, value, context=None):
        return {
            "tipo": "grupo_de_tarjetas",
            "titulo_apartado": value.get("titulo_apartado"),
            "tarjetas": [
                {
                    "fecha": date.today().strftime("%Y-%m-%d"),  
                    "categoria": item["categoria"].nombre if item.get("categoria") else None,
                    "descripcion": item["descripcion"].source,
                    "imagen": {
                        "url": item["imagen"].get_rendition("fill-800x400-c100").url,
                        "alt": item["imagen"].title
                    } if item.get("imagen") else None,
                    "url": item.get("url")
                } for item in value["tarjetas"]
            ]
        }

    class Meta:
        icon = "list-ul"
        label = "Grupo de Tarjetas clicables"
        template = "blocks/grupo_de_tarjetas_fondo.html"

class CardEventoBlock(blocks.StructBlock):
    fecha = blocks.DateBlock(required=True, label="Fecha del evento")
    categoria = SnippetChooserBlock(target_model='home.CategoriaEvento', label="Categoría")
    titulo = blocks.CharBlock(required=True, label="Título del evento")
    descripcion = blocks.TextBlock(required=False, label="Descripción")
    imagen = ImageChooserBlock(required=True, label="Imagen del evento")
    enlace = blocks.URLBlock(required=False, label="Enlace al evento")

    class Meta:
        icon = "date"
        label = "Tarjeta de Evento"
        template = "blocks/card_evento.html"

    def get_api_representation(self, value, context=None):
        imagen = value.get("imagen")
        categoria = value.get("categoria")

        return {
            "fecha": value["fecha"].strftime('%Y-%m-%d'),
            "categoria": categoria.nombre if categoria else None,
            "titulo": value["titulo"],
            "descripcion": value["descripcion"],
            "enlace": value.get("enlace"),
            "imagen": {
                "url": imagen.get_rendition("fill-800x400-c100").url if imagen else None,
                "title": imagen.title if imagen else None
            } if imagen else None
        }

class EventosGridBlock(blocks.StructBlock):
    eventos = blocks.ListBlock(CardEventoBlock(), label="Lista de eventos")

    class Meta:
        icon = "list-ul"
        label = "Sección de eventos"
        template = "blocks/eventos_grid.html"


class TarjetaNoticiaBlock(blocks.StructBlock):
    tipo = blocks.ChoiceBlock(
        choices=[
            ("noticia", "Noticia"),
            ("evento", "Evento"),
        ],
        required=True,
        label="Tipo de contenido"
    )
    titulo = blocks.CharBlock(required=False, label="Título (si aplica)")
    imagen = ImageChooserBlock(label="Imagen")
    categoria_noticia = SnippetChooserBlock(
        target_model="home.CategoriaNoticia", required=False, label="Categoría (Noticia)"
    )
    categoria_evento = SnippetChooserBlock(
        target_model="home.CategoriaEvento", required=False, label="Categoría (Evento)"
    )
    descripcion = blocks.RichTextBlock(label="Descripción")
    url = blocks.URLBlock(required=False, label="URL (al hacer clic en la tarjeta)")
    fecha = blocks.DateBlock(required=False, label="Fecha de publicación o evento")

    def clean(self, value):
        cleaned = super().clean(value)
        if not cleaned.get("fecha"):
            cleaned["fecha"] = datetime.date.today()
        return cleaned

    class Meta:
        icon = "doc-full"
        label = "Tarjeta (Noticia o Evento)"
        template = "blocks/tarjeta_noticia.html"


class GrupoDeNoticiasBlock(blocks.StructBlock):
    titulo_apartado = blocks.CharBlock(required=True, label="Título del apartado de noticias") 
    noticias = blocks.ListBlock(TarjetaNoticiaBlock(), label="Lista de noticias")

    def get_api_representation(self, value, context=None):
        noticias_list = []
        for item in value.get("noticias", []):
            tipo = item.get("tipo")

            if tipo == "noticia":
                categoria_obj = item.get("categoria_noticia")
            elif tipo == "evento":
                categoria_obj = item.get("categoria_evento")
            else:
                categoria_obj = None

            # Obtener nombre de la categoría si existe
            if categoria_obj and hasattr(categoria_obj, 'nombre'):
                categoria_nombre = categoria_obj.nombre
            else:
                categoria_nombre = None

            noticias_list.append({
                "fecha": item.get("fecha").strftime("%Y-%m-%d") if item.get("fecha") else None,
                "categoria": categoria_nombre,
                "descripcion": item["descripcion"].source if hasattr(item["descripcion"], 'source') else item["descripcion"],
                "url": item.get("url"),
                "imagen": {
                    "url": item["imagen"].get_rendition("fill-800x400-c100").url,
                    "title": item["imagen"].title
                } if item.get("imagen") else None,
                "tipo": tipo,
                "titulo": item.get("titulo"),
            })

        return {
            "tipo": "grupo_de_noticias",
            "titulo_apartado": value.get("titulo_apartado"),
            "noticias": noticias_list
        }

    class Meta:
        icon = "list-ul"
        label = "Sección de Noticias"
        template = "blocks/grupo_de_noticias.html"

class ModuloBlock(blocks.StructBlock):
    imagen = ImageChooserBlock(required=True, label="Imagen del módulo")
    titulo = blocks.CharBlock(required=True, label="Título del botón")
    enlace = blocks.URLBlock(required=False, label="URL del botón (opcional)")

    def get_api_representation(self, value, context=None):
        imagen = value.get('imagen')
        return {
            "imagen": {
                "id": imagen.id,
                "url": imagen.get_rendition("original").url,
                "title": imagen.title,
            } if imagen else None,
            "titulo": value.get('titulo', ''),
            "enlace": value.get('enlace', ''),
        }

    class Meta:
        icon = "placeholder"
        label = "Módulo individual"



class ModulosCertiffyBlockNuevo(blocks.StructBlock):
    titulo_seccion = blocks.CharBlock(required=True, label="Título de la sección")
    texto_principal = blocks.RichTextBlock(required=True, label="Texto introductorio")
    video_url = blocks.URLBlock(required=False, label="URL del video introductorio (opcional)")
    modulos = blocks.ListBlock(ModuloBlock, label="Módulos")

    def get_api_representation(self, value, context=None):
        return {
            "titulo_seccion": value.get("titulo_seccion", ""),
            "texto_principal": str(value.get("texto_principal", "")),
            "video_url": value.get("video_url", ""),
            "modulos": [
                self.child_blocks['modulos'].child_block.get_api_representation(modulo, context)
                for modulo in value.get("modulos", [])
            ],
        }

    class Meta:
        icon = "folder-open-inverse"
        label = "Bloque de módulos Certiffy"
        template = "blocks/modulos_certiffy.html"






# bloques reutilizables

common_streamfield = [
    ('heading', blocks.CharBlock(classname="full title", label="Encabezado")),
    ('paragraph', blocks.RichTextBlock(label="Párrafo enriquecido")),
    ('plain_text', blocks.TextBlock(label="Texto simple")),
    ('image', CustomImageBlock(label="Imagen")),
    ('gallery', GalleryBlock()),
    ('carousel', CarouselBlock()),
    ('button', ButtonBlock()),
    ('video', VideoBlock()),
    ('iframe', IframeBlock()),
    ('hover_image', HoverImageBlock()),
    ('testimonios', TestimoniosBlock()),
    ('cards', CardsBlock()),
    ('modulo_certiffy', ModuloCertiffyBlock()),
    ('mision', MisionBlock()),
    ('pacto_verde', PactoVerdeBlock()),
    ('cardED', CardEDBlock()),
    ('cardsED', CardsEDBlock()),
    ('PlataForm', PlataformBlock()),
    ('Document', DocumentBlock()),
    ('Socios', ListaDeLogosBlock()),
    ('ImagenTexto', ImagenConTextoBlock()),
    ('parrafo_con_estilo', CKEditorBlock()),
    ('ducumentocontexto', DocumentoItemBlock()),
    ('texto_y_documentos', TextoYDocumentosBlock()),
    ('texto_y_documentos_block', TextoYDocumentosBlock()),
    ('logo_con_url', LogoConURLBlock()),
    ('tarjeta_simple_fondo', TarjetaSimpleFondoBlock()),
    ('grupo_de_tarjetas_fondo', GrupoDeTarjetasFondoBlock()),
    ('card_evento', CardEventoBlock()),
    ('eventos_grid', EventosGridBlock()),
    ('tarjeta_noticia', TarjetaNoticiaBlock()),
    ('grupo_de_noticias', GrupoDeNoticiasBlock()),
    ('gallery_image', GalleryImageBlock()),
    ('modulos_certiffy', ModulosCertiffyBlockNuevo()),
    ('parrafo_con_alineacion', ParrafoConAlineacionBlock()),
    

]



class BaseContentPage(Page):
    body = StreamField(common_streamfield, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("body"),
    ]

    class Meta:
        abstract = True

class HomePage(BaseContentPage):
    subpage_types = [
        'home.NoticiasIndexPage',
        'home.EventosIndexPage',
        'home.ContactoPage',
        'home.PaginaInformativaPage',
        'home.ArticlePage',
    ]

    def get_context(self, request):
        context = super().get_context(request)

        children = self.get_children().type(PaginaInformativaPage).live()
        acerca_de = children.filter(slug="acerca_de").first()
        plataforma = children.filter(slug="plataforma").first()
        pacto_verde = children.filter(slug="pacto_verde").first()

        children = self.get_children().type(EventosIndexPage).live()
        eventos = children.filter(slug="eventos").first()

        children = self.get_children().type(NoticiasIndexPage).live()
        noticias = children.filter(slug="noticias").first()

        children = self.get_children().type(ContactoPage).live()
        contacto = children.filter(slug="contacto").first()

        context['acerca_de'] = acerca_de.specific if acerca_de else None
        context['plataforma'] = plataforma.specific if plataforma else None
        context['pacto_verde'] = pacto_verde.specific if pacto_verde else None
        context['eventos'] = eventos.specific if eventos else None
        context['noticias'] = noticias.specific if noticias else None
        context['contacto'] = contacto.specific if contacto else None

        if plataforma:
            subpaginas = plataforma.get_children().type(ArticlePage).live()
            trazabilidad = subpaginas.filter(slug="trazabilidad").first()
            administracion = subpaginas.filter(slug="administracion").first()
            certificacion = subpaginas.filter(slug="certificacion").first()
            context['trazabilidad'] = trazabilidad.specific if trazabilidad else None
            context['administracion'] = administracion.specific if administracion else None
            context['certificacion'] = certificacion.specific if certificacion else None
        else:
            context['trazabilidad'] = None
            context['administracion'] = None
            context['certificacion'] = None

        if pacto_verde:
            subpaginas = pacto_verde.get_children().type(ArticlePage).live()
            union_europea = subpaginas.filter(slug="union-europea").first()
            due_diligence = subpaginas.filter(slug="due-diligence").first()
            context['union_europea'] = union_europea.specific if union_europea else None
            context['due_diligence'] = due_diligence.specific if due_diligence else None
        else:
            context['union_europea'] = None
            context['due_diligence'] = None

        return context


    class Meta:
        verbose_name = "Inicio"

    



class NoticiasIndexPage(BaseContentPage):

    subpage_types = ['home.NoticiaPage']

    def get_context(self, request):
        context = super().get_context(request)
        

        noticias = NoticiaPage.objects.live().descendant_of(self)

        categoria = request.GET.get('categoria')
        tag = request.GET.get('tag')

        if categoria:
            noticias = noticias.filter(categoria__slug=categoria)

        if tag:
            noticias = noticias.filter(tags__slug=tag)

        noticia_ids = noticias.values_list('id', flat=True)

        tag_ids = NoticiaPageTag.objects.filter(
            content_object_id__in=noticia_ids  # ← aquí la corrección
        ).values_list('tag_id', flat=True)

        tags_relacionados = Tag.objects.filter(id__in=tag_ids).distinct()

        context['noticias'] = noticias
        context['categorias'] = CategoriaNoticia.objects.all()
        context['tags'] = tags_relacionados
        context['current_categoria'] = categoria
        context['current_tag'] = tag

        return context

class NoticiaPage(BaseContentPage):
    fecha = models.DateField("Fecha de Publicación", auto_now_add=True, editable=False) 
    categoria = models.ForeignKey(
        'home.CategoriaNoticia',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='noticias'
    )
    tags = ClusterTaggableManager(through=NoticiaPageTag, blank=True)

    content_panels = BaseContentPage.content_panels + [
        FieldPanel('categoria'),
        FieldPanel('tags'),
    ]

    api_fields = BaseContentPage.api_fields + [
        APIField("fecha"),
        APIField("categoria"),
        APIField("tags"),
    ]

    subpage_types = []
    parent_page_types = ['home.NoticiasIndexPage']

class EventosIndexPage(BaseContentPage):
    subpage_types = ['home.EventoPage']
    parent_page_types = ['home.HomePage']

    def get_context(self, request):
        context = super().get_context(request)

        eventos = EventoPage.objects.live().descendant_of(self)

        categoria = request.GET.get('categoria')
        tag = request.GET.get('tag')

        if categoria:
            eventos = eventos.filter(categoria__slug=categoria)

        if tag:
            eventos = eventos.filter(tags__slug=tag)

        evento_ids = eventos.values_list('id', flat=True)

        tag_ids = EventoPageTag.objects.filter(
            content_object_id__in=evento_ids
        ).values_list('tag_id', flat=True)

        tags_relacionados = Tag.objects.filter(id__in=tag_ids).distinct()

        context['eventos'] = eventos
        context['categorias'] = CategoriaEvento.objects.all()
        context['tags'] = tags_relacionados
        context['current_categoria'] = categoria
        context['current_tag'] = tag

        return context

class EventoPage(BaseContentPage):
    fecha = models.DateTimeField("Fecha del Evento")
    ubicacion = models.CharField("Ubicación", max_length=255)
    mapa_url = models.TextField("URL del Mapa", blank=True, help_text="Enlace a Google Maps u otro servicio de mapas")

    categoria = models.ForeignKey(
        'home.CategoriaEvento',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='eventos'
    )

    tags = ClusterTaggableManager(through='home.EventoPageTag', blank=True)

    content_panels = BaseContentPage.content_panels + [
        FieldPanel("fecha"),
        FieldPanel("ubicacion"),
        FieldPanel("mapa_url"),
        FieldPanel("categoria"),
        FieldPanel("tags"),
    ]

    api_fields = BaseContentPage.api_fields + [
        APIField("fecha"),
        APIField("ubicacion"),
        APIField("mapa_url"),
        APIField("categoria"),
        APIField("tags"),
    ]

    subpage_types = []
    parent_page_types = ['home.EventosIndexPage']

class PaginaInformativaPage(BaseContentPage):  
    parent_page_types = ['home.HomePage']
    subpage_types = ['home.ArticlePage']

class ArticlePage(BaseContentPage):
    parent_page_types = ['home.PaginaInformativaPage']
    subpage_types = []


class ContactoPage(BaseContentPage):
    telefono = models.CharField("Teléfono", max_length=20, blank=True)
    email = models.EmailField("Correo Electrónico", blank=True)
    direccion = models.TextField("Dirección", blank=True)
    horario = models.TextField("Horario", blank=True)

    content_panels = BaseContentPage.content_panels + [
        FieldPanel("telefono"),
        FieldPanel("email"),
        FieldPanel("direccion"),
        FieldPanel("horario"),
    ]

    api_fields = BaseContentPage.api_fields + [
        APIField("telefono"),
        APIField("email"),
        APIField("direccion"),
        APIField("horario"),
    ]
    parent_page_types = ['home.HomePage']
    subpage_types = []

    

