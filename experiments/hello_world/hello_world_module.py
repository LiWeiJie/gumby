from gumby.experiment import experiment_callback
from gumby.modules.community_experiment_module import CommunityExperimentModule
from gumby.modules.community_launcher import CommunityLauncher
from gumby.modules.experiment_module import static_module
from gumby.modules.isolated_community_loader import IsolatedCommunityLoader

from Tribler.dispersy.community import Community
from Tribler.dispersy.conversion import DefaultConversion


class HelloWorldCommunityLoader(IsolatedCommunityLoader):
    """
    This provides the capability to run your communities in an isolated fashion.
    You can include multiple launchers here.
    """

    def __init__(self, session_id):
        super(HelloWorldCommunityLoader, self).__init__(session_id)
        self.set_launcher(HelloWorldCommunityLauncher())


class HelloWorldCommunityLauncher(CommunityLauncher):
    """
    This class forwards all the information Dispersy needs to launch our community.
    """
    def get_community_class(self):
        return HelloWorldCommunity

    def get_my_member(self, dispersy, session):
        return dispersy.get_new_member()

    def get_kwargs(self, session):
        return {}


class HelloWorldCommunity(Community):
    """
    This is the Community we are testing. It does nothing right now.
    """
    def initiate_conversions(self):
        return [DefaultConversion(self)]


@static_module
class HelloWorldModule(CommunityExperimentModule):
    """
    This is the module we reference through the scenario (note @static_module).
    All of the functionality we want to expose to the scenario is marked `@experiment_callback`.
    """
    def __init__(self, experiment):
        super(HelloWorldModule, self).__init__(experiment, HelloWorldCommunity)
        self.dispersy_provider.custom_community_loader = HelloWorldCommunityLoader(self.dispersy_provider.session_id)

    @experiment_callback
    def hello(self):
        print "Hello human!"

    @experiment_callback
    def extended_hello(self, repetitions, separator=" "):
        print separator.join(["Hello human!"]*int(repetitions))