
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent
from pyretic.pyresonance.smv.translate import *


class sf(DynamicPolicy):
    def __init__(self,internal_hosts,ih_prd):

       ### DEFINE THE LPEC FUNCTION

        def lpec(f):
            hosts = list()
            internal_h = None
            external_h = None

            hosts.append(f['srcip'])
            hosts.append(f['dstip'])

            for host in hosts:
                if host in internal_hosts:
                    internal_h = host
                else:
                    external_h = host
                
            if internal_h is None or external_h is None:
                return None

            return (match(srcip=internal_h,dstip=external_h) |
                    match(srcip=external_h,dstip=internal_h) )

        ## SET UP TRANSITION FUNCTIONS

        def policy_trans(state):
            if state['outgoing']:
                return identity
            else:
                return ih_prd

        ### SET UP THE FSM DESCRIPTION

        self.fsm_description = FSMDescription(
            outgoing=VarDesc(type=bool, 
                             init=False, 
                             exogenous=True),
            policy=VarDesc(type=[identity,ih_prd],
                           init=ih_prd,
                           endogenous=policy_trans))

        ### DEFINE QUERY CALLBACKS

        def q_callback(pkt):
            src = pkt['srcip']
            dst = pkt['dstip']
            flow = frozendict(srcip=src,dstip=dst)
            return fsm_pol.event_handler(Event('outgoing',True,flow))

        ### SET UP POLICY AND EVENT STREAMS

        fsm_pol = FSMPolicy(lpec,self.fsm_description)
        q = FwdBucket()
        q.register_callback(q_callback)

        super(sf,self).__init__(fsm_pol + (ih_prd >> q))


def main():
    internal_hosts = [IPAddr('10.0.0.3'),IPAddr('10.0.0.4')]
    ih_prd = union([match(srcip=h) for h in internal_hosts])
    pol = sf(internal_hosts,ih_prd)

    # For NuSMV
#    mc = ModelChecker(pol)  

    return pol >> flood()
