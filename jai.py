from flask import *
from cacon import cassandra_connect
from random import*
from datetime import datetime,timedelta,date
from flask_mail import * 
import os

app = Flask(__name__)
account=[]
student=[]
det=["Code","Subject","Points","Assignment","Date","Time"]
stsub=["Assignment Code",'Subject','Answer','Points','Marks','Due date','Submited date']

@app.route('/', methods=['GET','POST'])
def log():
    if request.method=="GET":
        return render_template("login.html")
    else:
        
        mail=request.form['mail']
        pas=request.form['pas']

        session=cassandra_connect()
        session.execute('USE trial')
        rows = session.execute('select * from lecture where mail=%(mail)s and pwd=%(pwd)s ALLOW FILTERING',
        {'mail':mail,'pwd':pas})
        r=[]
        for l_row in rows:
            r.append([l_row.mail,l_row.pwd])
            if l_row.mail==mail and l_row.pwd==pas:
                account.append(l_row.name)
                account.append(l_row.mail) 
                account.append(l_row.pwd)      
                code=randint(1,99999) 
                print(account) 

                return render_template("upload.html",mail=account[1],code=code)
        return render_template("AllMessages.html",msg="Invalid Login Credentials",menu="Back")

@app.route('/assign',methods=['POST'])  
def upload():
    if request.method=='POST':
        code=int(request.form['code'])
        sub=request.form['sub']
        time=request.form['time']
        date=request.form['date']
        points=request.form['points']
        file = request.form['file'] 
        email=request.form['mail']
        sem=request.form['sem']

        app.config["MAIL_SERVER"]='smtp.gmail.com'  
        app.config["MAIL_PORT"] = 465  
        app.config["MAIL_USERNAME"] =account[1]  
        app.config['MAIL_PASSWORD'] =account[2]
        app.config['MAIL_USE_TLS'] = False  
        app.config['MAIL_USE_SSL'] = True

        mail = Mail(app) 

        users = []  
        session=cassandra_connect()
        session.execute('USE trial')
        rows = session.execute( 'select * from student where sem=%(sem)s ALLOW FILTERING',{'sem':sem})
        for a_row in rows:
            users.append(a_row.mail)
        #r=tuple(r)

        print(users)

        asnmsg ="Yor Lecture "+account[0]+" has assigned an assignment, you can get it by following code "+str(code)+". Submit the assignment Before Due date "+date
        print(asnmsg)
        #msgs = Message(body = Asnmsg, subject = sub+" Assignment", sender = 'nammannadon@gmail.com',recipients=users)  
        msg = Message(sub+" Assignment",sender = account[1], recipients = users)  
        msg.body = asnmsg

        mail.send(msg)  

        session=cassandra_connect()
        session.execute('USE trial')
        session.execute(
        """
        INSERT INTO assign(sub,code,date,time,points,f,mail)
        VALUES (%(sub)s,%(code)s,%(date)s,%(time)s,%(points)s,%(f)s,%(mail)s)
        """,{'sub':sub,'code':code,'time':time,'date':date,'points':points,'f':file,'mail':email},
        )

        return render_template("AllMessages.html",msg="assigned",menu="Logout",msg2="Logged in as",menu2="Submit details",mail=account[1])

@app.route('/success', methods = ['POST','GET'] )
def success():
    code=int(request.form['code'])
    session=cassandra_connect()
    session.execute('USE trial')  
    rows = session.execute('select * from submit where mail=%(mail)s and ascode=%(ascode)s ALLOW FILTERING',
    {'ascode':code,'mail':student[1]})
    r=[]
    for l_row in rows:
        r.append([l_row.mail,l_row.ascode])
        if l_row.mail==student[1] and l_row.ascode==code:
           return render_template("Msg.html",mail=student[1],msg="You have already submitted")

    code=int(request.form['code'])
    session=cassandra_connect()
    session.execute('USE trial')
    rows = session.execute( 'select * from assign where code=%(code)s',  
    {'code':code} )
    r=[]
    for a_row in rows:
         r.append([a_row.code,a_row.sub,a_row.points,a_row.f,a_row.date,a_row.time])
         r=tuple(r)
    print(r)
    return render_template("show assignment.html",r=r,det=det,zip=zip,mail=student[1])
    #return "Error"

