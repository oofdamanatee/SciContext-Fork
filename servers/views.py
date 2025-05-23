""" servers view file """
from django.shortcuts import render, redirect
from rdflib.extras.infixowl import Ontology

from config.functions import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime
from .forms import ServerAddForm


# Create your views here.
def index(request):
    """ view to generate a list of ontology servers """
    servers = getsvrs()
    return render(request, "servers/index.html", {'servers': servers})


def view(request, svrid):
    """view to show all data about an ontology server"""
    server = getsvr(svrid)
    return render(request, "servers/view.html", {'server': server})


def add(request):
    # add a server
    if request.method == "POST":
        # save new namespace
        form = ServerAddForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            for key in data.keys():  # only expecting single values for each field
                if data[key]:
                    if data[key][0] == '':
                        data[key][0] = None
                else:
                    data[key] = None
            s = Servers(
                name=data['name'],
                abbrev=data['abbrev'],
                description=data['desc'],
                homepage=data['home'],
                apiurl=data['apiurl'],
                apikey=data['apikey'],
                version=data['version'],
                type=data['type'],
                updated=datetime.now()
            )
            s.save()
            return redirect('/servers/')
    else:
        form = ServerAddForm

    return render(request, "servers/add.html", {"form": form})


# JavaScript AJAX functions


@csrf_exempt
def svrget(request, svrid):
    # get the current list of ontologies on server
    sonts = svronts(svrid)
    return JsonResponse(sonts, safe=False, status=200)


@csrf_exempt
def ontupd(request, svrid):
    # load DB with a list of ontologies from a server
    svr = Servers.objects.get(id=svrid)
    if svr.type == "ols":
        onts = olsonts(svrid)
        if onts:
            for ns, ont in enumerate(onts):
                found = Onts.objects.filter(ns=ns)

    else:
        pass

    return redirect('/servers/view/' + str(svrid))


@csrf_exempt
def updontcnt(request, svrid):
    onts = svronts(svrid)
    output = []
    for ont in onts:
        o = Onts.objects.get(ns=ont['ns'], server_id=svrid)
        o.trmcnt = ont['trmcnt']
        o.save()
        ostr = ont['ns'] + " updated"
        output.append(ostr)
    return JsonResponse(output, safe=False, status=200)


@csrf_exempt
def updontvrs(request, svrid):
    onts = svronts(svrid)
    output = []
    for ont in onts:
        o = Onts.objects.get(ns=ont['ns'], server_id=svrid)
        o.version = ont['version']
        o.updated = datetime.now()
        o.save()
        ostr = ont['ns'] + " updated"
        output.append(ostr)
    return JsonResponse(output, safe=False, status=200)
