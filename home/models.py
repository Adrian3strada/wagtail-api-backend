from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

# ---------- BLOQUE PERSONALIZADO PARA IMÁGENES ----------

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
    menu_children = APIField('menu_children')

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

# ---------- OPCIONES DE COLORES ----------

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

# ---------- BLOQUES PERSONALIZADOS CON IMAGEN ----------

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
                "url": imagen.get_rendition("original").url if imagen else None,
                "title": imagen.title if imagen else None
            } if imagen else None
        }

class CardsBlock(blocks.StructBlock):
    tarjetas = blocks.ListBlock(CardBlock(), label="tarjeta de noticias")

    class Meta:
        icon = "placeholder"
        label = "Grupo de tarjetas"
        template = "blocks/cards_block.html"

from wagtail import blocks

class TestimonioBlock(blocks.StructBlock):
    nombre = blocks.CharBlock(label="Nombre")
    comentario = blocks.TextBlock(label="Comentario")
    imagen = CustomImageBlock(required=False, label="Imagen (opcional)")

    class Meta:
        icon = "user"
        label = "Testimonio"

    def get_api_representation(self, value, context=None):
        imagen = value.get("imagen")
        return {
            "nombre": value["nombre"],
            "comentario": value["comentario"],
            "imagen": {
                "url": imagen.get_rendition("original").url if imagen else None,
                "title": imagen.title if imagen else None
            }
        }

class TestimoniosBlock(blocks.StructBlock):
    testimonios = blocks.ListBlock(TestimonioBlock(), label="Lista de testimonios")

    class Meta:
        template = "blocks/testimonios_carrusel.html"  
        icon = "group"
        label = "Testimonios Carrusel"

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


class ModuloCertiffyBlock(blocks.StructBlock):
    video_url = blocks.URLBlock(label="URL del video (YouTube, Vimeo, etc.)")
    video_caption = blocks.CharBlock(
        required=False, label="Descripción del video (abajo del reproductor)"
    )
    titulo = blocks.CharBlock(required=True, label="Título")
    descripcion = blocks.TextBlock(required=True, label="Descripción")
    botones = blocks.ListBlock(ButtonBlock(), label="Módulos disponibles")

    def get_api_representation(self, value, context=None):
        return {
            "caption": value.get("caption"),

            "video_url": value.get("video_url"),
            "video_caption": value.get("video_caption"),
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

    class Meta:
        icon = "image"
        label = "Carrusel de imágenes"
        template = "blocks/carrusel_block.html"

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

# ---------- BLOQUES DE TEXTO, VIDEO, BOTÓN, IFRAME ----------



class VideoBlock(blocks.StructBlock):
    video_url = blocks.URLBlock(label="URL del video (YouTube o Vimeo)")

    class Meta:
        icon = "media"
        label = "Video embebido"
        template = "blocks/video_block.html"

class IframeBlock(blocks.StructBlock):
    iframe_url = blocks.URLBlock(label="URL del contenido embebido")
    height = blocks.IntegerBlock(default=400, label="Altura (px)")

    class Meta:
        icon = "code"
        label = "Contenido embebido (iframe)"
        template = "blocks/iframe_block.html"

# ---------- STREAMFIELD GLOBAL ----------

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

]

# ---------- PÁGINAS WAGTAIL ----------

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
    ]
    class Meta:
        verbose_name = "Inicio"

class NoticiasIndexPage(BaseContentPage):
    subpage_types = ['home.NoticiaPage']
    parent_page_types = ['home.HomePage']

class NoticiaPage(BaseContentPage):
    fecha = models.DateField("Fecha de Publicación", auto_now_add=True, editable=False)

    content_panels = BaseContentPage.content_panels

    api_fields = BaseContentPage.api_fields + [
        APIField("fecha"),
    ]

    subpage_types = []
    parent_page_types = ['home.NoticiasIndexPage']

class EventosIndexPage(BaseContentPage):
    subpage_types = ['home.EventoPage']
    parent_page_types = ['home.HomePage']

class EventoPage(BaseContentPage):
    fecha = models.DateTimeField("Fecha del Evento")
    ubicacion = models.CharField("Ubicación", max_length=255)

    content_panels = BaseContentPage.content_panels + [
        FieldPanel("fecha"),
        FieldPanel("ubicacion"),
    ]

    api_fields = BaseContentPage.api_fields + [
        APIField("fecha"),
        APIField("ubicacion"),
    ]

    subpage_types = []
    parent_page_types = ['home.EventosIndexPage']

class PaginaInformativaPage(BaseContentPage):  
    parent_page_types = ['home.HomePage']
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