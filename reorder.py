from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import util
import random, pymysql, json, re, os

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database (Change database address when deploying)
engine = create_engine(os.getenv("DATABASE_URL"))
db = engine.connect()


# Home Page: choose to play existing games or create new
@app.route('/')
def index():
    """Load home page"""

    query="CREATE TABLE IF NOT EXISTS approved_games(game_id BIGINT(20) PRIMARY KEY, username VARCHAR(50) NOT NULL, user_email VARCHAR(255) NOT NULL, game_type enum('video','text','pictures','mixed') NOT NULL, game_length INTEGER NOT NULL, game_category enum('Abbigliamento','Albergo','Banca','Bar/Ristorante','Casa','Chiaroveggente','Concerto','Dottore','Meccanico','Mercato','Mezzi di comunicazione','Mezzi di trasporto','Scuola','Tempo') NOT NULL, game_title VARCHAR(255) NOT NULL, game_content json NOT NULL)"
    db.execute(query)
    
    query="CREATE TABLE IF NOT EXISTS game_scores(score_id SERIAL PRIMARY KEY, username VARCHAR(50) NOT NULL, game_difficulty ENUM('easy', 'medium', 'difficult') NOT NULL, game_type enum('video','text','pictures','mixed') NOT NULL, played_game_id BIGINT(20) NOT NULL, game_time TIME NOT NULL)"
    db.execute(query)
    
    query="SHOW TABLES"
    numtables = db.execute(query)

    if 'gameid' in session:
        session.pop('gameid', None)

    return render_template('index.html', numtables=numtables)

@app.route('/seetimes')
def seetimes():
    query = "SELECT username, game_difficulty, game_type, played_game_id, SEC_TO_TIME(game_time) AS game_time_sec FROM game_scores"
    scores = db.execute(query)

    return render_template('scores.html', scores=scores)

##----------------------------------------------------------PLAY GAME------------------------------------------------------------##

@app.route('/choosegames')
def choosegames():
    """Select Game to Play"""

    if 'gameid' in session:
        session.pop('gameid', None)

    return render_template('choosegames.html')

@app.route('/playgame', methods=["POST"])
def playgame():
    username = request.form.get("username")

    gametype = request.form["gametype"]
    gamedifficulty = request.form["gamedifficulty"]

    if gamedifficulty == 'easy':
        query = f"SELECT game_id, game_content FROM approved_games WHERE game_type='{gametype}' and game_length<=7 order by rand() limit 1"
    elif gamedifficulty == 'difficult':
        query = f"SELECT game_id, game_content FROM approved_games WHERE game_type='{gametype}' and game_length>=11 order by rand() limit 1"
    else:
        query = f"SELECT game_id, game_content FROM approved_games WHERE game_type='{gametype}' and game_length>=8 and game_length<=10 order by rand() limit 1"

    game = db.execute(query).fetchone()
    gameid = game[0]
    segmentvalues = json.loads(game[1])

    session['mode'] = 'game'
    session['gameid'] = gameid
    session['segmentvalues'] = segmentvalues
    session['username'] = username
    session['gamedifficulty'] = gamedifficulty
    session['gametype'] = gametype

    if gametype == 'text':
        return redirect(url_for('textgame'))


@app.route('/textgame')
def textgame():
    """Preview what value is entered into each card"""

    segmentvalues = session.get('segmentvalues')

    if 'gameid' in session:
        game_id = session.get('gameid')
    else:
        game_id = None

    if 'mode' in session:
        mode = session.get('mode')

    boxes = []
    cards = []
    order = dict()
    for i in range(0, len(segmentvalues)):
        value = segmentvalues.get(f'{i}')
        cards.append(value)
        order[value] = i
    boxes = cards.copy()
    random.shuffle(cards)
    random.shuffle(cards)
    random.shuffle(cards)
    cardnum = len(cards)
    return render_template("reorder.html", order=order, cards=cards, boxes=boxes, cardnum=cardnum, mode=mode, game_id=game_id)


@app.route('/submittime', methods=["POST"])
def submittime():
    timer = int(request.form["time"])
    
    if 'gameid' in session:
        gameid = session.get("gameid")
    
    username = session.get("username")
    gamedifficulty = session.get("gamedifficulty")
    gametype = session.get("gametype")

    query = "INSERT INTO game_scores(username, game_difficulty, game_type, played_game_id, game_time) VALUES(%s, %s, %s, %s, %s)"
    val = (username, gamedifficulty, gametype, gameid, timer)
    db.execute(query, val)

    session.pop('username', None)
    session.pop('gamedifficulty', None)
    session.pop('gametype', None)
    session.pop('segmentvalues', None)
    session.pop('gameid', None)

    return redirect(url_for('seetimes'))
    

