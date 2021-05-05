from django.shortcuts import render


def custom_bad_request_view(request, exception=None):
    return render(request, "pages/error/bad_request.html", {})


def custom_error_404_view(request, exception=None):
    data = {"name": "ThePythonDjango.com"}
    return render(request, 'pages/error/error_404.html', data)
