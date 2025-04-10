""" functions for the OntoPortal ontology servers"""
from config.models import *
from ontoportal_client import *
from dotenv import load_dotenv  # package is python-dotnev


load_dotenv()


def svronts(svrid):
    # get the list of ontologies in this server
    svr = Servers.objects.get(id=svrid)
    olist = []
    # what type of server?
    if svr.type == 'onto':
        # chooise which server
        if svr.name == "BioPortal":
            client = BioPortalClient(svr.apikey)
        elif svr.name == "AgriPortal":
            client = AgroPortalClient(svr.apikey)
        else:
            client = OntoPortalClient(svr.apikey)

        onts = client.get_ontologies()
        for ont in onts:
            # ontologyID is used as the pk for the ontology
            olist.append({'ns': ont['acronym'].lower(), 'title': ont['name']})
    else:
        pass
    return olist
