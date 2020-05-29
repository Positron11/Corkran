from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def lounge_index(request):
    return render(request, 'Lounge/lounge_index.html')

@login_required
def lounge(request, room_name):
    return render(request, 'Lounge/lounge.html', {'room_name': room_name})
