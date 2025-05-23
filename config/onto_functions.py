""" functions for the OntoPortal ontology servers"""
from config.models import *
from dotenv import load_dotenv  # package is python-dotnev
from datetime import datetime as dt
from config.settings import BASE_DIR
import requests
import json
import os

load_dotenv()


def ontoapi(epnt,svrid,ontid=None,cls=None):
    svr = Servers.objects.get(id=svrid)
    data = {}
    if svr.type == 'onto':
        epnts = ['classes', 'onts', 'class', 'ont', 'nss']
        api = svr.apiurl
        key = svr.apikey
        # page, size = 0, 1300
        now = dt.now()
        dts = now.strftime("%d%m%y")
        if epnt in epnts:
            # API functions to retrieve data on Ontoportal servers
            if epnt == 'classes':
                # get a list of the classes in an ontology
                # path = '{ns}/classes'
                # opts = ''
                pass
            elif epnt == 'onts':
                # get a list of the ontologies on a server
                # API Documentation: https://data.bioontology.org/documentation
                path = 'ontologies_full'
                opts = '?apikey={key}'
                url = api + path + opts.replace('{key}', key)
                req = requests.get(url)
                jdict = req.json()
                # save full ontology dump for later processing
                full = json.dumps(jdict, indent=4)
                fpath = str(BASE_DIR) + '/static/data/ontsfull_' + str(svrid) + '_' + dts + ".json"
                if not os.path.exists(fpath):
                    print("Saving a copy of the file")
                    print(url)
                    # save file if not already saved today
                    with open(fpath, "w") as outfile:
                        outfile.write(full)
                # create summary data file
                data = {}
                cnt = 1
                maxv = 1300
                for ont in jdict:
                    # initial data
                    odict = {}
                    odict.update({'name': ont['ontology']['name']})
                    # get URL to ontology (from either 'homepage' or 'documentation')
                    if ont['latest_submission'] is not None:
                        # get ontology url (there is not an obvious field with this information)
                        odict.update({'url': ''})
                        # get ontology version url (good?)
                        if ont['latest_submission']['documentation'] is not None:
                            odict.update({'verurl': ont['latest_submission']['documentation']})
                        else:
                            odict.update({'verurl': ''})
                        # get ontology homepage
                        if ont['latest_submission']['homepage'] is not None:
                            odict.update({'homepage': ont['latest_submission']['homepage']})
                        else:
                            odict.update({'homepage': ''})
                        # get ontology description
                        odict.update({'description': ont['latest_submission']['description']})
                        # get ontology version
                        odict.update({'version': ont['latest_submission']['version']})
                    else:
                        # get ontology url (there is not an obvious field with this information)
                        odict.update({'url': None})
                        odict.update({'verurl': None})
                        odict.update({'homepage': None})
                        odict.update({'description': None})
                        odict.update({'version': None})
                    # get ontology langauges (they are primarily available in english)
                    # TODO: how to get supported languages?
                    odict.update({'langs': 'en'})
                    # check for 'metrics' are available
                    if ont['metrics'] is not None:
                        # get ontology classes
                        odict.update({'classes': ont['metrics']['classes']})
                        # get ontology properties
                        odict.update({'properties': ont['metrics']['properties']})
                        # get ontology individuals
                        odict.update({'individuals': ont['metrics']['individuals']})
                    else:
                        odict.update({'classes': None})
                        odict.update({'properties': None})
                        odict.update({'individuals': None})
                    # add to data
                    data.update({ont['ontology']['acronym'].lower(): odict})
                    if cnt == maxv:
                        break
                    else:
                        cnt += 1
                file = json.dumps(data, indent=4)
                fname = 'onts_' + str(svrid) + '_' + dts + ".json"
                with open(str(BASE_DIR) + "/static/data/" + fname, "w") as outfile:
                    outfile.write(file)
            elif epnt == 'class':
                # get information about a class in an ontology
                pass
            elif epnt == 'ont':
                # get the terms for an ontology (static URL call?)
                pass
            elif epnt == 'nss':
                # get a list of namespaces on a server
                pass

    else:
        data = {'error': 'not an ontoportal server'}
    return data


def svronts(svrid):
    # get the list of ontologies in this server
    svr = Servers.objects.get(id=svrid)
    olist = []
    # what type of server?
    if svr.type == 'onto':
        # choose which server
        client = None
        if svr.name == "BioPortal":
            client = BioPortalClient(svr.apikey)
        elif svr.name == "AgriPortal":
            client = AgroPortalClient(svr.apikey)

        onts = client.get_ontologies()
        for ont in onts:
            # ontologyID is used as the pk for the ontology
            olist.append({'ns': ont['acronym'].lower(), 'title': ont['name']})
    else:
        pass
    return olist
