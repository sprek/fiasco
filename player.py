""" This module defines Player class and provides functions for
loading and writing Player to database
"""

class Player:
    """ This class describes a player in the fiasco game
    """

    def __init__(self, id_num=None, name=None, p_left_name=None, p_right_name=None,
                 rel_l_id=None, rel_l_role=None, rel_l_option=None,
                 rel_r_id=None, rel_r_role=None, rel_r_option=None,
                 game_id=None):
        self.id_num       = id_num
        self.name         = name
        self.p_left_name  = p_left_name
        self.p_right_name = p_right_name
        self.rel_l_id     = rel_l_id
        self.rel_l_role   = rel_l_role
        self.rel_l_option = rel_l_option
        self.rel_r_id     = rel_r_id
        self.rel_r_role   = rel_r_role
        self.rel_r_option = rel_r_option
        self.game_id      = game_id      

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

def get_player_names_from_db(game_id, db):
    """ input: String game_id, database db
    returns: list of strings of names
    """
    return list(map(lambda x: x.name, get_players_from_db(game_id, db)))
        
def _get_players_from_db_result(db_result):
    """ input: result of cur.execute("SELECT * from player")
    returns: list of Player objects
    """
    args_dict = {}
    cols = _list_columns_from_results(db_result)
    results = db_result.fetchall()
    players = []
    for result in results:
        for i, val in enumerate(result):
            args_dict[cols[i]] = val
        players.append(Player(**args_dict))
    return players
        
def get_player_from_db_by_name(name, game_id, db):
    """ input: name: String, game_id: String, db: Database
    returns: Player object that matches name
    """
    cur = db.cursor()
    db_result = cur.execute("SELECT * from player where game_id = ? and name = ?",
                            [game_id, name])
    players = _get_players_from_db_result(db_result)
    if len(players) == 0:
        return None
    return players[0]
        
def get_players_from_db(game_id, db):
    """ input: game_id: String
    returns: list of Player objects
    """
    cur = db.cursor()
    db_result = cur.execute("SELECT * from player where game_id = ?", game_id)
    return _get_players_from_db_result(db_result)

def insert_player_into_db(player, db):
    """ Inserts player into database
    """
    cur = db.cursor()
    attr_list = ','.join(_list_player_attributes())
    val_list = ','.join(list(len(_list_player_attributes()) * '?'))
    cur.execute("INSERT INTO player(" + attr_list + ") VALUES (" + val_list + ")",
                _get_player_vals(player))
    db.commit()

def update_player_by_name(player, db):
    """ Searches for the player object's name, and updates all
    attributes for that player
    """
    cur = db.cursor()
    attr_list = _list_player_attributes()
    val_list = _get_player_vals(player)
    assert(len(attr_list) == len(val_list))
    set_statement_list = []
    for i in range(0,len(val_list)):
        set_statement_list.append(attr_list[i] + '=?')
    set_statement = ','.join(set_statement_list)
    val_list.append(player.game_id)
    val_list.append(player.name)
    cur.execute("UPDATE player SET " + set_statement + " WHERE game_id=? and name=?",
                val_list)
    db.commit()

def clear_players(game_id, db):
    """ input: String game_id
    """
    cur = db.cursor()
    cur.execute("delete from player where game_id=?", (game_id,))
    db.commit()

def remove_player(name,game_id, db):
    cur = db.cursor()
    cur.execute("delete from player where name=? and game_id=?", (name,game_id))
    db.commit()

#def _get_player_by_id (id_num, players):
#    for p in players:
#        if p.id_num == id_num:
#            return p
            
def _list_player_attributes():
    """ returns: sorted list of Player attributes
    """
    return sorted(Player().__dict__.keys())

def _get_player_vals(player_obj):
    """ input: Player object
    returns: list of values for the class. Order is sorted by variable name
    """
    vals = []
    for attr in sorted(Player().__dict__.keys()):
        vals.append(getattr(player_obj, attr))
    return vals

def _list_columns_from_results(result):
    """ input: result of cur.execute()
    returns: list of strings containing column names for the result
    """
    return list(map(lambda x: x[0], result.description))
