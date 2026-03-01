# =============================================================================
# SeconiqueStockAPI | views.py
# =============================================================================
# View layer for SeconiqueStockAPI. Contains HTML views for login, registration,
# and profile management; REST API views for stock data endpoints; and
# CompanyScopedMixin which filters querysets to the authenticated user's company.
# =============================================================================

#Get Django files
from django.shortcuts import redirect, render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages

#Get DRF files
import csv

#Get Framework files
from rest_framework import generics
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey

#Get Authentication files
from api.authentication import CustomAPIKeyAuthentication
from drf_spectacular.utils import extend_schema
from django.conf import settings

#Get Local files
from .models import StockLevels, GroupDescView, SubGroupDescView, RangeNameView
from .serializers import StockLevelsSerializer, GroupDescSerializer, SubGroupDescSerializer, RangeNameSerializer
from api.forms import UserUpdateForm, UserProfileUpdateForm, UserRegistrationForm
from api.models import UserProfile, SiteSettings


def home(request):
    """Redirect the root URL to the API documentation page.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponseRedirect: A redirect to '/api/docs/'.
    """
    return redirect('/api/docs/')


class CustomLoginView(LoginView):
    """Custom login view that includes registration_enabled in context."""
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        """Extend the default login context with the site registration toggle.

        Args:
            **kwargs: Additional keyword arguments passed to the parent method.

        Returns:
            dict: Template context including 'registration_enabled' (bool),
                  which controls whether the registration link is shown on the
                  login page.
        """
        context = super().get_context_data(**kwargs)
        context['registration_enabled'] = SiteSettings.load().registration_enabled
        return context


def custom_login_view(request):
    """Dispatch an incoming request to CustomLoginView.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: The response from CustomLoginView.as_view().
    """
    return CustomLoginView.as_view()(request)


def register(request):
    """Handle user registration via GET (display form) and POST (submit form).

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponseRedirect: Redirects to 'login' if registration is disabled,
            or to 'profile' on successful registration or if already authenticated.
        HttpResponse: Renders 'register.html' with the form on GET or invalid POST.

    Contract:
        - Registration must be enabled via SiteSettings; otherwise the user is
          redirected to login with an error message.
        - Already-authenticated users are redirected to their profile immediately.
        - On valid POST, a User and linked UserProfile are created and the user
          is logged in automatically.
    """
    site_settings = SiteSettings.load()
    if not site_settings.registration_enabled:
        messages.error(request, "Registration is currently disabled. Please contact an administrator.")
        return redirect('login')

    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
                is_active=True
            )
            UserProfile.objects.create(
                user=user,
                company_Name=form.cleaned_data.get('company_Name', '')
            )
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account has been created successfully.")
            return redirect('profile')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def generate_api_key(request):
    """Generate a new API key for the logged-in user, replacing any existing key.

    Args:
        request (HttpRequest): The incoming HTTP POST request from an
            authenticated user.

    Returns:
        HttpResponseRedirect: Always redirects to 'profile' after processing.

    Contract:
        - Only responds to POST requests; GET requests are redirected to 'profile'.
        - Requires the user's cust_ID to be set (account verified). If not,
          an error message is shown and a verification modal flag is set in session.
        - Any existing API key with the same name is deleted before a new one
          is created, ensuring only one active key per user at a time.
        - The real key is stored once in the session for display; only a masked
          version is persisted in UserProfile.
    """
    if request.method != 'POST':
        return redirect('profile')

    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if not profile_obj.cust_ID or not profile_obj.cust_ID.strip():
        messages.error(
            request,
            "Account awaiting verification. Please contact it@seconique.co.uk to verify your account before generating an API key."
        )
        request.session['show_verification_modal'] = True
        return redirect('profile')

    # Format the API key name as CustomerID_Username
    cust_id = profile_obj.cust_ID
    key_name = f"{cust_id}_{request.user.username}"

    # Delete any existing API keys for this user before generating a new one
    try:
        old_key = APIKey.objects.get(name=key_name)
        old_key.delete()
    except APIKey.DoesNotExist:
        pass
    except APIKey.MultipleObjectsReturned:
        APIKey.objects.filter(name=key_name).delete()

    api_key, key = APIKey.objects.create_key(name=key_name)

    # Store only the masked version in the user profile — the real key is shown once via session
    masked_key = key[:8] + 'X' * max(0, len(key) - 8)
    profile_obj.api_key = masked_key
    profile_obj.save()

    request.session['new_api_key'] = key
    request.session['api_key_generated'] = True

    return redirect('profile')


