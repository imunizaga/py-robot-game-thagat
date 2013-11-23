import rg


class Robot:
    FRIEND_VALUE = 0.5
    EMPTY_LOCATION_VALUE = 1
    FRIEND_IN_NEED_VALUE = 4
    ENEMY_VALUE = -1
    OCCUPIED_LOCATION_VALUE = 0
    SPAWN_LOC_VALUE = -0.5

    def act(self, game):

        near_enemy = self.find_near_enemy(game)
        if near_enemy:
            return near_enemy

        # if we're in the center, stay put
        if self.location == rg.CENTER_POINT:
            return ['guard']

        return self.find_path(game)

    def find_near_enemy(self, game):
        location = self.location

        locations_around = rg.locs_around(location,
                                          filter_out=('invalid', 'obstacle'))

        for near_location in locations_around:
            try:
                if game.robots[near_location].player_id != self.player_id:
                    return ['attack', near_location]
            except:
                pass

        return None

    def friends_near(self, location, game):
        friends = []

        locations_around = rg.locs_around(location,
                                          filter_out=('invalid', 'obstacle'))

        for near_location in locations_around:
            try:
                robot = game.robots[near_location]
            except:
                pass
            else:
                if robot.player_id == self.player_id:
                    friends.append(robot)
        return friends

    def location_score(self, from_location, location, game):
        # return 0 score if the place is occupied
        try:
            if game.robots[location]:
                return self.OCCUPIED_LOCATION_VALUE
        except:
            pass

        # take all the places around that location
        locations_around = rg.locs_around(location,
                                          filter_out=('invalid', 'obstacle'))

        # every location starts with the number of near available locations
        # as a score - 1 for itself
        score = (len(locations_around) - 1) * self.EMPTY_LOCATION_VALUE

        for near_location in locations_around:
            # do not count the itself
            if near_location == from_location:
                continue

            try:
                robot = game.robots[near_location]
            except:
                # free space
                if 'spanw' in rg.loc_types(near_location):
                    score += self.SPAWN_LOC_VALUE - self.EMPTY_LOCATION_VALUE

            else:
                if robot.player_id != self.player_id:
                    if len(self.friends_near(near_location, game)):
                        score += (self.FRIEND_IN_NEED_VALUE -
                                  self.EMPTY_LOCATION_VALUE)
                    else:
                        score += self.ENEMY_VALUE - self.EMPTY_LOCATION_VALUE
                else:
                    score += self.FRIEND_VALUE - self.EMPTY_LOCATION_VALUE
        return score

    def find_path(self, game):
        location = self.location

        if location == rg.CENTER_POINT:
            return ['guard']

        locations_around = rg.locs_around(location,
                                          filter_out=('invalid', 'obstacle'))

        locations_around.append(location)
        rated_locations = []

        for possible_location in locations_around:
            center_dist = rg.wdist(possible_location, rg.CENTER_POINT)
            rated_locations.append((
                self.location_score(self.location, possible_location, game),
                -center_dist,
                possible_location
            ))

        rated_locations.sort(reverse=True)

        selected_location = rated_locations[0][2]

        if selected_location != location:
            return ['move', selected_location]
        else:
            return ['guard']
