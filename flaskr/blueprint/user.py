from flaskr import db
from flaskr.database import User, TeamMember, Team, Notice
from flask import Blueprint, request, jsonify
from ..function import is_none, is_int
from datetime import datetime

user = Blueprint("user", __name__, url_prefix='/user')


@user.route('/add')
def add_user():
    id = request.args.get('id')
    name = request.args.get('name')
    sex = request.args.get('sex')
    if id is None or name is None or sex is None:
        return 'incomplete data'
    try:
        id = int(id)
    except ValueError:
        return 'id type error'
    if len(name) > 15:
        return 'name too long'
    if sex not in ['男', '女']:
        return 'sex error'
    user = User.query.get(id)
    if user is not None:
        return 'id is exists'
    user = User(id=id, name=name, sex=sex)
    db.session.add(user)
    db.session.commit()
    return 'add user success'


@user.route('/isLeader')
def is_leader():
    user_id = request.args.get('userID')
    if is_none([user_id]):
        return jsonify(error='incomplete data', status=False)
    user_id = is_int(user_id)
    if user_id == 'error':
        return jsonify(error='data format error', status=False)
    team_member = TeamMember.query.filter_by(user_id=user_id).first()
    if is_none([team_member]):
        return jsonify(error='user have not team', status=False)
    if team_member.is_leader:
        return jsonify(content='is leader', status=True)
    else:
        return jsonify(error='not leader', status=False)


@user.route('/isNotice')
def is_notice():
    user_id = request.args.get('userID')
    if is_none([user_id]):
        return jsonify(error='incomplete data', status=False)
    user_id = is_int(user_id)
    if user_id == 'error':
        return jsonify(error='data format error', status=False)
    user = User.query.filter_by(id=user_id).first()
    if (user.is_notice):
        return jsonify(content='is notice', status=True)
    else:
        return jsonify(error='not notice', status=False)

@user.route('/notNotice')
def not_notice():
    user_id = request.args.get('userID')
    if is_none([user_id]):
        return jsonify(error='incomplete data', status=False)
    user_id = is_int(user_id)
    if user_id == 'error':
        return jsonify(error='data format error', status=False)
    user = User.query.filter_by(id=user_id).first()
    user.is_notice = False
    db.session.commit()
    return jsonify(content='not notice')

@user.route('/move')
def move_out_user():
    leader_id = request.args.get('leaderID')
    member_id = request.args.get('memberID')
    if is_none([leader_id, member_id]):
        return jsonify(error='incomplete data', status=False)
    if is_int(leader_id) == 'error' or is_int(member_id) == 'error':
        return jsonify(error='data format error', status=False)
    team_member01 = TeamMember.query.filter_by(user_id=leader_id).first()
    if team_member01 is None:
        return jsonify(error='leader have not team', status=False)
    team_member02 = TeamMember.query.filter_by(user_id=member_id).first()
    if team_member02 is None:
        return jsonify(error='member have not team', status=False)
    if not(team_member01.team_id == team_member02.team_id and team_member01.is_leader and not team_member02.is_leader):
        return jsonify(error='two users id error', status=False)
    leader = User.query.get(leader_id)
    member = User.query.get(member_id)
    if leader is None or member is None:
        return jsonify(error='user is not exists', status=False)
    team = team_member01.team
    # 队伍人数减一
    team.now_numbers = team.now_numbers - 1
    # 队伍对应性别减一
    if member.sex == '男':
        team.male = team.male - 1
    else:
        team.female = team.female - 1
    # 该用户微信头像
    img_url = member.img_url
    if img_url is None:
        return jsonify(error='img is not exists', status=False)
    # 创建这人退出的通知
    notice = Notice(team_id=team_member01.team_id, type=6, img_url=img_url, create_time=datetime.now())
    member.is_notice = False
    db.session.add(notice)
    db.session.delete(team_member02)
    db.session.commit()
    return jsonify(content='move out success', status=True)


@user.route('/team')
def show_my_team():
    user_id = request.args.get('userID')
    if user_id is None:
        return jsonify(error='incomplete data', isTeam=False)
    if is_int(user_id) == 'error':
        return jsonify(error='data format error', isTeam=False)
    team_member = TeamMember.query.filter_by(user_id=user_id).first()
    if team_member is None:
        return jsonify(error='user have not team', isTeam=False)
    team_id = team_member.team_id
    team = Team.query.filter_by(id=team_id).first()
    if team is None:
        return jsonify(error='team is not exists', isTeam=False)
    dict_team = dict()
    dict_team['startAddress'] = team.start_address
    dict_team['endAddress'] = team.end_address
    dict_team['startTime'] = team.start_time
    dict_team['endTime'] = team.end_time
    dict_team['numbers'] = team.numbers
    dict_team['nowNumbers'] = team.now_numbers
    dict_team['female'] = team.female
    dict_team['male'] = team.male
    dict_team['contact'] = team.contact
    dict_team['remark'] = team.remark
    notices = []
    team_notices = Notice.query.filter_by(team_id=team_id).order_by(Notice.create_time.desc()).all()
    for t_team_notice in team_notices:
        dict_notice = dict()
        dict_notice['type'] = t_team_notice.type
        dict_notice['createTime'] = t_team_notice.create_time
        dict_notice['imgUrl'] = t_team_notice.img_url
        notices.append(dict_notice)
    members = []
    team_members = TeamMember.query.filter_by(team_id=team_id).all()
    for t_team_member in team_members:
        t_user = t_team_member.user
        dict_member = dict()
        dict_member['userID'] = t_user.id
        dict_member['name'] = t_user.name
        dict_member['sex'] = t_user.sex
        dict_member['isLeader'] = t_team_member.is_leader
        dict_member['imgUrl'] = t_user.img_url
        members.append(dict_member)
    return jsonify(team=dict_team, members=members, notices=notices, isTeam=True)


@user.route('/img')
def insert_img_url():
    user_id = request.args.get('userID')
    img_url = request.args.get('imgUrl')
    if is_none([user_id, img_url]):
        return 'incomplete data'
    if is_int(user_id) == 'error':
        return 'data format error'
    user = User.query.get(user_id)
    if user is None:
        return 'user is not exists'
    user.img_url = img_url
    db.session.commit()
    return 'add img success'

