from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
from sqlalchemy import func
from src.models.user import User, JournalEntry, Solution, UserSolution, MoodEntry, db

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """Decorator to require admin authentication"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    return None

@admin_bp.route('/admin/dashboard', methods=['GET'])
def get_dashboard_stats():
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    # Get basic statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_journal_entries = JournalEntry.query.count()
    total_solutions = Solution.query.filter_by(is_published=True).count()
    
    # Get users registered in the last month
    last_month = datetime.utcnow() - timedelta(days=30)
    new_users_last_month = User.query.filter(
        User.created_at >= last_month
    ).count()
    
    # Calculate growth rate
    previous_month = datetime.utcnow() - timedelta(days=60)
    users_previous_month = User.query.filter(
        User.created_at >= previous_month,
        User.created_at < last_month
    ).count()
    
    if users_previous_month > 0:
        growth_rate = ((new_users_last_month - users_previous_month) / users_previous_month) * 100
    else:
        growth_rate = 100 if new_users_last_month > 0 else 0
    
    # Get active sessions (users who logged in today)
    today = datetime.utcnow().date()
    active_sessions = User.query.filter(
        func.date(User.last_login) == today
    ).count()
    
    # Get content engagement
    total_solution_views = db.session.query(
        func.sum(Solution.views)
    ).scalar() or 0
    
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'new_users_last_month': new_users_last_month,
        'growth_rate': round(growth_rate, 1),
        'active_sessions': active_sessions,
        'total_journal_entries': total_journal_entries,
        'total_solutions': total_solutions,
        'total_solution_views': total_solution_views
    }), 200

@admin_bp.route('/admin/users', methods=['GET'])
def get_users():
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    
    # Build query
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.name.contains(search),
                User.email.contains(search)
            )
        )
    
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    # Order by most recent first
    query = query.order_by(User.created_at.desc())
    
    # Paginate
    users = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Add additional stats for each user
    users_data = []
    for user in users.items:
        user_dict = user.to_dict()
        
        # Get user's journal entry count
        user_dict['journal_entries_count'] = JournalEntry.query.filter_by(
            user_id=user.id
        ).count()
        
        # Get user's solutions count
        user_dict['solutions_used_count'] = UserSolution.query.filter_by(
            user_id=user.id
        ).count()
        
        users_data.append(user_dict)
    
    return jsonify({
        'users': users_data,
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    }), 200

@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Update user fields
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'is_admin' in data:
        user.is_admin = data['is_admin']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting the current admin user
    current_user_id = session.get('user_id')
    if user_id == current_user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    # Delete related records first
    JournalEntry.query.filter_by(user_id=user_id).delete()
    UserSolution.query.filter_by(user_id=user_id).delete()
    MoodEntry.query.filter_by(user_id=user_id).delete()
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

@admin_bp.route('/admin/solutions', methods=['GET'])
def get_solutions():
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    status = request.args.get('status', 'all')
    
    # Build query
    query = Solution.query
    
    if category:
        query = query.filter_by(category=category)
    
    if status == 'published':
        query = query.filter_by(is_published=True)
    elif status == 'draft':
        query = query.filter_by(is_published=False)
    
    # Order by most recent first
    query = query.order_by(Solution.created_at.desc())
    
    # Paginate
    solutions = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Add usage statistics
    solutions_data = []
    for solution in solutions.items:
        solution_dict = solution.to_dict()
        
        # Get usage count
        solution_dict['usage_count'] = UserSolution.query.filter_by(
            solution_id=solution.id
        ).count()
        
        solutions_data.append(solution_dict)
    
    return jsonify({
        'solutions': solutions_data,
        'total': solutions.total,
        'pages': solutions.pages,
        'current_page': page
    }), 200

@admin_bp.route('/admin/solutions', methods=['POST'])
def create_solution():
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    data = request.json
    
    solution = Solution(
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category'),
        content=data.get('content'),
        estimated_time=data.get('estimated_time'),
        difficulty_level=data.get('difficulty_level', 'beginner'),
        is_published=data.get('is_published', False)
    )
    
    db.session.add(solution)
    db.session.commit()
    
    return jsonify({
        'message': 'Solution created successfully',
        'solution': solution.to_dict()
    }), 201

@admin_bp.route('/admin/solutions/<int:solution_id>', methods=['PUT'])
def update_solution(solution_id):
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    solution = Solution.query.get_or_404(solution_id)
    data = request.json
    
    # Update solution fields
    if 'title' in data:
        solution.title = data['title']
    if 'description' in data:
        solution.description = data['description']
    if 'category' in data:
        solution.category = data['category']
    if 'content' in data:
        solution.content = data['content']
    if 'estimated_time' in data:
        solution.estimated_time = data['estimated_time']
    if 'difficulty_level' in data:
        solution.difficulty_level = data['difficulty_level']
    if 'is_published' in data:
        solution.is_published = data['is_published']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Solution updated successfully',
        'solution': solution.to_dict()
    }), 200

@admin_bp.route('/admin/solutions/<int:solution_id>', methods=['DELETE'])
def delete_solution(solution_id):
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    solution = Solution.query.get_or_404(solution_id)
    
    # Delete related user solutions first
    UserSolution.query.filter_by(solution_id=solution_id).delete()
    
    # Delete solution
    db.session.delete(solution)
    db.session.commit()
    
    return jsonify({'message': 'Solution deleted successfully'}), 200

@admin_bp.route('/admin/analytics', methods=['GET'])
def get_analytics():
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    # Get date range
    days = request.args.get('days', 30, type=int)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # User registration analytics
    user_registrations = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at >= start_date,
        User.created_at <= end_date
    ).group_by(func.date(User.created_at)).all()
    
    # Journal entry analytics
    journal_entries = db.session.query(
        func.date(JournalEntry.created_at).label('date'),
        func.count(JournalEntry.id).label('count')
    ).filter(
        JournalEntry.created_at >= start_date,
        JournalEntry.created_at <= end_date
    ).group_by(func.date(JournalEntry.created_at)).all()
    
    # Mood analytics
    mood_analytics = db.session.query(
        func.date(MoodEntry.created_at).label('date'),
        func.avg(MoodEntry.mood_rating).label('average_mood')
    ).filter(
        MoodEntry.created_at >= start_date,
        MoodEntry.created_at <= end_date
    ).group_by(func.date(MoodEntry.created_at)).all()
    
    # Category usage analytics
    category_usage = db.session.query(
        JournalEntry.category,
        func.count(JournalEntry.id).label('count')
    ).filter(
        JournalEntry.created_at >= start_date,
        JournalEntry.created_at <= end_date,
        JournalEntry.category.isnot(None)
    ).group_by(JournalEntry.category).all()
    
    return jsonify({
        'user_registrations': [
            {'date': reg.date.isoformat(), 'count': reg.count}
            for reg in user_registrations
        ],
        'journal_entries': [
            {'date': entry.date.isoformat(), 'count': entry.count}
            for entry in journal_entries
        ],
        'mood_analytics': [
            {'date': mood.date.isoformat(), 'average_mood': float(mood.average_mood)}
            for mood in mood_analytics
        ],
        'category_usage': [
            {'category': cat.category, 'count': cat.count}
            for cat in category_usage
        ]
    }), 200

