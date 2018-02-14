from gumby.experiment import experiment_callback
from gumby.modules.community_experiment_module import CommunityExperimentModule
from gumby.modules.community_launcher import CommunityLauncher
from gumby.modules.experiment_module import static_module
from gumby.modules.isolated_community_loader import IsolatedCommunityLoader

from .say_to_each_community import SayToEachCommunity


class SayToEachCommunityLoader(IsolatedCommunityLoader):
    """
    This provides the capability to run your communities in an isolated fashion.
    You can include multiple launchers here.
    """

    def __init__(self, session_id):
        super(SayToEachCommunityLoader, self).__init__(session_id)
        self.set_launcher(SayToEachCommunityLauncher())


class SayToEachCommunityLauncher(CommunityLauncher):
    """
    This class forwards all the information Dispersy needs to launch our community.
    """
    def get_community_class(self):
        return SayToEachCommunity

    def get_my_member(self, dispersy, session):
        return dispersy.get_new_member()

    def get_kwargs(self, session):
        return {}

    # def get_name(self):
    #     return "SayToEachCommunity2Weijie"



@static_module
class SayToEachModule(CommunityExperimentModule):
    """
    This is the module we reference through the scenario (note @static_module).
    All of the functionality we want to expose to the scenario is marked `@experiment_callback`.
    """
    def __init__(self, experiment):
        super(SayToEachModule, self).__init__(experiment, SayToEachCommunity)
        self.dispersy_provider.custom_community_loader = SayToEachCommunityLoader(self.dispersy_provider.session_id)

    @experiment_callback
    def say_to_others(self):
        self.community.say_to_others()

    @experiment_callback
    def say_to_locals(self):
        self.community.say_to_locals()

    @experiment_callback
    def print_guestbook(self):
        print "guest book size: %d\n"%self.community.guestbook.__len__()
        print self.community.guestbook

    @experiment_callback
    def clean_guestbook(self):
        self.community.guestbook = []


    @experiment_callback
    def print_myself(self):
        print "I am ", self.community.my_member