@login_required
def delete_api_key(request):
    """Delete the active API key for the logged-in user.

    Args:
        request (HttpRequest): The incoming HTTP POST request from an
            authenticated user.

    Returns:
        HttpResponseRedirect: Always redirects to 'profile' after processing.

    Contract:
        - Only responds to POST requests; GET requests are redirected to 'profile'.
        - Removes the key from both the APIKey model and the UserProfile display field.
        - If no key exists, an informational message is shown and no error is raised.
    """
    if request.method != 'POST':
        return redirect('profile')

    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile_obj.api_key:
        cust_id = profile_obj.cust_ID or "NONE"
        key_name = f"{cust_id}_{request.user.username}"
        try:
            api_key_obj = APIKey.objects.get(name=key_name)
            api_key_obj.delete()
        except APIKey.DoesNotExist:
            pass
        except APIKey.MultipleObjectsReturned:
            APIKey.objects.filter(name=key_name).delete()

        profile_obj.api_key = None
        profile_obj.save()
        messages.success(request, "Your API key has been deleted.")
    else:
        messages.info(request, "No API key to delete.")

    return redirect('profile')


@login_required
def profile(request):
    """Display the user profile page and handle profile updates and API key actions.

    Args:
        request (HttpRequest): The incoming HTTP request from an authenticated user.

    Returns:
        HttpResponseRedirect: Redirects to 'profile' after a successful POST
            update (PRG pattern), or delegates to generate_api_key /
            delete_api_key for those actions.
        HttpResponse: Renders 'profile.html' on GET or invalid POST, passing
            user_form, profile_form, new_api_key (if just generated), and
            show_verification_modal flag.

    Contract:
        - Requires authentication; unauthenticated users are redirected to login.
        - Handles three types of POST: profile update, API key generation,
          and API key deletion — distinguished by the POST field name present.
        - A newly generated API key is read from session once and then cleared,
          so it is only displayed to the user a single time.
    """
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'generate_api_key' in request.POST:
            return generate_api_key(request)
        elif 'delete_api_key' in request.POST:
            return delete_api_key(request)

        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(request.POST, instance=profile_obj)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile')  # PRG pattern
        else:
            messages.error(request, "Please fix the errors below and try again.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=profile_obj)

    show_verification_modal = request.session.pop('show_verification_modal', False)

    new_api_key = None
    if request.session.get('api_key_generated'):
        new_api_key = request.session.get('new_api_key')
        del request.session['new_api_key']
        del request.session['api_key_generated']

    return render(request, "profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "new_api_key": new_api_key,
        "show_verification_modal": show_verification_modal,
    })


class CompanyScopedMixin:
    """
    Mixin that filters the queryset to records belonging to the authenticated
    user's company. If company_ID is blank (admin/unscoped users), all records
    are returned.

    Caches the UserProfile on the request object to avoid repeated DB hits
    across get_queryset() and serializer to_representation() calls.
    """

    def get_queryset(self):
        """Return a queryset filtered to the authenticated user's company.

        Returns:
            QuerySet: All StockLevels records if the user has no company_ID set,
                or records filtered to company=profile.company_ID otherwise.

        Contract:
            - Caches the resolved UserProfile on request._cached_profile to
              prevent repeated database lookups within the same request cycle.
            - If no UserProfile exists for the user, all records are returned
              (equivalent to admin/unscoped behaviour).
        """
        queryset = super().get_queryset()
        user = getattr(self.request, 'user', None)

        if user:
            if not hasattr(self.request, '_cached_profile'):
                try:
                    self.request._cached_profile = UserProfile.objects.select_related('user').get(user=user)
                except UserProfile.DoesNotExist:
                    self.request._cached_profile = None

            profile = self.request._cached_profile
            if profile and profile.company_ID and profile.company_ID.strip():
                queryset = queryset.filter(company=profile.company_ID)

        return queryset


class StockLevelsFilter(filters.FilterSet):
    """Custom filter set for stock levels with stockLev comparison filters."""
    # Standard field filters
    partNum = filters.CharFilter(field_name='partNum', lookup_expr='exact', label='- Filter by partNum')
    rangeName = filters.CharFilter(field_name='rangeName', lookup_expr='exact', label='- Filter by rangeName')
    groupDesc = filters.CharFilter(field_name='groupDesc', lookup_expr='exact', label='- Filter by group description')
    subGroupDesc = filters.CharFilter(field_name='subGroupDesc', lookup_expr='exact', label='- Filter by sub-group description')

    # Stock level comparison filters
    sl_greaterThan = filters.NumberFilter(field_name='stockLev', lookup_expr='gt', label='- Filter stockLevels greater than')
    sl_lessThan = filters.NumberFilter(field_name='stockLev', lookup_expr='lt', label='- Filter stockLevels less than')
    sl_equalTo = filters.NumberFilter(field_name='stockLev', lookup_expr='exact', label='- Filter stockLevels equal to')

    class Meta:
        model = StockLevels
        fields = ['partNum', 'rangeName', 'groupDesc', 'subGroupDesc']


