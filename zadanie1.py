from flask import Flask, request, g, jsonify, Response
import sqlite3
from datetime import datetime


app = Flask(__name__)

# location of database
DATABASE = './zadanie1.db'

def get_db():
    """
    Connects to SQL database.

    Returns:
            database
    """

    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def get_task():
    """
    Gets data from input JSON.

    Returns:
            JSON
    """

    task_data = request.get_json()
    if not task_data:
        pass
    return task_data


@app.route('/todolist', methods=['GET', 'POST'])
def todolist():
    """
    Returns list of JSONs of all tasks in database with GET method.
    Or adds new task to database from input JSON with POST method
    and returns JSON with id value of that task.
    """

    db = get_db()
    cursor = db.cursor()

    # returns list of JSONs of all tasks 
    if request.method == 'GET':
        data = cursor.execute('''SELECT * FROM zadania''').fetchall()
        cursor.close()
        return jsonify([dict(i) for i in data])


    elif request.method == 'POST':
        data = get_task()
        task_title = data.get('title')
        # if done is not given, sets done to false
        if 'done' not in data.keys():
            task_done = 0
        else:
            task_done = data.get('done')
        task_done_date = data.get('done_date')
        task_author_ip = request.remote_addr
        
        # if done:false and done_date is not null, returns 400
        if task_done == 0 and task_done_date is not None:
            return Response(status = 400)

        # if done:false, adds task without done_date value
        elif task_done == 0:
            cursor.execute('''INSERT INTO zadania (title, done, author_ip) VALUES (?, ?, ?)''',
                            (task_title, task_done, task_author_ip))
            db.commit()
            return_data = cursor.execute("SELECT id FROM zadania WHERE id = ?", (str(cursor.lastrowid),)).fetchone()
            cursor.close()
            return jsonify(dict(return_data))

        # if done:true and done_date is given, adds task with these values 
        elif task_done == 1 and task_done_date:
            cursor.execute('''INSERT INTO zadania (title, done, author_ip, done_date) VALUES (?, ?, ?, ?)''',
                            (task_title, task_done, task_author_ip, task_done_date ))
            db.commit()
            return_data = cursor.execute("SELECT id FROM zadania WHERE id = ?", (str(cursor.lastrowid),)).fetchone()
            cursor.close()
            return jsonify(dict(return_data))

        # if done:true and done_date is null, adds task with current time
        elif task_done == 1 and task_done_date is None:
            task_done_date = datetime.utcnow()
            cursor.execute('''INSERT INTO zadania (title, done, author_ip, done_date) VALUES (?, ?, ?, ?)''',
                            (task_title, task_done, task_author_ip, task_done_date ))
            db.commit()
            return_data = cursor.execute("SELECT id FROM zadania WHERE id = ?", (str(cursor.lastrowid),)).fetchone()
            cursor.close()
            return jsonify(dict(return_data))


@app.route('/todolist/<id_zadania>', methods=['GET', 'PATCH', 'DELETE'])
def id_zadania(id_zadania):
    """
    Deletes task from database with id given as a parameter.
    Returns JSON of task with id given as a parameter.
    Updates task with id given as a parameter with values given in JSON
    and returns 204 if operation was successful.
    """

    db = get_db()
    cursor = db.cursor()


    if request.method == 'GET':

        # if task with given id does not exist, returns 404
        data = cursor.execute('''SELECT id FROM zadania WHERE id = ?''',(id_zadania,)).fetchone()
        if not data:
            cursor.close()
            return Response(status = 404)

        # else returns JSON of task's values
        else:
            return_data = cursor.execute('''SELECT title, done, author_ip, created_date, done_date FROM zadania
                                            WHERE id = ?''', (id_zadania,)).fetchone()
            cursor.close()
            return jsonify(dict(return_data))


    elif request.method == 'DELETE':

        # if task with given id does not exist, returns 404
        data = cursor.execute('''SELECT id FROM zadania WHERE id = ?''',(id_zadania,)).fetchone()
        if not data:
            cursor.close()
            return Response(status = 404)
        
        # else deletes task with given id and returns 204
        else:
            cursor.execute('''DELETE FROM zadania WHERE id = ?''',(id_zadania,))
            db.commit()
            cursor.close()
            return Response(status = 204)


    elif request.method == 'PATCH':

        # if task with given id does not exist, returns 404
        data = cursor.execute('''SELECT id FROM zadania WHERE id = ?''',(id_zadania,)).fetchone()
        if not data:
            cursor.close()
            return Response(status = 404)

        # if some value is not given in JSON, updates with existing value from task
        else:
            json_data = get_task()
            if 'done' not in json_data.keys():
                task_done = cursor.execute('''SELECT done FROM zadania WHERE id = ?''',(id_zadania,)).fetchone()
            else:
                task_done = json_data.get('done')

            if 'done_date' not in json_data.keys():
                task_done_date = cursor.execute('''SELECT done_date FROM zadania WHERE id = ?''',(id_zadania,)).fetchone()
            else:
                task_done_date = json_data.get('done_date')

            if 'title' not in json_data.keys():
                task_title = cursor.execute('''SELECT title FROM zadania WHERE id = ?''',(id_zadania,)).fetchone()
            else:
                task_title = json_data.get('title')

            # if done:true and done_date is not given, updates with current time
            if task_done == 1 and task_done_date is None:
                task_done_date = datetime.utcnow()
                cursor.execute('''UPDATE zadania SET title=?, done=?, done_date=? WHERE id = ?'''
                                ,(task_title, task_done, task_done_date, id_zadania))
                db.commit()
                cursor.close()
                return Response(status = 204)

            # if done:false and done_date is not null, returns 400
            elif task_done == 0 and task_done_date is not None:
                return Response(status = 400)
            
            # if done is changed from true to false, updates done_date to None
            elif cursor.execute('''SELECT done FROM zadania WHERE id = ?''',(id_zadania,)).fetchone() == 1 and task_done == 0:
                cursor.execute('''UPDATE zadania SET title=?, done=?, done_date=? WHERE id = ?'''
                                ,(task_title, task_done, None, id_zadania))
                db.commit()
                cursor.close()
                return Response(status = 204)

            # else updates with all values given in JSON
            else:
                cursor.execute('''UPDATE zadania SET title=?, done=?, done_date=? WHERE id = ?'''
                                ,(task_title, task_done, task_done_date, id_zadania))
                db.commit()
                cursor.close()
                return Response(status = 204)


if __name__ == '__main__':
    app.run(debug=True)