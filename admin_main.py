from flask import Flask, render_template, request, send_file
import PyPDF4
from fpdf import FPDF
import mysql.connector
import os
import cv2
import random
from PIL import Image, ImageChops
app = Flask(__name__, template_folder='templates')
app.config["UPLOAD_FOLDER"] = "UPLOAD_DIR/"


@app.route('/')
def show():
    return render_template('login.html')


#---------------------------------------------------------LOGIN AND LOGOUT-----------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    mail = request.form['email']
    password = request.form['password']
    db = mysql.connector.connect(host="localhost", user="root", passwd="20022002", database="ADMIN")
    mycur = db.cursor()
    sql = "select * from LOGIN where email = %s and password = %s"
    mycur.execute(sql, [mail, password])
    results = mycur.fetchall()
    if results:
        for i in results:
            break
        db.close()
        return render_template('option.html', msg="login successful")
    else:
        db.close()
        return render_template('login.html', msg="INVALID CREDENTIALS")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return render_template('login.html')
#---------------------------------------------------------LOGIN AND LOGOUT------------------------------------------------


#---------------------------------------------------------NEW MOVIE UPLOAD------------------------------------------------
@app.route('/NEW MOVIE', methods=['GET', 'POST'])
def uploadnewmovie():
    return render_template('newmovie.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
       myres=0
       mid = request.form['mid']
       name = request.form['mname']
       db = mysql.connector.connect(host="localhost", user="root", passwd="20022002", database='MOVIEINFO')
       mycur = db.cursor()
       sel = 'SELECT * FROM '
       try:
           mycur.execute(sel + mid)
           myres = mycur.fetchall()
           db.close()
       finally:
           if myres:
               return render_template('newmovie.html', msg='ID EXISTS ALREADY')
           else:
               db = mysql.connector.connect(host="localhost", user="root", passwd="20022002", database='MOVIEINFO')
               mycur = db.cursor()
               sql = 'CREATE TABLE '
               sql1 = '(FILENAME VARCHAR(200),FRAMENO BIGINT,XCO INT(200),YCO INT(200),R INT(200),G INT(200),B INT(200))'
               sqlquery = sql + mid + sql1
               mycur.execute(sqlquery)
               sql = 'insert into '
               sql1 = '(FILENAME) '
               sql2 = 'values(%s)'
               sqlquery = sql + mid + sql1 + sql2
               val = [mid + '.mp4']
               mycur.execute(sqlquery, val)
               db.commit()
               db.close()
               f = request.files['file']
               f.save(os.path.join(app.config['UPLOAD_FOLDER'], mid+'.mp4'))
               return render_template('newmovie.html', msg='MOVIE UPLOADED SUCCESSFULLY')
#---------------------------------------------------------NEW MOVIE UPLOAD------------------------------------------------


#---------------------------------------------------------NEW MOVIE FRAMES------------------------------------------------
@app.route('/NEW FRAMES', methods=['GET', 'POST'])
def newmovie():
    return render_template('frame.html')


@app.route('/NEW FRAME', methods=['GET', 'POST'])
def newm():
    moid = request.form['moid']
    dbm = mysql.connector.connect(host="localhost", user="root", passwd="20022002", database="MOVIEINFO")
    mycurm = dbm.cursor(buffered=True)
    sel = 'SELECT * FROM '
    try:
        mycurm.execute(sel + moid)
        myres = mycurm.fetchall()
        f = 1
    finally:
        if f:
            global MovieId
            MovieId = moid
            sql = 'SELECT FILENAME FROM '
            mycurm.execute(sql + MovieId)
            res = mycurm.fetchone()
            filename = 'UPLOAD_DIR/' + res[0]
            cap = cv2.VideoCapture(filename)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fr = set()
            for i in range(0, 15):
                if len(fr) < 4:
                    fr.add(random.randint(0, frame_count - 50))
            li = list(fr)
            cap = cv2.VideoCapture(filename)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            framewidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frameheight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            count = 0
            while (cap.isOpened()):
                ret, frame = cap.read()
                if count in li:
                    print(count)
                    x, y = random.randint(50, framewidth - 50), random.randint(50, frameheight - 50)
                    global img
                    img = frame
                    colorsb = img[y, x, 0]
                    colorsg = img[y, x, 1]
                    colorsr = img[y, x, 2]
                    q1 = 'INSERT INTO '
                    q2 = '(FRAMENO, XCO, YCO, R,G,B) VALUES (%s,%s,%s,%s,%s,%s)'
                    quer = q1 + MovieId + q2
                    r = int(colorsr)-15
                    g = int(colorsg)-15
                    b = int(colorsb)-15
                    if r<10:
                        r=255
                    if g<10:
                        g=255
                    if b<10:
                        b=255
                    val = (count, x, y, r, g, b)
                    mycurm.execute(quer, val)
                    dbm.commit()
                if count == frame_count:
                    break
                count += 1
            dbm.close()
        else:
            return render_template('frame.html', msg='ERROR OCCURED')
#---------------------------------------------------------NEW MOVIE FRAMES------------------------------------------------


#---------------------------------------------------------EXTRACT FRAMES--------------------------------------------------
@app.route('/EXTRACT FRAMES', methods=['GET', 'POST'])
def extframe():
    return render_template('extract.html')


@app.route('/EXTRACT PIRATED FRAMES', methods=['GET', 'POST'])
def ext():
    moid = request.form['Moid']
    dbm = mysql.connector.connect(host="localhost", user="root", passwd="20022002", database="MOVIEINFO")
    mycurm = dbm.cursor(buffered=True)
    sel = 'SELECT * FROM '
    try:
        mycurm.execute(sel + moid)
        myres = mycurm.fetchall()
    finally:
        if myres:
            f = request.files['file']
            f.save(os.path.join("PIR_DIR/", moid + '.mp4'))
            flag = 0
            sel = 'SELECT * FROM '
            try:
                mycurm.execute(sel + moid)
                myres = mycurm.fetchall()
                flag = 1
            finally:
                if flag:
                    MovieId = moid
                    query = "SELECT FRAMENO FROM "
                    qu = query + MovieId
                    mycurm.execute(qu)
                    res = mycurm.fetchall()
                    frameno = [res[2][0]]
                    sql = 'SELECT FILENAME FROM '
                    mycurm.execute(sql + MovieId)
                    res = mycurm.fetchone()
                    filename = 'UPLOAD_DIR/' + res[0]
                    cap = cv2.VideoCapture(filename)
                    fla = 0
                    while (cap.isOpened()):
                        ret, frame = cap.read()
                        fla = (fla + 1)
                        if fla in frameno:
                            name = 'f.png'
                            cv2.imwrite(name, frame)
                            break
                    cap = cv2.VideoCapture("PIR_DIR/"+moid + '.mp4')
                    f_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    f = 0
                    while (cap.isOpened()):
                        ret, frame = cap.read()
                        if f in frameno:
                            cv2.imwrite('du.jpeg', frame)
                            break
                        if f == f_count:
                            break
                        f = f + 1
                    img1 = Image.open(name)
                    img2 = Image.open('du.jpeg')
                    diff = ImageChops.difference(img1, img2)
                    diff.save('ff.png')
                    image = cv2.imread('ff.png')
                    alpha = 2.9  # Contrast control (1.0-3.0)
                    beta = 30  # Brightness control (0-100)
                    manual_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
                    cv2.imwrite("DIFFFR.jpeg", manual_result)
                    dbm.close()
                    return send_file('DIFFFR.jpeg', as_attachment=True)
        else:
            dbm.close()
            return render_template('extract.html', msg='ERROR OCCURED')
#---------------------------------------------------------EXTRACT FRAMES--------------------------------------------------


#---------------------------------------------------------PIRATER REPORT GENRATION----------------------------------------
@app.route('/REPORT', methods=['GET', 'POST'])
def regen():
    return render_template('RE.html')


@app.route('/REPORTGEN', methods=['GET', 'POST'])
def re():
    pid = request.form['moid']
    dbu = mysql.connector.connect(host="localhost", user="root", passwd="20022002", database="USER")
    mycuru = dbu.cursor(buffered=True)
    query = 'SELECT mail,PHNO,LOC FROM LOGIN WHERE id=%s'
    mycuru.execute(query, [pid, ])
    global repo
    res = mycuru.fetchone()
    repo = res
    if res:
        dbu.close()
        return render_template('INFO.html', mail=res[0], phno=res[1], loc=res[2])
    else:
        dbu.close()
        return render_template('INFO.html', msg="USER ID DOESNT EXISTS")
#---------------------------------------------------------PIRATER REPORT GENRATION----------------------------------------


#---------------------------------------------------------MAIL SENDING----------------------------------------
@app.route('/sendmail', methods=['GET', 'POST'])
def sendmail():
    return render_template('mail2.html', msg=repo[0])
#---------------------------------------------------------MAIL SENDING----------------------------------------


#---------------------------------------------------------REPORT DOWLOAD----------------------------------------
@app.route('/dow', methods=['GET', 'POST'])
def do():
    pdf = FPDF()
    pdf.add_page()
    pdf.header()
    pdf.set_font("Arial", size=25)
    pdf.cell(200, 20, txt="REPORT AT ADMIN END",
             ln=5, align='C')
    pdf.cell(200, 55, txt="EMAIL ID ->> " + repo[0],
             ln=55, align='L')
    pdf.cell(200, 85, txt="LOCATION ->>" + repo[2],
             ln=85, align='L')
    pdf.cell(200, 105, txt="PHONE NUMBER ->>" + str(repo[1]),
             ln=105, align='L')
    pdf.output("GFG.pdf")
    PyPDF4.PdfFileReader('GFG.pdf')
    return send_file('GFG.pdf', as_attachment=True)
#---------------------------------------------------------REPORT DOWLOAD----------------------------------------


if __name__ == "__main__":
    app.run(debug=True, port=3400)
