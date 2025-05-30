from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.models import register_snippet


@register_snippet
class NavItem(models.Model):
    title = models.CharField(max_length=255)
    page = models.ForeignKey(Page, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.IntegerField(default=0)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


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
    imagen = CustomImageBlock(required=False, label="Foto del Testimonio")

    class Meta:
        icon = "user"
        label = "Testimonio"

    def get_api_representation(self, value, context=None):
        imagen = value.get("imagen")
        return {
            "nombre": value["nombre"],
            "comentario": value["comentario"],
            "organizacion": value["organizacion"],
            "imagen": {
                "url": imagen.get_rendition("original").url if imagen else None,
                "title": imagen.title if imagen else None
            }
        }



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
                "url": imagen.get_rendition("original").url if imagen else None,
                "title": imagen.title if imagen else None
            } if imagen else None
        }



class TestimoniosBlock(blocks.StructBlock):
    testimonios = blocks.ListBlock(TestimonioBlock(), label="Lista de testimonios")

    class Meta:
        template = "blocks/testimonios_carrusel.html"  
        icon = "group"
        label = "Testimonios Carrusel"





class ModuloCertiffyBlock(blocks.StructBlock):
    video_url = blocks.URLBlock(label="URL del video (YouTube, Vimeo, etc.)")
    video_caption = blocks.CharBlock(
        required=False, label="Descripción del video (abajo del reproductor)"
    )
    imagen = ImageChooserBlock(required=False, label="Imagen adicional")  
    titulo = blocks.CharBlock(required=True, label="Título")
    descripcion = blocks.TextBlock(required=True, label="Descripción")
    botones = blocks.ListBlock(ButtonBlock(), label="Módulos disponibles")

    def get_api_representation(self, value, context=None):
        return {
            "video_url": value.get("video_url"),
            "video_caption": value.get("video_caption"),
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
    video_url = blocks.URLBlock(required=False, label="Video (URL de YouTube o Vimeo)")
    mostrar_video = blocks.BooleanBlock(required=False, default=True, label="Mostrar video")

    class Meta:
        icon = "image"
        label = "Carrusel con video"
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
        return {
            "imagen": {
                "id": value["imagen"].id,
                "url": value["imagen"].get_rendition("original").url,
                "title": value["imagen"].title,
            },
            "titulo": value["titulo"],
            "descripcion": value["descripcion"],
            "botones": [
                {
                    "texto": boton["texto"],
                    "url": boton["url"],
                }
                for boton in value.get("botones", [])
            ],
        }

class ImagenConTextoBlock(blocks.StructBlock):
    imagen = ImageChooserBlock(required=True, label="Imagen")
    texto = blocks.CharBlock(required=True, label="Texto largo")

    class Meta:
        template = "blocks/texto_imagen_block.html"
        icon = "image"
        label = "Imagen y texto"

    def get_api_representation(self, value, context=None):
        return {
            "imagen": {
                "id": value["imagen"].id,
                "url": value["imagen"].get_rendition("original").url,
                "title": value["imagen"].title,
            },
            "texto": value["texto"],
          
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
                for logo in value['logos']
            ]
        }

    class Meta:
        icon = "list-ul"
        label = "Lista de Logos"
        template = "blocks/ListaDeLogosBlock.html"

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

    
