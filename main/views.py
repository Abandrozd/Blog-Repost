from django.http import JsonResponse
from django.contrib.auth import login
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Exists, OuterRef
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, BlogRequestForm, ProfileForm
from .models import BlogRequest, SavedRequest, UserProfile
from datetime import datetime
import json

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "webui/registration.html", {"form": form})

def home(request):
    return render(request, "webui/home.html")

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user_profile)

    return render(request, 'webui/profile.html', {
        'form': form,
        'user': request.user,
        'profile': user_profile,
    })


@login_required
def available_requests(request):
    genre = request.GET.get('genre')
    groupsize = request.GET.get('groupsize')

    saved_qs = SavedRequest.objects.filter(user=request.user, request=OuterRef('pk'))
    qs = BlogRequest.objects.exclude(user=request.user).exclude(saves__user=request.user)

    # Filter by genre and group size linked via user profile if provided
    if genre:
        qs = qs.filter(user__profile__genre=genre)
    if groupsize:
        qs = qs.filter(user__profile__groupsize=groupsize)

    requests = qs.annotate(saved=Exists(saved_qs)) \
        .select_related('user', 'user__profile') \
        .order_by('-date_exchange')

    context = {
        'requests': requests,
        'selected_genre': genre or '',
        'selected_groupsize': groupsize or '',
    }
    return render(request, 'webui/available-requests.html', context)


@login_required
def toggle_save_request(request, pk):
    if request.method == 'POST':
        br = get_object_or_404(BlogRequest, pk=pk)
        obj, created = SavedRequest.objects.get_or_create(user=request.user, request=br)
        if not created:
            obj.delete()

        # Redirect back to the referring page or default to available_requests
        referer = request.META.get('HTTP_REFERER')
        if referer and '/requests/' in referer and 'available' not in referer:
            return redirect('requests')
        else:
            return redirect('available_requests')

@login_required
def show_requests(request):
    # Created requests by user
    user_requests = BlogRequest.objects.filter(user=request.user).order_by('-date_exchange')

    # Accepted (saved) requests - Profile accepts requests that belong to others but saved by user
    accepted_requests = BlogRequest.objects.filter(saves__user=request.user).exclude(user=request.user).order_by('-date_exchange')

    context = {
        'created_requests': user_requests,
        'accepted_requests': accepted_requests,
    }
    return render(request, 'webui/requests.html', context)


@login_required(login_url='/login/')
def create_request(request):
    if request.method == "POST":
        form = BlogRequestForm(request.POST)
        if form.is_valid():
            blog_request = form.save(commit=False)
            blog_request.user = request.user
            blog_request.save()
            return redirect('requests')
    else:
        form = BlogRequestForm()
    return render(request, 'webui/request.html', {"form": form})


@login_required
def update_request(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    blog_request = get_object_or_404(BlogRequest, pk=pk, user=request.user)

    try:
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')

        if field == 'book_name':
            if len(value) < 1 or len(value) > 255:
                return JsonResponse({'success': False, 'error': 'Название должно быть от 1 до 255 символов'})
            blog_request.book_name = value

        elif field == 'date_exchange':
            try:
                # Parse date from ISO format (YYYY-MM-DD)
                date_obj = datetime.strptime(value, '%Y-%m-%d').date()
                blog_request.date_exchange = date_obj
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Неверный формат даты'})
        else:
            return JsonResponse({'success': False, 'error': 'Недопустимое поле'})

        blog_request.save()
        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def delete_request(request, pk):
    blog_request = get_object_or_404(BlogRequest, pk=pk, user=request.user)
    try:
        blog_request.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
