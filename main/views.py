from datetime import date
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.contrib.auth import login
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Exists, OuterRef
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, BlogRequestForm, ProfileForm
from .models import BlogRequest, SavedRequest, UserProfile

from django.contrib import messages
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
    if request.user.is_authenticated:
        action_dates = list(
            BlogRequest.objects.filter(saves__user=request.user).exclude(user=request.user)
            .values_list('start_date', flat=True)
        )
        action_dates = [d.strftime("%Y-%m-%d") for d in action_dates]
    else:
        action_dates = []
    return render(request, "webui/home.html", {"action_dates": action_dates})


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

def public_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    profile = user.profile  # OneToOneField ensures this exists
    return render(request, 'webui/public-profile.html', {
        'author': user,
        'profile': profile,
    })


@login_required
def available_requests(request):
    GROUPSIZE_RANGES = {
        'size1': (0, 100),
        'size2': (100, 500),
        'size3': (500, 1000),
        'size4': (1000, 1000000),
    }

    genre = request.GET.get('genre')
    groupsize = request.GET.get('groupsize')

    saved_qs = SavedRequest.objects.filter(user=request.user, request=OuterRef('pk'))
    qs = BlogRequest.objects.exclude(user=request.user).exclude(saves__user=request.user)

    # Filter by genre and group size linked via user profile if provided
    if genre:
        qs = qs.filter(user__profile__genres=genre)
    if groupsize:
        low, high = GROUPSIZE_RANGES[groupsize]
        qs = qs.filter(user__profile__subscribers_count__gte=low, user__profile__subscribers_count__lt=high)

    requests = qs.annotate(saved=Exists(saved_qs)) \
        .select_related('user', 'user__profile') \
        .order_by('-start_date')

    # Create blocked dates dictionary with properly formatted strings
    blocked_dates = {}
    for req in requests:
        taken_dates = SavedRequest.objects.filter(request=req).values_list('share_due_date', flat=True)
        blocked_dates[req.id] = [
            d.strftime("%Y-%m-%d") for d in taken_dates if d is not None
        ]

    context = {
        'requests': requests,
        'selected_genre': genre or '',
        'selected_groupsize': groupsize or '',
        'today': date.today().isoformat(),
        'blocked_dates_json': json.dumps(blocked_dates, cls=DjangoJSONEncoder)
    }

    return render(request, 'webui/available-requests.html', context)


@login_required
def toggle_save_request(request, pk):
    br = get_object_or_404(BlogRequest, pk=pk)
    if request.method == 'POST':
        share_due_date = request.POST.get('share_due_date')
        user_has_saved = SavedRequest.objects.filter(user=request.user, request=br).exists()

        # Remove request (cancelling) — no date posted
        if user_has_saved and not share_due_date:
            SavedRequest.objects.filter(user=request.user, request=br).delete()

        # Saving new request — must have a date
        elif share_due_date:
            try:
                share_due_date_obj = datetime.strptime(share_due_date, '%Y-%m-%d').date()
            except Exception:
                return render(request, "webui/error.html", {"error": "Неверный формат даты."})

            min_allowed = max(date.today(), br.available_from)
            if share_due_date_obj < min_allowed or share_due_date_obj > br.available_to:
                return render(request, "webui/error.html", {"error": f"Выберите дату от {min_allowed} до {br.available_to}."})

            date_taken = SavedRequest.objects.filter(request=br, share_due_date=share_due_date).exists()
            if date_taken:
                messages.error(request, "Этот день уже занят для этой заявки.")
                return redirect('available_requests')

            # Not already saved and date is free
            if not user_has_saved:
                SavedRequest.objects.create(
                    user=request.user,
                    request=br,
                    share_due_date=share_due_date
                )
        else:
            return render(request, "webui/error.html", {"error": "Дата должна быть выбрана."})

        referer = request.META.get('HTTP_REFERER')
        if referer and '/requests/' in referer and 'available' not in referer:
            return redirect('requests')
        else:
            return redirect('available_requests')



@login_required
def show_requests(request):
    # Created requests by user with acceptance counts
    user_requests = BlogRequest.objects.filter(user=request.user).order_by('-start_date')

    # Add acceptance count to each request
    for req in user_requests:
        req.acceptance_count = SavedRequest.objects.filter(request=req).count()

    # Accepted (saved) requests - Profile accepts requests that belong to others but saved by user
    accepted_requests = BlogRequest.objects.filter(saves__user=request.user).exclude(user=request.user).order_by(
        '-start_date')

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
def request_details(request, pk):
    blog_request = get_object_or_404(BlogRequest, pk=pk, user=request.user)
    acceptances = SavedRequest.objects.filter(request=blog_request).select_related('user', 'user__profile').order_by(
        '-created_at')
    context = {
        'blog_request': blog_request,
        'acceptances': acceptances,
        'acceptance_count': acceptances.count(),
    }
    return render(request, 'webui/request-details.html', context)


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

        elif field == 'start_date':
            try:
                # Parse date from ISO format (YYYY-MM-DD)
                date_obj = datetime.strptime(value, '%Y-%m-%d').date()
                blog_request.start_date = date_obj
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

def custom_404(request, exception):
    return render(request, 'webui/page-not-found.html', status=404)