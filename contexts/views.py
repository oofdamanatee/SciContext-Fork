from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from config.functions import *
from config.langs import *
from datetime import datetime
from collections import OrderedDict
from config.settings import *
from config.git_functions import *
from .forms import ContextAddForm
import os


def home(request):
    ctxcnt = Contexts.objects.all().count()
    return render(request, "home.html", {'ctxcnt': ctxcnt})

def tutorial(request):
    return render(request, "tutorial.html")

def index(request):
    ctxs = getctxs()
    return render(request, "contexts/index.html", {'ctxs': ctxs})


def view(request, ctxid):
    # get context
    ctx = getctx(ctxid)
    if ctx.subcontexts is not None:
        subids = ctx.subcontexts.split(',')
        ctxs = lstctxs(subids)
    else:
        subids = None
        ctxs = None
    # get fields assigned to this context
    fldids = ctx.contextsfields_set.filter(context_id=ctxid).values_list('field_id', flat=True)
    flds = Fields.objects.filter(id__in=fldids)
    # get the current list of terms to populate the dropdown
    trms = gettrms()
    # check if the context file is already on GitHub
    ctxup = None
    code = wpexists(ctx.url)
    if code is not None:
        ctxup = "yes"
    return render(request, "contexts/view.html", {'context': ctx, 'fields': flds, 'trms': trms,
                                                  'ctxs': ctxs, 'subids': subids, 'act': 'Add', 'ctxup': ctxup})


def add(request):
    """view to add data about a context"""
    if request.method == "POST":
        # save new namespace
        data = request.POST
        ctx = Contexts()
        ctx.name = data['name']
        ctx.description = data['description']
        ctx.filename = data['filename']
        if data['prjid']:
            ctx.project_id = data['prjid']
        else:
            ctx.project_id = None
        ctx.version = data['version']
        ctx.vocab = data['vocab']
        ctx.language = data['lang']
        temp = list(data.getlist('subctxs'))
        if temp != "":
            ctx.subcontexts = ','.join(temp)  # bizarre syntax, but it works!
        else:
            ctx.subcontexts = None
        # get the project prefix if there is one
        pre = ''
        if ctx.project_id:
            pre = ctx.project.prefix + '_'
        # get GitHub repo URL
        rurl = getgiturl()
        parts = rurl.split('/')
        usr, repo = parts[3], parts[4].replace('.git', '')
        # create context file URL
        url = 'https://' + usr + '.github.io/' + repo + '/ctxs/' + pre + ctx.filename + '.jsonld'
        ctx.url = url
        # save context
        ctx.updated = datetime.now()
        ctx.save()
        return redirect('/contexts/view/' + str(ctx.id))
    else:
        form = ContextAddForm

    ctxs = getctxs()
    prjs = getprjs()
    # load languages from config/langs.py (lang variable)
    return render(request, "contexts/add.html", {'ctxs': ctxs, 'prjs': prjs, 'langs': langs, 'form': form})


# ajax functions (wrappers)


@csrf_exempt
def terms(request, ontid):
    termz = getont(ontid)
    return JsonResponse({"terms": termz}, status=200)


@csrf_exempt
def jsfldadd(request):
    fld = None
    if request.method == "POST":
        data = request.POST
        fldid = data['fldid']
        ctxid = data['ctxid']
        # check if the field exists (assume context does)
        fld = Fields.objects.get(id=fldid)
        if not fld:
            fld = Fields()
            fld.name = data['name']
            fld.datatype = data['datatype']
            fld.cardinality = data['card']
        fld.save()
        # create the join table entry
        cf = ContextsFields()
        cf.field_id = fldid
        cf.context_id = ctxid
    return JsonResponse(model_to_dict(fld), status=200)


@csrf_exempt
def jsdelcwk(request):
    response = {}
    if request.method == "POST":
        data = request.POST
        cwkid = data['cwkid']
        Fields.objects.get(id=cwkid).delete()
        try:
            Fields.objects.get(id=cwkid)
            response.update({"response": "failure"})
        except Fields.DoesNotExist:
            response.update({"response": "success"})
    return JsonResponse(response, status=200)


@csrf_exempt
def jscwkread(request, cwkid=""):
    cwk = Fields.objects.get(id=cwkid)
    return JsonResponse(model_to_dict(cwk), status=200)


@csrf_exempt
def jswrtctx(request, ctxid: int):
    ctx = Contexts.objects.get(id=ctxid)
    tpl = '{"@vocab": "' + ctx.vocab + '"}'
    cdict = json.loads(tpl)
    nss = {}
    # add namespaces
    for cfjoin in ctx.contextsfields_set.all():
        ns = cfjoin.field.term.ont.ns
        if '.owl' in cfjoin.field.term.ont.path:
            path = cfjoin.field.term.ont.path + '#'
        else:
            path = cfjoin.field.term.ont.path
        nss.update({ns: path})
    srtd = OrderedDict(sorted(dict.items(nss)))
    for key in srtd.keys():
        cdict.update({key: nss[key]})
    # add entries
    for cfjoin in ctx.contextsfields_set.all():
        tmp = {}
        shortiri = cfjoin.field.term.ont.ns + ':' + cfjoin.field.term.code
        dtype = cfjoin.field.datatype
        if cfjoin.field.datatype == '@list':
            tmp.update({"@id": shortiri, "@type": dtype, "@container": "@list"})
        else:
            tmp.update({"@id": shortiri, "@type": dtype})
        cdict.update({cfjoin.field.name: tmp})
    jld = {"@context": cdict}
    # check for being part of a project
    fpath = 'ctxs/'
    if ctx.project_id:
        fpath += ctx.project.prefix + '_'
    fpath += ctx.filename + '.jsonld'
    jsn = json.dumps(jld, separators=(',', ':'))
    # save local
    os.makedirs(os.path.dirname(BASE_DIR + '/ctxs/'), exist_ok=True)  # create a directory if not exist
    with open(fpath, "w") as f:
        f.write(jsn)
    f.close()
    # save on GitHub
    resp = addctxfile(fpath, 'commit via API ' + str(datetime.now()), jsn)
    return JsonResponse({"response": resp}, status=200)
