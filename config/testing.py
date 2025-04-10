import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from config.models import *


# onts = Onts.objects.all()
# for ont in onts:
#     # Adding data using the through model
#     ontid = Onts.objects.get(pk=ont.id)
#     svrid = Servers.objects.get(pk=ont.server_id)
#     added = OntsServers.objects.create(ontid=ontid, svrid=svrid)
#     print("added " + str(ont.id) + ":" + str(svrid))

ont = Onts.objects.get(id=264)
svrs = ont.servers.all()
print(svrs)
