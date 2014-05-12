
from api import commander
from api import orders
from api.vector2 import Vector2

## Sample Commander for the Operation Dragnet Challenge.


class MyCommander(commander.Commander):
    """This default AI implementation will not do anything.
    All bots remain idle at their spawn location.
    """

    ## Called once when this commander is being initialized.
    def initialize(self):
        pass

    ## Here you put the main AI logic of your commander.
    def tick(self):
        pass

    ## Called once when the match ends.
    def shutdown(self):
        pass
