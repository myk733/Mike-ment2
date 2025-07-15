from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
from src.models.user import User, JournalEntry, MoodEntry, db

journal_bp = Blueprint('journal', __name__)

@journal_bp.route('/journal/entries', methods=['GET'])
def get_journal_entries():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    
    # Build query
    query = JournalEntry.query.filter_by(user_id=user_id)
    
    if category:
        query = query.filter_by(category=category)
    
    # Order by most recent first
    query = query.order_by(JournalEntry.created_at.desc())
    
    # Paginate
    entries = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'entries': [entry.to_dict() for entry in entries.items],
        'total': entries.total,
        'pages': entries.pages,
        'current_page': page
    }), 200

@journal_bp.route('/journal/entries', methods=['POST'])
def create_journal_entry():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    content = data.get('content')
    category = data.get('category')
    mood_rating = data.get('mood_rating')
    is_private = data.get('is_private', True)
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    entry = JournalEntry(
        user_id=user_id,
        content=content,
        category=category,
        mood_rating=mood_rating,
        is_private=is_private
    )
    
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({
        'message': 'Journal entry created',
        'entry': entry.to_dict()
    }), 201

@journal_bp.route('/journal/entries/<int:entry_id>', methods=['GET'])
def get_journal_entry(entry_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    entry = JournalEntry.query.filter_by(
        id=entry_id,
        user_id=user_id
    ).first()
    
    if not entry:
        return jsonify({'error': 'Journal entry not found'}), 404
    
    return jsonify({'entry': entry.to_dict()}), 200

@journal_bp.route('/journal/entries/<int:entry_id>', methods=['PUT'])
def update_journal_entry(entry_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    entry = JournalEntry.query.filter_by(
        id=entry_id,
        user_id=user_id
    ).first()
    
    if not entry:
        return jsonify({'error': 'Journal entry not found'}), 404
    
    data = request.json
    entry.content = data.get('content', entry.content)
    entry.category = data.get('category', entry.category)
    entry.mood_rating = data.get('mood_rating', entry.mood_rating)
    entry.is_private = data.get('is_private', entry.is_private)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Journal entry updated',
        'entry': entry.to_dict()
    }), 200

@journal_bp.route('/journal/entries/<int:entry_id>', methods=['DELETE'])
def delete_journal_entry(entry_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    entry = JournalEntry.query.filter_by(
        id=entry_id,
        user_id=user_id
    ).first()
    
    if not entry:
        return jsonify({'error': 'Journal entry not found'}), 404
    
    db.session.delete(entry)
    db.session.commit()
    
    return jsonify({'message': 'Journal entry deleted'}), 200

@journal_bp.route('/mood/entries', methods=['GET'])
def get_mood_entries():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get query parameters
    days = request.args.get('days', 30, type=int)
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get mood entries
    entries = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.created_at >= start_date,
        MoodEntry.created_at <= end_date
    ).order_by(MoodEntry.created_at.desc()).all()
    
    return jsonify({
        'entries': [entry.to_dict() for entry in entries],
        'period': f'{days} days'
    }), 200

@journal_bp.route('/mood/entries', methods=['POST'])
def create_mood_entry():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    mood_rating = data.get('mood_rating')
    notes = data.get('notes', '')
    
    if mood_rating is None or mood_rating < 1 or mood_rating > 5:
        return jsonify({'error': 'Mood rating must be between 1 and 5'}), 400
    
    # Check if user already has a mood entry for today
    today = datetime.utcnow().date()
    existing_entry = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        db.func.date(MoodEntry.created_at) == today
    ).first()
    
    if existing_entry:
        # Update existing entry
        existing_entry.mood_rating = mood_rating
        existing_entry.notes = notes
        db.session.commit()
        
        return jsonify({
            'message': 'Mood entry updated',
            'entry': existing_entry.to_dict()
        }), 200
    else:
        # Create new entry
        entry = MoodEntry(
            user_id=user_id,
            mood_rating=mood_rating,
            notes=notes
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Mood entry created',
            'entry': entry.to_dict()
        }), 201

@journal_bp.route('/mood/stats', methods=['GET'])
def get_mood_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get mood entries for the last 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    entries = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.created_at >= start_date,
        MoodEntry.created_at <= end_date
    ).all()
    
    if not entries:
        return jsonify({
            'average_mood': 0,
            'total_entries': 0,
            'mood_trend': 'neutral',
            'streak': 0
        }), 200
    
    # Calculate statistics
    total_entries = len(entries)
    average_mood = sum(entry.mood_rating for entry in entries) / total_entries
    
    # Calculate trend (compare first half vs second half of period)
    mid_point = len(entries) // 2
    if mid_point > 0:
        first_half_avg = sum(entry.mood_rating for entry in entries[mid_point:]) / (len(entries) - mid_point)
        second_half_avg = sum(entry.mood_rating for entry in entries[:mid_point]) / mid_point
        
        if second_half_avg > first_half_avg + 0.2:
            mood_trend = 'improving'
        elif second_half_avg < first_half_avg - 0.2:
            mood_trend = 'declining'
        else:
            mood_trend = 'stable'
    else:
        mood_trend = 'neutral'
    
    # Calculate current streak
    streak = 0
    current_date = datetime.utcnow().date()
    
    for i in range(30):  # Check last 30 days
        check_date = current_date - timedelta(days=i)
        has_entry = any(
            entry.created_at.date() == check_date 
            for entry in entries
        )
        
        if has_entry:
            streak += 1
        else:
            break
    
    return jsonify({
        'average_mood': round(average_mood, 1),
        'total_entries': total_entries,
        'mood_trend': mood_trend,
        'streak': streak
    }), 200

