""" This module defines Player class and provides functions for
loading and writing Player to database
"""

class Player:
    """ This class describes a player in the fiasco game
    """
    def __init__(self, id_num, name, p_left_id, p_right_id,
                 rel_l_id, rel_l_role, rel_l_sub1, rel_l_sub2,
                 rel_r_id, rel_r_role, rel_r_sub1, rel_r_sub2,
                 game_id):
        self.id_num=id_num
        self.name=name
        self.p_left_id=p_left_id
        self.p_right_id=p_right_id
        self.rel_l_id   = rel_l_id
        self.rel_l_role = rel_l_role
        self.rel_l_sub1 = rel_l_sub1
        self.rel_l_sub2 = rel_l_sub2
        self.rel_r_id   = rel_r_id
        self.rel_r_role = rel_r_role
        self.rel_r_sub1 = rel_r_sub1
        self.rel_r_sub2 = rel_r_sub2
        self.game_id    = game_id

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

def get_players_from_db(game_id, db):
    """ 
    input: game_id: String
    returns: Player
    """
    cur = db.cursor()
    db_result = cur.execute("SELECT * from player where game_id = ?", game_id)
    results = db_result.fetchall()
    players = []
    for result in results:
        players.append(Player (id_num=result[0],
                               name=result[1],
                               p_left_id=result[2],
                               p_right_id=result[3],
                               rel_l_id   = result[4],
                               rel_l_role = result[5],
                               rel_l_sub1 = result[6],
                               rel_l_sub2 = result[7],
                               rel_r_id   = result[8],
                               rel_r_role = result[9],
                               rel_r_sub1 = result[10],
                               rel_r_sub2 = result[11],
                               game_id    = result[12]))
    return players

def insert_player_into_db(player, db):
    """ Inserts player into database
    """
    cur = db.cursor()
    cur.execute(
        "INSERT INTO player (id_num, name, p_left_id, p_right_id, "
        "rel_l_id, rel_l_role, rel_l_sub1, rel_l_sub2, "
        "rel_r_id, rel_r_role, rel_r_sub1, rel_r_sub2, "
        "game_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [player.id_num, player.name, player.p_left_id, player.p_right_id,
         player.rel_l_id, player.rel_l_role, player.rel_l_sub1, player.rel_l_sub2,
         player.rel_r_id, player.rel_r_role, player.rel_r_sub1, player.rel_r_sub2,
         player.game_id])
    db.commit()

    
