#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关路由
处理用户注册、登录、密码重置等功能
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from datetime import datetime, timedelta
from models import db, User
from utils.validators import validate_email, validate_password, validate_username
from utils.auth import (
    generate_confirmation_token, confirm_token,
    generate_password_reset_token, confirm_password_reset_token,
    get_user_by_email, has_permission
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证必填字段
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', '').strip()
    
    if not username or not email or not password:
        return jsonify({
            'message': '请填写所有必填字段',
            'error': 'missing_fields',
            'details': {
                'username': not username,
                'email': not email,
                'password': not password
            }
        }), 400
    
    # 验证输入格式
    if not validate_username(username):
        return jsonify({
            'message': '用户名格式不正确',
            'error': 'invalid_username',
            'details': '用户名长度为3-20个字符，只能包含字母、数字和下划线，且不能以数字开头'
        }), 400
    
    if not validate_email(email):
        return jsonify({
            'message': '邮箱格式不正确',
            'error': 'invalid_email'
        }), 400
    
    if not validate_password(password):
        return jsonify({
            'message': '密码强度不符合要求',
            'error': 'invalid_password',
            'details': '密码至少8个字符，包含大小写字母、数字和特殊字符'
        }), 400
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({
            'message': '用户名已存在',
            'error': 'username_exists'
        }), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({
            'message': '邮箱已存在',
            'error': 'email_exists'
        }), 400
    
    # 创建新用户
    user = User(
        username=username,
        email=email,
        nickname=nickname or username
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    # 生成邮箱确认令牌
    token = generate_confirmation_token(email)
    
    # 创建访问令牌
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    
    return jsonify({
        'message': '注册成功',
        'user': user.to_dict(include_email=True),
        'access_token': access_token,
        'refresh_token': refresh_token,
        'email_confirmation_token': token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    username_or_email = data.get('username_or_email', '').strip()
    password = data.get('password', '')
    remember = data.get('remember', False)
    
    if not username_or_email or not password:
        return jsonify({
            'message': '请填写用户名/邮箱和密码',
            'error': 'missing_fields'
        }), 400
    
    # 查找用户
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()
    
    if not user:
        return jsonify({
            'message': '用户名/邮箱或密码错误',
            'error': 'invalid_credentials'
        }), 401
    
    if not user.check_password(password):
        return jsonify({
            'message': '用户名/邮箱或密码错误',
            'error': 'invalid_credentials'
        }), 401
    
    if not user.is_active:
        return jsonify({
            'message': '账户已被禁用',
            'error': 'account_disabled'
        }), 401
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.session.commit()
    
    # 创建令牌
    expires_delta = timedelta(days=30) if remember else timedelta(hours=1)
    access_token = create_access_token(identity=user, expires_delta=expires_delta)
    refresh_token = create_refresh_token(identity=user)
    
    return jsonify({
        'message': '登录成功',
        'user': user.to_dict(include_email=True),
        'access_token': access_token,
        'refresh_token': refresh_token
    })

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'message': '用户不存在或已被禁用',
            'error': 'invalid_user'
        }), 401
    
    new_access_token = create_access_token(identity=user)
    return jsonify({
        'access_token': new_access_token,
        'user': user.to_dict()
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    # 在实际应用中，可以将token加入黑名单
    # 这里简单返回成功消息
    return jsonify({'message': '登出成功'})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'message': '用户不存在',
            'error': 'user_not_found'
        }), 404
    
    return jsonify({
        'user': user.to_dict(include_email=True),
        'permissions': get_user_permissions(user)
    })

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户资料"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'message': '用户不存在',
            'error': 'user_not_found'
        }), 404
    
    data = request.get_json()
    
    # 可更新的字段
    allowed_fields = ['nickname', 'bio', 'website', 'location', 'avatar']
    
    for field in allowed_fields:
        if field in data:
            value = data[field]
            
            # 字段验证
            if field == 'nickname':
                if value and len(value) > 100:
                    return jsonify({
                        'message': '昵称长度不能超过100个字符',
                        'error': 'invalid_nickname'
                    }), 400
            
            elif field == 'bio':
                if value and len(value) > 500:
                    return jsonify({
                        'message': '个人简介长度不能超过500个字符',
                        'error': 'invalid_bio'
                    }), 400
            
            elif field == 'website':
                if value and not validate_url(value):
                    return jsonify({
                        'message': '网站地址格式不正确',
                        'error': 'invalid_website'
                    }), 400
            
            elif field == 'location':
                if value and len(value) > 100:
                    return jsonify({
                        'message': '位置信息长度不能超过100个字符',
                        'error': 'invalid_location'
                    }), 400
            
            setattr(user, field, value or '')
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': '资料更新成功',
        'user': user.to_dict(include_email=True)
    })

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'message': '用户不存在',
            'error': 'user_not_found'
        }), 404
    
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if not old_password or not new_password:
        return jsonify({
            'message': '请填写旧密码和新密码',
            'error': 'missing_fields'
        }), 400
    
    if not user.check_password(old_password):
        return jsonify({
            'message': '旧密码错误',
            'error': 'invalid_old_password'
        }), 400
    
    if not validate_password(new_password):
        return jsonify({
            'message': '新密码强度不符合要求',
            'error': 'invalid_new_password',
            'details': '密码至少8个字符，包含大小写字母、数字和特殊字符'
        }), 400
    
    user.set_password(new_password)
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'})

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """忘记密码"""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({
            'message': '请填写邮箱地址',
            'error': 'missing_email'
        }), 400
    
    if not validate_email(email):
        return jsonify({
        'message': '邮箱格式不正确',
        'error': 'invalid_email'
        }), 400
    
    user = get_user_by_email(email)
    if not user:
        # 不暴露用户是否存在
        return jsonify({'message': '如果邮箱存在，重置邮件已发送'})
    
    # 生成重置令牌
    token = generate_password_reset_token(email)
    
    # 在实际应用中，这里应该发送重置邮件
    # send_password_reset_email(user.email, token)
    
    return jsonify({
        'message': '如果邮箱存在，重置邮件已发送',
        'reset_token': token  # 开发环境返回令牌
    })

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    data = request.get_json()
    token = data.get('token', '')
    new_password = data.get('new_password', '')
    
    if not token or not new_password:
        return jsonify({
            'message': '请填写重置令牌和新密码',
            'error': 'missing_fields'
        }), 400
    
    # 验证重置令牌
    email = confirm_password_reset_token(token)
    if not email:
        return jsonify({
            'message': '重置令牌无效或已过期',
            'error': 'invalid_token'
        }), 400
    
    # 验证新密码
    if not validate_password(new_password):
        return jsonify({
            'message': '新密码强度不符合要求',
            'error': 'invalid_password',
            'details': '密码至少8个字符，包含大小写字母、数字和特殊字符'
        }), 400
    
    # 更新密码
    user = get_user_by_email(email)
    if not user:
        return jsonify({
            'message': '用户不存在',
            'error': 'user_not_found'
        }), 404
    
    user.set_password(new_password)
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '密码重置成功'})

