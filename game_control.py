""" This module contains functions for controlling the game
"""

import player, dice, random, status, playset

NO_ERROR = 0
ERROR_INVALID_RELATIONSHIP_VALUES = 1
ERROR_INVALID_PLAYERS = 2
ERROR_CURRENT_PLAYER_NOT_IN_RELATIONSHIP = 3
ERROR_PLAYERS_MUST_BE_DIFFERENT = 4
ERROR_NOT_ENOUGH_DICE = 5

def initialize_game(game_id, db):
    """ input: game_id String, db Database
    """
    # initialize players
    players = player.get_players_from_db(game_id, db)
    random.shuffle(players)
    for i, p in enumerate(players):
        p.id_num = i
        p.p_left_name = _get_left_item(players,i).name
        p.p_right_name = _get_right_item(players,i).name
        player.update_player_by_name(p, db)
    # initialize dice
    dice.insert_dice_into_db(dice.initialize_dice(len(players), game_id), db)
    status.set_round_in_db(0, game_id, db)

def player_name_check(request_name, session_name, player_names):
    """
    This function will handle what the correct user to log in is, based on the
    incoming GET request, and the current session player value
    input: request_name: 'player' GET request,
           session_name: current session['player'] value
           player_names: list of strings of all player names
    returns: string indicating the correct player name, or empty string if
             the player should be selected
    """
    if request_name in player_names:
        # go with request name by default
        return request_name
    else:
        if not request_name and session_name in player_names:
            # no request name: go with session name
            return session_name
    return ''

def set_left_relationship(rel_role, rel_option, rel_id, player_obj, db):
    player_obj.rel_l_role = rel_role
    player_obj.rel_l_option = rel_option
    player_obj.rel_l_id = rel_id
    player.update_player_by_name(player_obj, db)

def set_right_relationship(rel_role, rel_option, rel_id, player_obj,db):
    player_obj.rel_r_role = rel_role
    player_obj.rel_r_option = rel_option
    player_obj.rel_r_id = rel_id
    player.update_player_by_name(player_obj, db)

def set_relationship(rel1_role, rel1_option, rel1_player,
                     rel2_role, rel2_option, rel2_player,
                     cur_player_name, pset, game_id, db):
    """
    Updates the database - sets the relationships for one of the neighbor pairs
    """
    rel_indices = playset.get_relationship_indices(rel1_role, rel2_role, rel1_option, rel2_option, pset)
    if not rel_indices:
        return ERROR_INVALID_RELATIONSHIP_VALUES

    # check if dice are ok
    game_dice = dice.get_dice_from_db(game_id, db)
    if game_dice.dice[rel_indices[1]+1] <= 0:
        return ERROR_NOT_ENOUGH_DICE
    p1 = player.get_player_from_db_by_name(rel1_player, game_id, db)
    p2 = player.get_player_from_db_by_name(rel2_player, game_id, db)
    if not p1 or not p2:
        return ERROR_INVALID_PLAYERS
    if not rel1_player == cur_player_name and not rel2_player == cur_player_name:
        return ERROR_CURRENT_PLAYER_NOT_IN_RELATIONSHIP
    if rel1_player == rel2_player:
        return ERROR_PLAYERS_MUST_BE_DIFFERENT
    if p1.p_left_name == p2.name:
        # neighor is to the left
        set_left_relationship(rel1_role, rel1_option,
                              playset.get_relationship_id_from_indices(
                                  rel_indices, flip_a_b=False), p1, db)
        set_right_relationship(rel2_role, rel2_option, 
                               playset.get_relationship_id_from_indices(
                                   rel_indices, flip_a_b=True), p2, db)
    elif p1.p_right_name == p2.name:
        # neighbor is to the right
        set_right_relationship(rel1_role, rel1_option,
                              playset.get_relationship_id_from_indices(
                                  rel_indices, flip_a_b=False), p1, db)
        set_left_relationship(rel2_role, rel2_option,
                               playset.get_relationship_id_from_indices(
                                   rel_indices, flip_a_b=True), p2, db)
    player.update_player_by_name(p1, db)
    player.update_player_by_name(p2, db)
    return NO_ERROR

def enable_category(name, enabled, cur_player, game_id, db):
    """ input: target name: string
               enabled: boolean
               cur_player: string
    """
    cur_status = status.get_status_from_db(game_id, db)
    rel_table = status.get_table_from_rel_table(cur_status.player_rel_table)
    #if rel_table == 
    

def close_game(game_id, db):
    player.clear_players(game_id, db)
    dice.clear_dice(game_id, db)
    status.clear_status(game_id, db)

def _get_left_item(players, cur_index):
    """ returns the previous item in the players list (loops back to end if negative)
    """
    return players[(cur_index-1) % len(players)]

def _get_right_item(players, cur_index):
    """ returns the next item in the players list (loops back to end if negative)
    """
    return players[(cur_index+1) % len(players)]

