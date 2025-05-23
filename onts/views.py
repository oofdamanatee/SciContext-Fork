""" onts view file """
from io import BytesIO

from django.shortcuts import render, redirect
from django.template.defaultfilters import title

from config.functions import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from config.ols_functions import *
from rdflib import Graph, OWL, RDF
from datetime import datetime
import requests

def index(request):
    """ view to generate a list of namespaces """
    onts = getonts()
    return render(request, "onts/index.html", {'onts': onts})


def view(request, ontid):
    """view to show all data about a namespace"""
    ont = getont(ontid)
    cons = getcons(ontid)
    if not cons:
        # TODO!
        # no terms loaded, so get a list from the server
        tmp = ont.ontsservers_set.all()[0]
        tmpid = tmp.svrid_id
        svr = Servers.objects.get(id=tmpid)
        if svr.type == 'ols':
            trms = olsonttrms(svr.id, ontid)
            # add to the concepts table
            for trm in trms:
                con = Concepts(
                    title=trm.title,
                    ont_id=ontid,
                    updated=datetime.now()
                )
                con.save()
        loaded = 'no'
    else:
        loaded = 'yes'

    return render(request, "onts/view.html", {'ont': ont, 'cons': cons, 'loaded': loaded})


def add(request):
    """add a new ontology"""
    if request.method == "POST":
        # save new namespace
        data = request.POST
        o = Onts()
        o.name = data['name']
        o.ns = data['alias']
        o.url = data['url']
        o.homepage = data['homepage']
        o.server_id = data['svrid']
        o.save()
        return redirect('/onts/')

    aliases = ontaliases()
    svrs = Servers.objects.all().values_list('id', 'name').order_by('name')
    oonts = allonts()  # list of tuples (four values)
    # oonts.sorted(key=lambda tup: tup[1])
    return render(request, "onts/add.html", {'aliases': aliases, 'onts': oonts, 'svrs': svrs})


# JavaScript functions


@csrf_exempt
def ontget(request, svrid, ontid):
    # get the current list of ontologies on server
    svr = Servers.objects.get(id=svrid)
    trms = []
    if svr.type == 'ols':
        trms = olsonttrms(svrid, ontid)
    elif svr.type == 'onto':
        # TODO: add code!
        pass
    return JsonResponse(trms, safe=False, status=200)


@csrf_exempt
def ontupd(request, svrid, ontid):
    # load DB with a list of terms in an ontology (from a specific server) into concepts
    ontload(svrid, ontid)
    if is_ajax(request):
        return "success"
    else:
        return redirect('/onts/view/' + str(ontid))


@csrf_exempt
def bysvr(request, svrid):
    # get a list of ontologies on a server
    ontlist = svronts(svrid)
    return JsonResponse(ontlist, safe=False, status=200)


@csrf_exempt
def getlocal(request, ontid):
    ont = getont(ontid)
    file = requests.get(ont.url)
    g = Graph()
    # find all classes (subjects) and properties (relationships)
    classes = []
    if ont.url.find('ttl') != -1:
        g.parse(BytesIO(file.content), format='turtle')
        for subj, obj in g.subject_objects(predicate=RDF.type):
            if obj == OWL.ObjectProperty or obj == OWL.Class:
                if str(subj).find('http') != -1:
                    classes.append(subj)
    # iterate to get labels and description (comment etc.)
    for cls in classes:
        chunks = cls.split('/')
        sub = chunks[-1]
        con, created = Concepts.objects.get_or_create(
            name=sub,
            ont_id=ontid
        )
        con.updated = datetime.now()
        con.save()
    # update the ontology for this last time this update was done
    ont.lastconupd = datetime.now()
    ont.save()
    return "success"
