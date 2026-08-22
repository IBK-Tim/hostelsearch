from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Student, Agent, Hostel, HostelImage, Review, SavedHostel


# ── HELPER ─────────────────────────────────────────────────────
def redirect_by_role(user):
    if user.is_staff or user.is_superuser:
        return redirect('/admin/')
    elif hasattr(user, 'agent'):
        return redirect('agent_dashboard')
    elif hasattr(user, 'student'):
        return redirect('student_dashboard')
    else:
        return redirect('login')


# ── HOME ───────────────────────────────────────────────────────
def home(request):
    # if student is logged in send them to dashboard
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    featured = Hostel.objects.filter(status='approved')[:3]
    return render(request, 'main/home.html', {'featured': featured})


# ── REGISTER ───────────────────────────────────────────────────
def register(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        role     = request.POST.get('role', 'student')
        first    = request.POST.get('first_name', '').strip()
        last     = request.POST.get('last_name', '').strip()
        email    = request.POST.get('email', '').strip()
        phone    = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm  = request.POST.get('confirm', '')

        # validation
        if not all([first, last, email, phone, password, confirm]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'main/register.html')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'main/register.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'main/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'main/register.html')

        if role == 'agent':
            user = User.objects.create_user(
                username   = email,
                email      = email,
                password   = password,
                first_name = first,
                last_name  = last,
            )
            Agent.objects.create(
                user          = user,
                phone         = phone,
                business_name = request.POST.get('business_name', '').strip(),
                passport      = request.FILES.get('passport'),
                id_document   = request.FILES.get('id_document'),
                is_verified   = False,
            )
            messages.success(request,
                'Agent account submitted successfully. '
                'Wait for admin verification before you can login.'
            )
            return redirect('login')

        else:
           
            user = User.objects.create_user(
                username   = email,
                email      = email,
                password   = password,
                first_name = first,
                last_name  = last,
            )
            Student.objects.create(
                user      = user,
                phone     = phone,
            )
            messages.success(request,
                'Account created successfully. You can now login.'
            )
            return redirect('login')

    return render(request, 'main/register.html')


# ── LOGIN ──────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Please enter your email and password.')
            return render(request, 'main/login.html')

        try:
            user_obj = User.objects.get(email=email)
            user     = authenticate(
                request,
                username = user_obj.username,
                password = password
            )

            if user is not None:

                # ── block unverified agents ──────────────────
                if hasattr(user, 'agent') and not user.agent.is_verified:
                    messages.error(request,
                        'Your agent account is pending admin verification. '
                        'You will be notified once your account is approved.'
                    )
                    return render(request, 'main/login.html')
                # ─────────────────────────────────────────────

                login(request, user)
                return redirect_by_role(user)

            else:
                messages.error(request, 'Incorrect password. Please try again.')

        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')

    return render(request, 'main/login.html')


# ── LOGOUT ─────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')


# ── SEARCH / BROWSE ────────────────────────────────────────────
def Search(request):
    hostels = Hostel.objects.filter(status='approved')

    # show unavailable hostels but mark them clearly
    q = request.GET.get('q')
    if q:
        hostels = hostels.filter(
            Q(hostel_name__icontains=q) |
            Q(location__icontains=q)
        )

    hostel_type = request.GET.get('type')
    if hostel_type:
        hostels = hostels.filter(hostel_type=hostel_type)

    price_max = request.GET.get('price')
    if price_max:
        hostels = hostels.filter(price_session__lte=price_max)

    saved_ids = []
    if request.user.is_authenticated and hasattr(request.user, 'student'):
        saved_ids = SavedHostel.objects.filter(
            student=request.user.student
        ).values_list('hostel_id', flat=True)

    return render(request, 'main/Search.html', {
        'hostels'  : hostels,
        'saved_ids': saved_ids,
    })


# ── HOSTEL DETAIL ──────────────────────────────────────────────
def hostel_detail(request, pk):
    hostel       = get_object_or_404(Hostel, pk=pk, status='approved')
    reviews      = Review.objects.filter(hostel=hostel)
    show_contact = request.user.is_authenticated

    context = {
        'hostel'      : hostel,
        'reviews'     : reviews,
        'show_contact': show_contact,
    }
    return render(request, 'main/detail.html', context)


# ── STUDENT DASHBOARD ──────────────────────────────────────────
@login_required(login_url='/login/')
def student_dashboard(request):
    if not hasattr(request.user, 'student'):
        return redirect_by_role(request.user)

    student      = request.user.student
    review_count = Review.objects.filter(student=student).count()
    saved        = SavedHostel.objects.filter(student=student)
    saved_count  = saved.count()
    reviews      = Review.objects.filter(student=student)

    context = {
        'student'     : student,
        'review_count': review_count,
        'saved_count' : saved_count,
        'saved'       : saved,
        'reviews'     : reviews,
    }
    return render(request, 'main/StudentDashboard.html', context)


