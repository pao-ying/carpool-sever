from flaskr import db
from ..database import Team, TeamMember, User, Notice
from flask import request, Blueprint, jsonify
from ..function import is_none, is_int, is_date, is_small
from datetime import datetime
from sqlalchemy import and_

team = Blueprint("team", __name__, url_prefix='/team')
address = ['太平国际机场', '学校', '哈尔滨站', '哈尔滨西站', '哈尔滨东站', '哈尔滨北站']

# 获取起始地、目的地、开始时间、截至时间、人数要求（包括自己）、联系方式、备注、和创建队伍的人的ID
# 除了创建队伍人的ID和备注，其它数据都不能有缺省，并且对地点、时间等其他数字进行规范化处理，不符合要求就 return
# 队伍ID是自动获取的，依据是数据库中 ID 的最后一个 +1
# 最后创建 team 和 team_member
@team.route('/add')
def add_team():
    start_address = request.args.get('startAddress')
    end_address = request.args.get('endAddress')
    start_time = request.args.get('startTime')
    end_time = request.args.get('endTime')
    numbers = request.args.get('numbers')
    contact = request.args.get('contact')
    remark = request.args.get('remark')
    user_id = request.args.get('userID')
    if is_none([start_address, end_address, start_time, end_time, numbers, contact, user_id]):
        return 'incomplete data'
    start_time = is_date(start_time)
    end_time = is_date(end_time)
    numbers = is_int(numbers)
    contact = is_int(contact)
    user_id = is_int(user_id)
    if start_time == 'error' or end_time == 'error' or numbers == 'error' or contact == 'error' or user_id == 'error':
        return 'data format error'
    if (start_address not in address) or (end_address not in address):
        return 'address error'
    if start_time > end_time:
        return 'time error'
    if numbers > 4:
        return 'numbers error'
    if remark is not None and len(remark) > 25:
        return 'remark error'
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return 'user is not exists'
    if len(user.team_member) != 0:
        return 'user had team'
    female = 0
    male = 0
    if user.sex == "男":
        male = 1
    else:
        female = 1
    teams = Team.query.all()
    if len(teams) == 0:
        team_id = 1
    else:
        team_id = teams[-1].id + 1
    if remark is not None:
        team = Team(id=team_id, start_address=start_address, end_address=end_address, start_time=start_time,
                    end_time=end_time, female=female, male=male,
                    numbers=numbers, contact=contact, remark=remark, create_time=datetime.now())
    else:
        team = Team(id=team_id, start_address=start_address, end_address=end_address, start_time=start_time,
                    end_time=end_time, female=female, male=male,
                    numbers=numbers, contact=contact, create_time=datetime.now())
    team_member = TeamMember(team_id=team_id, user_id=user.id, is_leader=True)
    db.session.add(team)
    db.session.commit()
    db.session.add(team_member)
    db.session.commit()
    return 'add team success'


