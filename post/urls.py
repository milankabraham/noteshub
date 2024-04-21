from django.urls import path , re_path
from post.views import index, NewPost, PostDetail, Tags, like, favourite, product , privacy , terms
from .views import * 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    path('newpost', NewPost, name='newpost'),
    path('<uuid:post_id>', PostDetail, name='post-details'),
    path('tag/<slug:tag_slug>', Tags, name='tags'),
    path('<uuid:post_id>/like', like, name='like'),
    path('<uuid:post_id>/favourite', favourite, name='favourite'),
    path('products' , product , name='products'),
    path('privacy' , privacy , name='privacy'),
    path('terms' , terms , name='terms'),
    path('nav' , navbar , name='navbar'),
    path('homeNav' , homeNav , name='homeNav'),
    path('Modifyprofile' , Modifyprofile , name='Modifyprofile'),
    path('sellNotes' , sellNotes , name='sellNotes'),
    re_path(r'^post/(?P<post_id>[0-9a-f-]+)/delete/$', delete_post, name='delete-post'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete-comment'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
