from bottle import route, run
import sqlite3
import os
import notecard
from periphery import I2C
from datetime import datetime

#def setup_notecard():
#Make sure to Turn On i2c on Pi
port = I2C('/dev/i2c-1')
nCard = notecard.OpenI2C(port,0,0)

productUID = 'PRODUCTID'

req = {'req':'hub.set'}
req['product'] = productUID
req['mode'] = 'continuous'
req['inbound'] = 2
rsp = nCard.Transaction(req)
print(rsp)

def create_db():
    print('craete db')
    #Connect or Create Database and Table
    current_directory = os.path.dirname(os.path.abspath(__file__))
    db_name = 'message.db'
    file_path = os.path.join(current_directory, db_name)

    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    create_table = '''
    create table if not exists message(
        id integer primary key,
        timestamp_notecard text,
        message text
    )
    '''

    cursor.execute(create_table)

    conn.commit()
    conn.close()

def db_select():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    db_name = 'message.db'
    file_path = os.path.join(current_directory, db_name)
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    sql = 'select * from message order by timestamp_notecard desc'
    cursor.execute(sql)
    record = cursor.fetchall()

    conn.commit()
    conn.close()

    return record

def db_insert(time, message):
    print(f'insert db {time} {message}')
    current_directory = os.path.dirname(os.path.abspath(__file__))
    db_name = 'message.db'
    file_path = os.path.join(current_directory, db_name)

    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    sql = 'insert into message(timestamp_notecard, message) values(?,?)'
    cursor.execute(sql,(time,message))

    conn.commit()
    conn.close()

def message_get():
    #Get New Notes from Notehub, and Delete 
    req = {'cmd':'hub.sync'}
    nCard.Command(req)

    req = {"req":"note.changes"}
    req["file"] = "data.qi"
    req["delete"] = True
    print(f'req: {req}')
    rsp = nCard.Transaction(req)
    print(f'rsp: {rsp}')

    for outer_key, inner_dict in rsp.items():
        if 'message' in str(inner_dict):
            for key, value in inner_dict.items():
                print(f"Time:  {value['time']} Message:  {value['body']['message']}")
                db_insert(value['time'], value['body']['message'])

    timestamp_refresh = datetime.now()
    
    return timestamp_refresh

@route('/')
def index():
    timestamp_refresh = message_get()

    record = db_select()
    record_page =   '''
                    <table>
                        <tr>
                            <th>ID</th>
                            <th>Time Stamp</th>
                            <th>Message</th>
                        </tr>
                    '''
    for x in record:
        timestamp = datetime.fromtimestamp(int(x[1])).strftime('%a %H:%M:%S')
        record_page =   f'''
                        {record_page}
                        <tr>
                        <td>{x[0]}</td>
                        <td>{timestamp}</td>
                        <td>{x[2]}</td>
                        </tr>
                        '''

    record_page = f'{record_page} </table>'
    header = f'''
            <meta http-equiv="refresh" content="5">
            <h1>Message App</h1>
            <p>Last Refresh: {timestamp_refresh}</p>
            '''


    page = f'{header} {record_page}'

    return page

create_db()

run(host='0.0.0.0', port=8080, debug=True)
