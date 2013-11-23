import rg


class Robot:
    def act(self, game):
        # if there are enemies around, attack them
        for loc, bot in game.robots.iteritems():
            if bot.player_id != self.player_id:
                if rg.dist(loc, self.location) <= 1:
                    return ['attack', loc]

        # if we're in the center, stay put
        if self.location == rg.CENTER_POINT:
            return ['guard']

        # move toward the center
        return ['move', rg.toward(self.location, rg.CENTER_POINT)]
