from flask import Blueprint, render_template, request, jsonify, flash, current_app
from flask_login import login_required, current_user
from . import db
from .models import User
from .utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/manage')
@login_required
@admin_required
def manage():
    current_app.logger.info(f'User {current_user.email} accessed the manage page')
    users = User.query.all()
    pending_users = User.query.filter_by(role='pending').all()

    return render_template('admin_tabbed.html', users=users, pending_users=pending_users)

@admin_bp.route('/approve_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    current_app.logger.info(f'User {current_user.email} approved user {user_id}')

    try:
        #data = request.get_json()
        user = User.query.get(user_id)

        if not user:
            flash("User not found!", 'error')
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        user = User.query.get(user_id)
        if user and user.role == 'pending':
            user.role = 'user'
            db.session.commit()
            # TODO Notify the user about the approval
            flash('User approved successfully!', 'success')
            return jsonify({'success': True})
        
        #TODO add error handling

    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/update_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user(user_id):
    current_app.logger.info(f'User {current_user.email} updated user {user_id}')

    try:
        data = request.get_json()
        user = User.query.get(user_id)

        if not user:
            flash("User not found!", 'error')
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        user.name = data.get('name')
        user.email = data.get('email')
        user.role = data.get('role')
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return jsonify({'success': True, 'name': user.name, 'email': user.email, 'role': user.role})
    
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)}), 500
    
@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    current_app.logger.info(f'User {current_user.email} deleted user {user_id}')
    
    try:
        user = User.query.get(user_id)

        if not user:
            flash("User not found!", 'error')
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", 'success')
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)}), 500