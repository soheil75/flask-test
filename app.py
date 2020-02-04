from flask import Flask,render_template,request
from config import connection


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register',methods=['POST'])
def register():
        c,conn = connection()
        info = request.form
        username = info['username']
        password = info['password']
        c.execute('INSERT INTO users (username,password) VALUES(?, ?)',(username, password))
        conn.commit()
        c.close()
        return "ok"
    

#@app.route('/login',methods=['POST'])
#def login():
#    try:
#        c,conn = connection()
#        info = request.form
#        username = info['username']
#        password = info['password']
#        c.execute("SELECT * FROM users WHERE username = ? AND password = ? ,(username,password)")
#        user = c.fetchone()
#        if not user :
#            return "ooops this user not exist"
#        return f"welcome {user[1]}"
#    except:
#        print('false')
#    return render_template('login.html')