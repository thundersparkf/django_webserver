from django.shortcuts import render
from lockdown.decorators import lockdown
# Create your views here.
@lockdown()
def index(request):  

    return render(request, 'chat_test/index.html')