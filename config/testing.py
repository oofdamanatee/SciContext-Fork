import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
# from config.models import *
from config.olsapi import *

# onts = Onts.objects.all()
# for ont in onts:
#     # Adding data using the through model
#     ontid = Onts.objects.get(pk=ont.id)
#     svrid = Servers.objects.get(pk=ont.server_id)
#     added = OntsServers.objects.create(ontid=ontid, svrid=svrid)
#     print("added " + str(ont.id) + ":" + str(svrid))


olist = getonts(1, True)
print(json.dumps(olist, indent=4))