# 修改队伍数据
# 除了创建队伍人的ID，其它数据都是可以缺省的，哪项数据不缺省，那么哪些项就是需要修改的
@team.route('/modify')
def modify_start_time():
    start_address = request.args.get('startAddress')
    end_address = request.args.get('endAddress')
    start_time = request.args.get('startTime')
    end_time = request.args.get('endTime')
    numbers = request.args.get('numbers')
    contact = request.args.get('contact')
    remark = request.args.get('remark')
    user_id = request.args.get('userID')
    if is_none([user_id]):
        return 'user_id error'
    user_id = is_int(user_id)
    if user_id == 'error':
        return 'user_id format error'
    # 获取微信头像
    user = User.query.get(user_id)
    if user is None:
        return 'user is not exists'
    img_url = user.img_url
    if img_url is None:
        return 'img is not exists'
    # 判断是不是队长
    team_member = TeamMember.query.filter_by(user_id=user_id).first()
    if team_member.is_leader is False:
        return 'user is not leader'

    team = team_member.team
    # 检查数据类型的同时，哪种或多种数据被修改，则添加相应新的通知。若数据不需修改，则让它为数据库原始数据。
    if is_none([start_address, end_address]):
        if start_address is None and end_address is None:
            start_address = team.start_address
            end_address = team.end_address
        if (start_address is None and end_address is not None) or (end_address is None and start_address is not None):
            return 'address must be pair'
    else:
        if start_address not in address or end_address not in address:
            return 'address error'
        elif start_address == end_address:
            return 'address can not be equal'
        else:
            new_address = str(start_address) + " - " + str(end_address)
            notice = Notice(team_id=team.id, type=1, create_time=datetime.now(), img_url=img_url)
            db.session.add(notice)

    if is_none([start_time, end_time]):
        if start_time is None and end_time is None:
            start_time = team.start_time
            end_time = team.end_time
        if (start_time is None and end_time is not None) or (end_time is None and start_time is not None):
            return 'time must be pair'
    else:
        start_time = is_date(start_time)
        end_time = is_date(end_time)
        if start_time == 'error' or end_time == 'error':
            return 'data format error'
        else:
            new_time = str(start_time) + " ~ " + str(end_time)
            notice = Notice(team_id=team.id, type=0, create_time=datetime.now(), img_url=img_url)
            db.session.add(notice)

    if numbers is None:
        numbers = team.numbers
    else:
        now_numbers = team.now_numbers
        numbers = is_int(numbers)
        if numbers == 'error':
            return 'data format error'
        elif numbers > 4:
            return 'numbers error'
        elif numbers < now_numbers:
            return jsonify(error='numbers smaller', status=False)
        else:
            notice = Notice(team_id=team.id, type=2, create_time=datetime.now(), img_url=img_url)
            db.session.add(notice)

    if contact is None:
        contact = team.contact
    else:
        contact = is_int(contact)
        if contact == 'error':
            return 'data format error'
        else:
            notice = Notice(team_id=team.id, type=3, create_time=datetime.now(), img_url=img_url)
            db.session.add(notice)

    if remark is None:
        remark = team.remark
    else:
        if len(remark) > 25:
            return 'remark error'
        else:
            notice = Notice(team_id=team.id, type=4, create_time=datetime.now(), img_url=img_url)
            db.session.add(notice)

    # 为该队伍下的所有成员设为有新通知。
    team_members = TeamMember.query.filter_by(team_id=team.id).all()
    for t_team_member in team_members:
        t_user = t_team_member.user
        t_user.is_notice = True
    # 将队伍的信息修改。
    team.start_address = start_address
    team.end_address = end_address
    team.start_time = start_time
    team.end_time = end_time
    team.numbers = numbers
    team.contact = contact
    team.remark = remark
    db.session.commit()
    return 'modify team success'


@team.route('/join')
def join_team():
    user_id = request.args.get('userID')
    team_id = request.args.get('teamID')
    if is_none([user_id, team_id]):
        return jsonify(error='incomplete data', status=False)
    user_id = is_int(user_id)
    team_id = is_int(team_id)
    if user_id == 'error' or team_id == 'error':
        return jsonify(error='data format error', status=False)
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify(error='user is not exists', status=False)
    # 该用户的微信头像
    img_url = user.img_url
    if img_url is None:
        return jsonify(error='img is not exists', status=False)
    team = Team.query.filter_by(id=team_id).first()
    if team is None:
        return jsonify(error='team is not exists', status=False)
    team_member = TeamMember.query.filter_by(user_id=user_id).first()
    if team_member is not None:
        return jsonify(error='user had team', status=False)
    # 创建一个通知
    notice = Notice(team_id=team_id, type=5, create_time=datetime.now(), img_url=img_url)
    # 该队伍下所有用户都设为有新通知
    team_members = TeamMember.query.filter_by(team_id=team_id).all()
    for t_team_member in team_members:
        t_user = t_team_member.user
        t_user.is_notice = True
    # 为该用户添加进队伍
    team_member = TeamMember(user_id=user_id, team_id=team_id, is_leader=False)
    # 对应的性别加一
    if user.sex == '男':
        team.male = team.male + 1
    else:
        team.female = team.female + 1
    # 队伍的人数加一
    team.now_numbers = team.now_numbers + 1
    db.session.add(notice)
    db.session.add(team_member)
    db.session.commit()
    return jsonify(content='join success', status=True)


