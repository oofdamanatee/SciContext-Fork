""" functions for the OLS ontology servers"""
from config.models import *
from datetime import datetime as dt
from config.settings import BASE_DIR
import requests
import json
import os


# call the OLS API endpoint
def olsapi(epnt,svrid,ontid=None,cls=None):
    # OLS endpoints
    svr = Servers.objects.get(id=svrid)
    data = {}
    if svr.type == 'ols':
        epnts = ['classes','onts','class','ont','nss']
        api = svr.apiurl
        page, size = 0, 1000
        now = dt.now()
        dts = now.strftime("%d%m%y")
        if epnt in epnts:
            # API functions to retrieve data
            if epnt == 'classes':
                # get a list of the classes in an ontology
                path = '/v2/ontologies/{ns}/classes'
                opts = '?page=0&size=20&lang=en&exactMatch=false&includeObsoleteEntities=false'
                pass
            elif epnt == 'onts':
                # get a list of the ontologies on a server
                # API Documentation: https://www.ebi.ac.uk/ols4/swagger-ui/index.html#/Ontology%20Controller/getOntologies_1
                path = 'ontologies'
                opts = '?lang=en&page={page}&size={size}'

                # has the data been downloaded today?
                jdict = {}
                fpath = str(BASE_DIR) + '/static/data/ontsfull_' + str(svrid) + '_' + dts + ".json"
                if not os.path.exists(fpath):
                    # call OLS server to get the data
                    url = api + path + opts.replace('{page}', str(page)).replace('{size}', str(size))
                    req = requests.get(url)
                    jdict = req.json()
                    # save file if not already saved today
                    full = json.dumps(jdict, indent=4)
                    with open(fpath, "w") as outfile:
                        outfile.write(full)
                else:
                    # read file
                    with open(fpath, "r") as outfile:
                        jdict = json.load(outfile)

                # create summary data file
                data = {}
                for ont in jdict['_embedded']['ontologies']:
                    if ont['numberOfTerms'] == 0:
                        continue
                    if ont['config']['title'] is None:
                        ont['config']['title'] = ont['ontologyId']
                    if 'languages' not in ont.keys():
                        ont['languages'] = ""
                    if ont['config']['fileLocation'] is not None:
                        if 'file:' in ont['config']['fileLocation']:
                            ont['config']['fileLocation'] = ''
                    data.update({ont['ontologyId']: {
                        'name': ont['config']['title'],
                        'url': ont['config']['fileLocation'],
                        'verurl': ont['config']['versionIri'],
                        'homepage': ont['config']['homepage'],
                        'description': ont['config']['description'],
                        'version': ont['config']['version'],
                        'langs': ",".join(ont['languages']),
                        'classes': ont['numberOfTerms'],
                        'properties': ont['numberOfProperties'],
                        'individuals': ont['numberOfIndividuals']
                    }})
                file = json.dumps(data, indent=4)
                fname = 'onts_' + str(svrid) + '_' + dts + ".json"
                with open(str(BASE_DIR) + "/static/data/" + fname, "w") as outfile:
                    outfile.write(file)
            elif epnt == 'class':
                # get information about a class in an ontology
                # URL must be URL encoded to create the request URL
                # example: https://www.ebi.ac.uk/ols4/api/v2/ontologies/chmo/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FCHMO_0000169?lang=en
                # API Documentation: https://www.ebi.ac.uk/ols4/swagger-ui/index.html#/V2%20Class%20Controller/getClass
                path = '/v2/ontologies/{ns}/classes/{classURI}'
                opts = '?lang=en'

                pass
            elif epnt == 'ont':
                # get the terms for an ontology (static URL call?)
                pass
            elif epnt == 'nss':
                # get a list of namespaces on a server
                path = '/v2/ontologies/{ns}/classes'
                opts = '?page=0&size=20&lang=en&exactMatch=false&includeObsoleteEntities=false'
                pass
        else:
            data = {'error': 'not an ols endpoint'}
    else:
        data = {'error': 'not an ols server'}
    return data


# get a list (list of dictionaries) of ontologies on an OLS server
def olsonts(svrid):
    # call the OLS API and return the list of ontologies
    olist = olsapi('onts', svrid)
    return olist


def olsonttrms(svrid, ontid):
    # get terms in ontology (ontns) on server (svrid)
    pass
    # svr = Servers.objects.get(id=svrid)
    # ont = Onts.objects.get(id=ontid)
    # # ping the OLS API
    # client = Ols4Client(svr.apiurl)
    # tlist, page = [], 0
    # ns = ont.ns
    # resp = client.get_terms(ns)
    # terms = resp.embedded.terms
    # for term in terms:
    #     desc = None
    #     if term.description:
    #         desc = term.description[0]
    #     tlist.append({'title': term.label, 'code': term.ontology_name, 'description': desc, 'visible': 'yes', 'ontid': ontid})
    # return tlist


def olssearch(svrid, query):
    # search for terms in server (svrid)
    pass
    # svr = Servers.objects.get(id=svrid)
    # results = []
    # if svr.type == 'ols':
    #     client = Ols4Client(svr.apiurl)
    #     # local = true indicates that the term is defined in the current ontology (not reused)
    #     resp = client.search(query)
    #     hits = resp.response.docs
    #     for hit in hits:
    #         # only get terms where the title is exact (exact above searched more than the title)
    #         title = hit.label.replace('_', ' ').lower()
    #         if query.lower() != title:
    #             continue
    #         # check to see if this term has already been added to the DB
    #         found = Terms.objects.filter(code=hit.short_form)
    #         local = 'no'
    #         if found:
    #             local = 'yes'
    #         desc = ''
    #         if hit.description:
    #             desc = hit.description[0]
    #         results.append({'ns': hit.ontology_name, 'code': hit.short_form, 'title': hit.label,
    #                         'defn': desc, 'iri': hit.iri, 'type': hit.type, 'local': local})
    # else:
    #     pass
    # return results
