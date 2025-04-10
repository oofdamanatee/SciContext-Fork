""" functions for the OLS ontology servers"""
from config.models import *
from ols_py.client import *


def svronts(svrid):
    # get the list of ontologies in this server
    svr = Servers.objects.get(id=svrid)
    olist = []
    # what type of server?
    if svr.type == 'ols':
        client = Ols4Client(svr.apiurl)
        resp = client.get_ontologies(0, 300)
        onts = resp.embedded.ontologies
        for ont in onts:
            meta = ont.config
            # ontologyID is used as the pk for the ontology
            olist.append({'ns': ont.ontologyId, 'title': str(meta['title']).strip(), 'description': meta['description'],
                          'path': meta['fileLocation'], 'homepage': meta['homepage'], 'trmcnt': ont.numberOfTerms,
                          'version': ont.version})
    else:
        pass
    return olist


def svronttrms(svrid, ontid):
    # get terms in ontology (ontns) on server (svrid)
    svr = Servers.objects.get(id=svrid)
    ont = Onts.objects.get(id=ontid)
    tlist = []
    if svr.type == 'ols':
        client = Ols4Client(svr.apiurl)
        resp = client.get_terms(ont.ns, params=)
        terms = resp.embedded.terms
        for term in terms:
            desc = None
            if term.description:
                desc = term.description[0]
            tlist.append({'title': term.label, 'code': term.ontology_name,
                          'description': desc, 'visible': 'yes', 'ontid': ontid})
    else:
        pass
    return tlist


def svrsearch(svrid, query):
    # search for terms in server (svrid)
    svr = Servers.objects.get(id=svrid)
    results = []
    if svr.type == 'ols':
        client = Ols4Client(svr.apiurl)
        # local = true indicates that the term is defined in the current ontology (not reused)
        resp = client.search(query,  params={"exact": 'true', "local": 'true'})
        hits = resp.response.docs
        for hit in hits:
            # only get terms where the title is exact (exact above searched more than the title)
            title = hit.label.replace('_', ' ').lower()
            if query.lower() != title:
                continue
            # check to see if this term has already been added to the DB
            found = Terms.objects.filter(code=hit.short_form)
            local = 'no'
            if found:
                local = 'yes'
            desc = ''
            if hit.description:
                desc = hit.description[0]
            results.append({'ns': hit.ontology_name, 'code': hit.short_form, 'title': hit.label,
                            'defn': desc, 'iri': hit.iri, 'type': hit.type, 'local': local})
    else:
        pass
    return results