# ── AGENT DASHBOARD ────────────────────────────────────────────
@login_required(login_url='/login/')
def agent_dashboard(request):
    if not hasattr(request.user, 'agent'):
        return redirect_by_role(request.user)

    agent    = request.user.agent
    listings = Hostel.objects.filter(agent=agent)

    context = {
        'agent'         : agent,
        'listings'      : listings,
        'total_listings': listings.count(),
        'approved_count': listings.filter(status='approved').count(),
        'pending_count' : listings.filter(status='pending').count(),
        'total_views'   : 0,
    }
    return render(request, 'main/Agent.html', context)


# ── SUBMIT LISTING ─────────────────────────────────────────────
@login_required(login_url='/login/')
def submit_listing(request):
    if not hasattr(request.user, 'agent'):
        messages.error(request, 'Only verified agents can submit listings.')
        return redirect('login')

    if request.method == 'POST':
        agent       = request.user.agent
        hostel_name = request.POST.get('hostel_name', '').strip()
        hostel_type = request.POST.get('hostel_type', '').strip()
        description = request.POST.get('description', '').strip()
        price       = request.POST.get('price_session', 0)
        location    = request.POST.get('location', '').strip()
        distance    = request.POST.get('distance', '').strip()
        total_rooms = request.POST.get('total_rooms') or 0
        fac         = request.POST.getlist('fac')

        if not all([hostel_name, hostel_type, description, price, location]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'main/Agent.html')

        # save hostel
        hostel = Hostel.objects.create(
            agent           = agent,
            hostel_name     = hostel_name,
            hostel_type     = hostel_type,
            description     = description,
            price_session   = price,
            location        = location,
            distance        = distance,
            total_rooms     = total_rooms,
            has_electricity = 'electricity' in fac,
            has_water       = 'water'       in fac,
            has_security    = 'security'    in fac,
            has_wifi        = 'wifi'        in fac,
            has_parking     = 'parking'     in fac,
            has_generator   = 'generator'   in fac,
            has_bathroom    = 'bathroom'    in fac,
            has_kitchen     = 'kitchen'     in fac,
            status          = 'pending',
        )

        # save uploaded photos
        photos = request.FILES.getlist('photos')
        for photo in photos:
            HostelImage.objects.create(
                hostel = hostel,
                image  = photo
            )

        messages.success(request, 'Listing submitted for admin review.')
        return redirect('agent_dashboard')

    return render(request, 'main/Agent.html')

@login_required(login_url='/login/')
def toggle_save(request, pk):
    if not hasattr(request.user, 'student'):
        return redirect('login')

    hostel  = get_object_or_404(Hostel, pk=pk)
    student = request.user.student

    saved = SavedHostel.objects.filter(student=student, hostel=hostel)

    if saved.exists():
        saved.delete()
        messages.success(request, f'{hostel.hostel_name} removed from saved.')
    else:
        SavedHostel.objects.create(student=student, hostel=hostel)
        messages.success(request, f'{hostel.hostel_name} saved successfully.')

    return redirect('Search')

@login_required(login_url='/login/')
def update_agent_profile(request):
    if not hasattr(request.user, 'agent'):
        return redirect('login')

    if request.method == 'POST':
        agent = request.user.agent
        user  = request.user

        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name  = request.POST.get('last_name', '').strip()
        user.email      = request.POST.get('email', '').strip()
        user.save()

        agent.phone         = request.POST.get('phone', '').strip()
        agent.business_name = request.POST.get('business_name', '').strip()
        agent.save()

        messages.success(request, 'Profile updated successfully.')

    return redirect('agent_dashboard')

@login_required(login_url='/login/')
def update_student_profile(request):
    if not hasattr(request.user, 'student'):
        return redirect('login')

    if request.method == 'POST':
        student = request.user.student
        user    = request.user

        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name  = request.POST.get('last_name', '').strip()
        user.email      = request.POST.get('email', '').strip()
        user.save()

        student.phone = request.POST.get('phone', '').strip()
        student.save()

        messages.success(request, 'Profile updated successfully.')

    return redirect('student_dashboard')

@login_required(login_url='/login/')
def toggle_availability(request, pk):
    if not hasattr(request.user, 'agent'):
        return redirect('login')

    hostel = get_object_or_404(Hostel, pk=pk, agent=request.user.agent)
    hostel.is_available = not hostel.is_available
    hostel.save()

    if hostel.is_available:
        messages.success(request, f'{hostel.hostel_name} marked as Available.')
    else:
        messages.success(request, f'{hostel.hostel_name} marked as Fully Occupied.')

    return redirect('agent_dashboard')