from django.urls import reverse 
from django.shortcuts import get_object_or_404, redirect 
from .models import Course


def subdomain_middleware(get_response):
    def middleware(request):
        host_parts = request.get_host().split('.')
        if len(host_parts) > 2 and host_parts[0] != 'www':
            course = get_object_or_404(Course, slug=host_parts[0])
            c_url = reverse('course_detail', args=[course.slug])
            url = f"{request.scheme}://{''.join(host_parts[2:])}{c_url}"
            return redirect(url)
        r = get_response(request)
        return r
    return middleware