@app.route('/submit/<int:asn>' )
def submitnow(asn):
    asid=asn
    sb=randint(000000,999999)
    now=datetime.now()
    subtime=now.strftime("%H:%M:%S")
    subdate=date.today().strftime("%b-%d-%Y");
    sid="SUBID"+str(sb)

    csession=cassandra_connect()
    csession.execute('USE trial')

    rows = csession.execute('select * from assign where code=%(code)s',
    {'code':asid})
    r=[]
    for pdt_row in rows:
        r.append([pdt_row.code,pdt_row.sub,pdt_row.points,pdt_row.mail,pdt_row.date,pdt_row.f,pdt_row.time])
    r=tuple(r)
    c=[]
    for row in r:
        for col in row:
            c.append(col)
            print(col)
    print("Submit Assignment details in c:",c)
    print("Submit ID :",sid)
    print("Submit Time :",subtime)
    print("Submit Date :",subdate)
    print("Student details in student :",student)
    return render_template("submit.html",sid=sid,usn=student[0],asc=c[0],sub=c[1],dud=c[4],dut=c[6],smail=student[1],pts=c[2],sbdt=subdate,sbtm=subtime)

@app.route('/submit', methods=['POST'])
def submit():
    sid=request.form['sid']
    sun=request.form['usn']
    asc=int(request.form['asc'])
    sub=request.form['sub']
    dud=request.form['dte']
    dut=request.form['dtm']
    lmail=request.form['email']
    pts=int(request.form['points'])
    mrs=int(request.form['mrs'])
    ans=request.form['ans']
    sbdt=request.form['sbdt']
    sbtm=request.form['sbt']
    status=request.form['status']

    session=cassandra_connect()
    session.execute('USE trial')

    session.execute(
    """
    INSERT INTO submit(subid,ascode,asignans,duedate,duetime,mail,marks,points,sub,subdate,subtime,usn)
    VALUES (%(subid)s,%(ascode)s,%(asignans)s,%(duedate)s,%(duetime)s,%(mail)s,%(marks)s,%(points)s,%(sub)s,%(subdate)s,%(subtime)s,%(usn)s)
    """
    ,{'subid':sid,"ascode":asc,'asignans':ans,"duedate":dud,'duetime':dut,"mail":lmail,'marks':mrs,"points":pts,'sub':sub,"subdate":sbdt,'subtime':sbtm,"usn":sun}
    )
            
    return render_template("Msg.html",msg="Assignment Submitted",mail=student[1])
    #return render_template("Msg.html",msg="Error!!",mail=student[1])

@app.route('/create', methods=['GET','POST'])
def add():
    if  request.method=="GET":
        return render_template("create.html")
    else:
        name=request.form['name']
        mail=request.form['mail']
        pas=request.form['pas']

        session=cassandra_connect()
        session.execute('USE trial')
        session.execute(
        """
        INSERT INTO lecture(name,mail,pwd)
        VALUES (%(name)s,%(mail)s,%(pwd)s)
        """,{'name':name,"mail":mail,'pwd':pas},
        )
        return render_template("AllMessages.html",msg="account created",menu="Login")

@app.route('/logst', methods=['GET','POST'])
def stlog():
    if request.method=="GET":
        return render_template("stlogin.html")
    else:
        usn=request.form['usn']
        pas=request.form['pas']

        session=cassandra_connect()
        session.execute('USE trial')
        rows = session.execute('select * from student where usn=%(usn)s and pas=%(pas)s ALLOW FILTERING',
        {'usn':usn,'pas':pas})
        r=[]
        for row in rows:
            r.append([row.usn,row.pas])
            if row.usn==usn and row.pas==pas:
               student.append(row.usn)
               student.append(row.mail)
               return render_template("enter.html",mail=student[1])
        r=tuple(r)
        print(student)
        return "<h2>Invalid password</h2>"

