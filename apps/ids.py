
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent
from pyretic.pyresonance.smv.model_checker import *


#####################################################################################################
# * App launch
#   - pyretic.py pyretic.pyresonance.apps.ids
#
# * Mininet Generation (in "~/pyretic/pyretic/pyresonance" directory)
#   - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --topo=single,3
#
# * Start ping from h1 to h2 
#   - mininet> h1 ping h2
#
# * Events to block traffic "h1 ping h2" (in "~/pyretic/pyretic/pyresonance" directory)
#   - python json_sender.py -n infected -l True --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001
#
# * Events to again allow traffic "h1 ping h2" (in "~/pyretic/pyretic/pyresonance" directory)
#   - python json_sender.py -n infected -l False --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001
#####################################################################################################

class ids(DynamicPolicy):
    def __init__(self):

       ### DEFINE THE LPEC FUNCTION

        def lpec(f):
            return match(srcip=f['srcip'])

        ## SET UP TRANSITION FUNCTIONS

        @transition
        def infected(self):
            self.case(occured(self.event),self.event)

        @transition
        def policy(self):
            self.case(is_true(V('infected')),C(drop))
            self.default(C(identity))

        ### SET UP THE FSM DESCRIPTION

        self.fsm_def = FSMDef(
            infected=FSMVar(type=BoolType(), 
                            init=False, 
                            trans=infected),
            policy=FSMVar(type=Type(Policy,{drop,identity}),
                          init=identity,
                          trans=policy))

        ### SET UP POLICY AND EVENT STREAMS

        fsm_pol = FSMPolicy(lpec,self.fsm_def)
        json_event = JSONEvent()
        json_event.register_callback(fsm_pol.event_handler)

        super(ids,self).__init__(fsm_pol)


def main():
    pol = ids()

    # For NuSMV
    smv_str = fsm_def_to_smv_model(pol.fsm_def)
    mc = ModelChecker(smv_str,'ids')  

    ## Add specs
    mc.add_spec("FAIRNESS\n  infected;")

    ### If infected event is true, next policy state is 'drop'
    mc.add_spec("SPEC AG (infected -> AX policy=policy_1)")

    ### If infected event is false, next policy state is 'allow'
    mc.add_spec("SPEC AG (!infected -> AX policy=policy_2)")

    ### Policy state is 'allow' until infected is true.
    mc.add_spec("SPEC A [ policy=policy_2 U infected ]")

    mc.save_as_smv_file()

    import datetime as dt
    n1=dt.datetime.now()
    mc.verify()
    n2=dt.datetime.now()

    print (n2-n1).microseconds

    return pol >> flood()
