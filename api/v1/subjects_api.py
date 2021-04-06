import flask
from flask import jsonify, request

from data import db_session
from data.subjects import Subject

blueprint = flask.Blueprint(
    'subjects_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/v1/subjects', methods=['GET'])
def get_all_subjects():
    db_sess = db_session.create_session()
    subjects = db_sess.query(Subject).all()
    return jsonify(
        {
            'subjects': [item.to_dict() for item in subjects]
        }
    )


@blueprint.route('/api/v1/subjects/<int:subject_id>', methods=['GET'])
def get_one_subject(subject_id):
    db_sess = db_session.create_session()
    subj = db_sess.query(Subject).get(subject_id)
    if not subj:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'subject': subj.to_dict()
        }
    )


@blueprint.route('/api/v1/subjects', methods=['POST'])
def add_subject():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ('subject_id', 'subject_name')):
        return jsonify({'error': 'Wrong request'})

    db_sess = db_session.create_session()
    exist = db_sess.query(Subject).get(request.json['subject_id'])
    if exist:
        return jsonify({'error': 'This id already exist'})

    try:
        new_subj = Subject(
            subject_id=int(request.json['subject_id']),
            subject_name=request.json['subject_name'],
        )
    except ValueError:
        return jsonify({'error': 'Id must be integer'})
    db_sess.add(new_subj)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/v1/subjects/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    db_sess = db_session.create_session()
    exist = db_sess.query(Subject).get(subject_id)
    if not exist:
        return jsonify({'error': 'Not exist'})
    db_sess.delete(exist)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/v1/subjects/<int:subject_id>', methods=['PUT'])
def upd_subject(subject_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    db_sess = db_session.create_session()
    sch = db_sess.query(Subject).get(subject_id)
    if not sch:
        return jsonify({'error': 'Not found'})
    sch: Subject
    for key in ['subject_name', ]:
        if key not in request.json:
            continue
        exec(f'sch.{key} = "{request.json[f"{key}"]}"')
    db_sess.commit()
    return jsonify({'success': 'OK'})
