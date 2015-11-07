from flask import Flask, render_template, request, session, redirect, url_for
from flask import g, jsonify
from flask_bootstrap import Bootstrap, StaticCDN
from cgi import escape
import sqlite3
import json
from random import randint
import player, dice, game_control, view, create_db, playset, status
import os.path

DATABASE = 'fiasco.db'
GAME_ID = "0"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        if os.path.isfile(DATABASE):
            db = g._database = sqlite3.connect(DATABASE)
        else:
            create_db.create_db(DATABASE)
    return db


#def get_playset_meta_html():
#
#
#    return json.dumps({'data' : 'asdf'})

def create_app():
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
        player_names = player.get_player_names_from_db(GAME_ID, get_db())
        cur_player_name = game_control.player_name_check(request.args.get('player',''),
                                                         session['player'],
                                                         player_names)
        if cur_player_name:
            session['player'] = cur_player_name
        else:
            return render_template('select_player.html', players=player_names)
        
        if status.get_round_from_db(GAME_ID, get_db()) == -1:
            game_control.initialize_game(GAME_ID, get_db())
        cur_player = player.get_player_from_db_by_name(cur_player_name, GAME_ID, get_db())
        pd = playset.parse_playset('/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt')
        return render_template('play.html',
                               player=session['player'],
                               playset_name='Main St.',
                               dice_html=view.get_dice_html(dice.get_dice_from_db(GAME_ID, get_db()).dice),
                               neighbors=[cur_player.p_left_name, cur_player.p_right_name],
                               playset_html = view.get_playset_html(pd, get_db(), cur_player_name, GAME_ID))

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
        #player.clear_players(GAME_ID, get_db())
        create_db.create_db()
        return ''
    
    @app.route('/removeplayer', methods=('POST', 'GET'))
    def removeplayer():
        player.remove_player(request.form['data'], GAME_ID, get_db())
        return ''

    @app.route('/playerlist', methods=('POST', 'GET'))
    def playerlist():
        player_names = player.get_player_names_from_db(GAME_ID, get_db())
        result_str = view.get_player_list_html(player_names)
        return result_str

    @app.route('/enablecategory', methods=('POST', 'GET'))
    def enablecategory():
        name = request.form['player']
        enabled = request.form['enabled']
        cur_player = session['player']
        game_control.enable_category(name, enabled, cur_player)
        return ''

    @app.route('/setrelationship', methods=('POST', 'GET'))
    def setrelationship():
        pd = playset.parse_playset('/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt')
        result = game_control.set_relationship(request.form['rel1_name'],
                                               request.form['rel1_option'],
                                               request.form['rel1_player'],
                                               request.form['rel2_name'],
                                               request.form['rel2_option'],
                                               request.form['rel2_player'],
                                               session['player'],
                                               pd,
                                               GAME_ID,
                                               get_db())
        return ''

    @app.route('/playerjoin', methods=('POST', 'GET'))
    def playerjoin():
        name = request.form['data']
        if not name in player.get_players_from_db(GAME_ID, get_db()):
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
