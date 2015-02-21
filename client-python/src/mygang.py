'''
@author: Mathieu Plourde - mat.plourde@gmail.com
'''

import world as world_module
import utilities
import actions
import random
import helpers

roles = {
    'aggressive':
        [helpers.attack_enemy, {
            True: [],
            False: [helpers.walk_toward_enemy]
        }]
}


class MyGang(world_module.Gang):
    def __init__(self, port, name):
        super(MyGang, self).__init__(port, name)

    def compute(self, world):
        '''
        compute

        :param world: world_module.World object
        :return:
        '''

        a = []

        i = -1

        for player in world.teams[self.teamId].players:
            i += 1

            act = actions.IdleAction(player)
            if world.canPickFlag:
                flag_holder = world.flag.holder

                if flag_holder is None:
                    if helpers.dist(player.point, world.flag.point) <= 10:
                        act = actions.PickFlagAction(player)
                        pass
                    else:
                        act = helpers.walk_to_flag(player, world)
                elif flag_holder.team == world.currentTeam:
                    # W/ flag mode w/ flag
                    if player.isFlagHolder:
                        # has flag -> to home
                        if helpers.dist(player.point, world.currentTeam.startingPosition) <= 10:
                            act = actions.DropFlagAction(player)
                        else:
                            act = helpers.walk_to_home(player, world)
                    else:
                        # attack enemies near flag_holder
                        # walk near flag holder or near base and attack enemy waiting
                        act = helpers.attack_enemy(player, world)
                        if act is None:
                            if i % 2 == 0:
                                act = helpers.walk_to_home(player, world)
                            else:
                                act = helpers.walk_near_flag(player, world)

                else:
                    #
                    # W/ flag mode w/o flag
                    #
                    # attack flag holder
                    # walk toward enemy base
                    if i % 2 == 0 or helpers.dist(player, world.flag.holder.team.startingPosition) < 100:
                        act = helpers.attack_flag_holder(player, world)
                        if act is None:
                            act = helpers.walk_to_flag_holder_home(player, world)
                    else:
                        act = helpers.walk_near_flag(player, world)
            else:
                # attack enemy (that with the less ally nearby)
                # move near enemy (but not near an ally)
                # move near flag (but not near an ally)

                if player.playerState.stateType == world_module.StateType.Throwing:
                    continue

                act = helpers.attack_enemy(player, world)

                if act is None:
                    act = helpers.walk_near_enemy(player, world)
                    if act is None:
                        act = helpers.walk_near_flag(player, world)

            if player.playerState.stateType == world_module.StateType.Idle or player.playerState.stateType != world_module.StateType.Throwing and isinstance(
                    act, actions.ThrowAction):
                a.append(act)

            continue


            # if no one holds the flag and the flag can be picked (can only be picked if 20% of the players are dead)
            if (world.flag.holder is None and world.canPickFlag):

                # if the player is close enough, we pick it, else we move to it. distance to pick flag is <= 10
                if (utilities.maths.getEuclidianDistance(player.x, player.y, world.flag.x,
                                                         world.flag.y) <= actions.PickFlagAction.MIN_DISTANCE_TO_PICK):
                    a.append(actions.PickFlagAction(player))
                elif (not (
                                    player.playerState.stateType == world_module.StateType.Moving and player.playerState.currentAction.destination.x == world.flag.x and player.playerState.currentAction.destination.y == world.flag.y)):
                    # if the player is not going to the flag, send him to the flag
                    a.append(actions.MoveAction(player, world.flag.point))
            else:
                # if the holder is from the OTHER team, we chase him! (follow stupidly)
                if (world.flag.holder is not None and world.flag.holder.team.id != self.teamId):
                    # chase
                    a.append(actions.MoveAction(player, world.flag.holder.point))
                elif (player.isFlagHolder and player.x == world.teams[self.teamId].startingPosition.x and player.y ==
                    world.teams[self.teamId].startingPosition.y):
                    # if the player is holding the flag and is on the starting position, we drop the flag to win the game
                    a.append(actions.DropFlagAction(player))
                elif (player.isFlagHolder and player.playerState.stateType != world_module.StateType.Moving):
                    # if the player is the flag holder and is not moving

                    # if the player is not at the starting point, we move it there
                    if (player.x != world.teams[self.teamId].startingPosition.x or player.y != world.teams[
                        self.teamId].startingPosition.y):
                        a.append(actions.MoveAction(player, world.teams[self.teamId].startingPosition))
                else:
                    if (
                                    player.playerState.stateType == world_module.StateType.Idle and player.playerState.pendingAction is None):
                        # if the player isn't doing anything and has no pending actions, do something random!!! Throw or move!
                        p = None
                        while (True):
                            # random point
                            p = world_module.Point(random.random() * world.map.width,
                                                   random.random() * world.map.height)

                            # while the point is not in a wall and far enough from the player
                            if ((not world.map.isPointInWall(p)) and utilities.maths.getEuclidianDistance(player.x,
                                                                                                          player.y, p.x,
                                                                                                          p.y) > 50):
                                break

                        if (random.random() * 2 < 0.5):
                            a.append(actions.MoveAction(player, p))
                        else:
                            a.append(actions.ThrowAction(player, p))

            # examples of helpers you can use!!! read the doc!
            for otherPlayer in world.otherTeams[0].players:
                player.canHit(otherPlayer)
                player.canBeHitBy(otherPlayer)
                player.wouldHitPlayer(otherPlayer, world_module.Point(500.0, 500.0))
                player.canSee(otherPlayer)

            for snowball in world.snowballs:
                snowball.canHit(player)

            line1 = utilities.maths.getLine(player.point, world.flag.point)
            line2 = utilities.maths.getLine(world_module.Point(0.0, 0.0), world_module.Point(1000.0, 1000.0))
            line1.intersect(line2)
            line1.getX(0.0)
            line1.getX(0.5)
            line1.getX(1.0)

            world.map.isCrossingWall(world_module.Point(0.0, 0.0), world_module.Point(1000.0, 1000.0))
            world.map.isPointInWall(50.0, 50.0)
            # end of the examples

        # print a

        return a
