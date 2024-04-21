from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect

from post.models import Post, Tag, Follow, Stream, Likes
from django.contrib.auth.models import User
from post.forms import NewPostform
from authy.models import Profile
from django.urls import resolve
from comment.models import Comment
from comment.forms import NewCommentForm
from django.core.paginator import Paginator
from .models import *
from django.db.models import Q
from pdf2image import convert_from_path
import os
from django.conf import settings
# from post.models import Post, Follow, Stream




@login_required
def index(request):
    user = request.user
    user = request.user
    all_users = User.objects.all()
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    profile = Profile.objects.all()

    posts = Stream.objects.filter(user=user)
    group_ids = []

    
    for post in posts:
        group_ids.append(post.post_id)
        
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')

    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(username__icontains=query))

        paginator = Paginator(users, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)


    context = {
        'post_items': post_items,
        'follow_status': follow_status,
        'profile': profile,
        'all_users': all_users,
        # 'users_paginator': users_paginator,
    }
    return render(request, 'index.html', context)


@login_required
def NewPost(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    tags_obj = []
    
    if request.method == "POST":
        form = NewPostform(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = form.cleaned_data.get('caption')
            tag_form = form.cleaned_data.get('tags')
            tag_list = list(tag_form.split(','))

            for tag in tag_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_obj.append(t)
            p, created = Post.objects.get_or_create(picture=picture, caption=caption, user=user)
            p.tags.set(tags_obj)
            p.save()
            return redirect('profile', request.user.username)
    else:
        form = NewPostform()
    context = {
        'form': form
    }
    return render(request, 'newpost.html', context)

@login_required
def PostDetail(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-date')

    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('post-details', args=[post.id]))
    else:
        form = NewCommentForm()

    context = {
        'post': post,
        'form': form,
        'comments': comments
    }

    return render(request, 'postdetail.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.user:  # Ensure only the owner can delete the post
        post.delete()
    return redirect('index')  # Redirect to home page after deletion, you can change this as per your requirement


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user:  # Ensure only the comment owner can delete the comment
        comment.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  # Redirect back to the same page after deletion


@login_required
def Tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-posted')

    context = {
        'posts': posts,
        'tag': tag

    }
    return render(request, 'tag.html', context)


# Like function
@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes
    liked = Likes.objects.filter(user=user, post=post).count()
    if not liked:
        Likes.objects.create(user=user, post=post)
        current_likes = current_likes + 1
    else:
        Likes.objects.filter(user=user, post=post).delete()
        current_likes = current_likes - 1
        
    post.likes = current_likes
    post.save()
    # return HttpResponseRedirect(reverse('post-details', args=[post_id]))
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))

@login_required
def favourite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(post)
    else:
        profile.favourite.add(post)
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))


def privacy(request):
    return render(request , "privacy.html")

def terms(request):
    return render(request , "terms.html")

def navbar(request):
    return render(request , "products/navbar.html")

def homeNav(request):
    return render(request , "products/home-nav.html")

def Modifyprofile(request):
    return render(request , "Modifyprofile.html")




def generate_preview_image(pdf_path, output_path):
    # Convert PDF to images
    images = convert_from_path(pdf_path , 500,poppler_path= 'C:/Users/MILAN/Downloads/Release-24.02.0-0/poppler-24.02.0/Library/bin')

    # Save the first page as the preview image
    preview_image = images[0]
    preview_image.save(output_path, 'JPEG')

    return os.path.basename(output_path)

@login_required
def product(request):
    if request.method == "GET" and 'search' in request.GET:
        query = request.GET.get('search')
        notes = NoteDetails.objects.filter(title__icontains=query)
    else:
        notes = NoteDetails.objects.all()
    return render(request, "product.html", {'notes': notes})






def sellNotes(request):
    if request.method == "POST":
        note = request.FILES["note_file"]
        title = request.POST.get("title")
        course = request.POST.get("course")
        institution = request.POST.get("institution")
        field = request.POST.get("field")
        desc = request.POST.get("note_desc")
        # exp_amount = request.POST.get("exp_amount")

        # Create NoteDetails object
        add_notes = NoteDetails.objects.create(
            note=note,
            title=title,
            course=course,
            institution=institution,
            field=field,
            description=desc,
            # exp_amount=exp_amount
        )

        # Generate preview image
        preview_image_path = os.path.join(settings.MEDIA_ROOT, 'preview_images', f'{add_notes.id}.jpg')
        os.makedirs(os.path.dirname(preview_image_path), exist_ok=True)
        preview_image_name = generate_preview_image(add_notes.note.path, preview_image_path)

        # Update the preview_image field
        add_notes.preview_image = os.path.join('preview_images', preview_image_name)
        add_notes.save()

        print("notes added ")
    return render(request, "products/sellNotes.html")