from django.shortcuts import render,redirect
from .models import *
from .forms import *
from django.http import HttpResponseRedirect

# Create your views here.

def activate(request,address_id):
    addresses = UserAddressBook.objects.filter(user = request.user)
    for add in addresses:
        add.status = False
        add.save()
    
    active_address = UserAddressBook.objects.get(id = address_id)
    active_address.status = True
    active_address.save()

    ref = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(ref)


def add_address(request):
    referring_url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        form = UserAddressForm(request.POST)
        ref = request.POST['referring_url']

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return HttpResponseRedirect(ref)
    form = UserAddressForm()
    context = {
        'form':form,
        'referring_url' : referring_url

    }
    return render(request, 'addressbook/addressform.html',context)



def edit_address(request, address_id):
    address = UserAddressBook.objects.get(id = address_id, user= request.user)
    referring_url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        ref = request.POST['referring_url']
        form = UserAddressForm(request.POST, instance = address)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(ref)

    form = UserAddressForm(instance = address)


    context = {
        'form': form,
        'referring_url' : referring_url
    }

    return render(request, "addressbook/addressform.html", context)