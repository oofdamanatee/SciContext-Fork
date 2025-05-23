""" OLS API functions based on v4 of OLS (https://www.ebi.ac.uk/ols4/help) """
""" may be obsolete due to API work in ols_functions SJC 05/22/25 """
from config.models import *
import requests
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
            found = Onts.objects.filter(ns=ont['ontologyId'])
            if found:
                upd = found[0]
                upd.trmcnt = ont['numberOfTerms']
                upd.updated = datetime.now(tz)
                upd.save()
                print("found " + ont['ontologyId'] + " in the database")
                # check if there is a join for this ontology
                langs = None
                if 'languages' in ont.keys():
                    langs = ", ".join(ont['languages'])
                found2 = OntsServers.objects.filter(ontid=upd, svrid=svrid)
                if found2:
                    # update server-specific info in the join table
                    found2[0].langs = langs
                    found2[0].version = ont['version']
                    found2[0].save()
                    print("updated join table for " + ont['ontologyId'])
                else:
                    # add join to onts_servers
                    newos = OntsServers.objects.create(
                        svrid=svr, ontid=upd, langs=langs, version=ont['version']
                    )
                    newos.save()
                    print("added join for ontology " + ont['ontologyId'])

            else:
                langs = None
                if 'fileLocation' not in ont.keys():
                    ont['fileLocation'] = None
                if 'languages' not in ont.keys():
                    ont['languages'] = None
                else:
                    langs = ", ".join(ont['languages'])

                # add ontology to onts table
                newont = Onts.objects.create(
                    name=config['title'], ns=ont['ontologyId'], path=ont['fileLocation'], homepage=config['homepage'],
                    description=config['description'], trmcnt=ont['numberOfTerms'], updated=datetime.now(tz)
                )
                newont.save()
                print("added " + ont['ontologyId'] + " to the database")

                # add join to onts_servers
                newos = OntsServers.objects.create(
                    svrid=svr, ontid=newont, langs=langs, version=ont['version']
                )
                newos.save()
                print("added join for ontology " + ont['ontologyId'])

        # create output json
        olist.update({ont['ontologyId']: config['title']})
        temp = dict(sorted(olist.items(), key=lambda item: str(item[1].lower())))
    return temp
