class Status:
    """
    self.round_num : integer
    self.game_id : string
    """
    def __init__(self, round_num, game_id):
        self.round_num = round_num
        self.game_id = game_id

def get_round_from_db(game_id, db):
    """
    returns: -1 if there is no entry
    """
    cur = db.cursor()
    db_result = cur.execute("SELECT round_num from status where game_id=?", game_id)
    results = db_result.fetchall()
    if len(results) == 0:
        return -1
    if len(results[0]) == 0:
        return -1
    return results[0][0]

def set_round_in_db(round_num, game_id, db):
    """
    Sets the round_num for the game_id
    """
    cur = db.cursor()
    cur_round = get_round_from_db(game_id, db)
    if (cur_round == -1):
        print ("INSERTING: " + str(round_num) + " GAMEID: " + game_id)
        cur.execute("INSERT INTO status (round_num, game_id) VALUES (?,?)", [round_num, game_id])
        db.commit()
    else:
        cur.execute("UPDATE status SET round_num=? WHERE game_id=?", [round_num, game_id])
        db.commit()

def clear_status(game_id, db):
    """
    Deletes entry for game_id
    """
    cur = db.cursor()
    cur.execute("DELETE FROM status WHERE game_id=?", (game_id,))
    db.commit()
