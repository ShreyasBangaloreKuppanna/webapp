from flask import Flask , render_template , flash , redirect , url_for , session, logging,request
from flask_mysqldb import MySQL
import MySQLdb
import pymysql
from wtforms import Form,StringField, TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps



app = Flask(__name__)

conn = pymysql.Connect(host='localhost',user='root',password='',db='registration')

class RegisterForm(Form):
    name = StringField('name', [validators.length(min=1,max=50)])
    username = StringField('username', [validators.length(min=1,max=50)])
    email=StringField('email', [validators.length(min=1,max=50)])
    password= PasswordField('password',[
        validators.DataRequired(),
        validators.EqualTo('confirm',message='no match ')
    ])
    confirm = StringField('confirm')

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
         fname=form.name.data
         fusername=form.username.data
         femail=form.email.data
         fpassword=sha256_crypt.encrypt(str(form.password.data))

         #print(fname, fusername,femail,fpassword )
         cursor = conn.cursor()
         cursor.execute("INSERT INTO `user` (`name`, `username`, `email`, `password`)"
                        " VALUES(%s, %s, %s, %s )",(fname, fusername, femail, fpassword))

         conn.commit()

         cursor.close()
         flash('you are now registered','success')
         return redirect(url_for('index'))
    return render_template("register.html", form=form)


@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        password_entered= request.form['password']
        print(username)
        print(password_entered)


        cursor=conn.cursor()
        result=cursor.execute("SELECT * FROM `user` WHERE name = %s",[username])
        print(result)

        if (result>0):
            password = cursor.fetchone()[3]


            if sha256_crypt.verify(password_entered,password):
                session['logged_in']=True
                session['username']=username
                flash('You are logged in ','success')

                print("Yes matched" )
                app.logger.info('Password matched')
                return redirect(url_for('index'))

            else:
                print("not matched")
                app.logger.info('password unmatched')
                error='Password not matched'
                return render_template("login.html", error=error)
            cursor.close()
        else:
            print("no user")
            error= 'Username not found'
            return render_template("login.html", error= error )

    return render_template("login.html" )



@app.route("/logout")

def logout():
    session['logged_in'] = False
    session.clear()
    flash('You are now successfully logged out','success')
    return redirect(url_for('login'))


def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('unauthorised ,pls login','danger')
            return redirect(url_for('login'))
    return wrap


@app.route("/")
#@is_logged_in
def index():
    return render_template("dashboard.html", )


class ticketform(Form):
    problem = StringField('problem', [validators.length(min=1,max=50)])
    device = StringField('device', [validators.length(min=1,max=10)])


@app.route("/newticket",methods=['GET','POST'])

#@is_logged_in
def newticket():
    form = ticketform(request.form)
    if request.method == 'POST' :
        print("starting to create ticket")

        problem = form.problem.data
        device = form.device.data

        print(problem)
        print(device)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO `ticket` (`problem`,`device`)"
                       " VALUES(%s, %s)", (problem,device ))
        conn.commit()

        cursor.close()
        flash('you have created ticket', 'success')
        return redirect(url_for('index'))



    return render_template("newticket.html", )



@app.route("/ticketlist")
#@is_logged_in
def ticketlist():
    cursor = conn.cursor()
    result=cursor.execute("SELECT * FROM ticket ")
    tickets=cursor.fetchall()
    if result>0:
        return render_template("ticketlist.html",tickets=tickets )
    else:
        msg='no articles found'
        return render_template("ticketlist.html", )
    cursor.close




@app.route("/editticket/<string:number>",methods=['GET','POST'])

@is_logged_in
def editticket(number):
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM ticket WHERE ticketnumber= %s", [number])
    ticket = cursor.fetchone()
    print(ticket[0])
    print(ticket[1])

    form = ticketform(request.form)

    form.problem.data= 'abcde'
    form.device.data='pqrst'

    if request.method == 'POST'  and form.validate() :
        print("update ticket")


        problem = request.form['problem']
        device = request.form['device']

        print(problem)
        print(device)
        cursor = conn.cursor()
        cursor.execute("UPDATE ticket set problem = %s device= %s WHERE ticketnumber=%s", (problem,device,number))
        conn.commit()

        cursor.close()
        flash('ticket updated', 'success')
        return redirect(url_for('editticket'))



    return render_template("editticket.html", form=form )


@app.route("/page1")
@is_logged_in
def page1():
    return render_template("page1.html", )

@app.route("/page2")
@is_logged_in
def page2():
    return render_template("page2.html", )


@app.route("/page3")
@is_logged_in
def page3():
    return render_template("page3.html", )




if __name__=="__main__":
    app.secret_key='secret123'
    app.run()










