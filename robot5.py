import rg


class Robot:
    # parameters
    FRIEND_VALUE = 0.5
    EMPTY_LOCATION_VALUE = 1
    ENEMY_WITH_FRIENDS_AROUND_VALUE = 4
    FRIEND_WITH_ENEMIES_AROUND_VALUE = 0.5
    ENEMY_VALUE = -1
    OCCUPIED_LOCATION_VALUE = 0
    SPAWN_LOC_VALUE = -0.5
    EXPECTED_ENEMY_DAMAGE = 9

    def __init__(self):
        self.locations = {}

    def act(self, game):

        action = self.handle_near_enemies(game)
        if action:
            return action

        # if we're in the center, stay put
        if self.location == rg.CENTER_POINT:
            return ['guard']

        # at this point we don't have enemies near and we are not at the center
        return self.find_path(game)

    # utils
    def enemies_around(self, location, game):
        return self.look_surroundings(location, game)['enemies_near']

    def friends_around(self, location, game):
        return self.look_surroundings(location, game)['friends_near']

    def is_save(self, location, game):
        enemies_around = self.enemies_around(location, game)
        return len(enemies_around) == 0

    def look_surroundings(self, location, game):
        if location in self.locations:
            return self.locations[location]

        locations_around = rg.locs_around(location,
                                          filter_out=('invalid', 'obstacle'))

        friends_near = []
        enemies_near = []

        for location in locations_around:
            try:
                if game.robots[location].player_id == self.player_id:
                    friends_near.append(game.robots[location])
                else:
                    enemies_near.append(game.robots[location])
            except:
                pass

        location_dict = {
            'friends_near': friends_near,
            'enemies_near': enemies_near,
        }

        self.locations[location] = location_dict
        return location_dict

    # algorithim utils
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
                # we found a robot,
                # if it's an enemy
                if robot.player_id != self.player_id:
                    # and it has friends around
                    if len(self.friends_around(near_location, game)):
                        score += (self.ENEMY_WITH_FRIENDS_AROUND_VALUE -
                                  self.EMPTY_LOCATION_VALUE)
                    else:
                        # set the score to an enemy alone
                        score += self.ENEMY_VALUE - self.EMPTY_LOCATION_VALUE
                else:  # it's a friend
                    # and it has enemies around
                    if len(self.enemies_around(near_location, game)):
                        score += (self.FRIEND_WITH_ENEMIES_AROUND_VALUE -
                                  self.EMPTY_LOCATION_VALUE)
                    else:
                        # set the score to an enemy alone
                        score += self.FRIEND_VALUE - self.EMPTY_LOCATION_VALUE
        return score

    # behaviours
    def handle_near_enemies(self, game):
        location = self.location

        locations_around = rg.locs_around(
            location, filter_out=('invalid', 'obstacle')
        )

        enemy_count = 0
        enemy = None
        safe_location = None

        # search for enemies
        for near_location in locations_around:
            try:
                if game.robots[near_location].player_id != self.player_id:
                    # enemy found
                    near_enemy = game.robots[near_location]

                    # store the weakest enemy
                    if enemy is None or near_enemy.hp < enemy.hp:
                        enemy = near_enemy
                    enemy_count += 1
            except:
                # there is not a robot in this location
                if self.is_save(near_location, game):
                    safe_location = near_location

        # if we found an enemy
        if enemy:
            # if the damage they can deal to me is less than my life
            if self.hp > enemy_count * self.EXPECTED_ENEMY_DAMAGE:
                return ['attack', enemy.location]

            # we are most certenly dead at this point if we don't move

            if enemy_count == 1 and safe_location:
                return ['move', safe_location]

            # suicide
            return ['suicide']

        return None

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
