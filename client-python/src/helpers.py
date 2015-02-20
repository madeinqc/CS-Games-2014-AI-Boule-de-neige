import pprint

__author__ = 'madeinqc'

import world as world_module
import utilities
import actions
import random

#
# Helper methods needed:
# - should cancel shooting (player out of the hit zone)
# - has ally nearby
# - number of allies nearby
#

def attack_enemy(player, world):
    enemy = find_in_range_enemy(player, world)
    if enemy is not None:
        dest = get_hit_point(player, enemy)
        if dest is not None:
            dest = get_hit_point(player, enemy)
            print 'attacking, enemy(%s,%s | speed %s | dir(%s,%s)) snowball(%s,%s)' % (enemy.point.x, enemy.point.y, enemy.speed, enemy.orientation.x, enemy.orientation.y, dest.x, dest.y)
            return actions.ThrowAction(player, dest)
    return None

def attack_flag_holder(player, world):
    enemy = world.flag.holder
    if enemy is not None:
        dest = get_hit_point(player, enemy)
        if dest is not None:
            return actions.ThrowAction(player, dest)

    return None

def walk_toward_enemy(player, world):
    enemy = find_visible_enemy(player, world)
    if enemy is not None:
        # print 'moving to enemy'
        return actions.MoveAction(player, enemy.point)
    return None

def walk_near_enemy(player, world):
    enemy = find_visible_enemy(player, world)
    if enemy is not None:
        # print 'moving to enemy'
        return actions.MoveAction(player, world_module.Point(enemy.point.x + random.random() * 800 - 400, enemy.point.y + random.random() * 800 - 400))
    return None

def find_in_range_enemy(player, world):
    players = get_alive_enemies(world)
    for enemy in players:
        if player.canSee(enemy) and utilities.maths.getEuclidianDistance(enemy.x, enemy.y, player.x, player.y) < 500:
            return enemy

def can_hit_an_enemy(player, world):
    players = get_alive_enemies(world)
    for enemy in players:
        if player.canHit(enemy) and utilities.maths.getEuclidianDistance(enemy.x, enemy.y, player.x, player.y) < 500:
            return enemy

def walk_to_flag(player, world):
    return actions.MoveAction(player, world.flag.point)

def walk_near_flag(player, world):
    # print 'moving near flag'
    return actions.MoveAction(player, world_module.Point(world.flag.point.x + random.random() * 800 - 400, world.flag.point.y + random.random() * 800 - 400))

def walk_to_home(player, world):
    return actions.MoveAction(player, world.currentTeam.startingPosition)

def walk_to_flag_holder_home(player, world):
    return actions.MoveAction(player, world.flag.holder.team.startingPosition)

def find_visible_enemy(player, world):
    players = get_alive_enemies(world)
    for enemy in players:
        if player.canSee(enemy):
            return enemy

def get_alive_enemies(world):
    players = []
    for team in world.otherTeams:
        for player in team.players:
            players.append(player)
    return filter(lambda p: p.playerState != None and p.playerState.stateType != world_module.StateType.Dead, players)

def get_hit_point(player, enemy):
    """
    :param player: world_module.Player
    :param enemy: world_module.Player
    :return: world_module.Point
    """

    if enemy.playerState.stateType != world_module.StateType.Moving:
        return enemy.point

    t = 5

    delta_pos = None
    last_delta_pos = None

    px = enemy.point.x
    py = enemy.point.y

    while last_delta_pos == None or last_delta_pos > delta_pos:
        pbx = px + enemy.speed * enemy.orientation.x * t
        pby = py + enemy.speed * enemy.orientation.y * t

        dist = utilities.maths.getEuclidianDistance(player.point.x, player.point.y, pbx, pby)

        t = snowball_charge_time(dist) + dist / snowball_speed(dist) + 5

        pex = px + enemy.speed * enemy.orientation.x * t
        pey = py + enemy.speed * enemy.orientation.y * t

        dist_be = utilities.maths.getEuclidianDistance(pbx, pby, pex, pey)

        last_delta_pos = delta_pos
        delta_pos = dist_be

        if delta_pos <= 5:
            pt = world_module.Point(pbx, pby)
            print 'Hit at %s, %s. Should hit at %s, %s' % (pt.x, pt.y, enemy.x + enemy.speed * enemy.orientation.x * t, enemy.y + enemy.speed * enemy.orientation.y * t)
            return pt

    return None

def snowball_speed(dist):
    return min(20, max(5, 5+0.05 * dist * 100))

def snowball_charge_time(dist):
    return dist/15

def dist(p1, p2):
    return utilities.maths.getEuclidianDistance(p1, p2)