@auth_bp.route('/confirm-email', methods=['POST'])
def confirm_email():
    """确认邮箱"""
    data = request.get_json()
    token = data.get('token', '')
    
    if not token:
        return jsonify({
            'message': '请提供确认令牌',
            'error': 'missing_token'
        }), 400
    
    email = confirm_token(token)
    if not email:
        return jsonify({
            'message': '确认令牌无效或已过期',
            'error': 'invalid_token'
        }), 400
    
    user = get_user_by_email(email)
    if not user:
        return jsonify({
            'message': '用户不存在',
            'error': 'user_not_found'
        }), 404
    
    if user.is_verified:
        return jsonify({'message': '邮箱已经验证过了'})
    
    user.is_verified = True
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '邮箱验证成功'})

@auth_bp.route('/resend-confirmation', methods=['POST'])
def resend_confirmation():
    """重新发送邮箱确认邮件"""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({
            'message': '请填写邮箱地址',
            'error': 'missing_email'
        }), 400
    
    user = get_user_by_email(email)
    if not user:
        return jsonify({'message': '如果邮箱存在，确认邮件已发送'})
    
    if user.is_verified:
        return jsonify({'message': '邮箱已经验证过了'})
    
    # 生成新的确认令牌
    token = generate_confirmation_token(email)
    
    # 在实际应用中，这里应该发送确认邮件
    # send_confirmation_email(user.email, token)
    
    return jsonify({
        'message': '如果邮箱存在，确认邮件已发送',
        'confirmation_token': token  # 开发环境返回令牌
    })

@auth_bp.route('/check-username', methods=['GET'])
def check_username():
    """检查用户名是否可用"""
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({
            'message': '请提供用户名',
            'error': 'missing_username'
        }), 400
    
    if not validate_username(username):
        return jsonify({
            'available': False,
            'message': '用户名格式不正确'
        })
    
    existing_user = User.query.filter_by(username=username).first()
    
    return jsonify({
        'available': not bool(existing_user),
        'message': '用户名可用' if not existing_user else '用户名已存在'
    })

@auth_bp.route('/check-email', methods=['GET'])
def check_email():
    """检查邮箱是否可用"""
    email = request.args.get('email', '').strip()
    
    if not email:
        return jsonify({
            'message': '请提供邮箱地址',
            'error': 'missing_email'
        }), 400
    
    if not validate_email(email):
        return jsonify({
            'available': False,
            'message': '邮箱格式不正确'
        })
    
    existing_user = User.query.filter_by(email=email).first()
    
    return jsonify({
        'available': not bool(existing_user),
        'message': '邮箱可用' if not existing_user else '邮箱已存在'
    })