from random import randint

class Dice:
    """
    self.dice : dict>(int, int)
        Key: 1-6
        Value: the quantity of dice with that number
    """
    def __init__(self, dice, game_id):
        self.dice = dice
        self.game_id = game_id

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

def get_dice_from_db(game_id, db):
    """ 
    input: game_id string, database object
    returns: Dice object
    """
    cur = db.cursor()
    db_result = cur.execute("SELECT * from dice where game_id=?", game_id)
    results = db_result.fetchall()

    if len(results) == 0:
        return None
    
    dice = {}
    for i in range (0, len(results[0])-1):
        dice[i+1] = results[0][i]
    return Dice(dice, game_id)

def insert_dice_into_db(dice, db):
    """ input: Dice object, database object
    """

    if get_dice_from_db(dice.game_id, db) == None:
        cur = db.cursor()
        cur.execute("INSERT INTO dice (d1,d2,d3,d4,d5,d6,game_id) VALUES (?,?,?,?,?,?,?)", \
                    (dice.dice[1],  dice.dice[2], dice.dice[3], dice.dice[4], dice.dice[5],
                     dice.dice[6], dice.game_id))
    else:
        clear_dice(dice.game_id, db)
        insert_dice_into_db(dice, db)
    db.commit()

def initialize_dice(num_players, game_id):
    """ input: Int number of players, String game_id 
    returns Dice
    """
    dice = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
    for _ in range(0,num_players*4):
        r = randint(1,6)
        dice[r] = dice[r] + 1
    return Dice(dice, game_id)

def clear_dice(game_id, db):
    """ input: String game_id
    """
    cur = db.cursor()
    cur.execute("delete from dice where game_id=?", game_id)
    db.commit()
