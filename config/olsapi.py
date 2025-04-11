""" OLS API functions based on v4 of OLS (https://www.ebi.ac.uk/ols4/help) """
from config.models import *
import requests
import json
from datetime import datetime
from pytz import timezone

tz = timezone("America/New_York")

indep = "individuals"
ontep = "ontologies"
clsep = "classes"

# missing names from OLS servers...
ontnames = {
    "evorao": "European Viral Outbreak Response Alliance Ontology",
    "unitprotrdfs": "UniProt RDF Schema Ontology",
    "dcat": "The Data Catalog Ontology",
    "biolink": "Biolink-Model",
    "oio": "OBO Format Metamodel Ontology",
    "skos": "Simple Knowledge Organization System Vocabulary",
    "dcterms": "Dublin Core DCMI Metadata Terms",
    "dc": "Dublin Core Metadata Element Set",
    "schemaorg_http": "Schema.org Ontology (HTTP)",
    "schemaorg_https": "Schema.org Ontology (HTTPS)"
}


# get a list of ontologies from an OLS server
def getonts(svrid, upd=False):
    svr = Servers.objects.get(id=svrid)
    apiep = svr.apiurl + ontep + "?lang=en&page=0&size=300"
    resp = requests.get(url=apiep)
    jsn = resp.json()
    onts = jsn['_embedded']['ontologies']
    olist = {}
    temp = {}
    for ont in onts:
        config = ont['config']
        if config['title'] is None:
            if ont['ontologyId'] in ontnames.keys():
                config['title'] = ontnames[ont['ontologyId']]
            else:
                config['title'] = ont['ontologyId']
        # add/update to the onts table
        if upd:
            found = Onts.objects.get(ns=ont['ontologyId'])
            if found:
                found.version = ont['version']
                found.langs = ", ".join(ont['languages'])
                found.trmcnt = ont['numberOfTerms']
                found.updated = datetime.now(tz)
                found.save()
            else:
                newont = Onts.objects.create(
                    name=config['title'], ns=ont['ontologyId'], path=ont['fileLocation'], homepage=config['homepage'],
                    description=config['description'], trmcnt=ont['numberOfTerms'], version=ont['version'],
                    langs=", ".join(ont['languages']), updated=datetime.now(tz)
                )
                newont.save()
        # create output json
        olist.update({ont['ontologyId']: config['title']})
        temp = dict(sorted(olist.items(), key=lambda item: str(item[1].lower())))
    return temp