@app.route('/add account', methods=['GET','POST'])
def stadd():
    if request.method=="GET":
        return render_template("add acount.html")
    else:
        usn=request.form['usn']
        mail=request.form['mail']
        pas=request.form['pas']
        name=request.form['name']
        sem=request.form['sem']

        session=cassandra_connect()
        session.execute('USE trial')
        session.execute(
        """
        INSERT INTO student(usn,mail,pas,name,sem)
        VALUES (%(usn)s,%(mail)s,%(pas)s,%(name)s,%(sem)s)
        """,{'usn':usn,"mail":mail,'pas':pas,'name':name,'sem':sem},
        )
        return render_template("AllMessages.html",msg="Joined to Class",menu="login")

@app.route('/show/<int:j>/', methods=['GET'])
def showas(j):
    code=j    
    csession=cassandra_connect()
    csession.execute('USE trial')

    rows = csession.execute('select * from submit where code=%(code)s',
    {'code':j})
    r=[]
    for a_row in rows:
        r.append([a_row.submitid,a_row.usn,a_row.code,a_row.lecturename,a_row.subject,a_row.points,a_row.duedate,a_row.duetime,a_row.submiteddate,a_row.submitedtime,a_row.submited])
    r=tuple(r)
    #pt,br,mdl,prc,wt,st
    c=[]
    for row in r:
        for col in row:
            c.append(col)
            print(col)
    return render_template("Update.html",sid=c[0],usn=c[1],code=c[2],lname=c[3],sub=c[4],pt=c[5],ddt=c[6],dt=c[7],sdt=c[8],st=c[9],sf=c[9]) 

@app.route('/updatemarks/<asc>/<usn>', methods = ['POST','GET'] )
def alot(usn,asc):
    asc=int(asc)
    usn=usn
    csession=cassandra_connect()
    csession.execute('USE trial')

    rows = csession.execute('select * from submit where ascode=%(ascode)s and usn=%(usn)s ALLOW FILTERING',
    {'ascode':asc,'usn':usn})
    r=[]
    for a_row in rows:
        r.append([a_row.ascode,a_row.usn,a_row.sub,a_row.points,a_row.asignans,a_row.duedate,a_row.marks,a_row.subdate,a_row.subid])
    r=tuple(r)
    c=[]
    for row in r:
        for col in row:
            c.append(col)
            print(col)
    return render_template("allotmarks.html",sid=c[8],asn=c[0],usn=c[1],sub=c[2],pts=c[3],answer=c[4],due=c[5],sdt=c[7],mrs=c[6],mail=account[1])

@app.route('/allocated', methods=['POST'])
def allocated():
    sid=request.form['sid']
    asn=int(request.form['asc'])
    mrs=int(request.form['mrs'])

    session=cassandra_connect()
    session.execute('USE trial')
    session.execute(
    """
    UPDATE submit set marks=%(marks)s where subid=%(subid)s 
    """,{'subid':sid,"marks":mrs},
    )

    app.config["MAIL_SERVER"]='smtp.gmail.com'  
    app.config["MAIL_PORT"] = 465  
    app.config["MAIL_USERNAME"] =account[1]  
    app.config['MAIL_PASSWORD'] =account[2]
    app.config['MAIL_USE_TLS'] = False  
    app.config['MAIL_USE_SSL'] = True

    email = Mail(app) 

    users = []  
    session=cassandra_connect()
    session.execute('USE trial')
    rows = session.execute( 'select * from submit where subid=%(subid)s',{'subid':sid})
    for a_row in rows:
        users.append(a_row.mail)
        users.append(a_row.sub)
        #r=tuple(r)

    print(users)

    asnmsg ="Your Marks for "+users[1]+" Assignment = "+str(mrs)+". You can also check ur marks by Given Assignment Code :"+str(asn)
    print(asnmsg)
        #msgs = Message(body = Asnmsg, subject = sub+" Assignment", sender = 'nammannadon@gmail.com',recipients=users)  
    msg = Message(users[1]+"  marks",sender = account[1], recipients =[users[0]])  
    msg.body = asnmsg

    email.send(msg)
    return render_template("msg2.html",asn=asn)

@app.route('/showsub' )
def showsub():
    return render_template("lenter.html")

