from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent
from pyretic.pyresonance.smv.translate import *

from pyretic.pyresonance.apps.ids import *
from pyretic.pyresonance.apps.mac_learner import *


#####################################################################################################
# App launch
#  - pyretic.py pyretic.pyresonance.apps.ids_maclearn
#
# Mininet Generation
#  - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --topo=single,3
#
# Events to block traffic "h1 ping h2"
#  - python json_sender.py -n infected -l True --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001}
#
# Events to again allow traffic "h1 ping h2"
#  - python json_sender.py -n infected -l False --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001}
#####################################################################################################


def main():

    pol1 = ids()
    pol2 = mac_learner()
    
    return pol1 >> pol2