@extend_schema(description=settings.API_ENDPOINT_DESCRIPTIONS.get("stocklevels", ""))
class StockLevelsListView(CompanyScopedMixin, generics.ListAPIView):
    queryset = StockLevels.objects.all()
    serializer_class = StockLevelsSerializer
    permission_classes = [HasAPIKey]
    filter_backends = [DjangoFilterBackend]
    filterset_class = StockLevelsFilter


@extend_schema(description=settings.API_ENDPOINT_DESCRIPTIONS.get("stocklevels_csv", ""))
class StockLevelsCSVDownloadView(CompanyScopedMixin, generics.ListAPIView):
    queryset = StockLevels.objects.all()
    serializer_class = StockLevelsSerializer
    permission_classes = [HasAPIKey]
    authentication_classes = [CustomAPIKeyAuthentication]
    pagination_class = None  # CSV always returns all records

    def list(self, request, *args, **kwargs):
        """Return all stock levels for the authenticated user as a downloadable CSV file.

        Args:
            request (HttpRequest): The authenticated API request.
            *args: Additional positional arguments (passed by DRF).
            **kwargs: Additional keyword arguments (passed by DRF).

        Returns:
            HttpResponse: A text/csv response with Content-Disposition set to
                'attachment; filename="stocklevels.csv"'. Rows contain part number,
                description, range, group, sub-group, stock level, and last updated.
                An additional 'Company' column is appended for unscoped users.

        Contract:
            - Pagination is disabled; the full filtered dataset is always returned.
            - Company column is included only when the user's company_ID is blank,
              indicating an admin or unscoped account.
        """
        queryset = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stocklevels.csv"'
        writer = csv.writer(response)

        # Include the company column only for admin/unscoped users
        user = getattr(request, 'user', None)
        include_company = False
        if user:
            try:
                profile = UserProfile.objects.get(user=user)
                if not profile.company_ID or not profile.company_ID.strip():
                    include_company = True
            except UserProfile.DoesNotExist:
                include_company = True

        headers = ['Part Number', 'Part Description', 'Range Name', 'Group Description',
                   'Sub Group Description', 'Stock Level', 'Last Updated']
        if include_company:
            headers.append('Company')
        writer.writerow(headers)

        for item in queryset:
            row = [
                item.partNum,
                item.partDesc,
                item.rangeName,
                item.groupDesc,
                item.subGroupDesc,
                item.stockLev,
                item.lastUpdatedDT.strftime('%Y-%m-%d %H:%M:%S') if item.lastUpdatedDT else '',
            ]
            if include_company:
                row.append(item.company)
            writer.writerow(row)

        return response


def csv_download_page(request):
    """Render a simple HTML page for non-technical users to download stock CSV.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders 'csv_download.html', which uses JavaScript to
            fetch the CSV from the API with the user's stored API key.
    """
    return render(request, 'csv_download.html')


def group_desc_list(request):
    """Return a JSON list of all distinct product group descriptions.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        JsonResponse: A JSON object with a 'groups' key containing a sorted
            list of all distinct groupDesc values from GroupDescView.
    """
    data = list(GroupDescView.objects.values_list("groupDesc", flat=True).order_by("groupDesc"))
    return JsonResponse({"groups": data})


@extend_schema(description=settings.API_ENDPOINT_DESCRIPTIONS.get("prodgroups", ""))
class GroupDescListAPI(generics.ListAPIView):
    queryset = GroupDescView.objects.all().order_by("groupDesc")
    serializer_class = GroupDescSerializer


def sub_group_desc_list(request):
    """Return a JSON list of all distinct product sub-group descriptions.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        JsonResponse: A JSON object with a 'subgroups' key containing a sorted
            list of all distinct subGroupDesc values from GroupDescView.
    """
    data = list(GroupDescView.objects.values_list("subGroupDesc", flat=True).order_by("subGroupDesc"))
    return JsonResponse({"subgroups": data})


@extend_schema(description=settings.API_ENDPOINT_DESCRIPTIONS.get("prodsubgroups", ""))
class SubGroupDescListAPI(generics.ListAPIView):
    queryset = SubGroupDescView.objects.all().order_by("subGroupDesc")
    serializer_class = SubGroupDescSerializer


def ranges_list(request):
    """Return a JSON list of all distinct product range names.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        JsonResponse: A JSON object with a 'ranges' key containing a sorted
            list of all distinct rangeName values from RangeNameView.
    """
    data = list(RangeNameView.objects.values_list("rangeName", flat=True).order_by("rangeName"))
    return JsonResponse({"ranges": data})


@extend_schema(description=settings.API_ENDPOINT_DESCRIPTIONS.get("ranges", ""))
class RangeNameListAPI(generics.ListAPIView):
    queryset = RangeNameView.objects.all().order_by("rangeName")
    serializer_class = RangeNameSerializer
