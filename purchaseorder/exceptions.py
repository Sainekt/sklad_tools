from django.shortcuts import render


def ratelimited_error(request, exception):
    redirect_url = request.META.get('HTTP_REFERER')

    if not redirect_url:
        redirect_url = '/'

    context = {
        'redirect_url': redirect_url,
    }
    return render(request, 'handlers/ratelimited.html', context, status=429)