@app.route('/view', methods = ['POST'] )
def view(): 
    code=int(request.form['code'] )
    session=cassandra_connect()
    session.execute('USE trial')
    rows = session.execute( 'select * from submit where ascode=%(ascode)s ALLOW FILTERING',  
    {'ascode':code} )
    r=[]
    for a_row in rows:
        r.append([a_row.ascode,a_row.usn,a_row.sub,a_row.points,a_row.marks,a_row.asignans,a_row.duedate,a_row.duetime,a_row.subdate])
        #r=tuple(r)
        print(r)
    return render_template("updatemarks.html",r=r)


@app.route('/view/<int:asc>')
def view2(asc): 
    code=int(asc)
    session=cassandra_connect()
    session.execute('USE trial')
    rows = session.execute( 'select * from submit where ascode=%(ascode)s ALLOW FILTERING',  
    {'ascode':code} )
    r=[]
    for a_row in rows:
        r.append([a_row.ascode,a_row.usn,a_row.sub,a_row.points,a_row.marks,a_row.asignans,a_row.duedate,a_row.duetime,a_row.subdate])
        #r=tuple(r)
        print(r)
    return render_template("updatemarks.html",r=r,mail=account[1])

det2=['Assignment code','usn','subject','points','Marks Obtained','Assigned','Due Date','Due time','Subdate']
@app.route('/fetchMarks', methods = ['POST','GET'] )
def fetchMarks():  
    if request.method == 'GET':
        return render_template("enter2.html")
    else:
        code=int(request.form['code'])
        session=cassandra_connect()
        session.execute('USE trial')
        rows=session.execute( 'select * from submit where ascode=%(ascode)s and usn=%(usn)s ALLOW FILTERING',  
        {'ascode':code,'usn':student[0]})
        r=[]
        for a_row in rows:
            r.append([a_row.ascode,a_row.usn,a_row.sub,a_row.points,a_row.marks,a_row.asignans,a_row.duedate,a_row.duetime,a_row.subdate])
        print(r)
        return render_template("entershow.html",r=r,det=det2,zip=zip)

@app.route('/submitassigns/<mail>')
def showmyassin(mail): 
    mail=mail
    session=cassandra_connect()
    session.execute('USE trial')
    rows = session.execute( 'select * from assign where mail=%(mail)s ALLOW FILTERING',  
    {'mail':mail} )
    r=[]
    for a_row in rows:
        r.append([a_row.code,a_row.sub,a_row.mail,a_row.f,a_row.points,a_row.date,a_row.time])
        #r=tuple(r)
        print(r)
    return render_template("subdet.html",r=r,mail=account[1])

@app.route('/menu')
def menu():
    return render_template('menu1.html',mail=student[1])

@app.route('/stenter')
def enter():
    return render_template('enter.html',mail=student[1])

@app.route('/logout')
def logout():
    account.clear()
    student.clear()
    print("Account :",account)
    print("Student :",student)
    return render_template('login.html')

@app.route('/studentsub/<mail>')
def stdsub(mail): 
    mail=mail
    session=cassandra_connect()
    session.execute('USE trial')
    rows = session.execute( 'select * from submit where mail=%(mail)s and marks>0 ALLOW FILTERING',  
    {'mail':mail} )
    r=[]
    for a_row in rows:
        r.append([a_row.ascode,a_row.sub,a_row.asignans,a_row.points,a_row.marks,a_row.duedate,a_row.subdate])
        #r=tuple(r)
    print(r)
    return render_template("StudentSubmited.html",r=r,mail=student[1],det=stsub,zip=zip)

@app.route('/pending/<mail>')
def pending(mail): 
    mail=mail
    session=cassandra_connect()
    session.execute('USE trial')
    rows = session.execute( 'select * from submit where mail=%(mail)s and marks=0 ALLOW FILTERING',  
    {'mail':mail} )
    r=[]
    for a_row in rows:
        r.append([a_row.ascode,a_row.sub,a_row.asignans,a_row.points,a_row.marks,a_row.duedate,a_row.subdate])
        #r=tuple(r)
        print(r)
    return render_template("StudentSubmited.html",r=r,mail=student[1],det=stsub,zip=zip)

if __name__ == "__main__":
    app.run(debug=True)