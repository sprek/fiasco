from flask import Flask, render_template, request, session, redirect, url_for
from flask import g, jsonify
from flask_bootstrap import Bootstrap, StaticCDN
from cgi import escape
import sqlite3
import json
from random import randint
import player, dice, game_control, view, create_db, playset
import os.path

DATABASE = 'fiasco.db'
GAME_ID = "0"

#def get_players(game_id):
#    cur = get_db().cursor()
#    db_result = cur.execute("SELECT name from player where game_id = ?", game_id)
#    results = db_result.fetchall()
#    players = []
#    for name in results:
#        if len(name) > 0:
#            players.append(name[0])
#    return players

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        if os.path.isfile(DATABASE):
            db = g._database = sqlite3.connect(DATABASE)
        else:
            create_db.create_db(DATABASE)
    return db

#def get_num_players(game_id):
#    return len(get_players(game_id))
#
#def get_dice(num_players):
#    dice = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
#    for i in range(0,num_players*4):
#        r = randint(1,6)
#        dice[r] = dice[r] + 1
#    return dice

#def get_dice_from_db(game_id):
#    dice = {}
#    db = get_db()
#    cur = db.cursor()
#    db_result = cur.execute("SELECT * from dice where game_id=?", GAME_ID)
#    if len(db_result.fetchall()) > 0:
#        db_result = cur.execute ("SELECT d1,d2,d3,d4,d5,d6 from dice where game_id=?", GAME_ID)
#        results = db_result.fetchall()
#        if len(results) > 0:
#            print "RESULTS: " + str(results[0])
#            for i in range (0, len(results[0])):
#                dice[i+1] = results[0][i]
#        else:
#            print "ERROR NO RESULTS"
#    else:
#        print "SETTING DICE"
#        dice = get_dice(get_num_players())
#        cur.execute("INSERT INTO dice (d1,d2,d3,d4,d5,d6,game_id) VALUES (?,?,?,?,?,?,?)", \
#                    (dice[1],  dice[2], dice[3], dice[4], dice[5], dice[6], GAME_ID,))
#        db.commit()
#    return dice

#def initialize_game(game_id):
#    players = get_players(game_id)
#    rand_ids = random.shuffle(players)
#    db = get_db()
#    cur = db.cursor()
#    for i, player in enumerate(players):
#        pleft = get_left_id(i)
#        pright = get_right_id(i)
#        cur.execute("UPDATE player SET id=?, p_left_id=?, p_right_id=? where game_id=? and name=?",
#                    i, pleft, pright, game_id, player)
#        db.commit()
#    cur.execute("UPDATE status SET round=? where game_id=?", 0, game_id)
#    db.commit()

#def get_playset_meta_html():
#
#    
#    return json.dumps({'data' : 'asdf'})

def create_app(configfile=None):
    app = Flask(__name__)
    Bootstrap(app)
    app.extensions['bootstrap']['cdns']['jquery'] = StaticCDN()
    app.extensions['bootstrap']['cdns']['bootstrap'] = StaticCDN()
    app.secret_key = 'K\x9a\xa1\xa1\x84\x1a\x9b\xdc\xb3m\x0c\xdf[\x1c;\xc1S\xbd\xd6\x90\xec#\xdaX'

    @app.route('/get_setup_status', methods=('POST', 'GET'))
    def get_setup_status():
        dice_html = view.get_dice_html(dice.get_dice_from_db(GAME_ID, get_db()).dice)
        data = {'dice_html' : dice_html}
        #data = {'test1' : 'a', 'test2' : 'b'}
        #print "RETURNING: " + str(jsonify(data))
        return jsonify(data)

    @app.route('/play', methods=('POST', 'GET'))
    def play():
        db = get_db()
        cur_player = request.args.get('player', '')
        players = player.get_players_from_db(GAME_ID, db)
        player_names = list(map(lambda x: x.name, players))
        if cur_player:
            if cur_player in players:
                session['player'] = cur_player
        if not 'player' in session or len(session['player']) == 0:
            return render_template('select_player.html', players=player_names)
        else:
            #pd = parse_playset('/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt')
            #dice = get_dice_from_db(GAME_ID)
            game_control.initialize_game(GAME_ID, get_db())
            pd = playset.parse_playset('/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt')
            return render_template('play.html',
                                   player=session['player'],
                                   playset_name='Main St.',
                                   dice_html=view.get_dice_html(dice.get_dice_from_db(GAME_ID, get_db()).dice),
                                   playset_html = view.get_playset_html(pd))

    @app.route('/endgame', methods=('POST', 'GET'))
    def endgame():
        dice.clear_dice(GAME_ID, get_db())
        return redirect('/')

    @app.route('/changeplayer', methods=('POST', 'GET'))
    def changeplayer():
        session['player'] = ''
        return redirect('/play')
        
    @app.route('/clearplayers', methods=('POST', 'GET'))
    def clearplayers():
        cur = get_db().cursor()
        cur.execute("delete from player")
        db.commit()
        return ''
    
    @app.route('/removeplayer', methods=('POST', 'GET'))
    def removeplayer():
        player.remove_player(request.form['data'], GAME_ID, get_db())
        return ''

    @app.route('/playerlist', methods=('POST', 'GET'))
    def playerlist():
        player_names = player.get_player_names_from_db(GAME_ID, get_db())
        #print ("PLAYER NAMES IN PLAYERLIST: " + str(player_names))
        #result_str = ''
        #if (session['player'] in player_names):
        #    player_names.remove(session['player'])
        result_str = view.get_player_list_html(player_names)
        #else:
        #    session['player'] = ''
        return result_str

    @app.route('/playerjoin', methods=('POST', 'GET'))
    def playerjoin():
        name = request.form['data']
        if not name in player.get_players_from_db(GAME_ID, get_db()):
            print ("INSERTING PLAYER: " + name)
            player.insert_player_into_db(player.Player(name=name, game_id=GAME_ID), db=get_db())
        session['player'] = name
        return ''

    @app.route('/', methods=('GET', 'POST'))
    def index():
        player_name = ''
        if 'player' in session:
            player_name = session['player']
        else:
            session['player'] = player_name
        return render_template('index.html', player=player_name)

    #@app.route('/test', methods=('GET', 'POST'))
    #def test():
    #    return render_template('test2.html')
    
    return app