##---------------------------------------------------MANAGE GAMES (FOR ADMIN)-------------------------------------------------------##


@app.route('/managegames')
def managegames():
    """Show game database to administrator only"""

    query = "SELECT game_id, game_type, game_length, game_category, game_title, username, user_email FROM to_approve_games"
    toapprove = db.execute(query)
    query = "SELECT game_id, game_type, game_length, game_category, game_title, username, user_email FROM approved_games"
    approved = db.execute(query)
    return render_template('managegames.html', toapprove=toapprove, approved=approved)


@app.route('/adminpreview/<table>/<game_id>')
def adminpreview(table, game_id):
    """Preview games in databases to administrator"""

    query = f"SELECT game_content FROM {table} WHERE game_id={game_id}"
    segmentvalues = json.loads(db.execute(query).fetchone()[0])
    session['segmentvalues'] = segmentvalues

    query = f"SELECT game_type FROM {table} WHERE game_id={game_id}"
    gametype = db.execute(query).fetchone()[0]

    if table=='to_approve_games':
        session['mode'] = 'adminapprove'
    elif table=='approved_games':
        session['mode'] = 'preview'

    session['gameid'] = game_id

    if gametype == 'text':
        return redirect(url_for('textgame'))


@app.route('/adminapprove/<game_id>')
def adminapprove(game_id):
    """Lets administrator approve user-submitted games (by moving a game from to_approve_games table to approved_games table in MySQL)"""

    query = f"SELECT game_category FROM to_approve_games WHERE game_id={game_id}"
    category = db.execute(query).fetchone()[0]

    allcatquery, allcat = util.getCategories('approved_games')

    if category not in allcat:
        query = f"ALTER TABLE approved_games MODIFY COLUMN game_category {allcatquery[:len(allcatquery)-1]}, '{category}')"
        db.execute(query)
    
    query = f"INSERT INTO approved_games SELECT game_id, username, user_email, game_type, game_length, game_category, game_title, game_content from to_approve_games WHERE game_id={game_id}"
    db.execute(query)
    query = f"DELETE FROM to_approve_games WHERE game_id={game_id}"
    db.execute(query)
    
    return redirect(url_for('managegames'))


@app.route('/admindiscard/<table>/<game_id>')
def admindiscard(table, game_id):
    """Lets administrator delete games (from either to_approve_games or approved_games table)"""

    query = f"DELETE FROM {table} WHERE game_id={game_id}"
    db.execute(query)

    return redirect(url_for('managegames'))


##------------------------------------------------- CREATE GAME--------------------------------------------------------------------##

@app.route('/cancelcreate')
def cancelcreate():
    """Let user cancel game creation, deletes autosaved game info from session"""

    if 'gametitle' in session:
        session.pop('username', None)
        session.pop('useremail', None)
        session.pop('gametitle', None)
        session.pop('gametype', None)
        session.pop('gamecategory', None)
        session.pop('allcatquery', None)
        session.pop('newcat', None)
        if 'segmentvalues' in session:
            session.pop('segmentvalues', None)
        if 'gameinput' in session:
            session.pop('gameinput', None)
    return redirect(url_for('index'))



@app.route('/gameinfo')
def gameinfo():
    """Generate form to submit new game"""

    # Load form input values if in session
    if 'gametitle' in session:
        username = session.get('username')
        useremail = session.get('useremail')
        gametitle = session.get('gametitle')
        gametype = session.get('gametype')
        gamecategory = session.get('gamecategory')
        newcat = session.get('newcat')
        saved = {'username': username, 'useremail': useremail, 'gametitle':gametitle, 'gametype':gametype, 'gamecategory':gamecategory, 'newcat':newcat}
    else:
        saved = dict()

    allcatquery, allcat = util.getCategories('to_approve_games')

    session['allcatquery'] = allcatquery
    session['allcat'] = allcat
    session['saved'] = saved
    message=""
    return render_template("gameinfo.html", allcat=allcat, saved=saved, message=message)


