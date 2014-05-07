from api.commander import Commander

class ScriptedCommander(Commander):
    """
    Executes a set of orders indexed by game time
    """

    def __init__(self, orders, nick, **kwargs):
        super(ScriptedCommander, self).__init__(nick, **kwargs)
        self.orders = sorted(orders, key=lambda time_and_order: time_and_order[0])
        self.initialWaitTime = 0.0

    def tick(self):
        n = 0
        for time, order in self.orders:
            if time <= self.game.match.timePassed - self.initialWaitTime:
                self.orderQueue.append(order)
                n += 1
            else:
                break

        self.orders = self.orders[n:]

