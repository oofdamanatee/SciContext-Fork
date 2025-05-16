""" terms view file """
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from config.functions import *
import json
import urllib.error
import urllib.parse
import urllib.request


# Create your views here.
def index(request):
    """ view to generate a list of namespaces """
    termz = gettrms()
    return render(request, "terms/index.html", {'terms': termz})


def view(request, trmid):
    """view to show all data about an ont term"""
    term = gettrm(trmid)
    nsiri = term.ont.ns + ':' + term.code
    flds = term.fields_set.all()
    return render(request, "terms/view.html", {'term': term, 'nsiri': nsiri, 'flds': flds})


def add(request):
    """add a term or create a page so a user can do that"""
    if request.method == "POST":
        # save new term
        data = request.POST
        term = Terms()
        term.title = data['title']
        term.definition = data['definition']
        term.code = data['code']
        if data['ns'].isnumeric():  # ns is an integer (as a string) if the term is from a local ontology
            ont = Onts.objects.get(id=data['ns'])
        else:
            ont = Onts.objects.get(ns=data['ns'], server_id=data['svrid'])  # ns is the text code for the ontology
        term.ont_id = ont.id
        term.iri = ont.url + '#' + data['code']
        term.updated = datetime.now()
        term.save()
        return redirect('/terms/')

    svrs = Servers.objects.all()
    # gets all ontologies that have been added locally
    ontids = OntsServers.objects.filter(svrid=None).values_list('ontid', flat=True)
    onts = Onts.objects.filter(id__in=ontids)
    return render(request, "terms/add.html", {'svrs': svrs, 'onts': onts})


@csrf_exempt
def byont(request, svrid, ontid):
    svr = Servers.objects.get(id=svrid)
    with urllib.request.urlopen(svr.apiurl + 'ontologies/' + ontid + '/terms?size=500') as url:
        data = json.loads(url.read().decode())
    terms = data['_embedded']['terms']
    tlist = []
    for term in terms:
        tlist.append({"label": term['label'], "code": term['short_form']})
    return JsonResponse(tlist, safe=False, status=200)


@csrf_exempt
def trmsrc(request, svrid, srcstr):
    # remove any URL encoding in the incoming search string
    srcstr = urllib.parse.unquote(srcstr)
    # search the OLS server
    output = svrsearch(svrid, srcstr)
    # sort the results by title
    out2 = sorted(output, key=lambda d: d['title'])
    return JsonResponse(out2, safe=False, status=200)
