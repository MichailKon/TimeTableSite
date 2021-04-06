import flask
from flask import jsonify, request

from data import db_session
from data.schedules import Schedule

blueprint = flask.Blueprint(
    'schedule_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/v1/schedule', methods=['GET'])
def get_all_schedule():
    db_sess = db_session.create_session()
    schedule = db_sess.query(Schedule).all()
    return jsonify(
        {
            'schedules': [item.to_dict() for item in schedule]
        }
    )


@blueprint.route('/api/v1/schedule/<int:schedule_id>', methods=['GET'])
def get_one_schedule(schedule_id):
    db_sess = db_session.create_session()
    sch = db_sess.query(Schedule).get(schedule_id)
    if not sch:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'schedule': sch.to_dict()
        }
    )


@blueprint.route('/api/v1/schedule', methods=['POST'])
def add_schedule():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ('schedule_id', 'schedule_day', 'schedule_num', 'schedule_subject')):
        return jsonify({'error': 'Wrong request'})

    db_sess = db_session.create_session()
    exist = db_sess.query(Schedule).get(request.json['schedule_id'])
    if exist:
        return jsonify({'error': 'This id already exist'})

    try:
        new_sch = Schedule(
            schedule_id=int(request.json['schedule_id']),
            schedule_day=int(request.json['schedule_day']),
            schedule_num=int(request.json['schedule_num']),
            schedule_subject=int(request.json['schedule_subject']),
        )
    except ValueError:
        return jsonify({'error': 'All fields must be integers'})
    db_sess.add(new_sch)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/v1/schedule/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    db_sess = db_session.create_session()
    exist = db_sess.query(Schedule).get(schedule_id)
    if not exist:
        return jsonify({'error': 'Not exist'})
    db_sess.delete(exist)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/v1/schedule/<int:schedule_id>', methods=['PUT'])
def upd_schedule(schedule_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    db_sess = db_session.create_session()
    sch = db_sess.query(Schedule).get(schedule_id)
    if not sch:
        return jsonify({'error': 'Not found'})
    sch: Schedule
    for key in ['schedule_day', 'schedule_subject', 'schedule_num']:
        if key not in request.json:
            continue
        try:
            exec(f'sch.{key} = {int(request.json[f"{key}"])}')
        except ValueError:
            return jsonify({'error': 'All fields must be integers'})
    db_sess.commit()
    return jsonify({'success': 'OK'})
