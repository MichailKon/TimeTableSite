import flask
from flask import jsonify, request

from data import db_session
from data.homework import Homework

blueprint = flask.Blueprint(
    'homework_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/v1/homework', methods=['GET'])
def get_all_schedule():
    db_sess = db_session.create_session()
    hmw = db_sess.query(Homework).all()
    return jsonify(
        {
            'homeworks': [item.to_dict() for item in hmw]
        }
    )


@blueprint.route('/api/v1/homework/<int:homework_id>', methods=['GET'])
def get_one_homework(homework_id):
    db_sess = db_session.create_session()
    hmw = db_sess.query(Homework).get(homework_id)
    if not hmw:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'homework': hmw.to_dict()
        }
    )


@blueprint.route('/api/v1/homework', methods=['POST'])
def add_homework():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ('homework_id', 'homework_schedule', 'homework_week',
                  'homework_year', 'homework_text')):
        return jsonify({'error': 'Wrong request'})

    db_sess = db_session.create_session()
    exist = db_sess.query(Homework).get(request.json['homework_id'])
    if exist:
        return jsonify({'error': 'This id already exist'})

    try:
        new_hmw = Homework(
            homework_id=int(request.json['homework_id']),
            homework_schedule=int(request.json['homework_schedule']),
            homework_week=int(request.json['homework_week']),
            homework_year=int(request.json['homework_year']),
            homework_text=request.json['homework_text']
        )
    except ValueError:
        return jsonify({'error': 'All fields must be integers'})
    db_sess.add(new_hmw)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/v1/homework/<int:homework_id>', methods=['DELETE'])
def delete_homework(homework_id):
    db_sess = db_session.create_session()
    exist = db_sess.query(Homework).get(homework_id)
    if not exist:
        return jsonify({'error': 'Not exist'})
    db_sess.delete(exist)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/v1/homework/<int:homework_id>', methods=['PUT'])
def upd_homework(homework_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    db_sess = db_session.create_session()
    hmw = db_sess.query(Homework).get(homework_id)
    if not hmw:
        return jsonify({'error': 'Not found'})
    hmw: Homework
    for key in ('homework_schedule', 'homework_week',
                'homework_year', 'homework_text'):
        if key not in request.json:
            continue
        if key == 'homework_text':
            hmw.homework_text = request.json[key]
        else:
            try:
                exec(f'hmw.{key} = {int(request.json[f"{key}"])}')
            except ValueError:
                return jsonify({'error': f'Field {key} must be integer'})
    db_sess.commit()
    return jsonify({'success': 'OK'})