@app.route('/create', methods=["GET", "POST"])
def create():
    """Store form input to submit new game"""

    if 'gametype' in session:
        gametype = session.get('gametype')

    if 'allcat' in session:
        allcat = session.get('allcat')
        saved = session.get('saved')

    # Load game content if in session
    if 'segmentvalues' in session:
        segmentvalues = session.get('segmentvalues')
    else:
        segmentvalues = dict()
    if 'gameinput' in session:
        gameinput = session.get('gameinput')
    else:
        gameinput = ""

    if request.method == 'POST':
        # Save form input into variables
        # Do not ask for username & password game is housed in larger website.
        # Instead get username & e-mail from session
        username = str(request.form.get("username"))
        useremail = str(request.form.get("useremail"))
        gametitle = str(request.form.get("gametitle"))
        gametype = str(request.form.get("gametype"))
        gamecategory = str(request.form.get("gamecategory"))
        newcat = ""

        # If 'Other' category is selected, save the string input into new category
        if gamecategory == "Other":
            gamecategory = str(request.form.get("newcategory"))
            if gamecategory not in allcat:
                newcat = "other"
            else:
                message = "The category you entered already exists. Please select it from the dropdown menu."
                return render_template("gameinfo.html", allcat=allcat, saved=saved, message=message)
        
        # Store form input into session
        session['username'] = username
        session['useremail'] = useremail
        session['gametitle'] = gametitle
        session['gametype'] = gametype
        session['gamecategory'] = gamecategory
        session['newcat'] = newcat
        session['mode'] = 'createpreview'

    if gametype == 'text':
        return render_template("createtext1.html", segmentvalues=segmentvalues, gameinput=gameinput)


@app.route('/createtext2a', methods=["POST"])
def createtext2a():
    """Store values entered into each card from multiple fields"""

    segmentvalues = request.form.to_dict()
    gameinput = "multifields"

    gamelength = len(dict(segmentvalues))

    session['segmentvalues'] = segmentvalues
    session['gamelength'] = gamelength
    session['gameinput'] = gameinput
    return render_template("previewtext.html", segmentvalues=segmentvalues)


@app.route('/createtext2b', methods=["POST"])
def createtext2b():
    """Automatically cut paragraphs into sentences, and store each sentence into each card"""

    gameinput = "paragraph"

    # Get text from textarea
    paragraph = str(request.form.get("inputparagraph"))

    # Remove extra whitespace
    paragraph = paragraph.strip()
    paragraph = re.sub("\s+", " ", paragraph)

    # Add each sentence ending with period, question mark, or exclamation mark as a dictionary item
    ## Figure out how to detect multiple punctuations in a row
    segmentvalues = dict()
    sentence=""
    j=0
    for i in range(len(paragraph)):
        if (paragraph[i] in '.!?') or (i==(len(paragraph)-1)):
            sentence += paragraph[i]
            segmentvalues.update({f'{j}': sentence})
            sentence = ""
            j += 1
        else:
            sentence += paragraph[i]

    gamelength = len(segmentvalues)

    session['segmentvalues'] = segmentvalues
    session['gamelength'] = gamelength
    session['gameinput'] = gameinput

    return render_template("previewtext.html", segmentvalues=segmentvalues)


# Create New Game - Step4: preview card reordering game


# Create New Game - Step5: save game into SQL database
@app.route('/save')
def save():
    """Save game information into SQL table to be reviewed by administrator"""

    segmentvalues = session.get('segmentvalues')
    gamecontent = json.dumps(segmentvalues)
    username = session.get('username')
    useremail = session.get('useremail')
    gametitle = session.get('gametitle')
    gamelength = session.get('gamelength')
    gametype = session.get('gametype')
    gamecategory = session.get('gamecategory')
    newcat = session.get('newcat')
    allcatquery = session.get('allcatquery')
    if newcat == "other":
        query = f"ALTER TABLE to_approve_games MODIFY COLUMN game_category {allcatquery[:len(allcatquery)-1]}, '{gamecategory}')"
        db.execute(query)
    query = "INSERT INTO to_approve_games(username, user_email, game_title, game_length, game_type, game_category, game_content) VALUES(%s, %s, %s, %s, %s, %s, %s)"
    val = (username, useremail, gametitle, gamelength, gametype, gamecategory, gamecontent)
    db.execute(query, val)

    # Remove any previous form input from session
    # Do not drop username & useremail from session if housed in larger website
    session.pop('username', None)
    session.pop('useremail', None)
    session.pop('gametitle', None)
    session.pop('gamelength', None)
    session.pop('gametype', None)
    session.pop('gamecategory', None)
    session.pop('allcatquery', None)
    session.pop('newcat', None)
    session.pop('segmentvalues', None)
    session.pop('saved', None)
    if 'gameinput' in session:
        session.pop('gameinput', None)
    if 'mode' in session:
        session.pop('mode', None)

    return render_template("saved.html")

if __name__=='__main__':
    app.run(debug=True)
