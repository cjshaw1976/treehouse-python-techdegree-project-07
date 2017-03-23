from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from PIL import Image, ExifTags

from . import forms
from . import models


def sign_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            if form.user_cache is not None:
                user = form.user_cache
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(
                        reverse('accounts:profile')
                    )
                else:
                    messages.error(
                        request,
                        "That user account has been disabled."
                    )
            else:
                messages.error(
                    request,
                    "Username or password is incorrect."
                )
    return render(request, 'accounts/sign_in.html', {'form': form})


def sign_up(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)
            messages.success(
                request,
                "You're now a user! You've been signed in, too."
            )
            return HttpResponseRedirect(reverse('accounts:profile'))
    return render(request, 'accounts/sign_up.html', {'form': form})


def sign_out(request):
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return HttpResponseRedirect(reverse('home'))


@login_required
def profile(request):
    current_user = request.user
    profile = request.user.userprofile
    return render(request, 'accounts/profile.html',
                  {'current_user': current_user, 'profile': profile})


@login_required
def profile_edit(request):
    current_user = request.user
    form = forms.ProfileForm(instance=request.user.userprofile)

    if request.method == 'POST':
        form = forms.ProfileForm(request.POST, request.FILES or None,
                                 instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            if len(request.FILES) != 0:
                # preprocess uploaded image
                new_image = str(request.user.userprofile.avatar.file)
                im = Image.open(new_image)
                # sort out issue that kept making avata upside down
                exif = dict((ExifTags.TAGS[k], v)
                            for k, v in im._getexif().items()
                            if k in ExifTags.TAGS)
                if not exif['Orientation']:
                    im = im.rotate(90, expand=True)
                # Resize to manageable
                im.thumbnail((400, 600), Image.ANTIALIAS)
                im.save(new_image)

                # Redirect to cropping
                return HttpResponseRedirect(reverse('accounts:profile_crop'))

            return HttpResponseRedirect(reverse('accounts:profile'))

    return render(request, 'accounts/profile_edit.html',
                  {'form': form, 'current_user': current_user})


@login_required
def password_change(request):
    form = forms.PasswordChangeCustomForm()
    user = request.user
    if request.method == 'POST':
        form = forms.PasswordChangeCustomForm(data=request.POST, user=user,
                                              profile=user.userprofile)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request,
                             'Your password was successfully changed!')
            return HttpResponseRedirect(reverse('home'))

    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
def profile_crop(request):
    form = forms.CropForm()
    user = request.user
    profile = request.user.userprofile
    if request.method == 'POST':
        form = forms.CropForm(data=request.POST)
        if form.is_valid():
            original_image = str(profile.avatar.file)
            crop_coords = {
                'scale': float(form.cleaned_data['scale']),
                'angle': 0 - float(form.cleaned_data['angle']),
                'x': float(form.cleaned_data['x']),
                'y': float(form.cleaned_data['y']),
                'w': float(form.cleaned_data['w']),
                'h': float(form.cleaned_data['h'])
            }
            cropped_image = cropper(original_image, crop_coords)
            return render(request, 'accounts/profile.html',
                          {'current_user': user, 'profile': profile})

    return render(request, 'accounts/profile_crop.html',
                  {'user': user, 'profile': profile, 'form': form})


def cropper(original_image_path, crop_coords):
    """ Open original, create and save a new cropped image"""
    editable = Image.open(original_image_path)

    # rotate first
    if crop_coords['angle'] != 0:
        editable = editable.rotate(crop_coords['angle'], expand=True)

    # cropping area
    box = (int(crop_coords['x']/crop_coords['scale']),
           int(crop_coords['y']/crop_coords['scale']),
           int((crop_coords['x'] + crop_coords['w'])/crop_coords['scale']),
           int((crop_coords['y'] + crop_coords['h'])/crop_coords['scale']))
    editable = editable.crop(box)

    # save over original_image_path
    editable.save(original_image_path)
