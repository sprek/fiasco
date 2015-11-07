class Status:
    """
    self.round_num : integer
    self.game_id : string
    self.player_rel_table : string (space & newline separated 2d array with each
                                    element a number indicating the relationship category)
    """
    def __init__(self, round_num=-1, game_id='', player_rel_table=None):
        self.round_num = round_num
        self.game_id = game_id
        self.player_rel_table = player_rel_table

def get_status_from_db(game_id, db):
    cur = db.cursor()
    db_result = cur.execute("SELECT * from status where game_id = ?", (game_id,))
    return _get_status_from_db_result(db_result)

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

def initialize_status(game_id, db, num_players):
    cur = db.cursor()
    db_result = cur.execute("SELECT count(*) FROM status where game_id=?", game_id)
    result = db_result.fetchall()[0][0]
    if result > 0:
        cur.execute("delete from status where game_id=?", game_id)
        db.commit()
    cur.execute("INSERT INTO status (round_num, game_id, player_rel_table) VALUES (?,?,?)",
                (0, game_id, create_player_rel_table(num_players)))
    db.commit()

def set_round_in_db(round_num, game_id, db):
    """
    Sets the round_num for the game_id
    """
    cur = db.cursor()
    cur.execute("UPDATE status SET round_num=? WHERE game_id=?", [round_num, game_id])
    db.commit()

def create_player_rel_table(num_players):
    if num_players <= 1:
        return ''
    return '\n'.join(num_players * [' '.join(num_players * ['-1'])])

def get_table_from_rel_table(player_rel_table):
    table = []
    for r in player_rel_table.split('\n'):
        table.append(r.split())
    return table

def get_rel_table_from_table(table):
    tmp_table = []
    for r in table:
        tmp_table.append(' '.join(r))
    return '\n'.join(tmp_table)

def update_player_rel_table(player_rel_table, player1, player2, rel_num):
    table = get_table_from_rel_table(player_rel_table)
    if player1 < 0 or player1 > len(table[0]):
        return
    if player2 < 0 or player2 > len(table[0]):
        return
    table[player1][player2] = str(rel_num)
    return get_rel_table_from_table(table)

def set_player_rel_table_in_db(game_id, player_rel_table, db):
    cur = db.cursor()                     
    cur.execute("UPDATE status SET player_rel_table=? WHERE game_id=?", (player_rel_table, game_id))
    db.commit()
    
def clear_status(game_id, db):
    """
    Deletes entry for game_id
    """
    cur = db.cursor()
    cur.execute("DELETE FROM status WHERE game_id=?", (game_id,))
    db.commit()

def _get_status_from_db_result(db_result):
    """ input: result of cur.execute("SELECT * from status")
    returns: list of Status objects
    """
    args_dict = {}
    cols = _list_columns_from_results(db_result)
    results = db_result.fetchall()
    if len(results) == 0 or len(results[0]) == 0:
        return None
    for i, val in enumerate(results[0]):
        args_dict[cols[i]] = val
    status = Status(**args_dict)
    return status
    
def _list_status_attributes():
    """ returns: sorted list of Status attributes
    """
    return sorted(Status().__dict__.keys())

def _get_status_vals(status_obj):
    """ input: Status object
    returns: list of values for the class. Order is sorted by variable name
    """
    vals = []
    for attr in sorted(Status().__dict__.keys()):
        vals.append(getattr(status_obj, attr))
    return vals

def _list_columns_from_results(result):
    """ input: result of cur.execute()
    returns: list of strings containing column names for the result
    """
    return list(map(lambda x: x[0], result.description))
