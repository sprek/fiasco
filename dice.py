from random import randint
import data_model

class Dice:
    """
    self.dice : dict>(int, int)
        Key: 1-6
        Value: the quantity of dice with that number
    """
    def __init__(self, dice_dic, game_id):
        self.dice_dic = dice_dic
        self.game_id = game_id

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

class DiceDataModel:
    def __init__(self, d1=0, d2=0, d3=0, d4=0, d5=0, d6=0, game_id=-1):
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4
        self.d5 = d5
        self.d6 = d6
        self.game_id = game_id

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

def diceToDiceDataModel(dice):
    return DiceDataModel(dice.dice_dic[1], dice.dice_dic[2], dice.dice_dic[3], dice.dice_dic[4], dice.dice_dic[5], dice.dice_dic[6], dice.game_id)

def diceDataModelToDice(diceDataModel):
    dice_dic = { 1:diceDataModel.d1, 2:diceDataModel.d2, 3:diceDataModel.d3, 4:diceDataModel.d4, 5:diceDataModel.d5, 6:diceDataModel.d6 }
    return Dice(dice_dic, diceDataModel.game_id)

def get_dice_from_db(game_id, db):
    """
    input: game_id string, database object
    returns: Dice object
    """
    diceDataModel = data_model.get_object_from_db_by_key(DiceDataModel, "game_id", game_id, db)
    if not diceDataModel:
        return None
    dice_dic = {}
    dice_dic[1] = diceDataModel.d1 
    dice_dic[2] = diceDataModel.d2 
    dice_dic[3] = diceDataModel.d3 
    dice_dic[4] = diceDataModel.d4 
    dice_dic[5] = diceDataModel.d5 
    dice_dic[6] = diceDataModel.d6
    return Dice(dice_dic, game_id)

def insert_dice_into_db(dice, db):
    """ input: Dice object, database object
    """
    data_model.update_object_in_db_by_key(diceToDiceDataModel(dice), "game_id", dice.game_id, db, True)

def initialize_dice(num_players, game_id):
    """ input: Int number of players, String game_id
    returns Dice
    """
    dice_dic = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
    for _ in range(0,num_players*4):
        r = randint(1,6)
        dice_dic[r] = dice_dic[r] + 1
    return Dice(dice_dic, game_id)

def clear_dice(game_id, db):
    """ input: String game_id
    """
    data_model.clear_table_by_key(DiceDataModel, "game_id", game_id, db)