@team.route('/leave')
def leave_team():
    user_id = request.args.get('userID')
    if user_id is None:
        return jsonify(error='incomplete data', status=False)
    user_id = is_int(user_id)
    if user_id == 'error':
        return jsonify(error='data format error', status=False)
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify(error='user is not exists', status=False)
    # 该用户的微信头像
    img_url = user.img_url
    if img_url is None:
        return jsonify(error='img is not exists', status=False)
    team_member = TeamMember.query.filter_by(user_id=user_id).first()
    if team_member is None:
        return jsonify(error='user have no team', status=False)
    team_id = team_member.team_id
    notice = Notice(team_id=team_id, type=6, create_time=datetime.now(), img_url=img_url)
    db.session.add(notice)
    is_leader = team_member.is_leader
    if is_leader:
        Notice.query.filter_by(team_id=team_id).delete()
        team_members = TeamMember.query.filter_by(team_id=team_id).all()
        for t_team_member in team_members:
            t_user = t_team_member.user
            t_user.is_notice = False
            db.session.delete(t_team_member)
        Team.query.filter_by(id=team_id).delete()
    else:
        TeamMember.query.filter_by(user_id=user_id).delete()
        team = Team.query.filter_by(id=team_id).first()
        # 队伍对应性别减一
        if user.sex == '男':
            team.male = team.male - 1
        else:
            team.female = team.female - 1
        # 队伍对应人数减一
        team.now_numbers = team.now_numbers - 1
        user.is_notice = False
    db.session.commit()
    return jsonify(content='leave success', status=True)


@team.route('/search')
def search_team():
    start_address = request.args.get('startAddress')
    end_address = request.args.get('endAddress')
    start_time = request.args.get('startTime')
    end_time = request.args.get('endTime')
    if is_none([start_address, end_address, start_time, end_time]):
        return jsonify(error='incomplete data', status=False)
    if start_address not in address or end_address not in address \
            or is_date(start_time) == 'error' or is_date(end_time) == 'error':
        return jsonify(error='data format error', status=False)
    if is_small(start_time, end_time):
        return 'time error'
    teams = Team.query.filter(
        and_(Team.start_time >= datetime.strptime(start_time, '%Y-%m-%d %H:%M'),
             Team.end_time <= datetime.strptime(end_time, '%Y-%m-%d %H:%M'),
             Team.now_numbers != Team.numbers, Team.start_address == start_address, Team.end_address == end_address)
    ).order_by(Team.create_time).all()
    j_team = []
    for index in range(len(teams)):
        t_team = teams[index]
        t_team_id = t_team.id
        team_member = TeamMember.query.filter_by(team_id=t_team_id, is_leader=True).first()
        leader_img_url = ''
        if team_member is not None:
            t_user = team_member.user
            if t_user is not None:
                leader_img_url = t_user.img_url
        j_team.append({
            'teamID': t_team_id,
            'startAddress': t_team.start_address,
            'endAddress': t_team.end_address,
            'startTime': t_team.start_time,
            'endTime': t_team.end_time,
            'nowNumbers': t_team.now_numbers,
            'numbers': t_team.numbers,
            'female': t_team.female,
            'male': t_team.male,
            'remark': t_team.remark,
            'leaderImgUrl': leader_img_url,
            'createTime': t_team.create_time
        })
    return jsonify(team=j_team, status=True)
