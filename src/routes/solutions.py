from flask import Blueprint, jsonify, request, session
from datetime import datetime
import json
import re
from src.models.user import User, Solution, UserSolution, JournalEntry, db

solutions_bp = Blueprint('solutions', __name__)

def analyze_user_input(text, category):
    """
    Analyze user input and generate personalized solutions.
    This is a simplified version - in production, this would use NLP services.
    """
    
    # Define solution templates based on categories
    solution_templates = {
        'relationships': {
            'title': 'Building Healthy Relationships',
            'description': 'Evidence-based strategies for improving communication and trust in relationships',
            'estimated_time': '3-6 weeks',
            'steps': [
                {
                    'title': 'Practice Active Listening',
                    'description': 'Learn to truly hear and understand your partner\'s perspective',
                    'duration': '1 week',
                    'activities': [
                        'Set aside 15 minutes daily for uninterrupted conversation',
                        'Practice reflecting back what you heard before responding',
                        'Ask open-ended questions to understand deeper feelings'
                    ]
                },
                {
                    'title': 'Improve Communication Skills',
                    'description': 'Develop healthy ways to express your needs and feelings',
                    'duration': '2 weeks',
                    'activities': [
                        'Use "I" statements instead of "you" statements',
                        'Practice expressing appreciation daily',
                        'Learn to address conflicts constructively'
                    ]
                },
                {
                    'title': 'Build Trust and Intimacy',
                    'description': 'Strengthen emotional connection and trust',
                    'duration': '2-3 weeks',
                    'activities': [
                        'Share one vulnerable thought or feeling each day',
                        'Follow through on commitments consistently',
                        'Create regular quality time together'
                    ]
                }
            ],
            'resources': [
                {
                    'type': 'book',
                    'title': 'The Seven Principles for Making Marriage Work',
                    'author': 'John Gottman',
                    'description': 'Research-based guide to building strong relationships'
                },
                {
                    'type': 'video',
                    'title': 'Communication in Relationships',
                    'url': 'https://example.com/communication-video',
                    'duration': '15 minutes'
                }
            ]
        },
        'family': {
            'title': 'Strengthening Family Bonds',
            'description': 'Strategies for managing family stress and improving relationships',
            'estimated_time': '4-8 weeks',
            'steps': [
                {
                    'title': 'Establish Family Routines',
                    'description': 'Create predictable structures that reduce stress',
                    'duration': '1-2 weeks',
                    'activities': [
                        'Set regular meal times and family meetings',
                        'Create bedtime routines for children',
                        'Establish weekly family activities'
                    ]
                },
                {
                    'title': 'Improve Family Communication',
                    'description': 'Foster open and respectful dialogue',
                    'duration': '2-3 weeks',
                    'activities': [
                        'Hold weekly family meetings',
                        'Practice conflict resolution skills',
                        'Encourage each family member to share daily highlights'
                    ]
                },
                {
                    'title': 'Manage Financial Stress',
                    'description': 'Address money-related family tensions',
                    'duration': '2-3 weeks',
                    'activities': [
                        'Create a family budget together',
                        'Discuss financial goals openly',
                        'Find free or low-cost family activities'
                    ]
                }
            ],
            'resources': [
                {
                    'type': 'book',
                    'title': 'The Whole-Brain Child',
                    'author': 'Daniel Siegel',
                    'description': 'Understanding child development and family dynamics'
                }
            ]
        },
        'work': {
            'title': 'Managing Work Stress and Burnout',
            'description': 'Comprehensive approach to workplace wellness and career balance',
            'estimated_time': '4-6 weeks',
            'steps': [
                {
                    'title': 'Assess Your Work-Life Balance',
                    'description': 'Identify areas of imbalance and stress triggers',
                    'duration': '1 week',
                    'activities': [
                        'Track your daily activities and stress levels',
                        'Identify peak stress times and situations',
                        'Evaluate your current boundaries between work and personal life'
                    ]
                },
                {
                    'title': 'Develop Stress Management Techniques',
                    'description': 'Learn practical tools for managing workplace stress',
                    'duration': '2 weeks',
                    'activities': [
                        'Practice deep breathing exercises during work breaks',
                        'Use the Pomodoro Technique for better time management',
                        'Learn to say no to non-essential tasks'
                    ]
                },
                {
                    'title': 'Create Healthy Work Boundaries',
                    'description': 'Establish clear limits to protect your well-being',
                    'duration': '2-3 weeks',
                    'activities': [
                        'Set specific work hours and stick to them',
                        'Create a dedicated workspace if working from home',
                        'Develop an end-of-workday ritual'
                    ]
                }
            ],
            'resources': [
                {
                    'type': 'book',
                    'title': 'Burnout: The Secret to Unlocking the Stress Cycle',
                    'author': 'Emily Nagoski',
                    'description': 'Science-based approach to managing stress and preventing burnout'
                },
                {
                    'type': 'video',
                    'title': 'Workplace Stress Management',
                    'url': 'https://example.com/stress-management',
                    'duration': '20 minutes'
                }
            ]
        },
        'financial': {
            'title': 'Financial Wellness and Stress Relief',
            'description': 'Practical strategies for managing money-related anxiety',
            'estimated_time': '6-8 weeks',
            'steps': [
                {
                    'title': 'Assess Your Financial Situation',
                    'description': 'Get a clear picture of your finances',
                    'duration': '1 week',
                    'activities': [
                        'List all income sources and expenses',
                        'Calculate your net worth',
                        'Identify areas of financial stress'
                    ]
                },
                {
                    'title': 'Create a Budget and Emergency Fund',
                    'description': 'Build financial security and reduce anxiety',
                    'duration': '2-3 weeks',
                    'activities': [
                        'Use the 50/30/20 budgeting rule',
                        'Start an emergency fund with small amounts',
                        'Track expenses daily for awareness'
                    ]
                },
                {
                    'title': 'Develop Long-term Financial Goals',
                    'description': 'Plan for future financial security',
                    'duration': '3-4 weeks',
                    'activities': [
                        'Set SMART financial goals',
                        'Research investment options suitable for Kenya',
                        'Consider additional income streams'
                    ]
                }
            ],
            'resources': [
                {
                    'type': 'book',
                    'title': 'Your Money or Your Life',
                    'author': 'Vicki Robin',
                    'description': 'Transform your relationship with money'
                }
            ]
        },
        'personal': {
            'title': 'Personal Growth and Self-Esteem',
            'description': 'Building confidence and discovering your authentic self',
            'estimated_time': '6-10 weeks',
            'steps': [
                {
                    'title': 'Self-Reflection and Awareness',
                    'description': 'Understand your values, strengths, and areas for growth',
                    'duration': '2 weeks',
                    'activities': [
                        'Complete a values assessment exercise',
                        'Journal about your strengths and achievements',
                        'Identify limiting beliefs about yourself'
                    ]
                },
                {
                    'title': 'Build Self-Compassion',
                    'description': 'Learn to treat yourself with kindness',
                    'duration': '2-3 weeks',
                    'activities': [
                        'Practice self-compassion meditation',
                        'Challenge negative self-talk',
                        'Celebrate small wins daily'
                    ]
                },
                {
                    'title': 'Set and Achieve Personal Goals',
                    'description': 'Create momentum through meaningful accomplishments',
                    'duration': '3-5 weeks',
                    'activities': [
                        'Set 3 achievable short-term goals',
                        'Break goals into daily actions',
                        'Track progress and adjust as needed'
                    ]
                }
            ],
            'resources': [
                {
                    'type': 'book',
                    'title': 'Self-Compassion',
                    'author': 'Kristin Neff',
                    'description': 'The proven power of being kind to yourself'
                }
            ]
        },
        'social': {
            'title': 'Overcoming Social Anxiety and Building Connections',
            'description': 'Strategies for managing social pressure and building meaningful relationships',
            'estimated_time': '4-8 weeks',
            'steps': [
                {
                    'title': 'Understand Social Anxiety',
                    'description': 'Recognize triggers and patterns',
                    'duration': '1 week',
                    'activities': [
                        'Keep a social anxiety journal',
                        'Identify specific social situations that cause stress',
                        'Learn about the fight-or-flight response'
                    ]
                },
                {
                    'title': 'Practice Gradual Exposure',
                    'description': 'Slowly build confidence in social situations',
                    'duration': '3-4 weeks',
                    'activities': [
                        'Start with low-stakes social interactions',
                        'Practice small talk with cashiers or neighbors',
                        'Gradually increase social challenges'
                    ]
                },
                {
                    'title': 'Build Authentic Connections',
                    'description': 'Focus on quality relationships over quantity',
                    'duration': '2-3 weeks',
                    'activities': [
                        'Join groups based on your interests',
                        'Practice active listening in conversations',
                        'Be vulnerable and share your authentic self'
                    ]
                }
            ],
            'resources': [
                {
                    'type': 'book',
                    'title': 'Quiet: The Power of Introverts',
                    'author': 'Susan Cain',
                    'description': 'Understanding and embracing your social style'
                }
            ]
        },
        'health': {
            'title': 'Holistic Health and Lifestyle Wellness',
            'description': 'Comprehensive approach to physical and mental well-being',
            'estimated_time': '8-12 weeks',
            'steps': [
                {
                    'title': 'Establish Healthy Sleep Habits',
                    'description': 'Improve sleep quality for better mental health',
                    'duration': '2-3 weeks',
                    'activities': [
                        'Create a consistent bedtime routine',
                        'Limit screen time before bed',
                        'Optimize your sleep environment'
                    ]
                },
                {
                    'title': 'Develop Regular Exercise Routine',
                    'description': 'Use physical activity to boost mood and energy',
                    'duration': '3-4 weeks',
                    'activities': [
                        'Start with 15-minute daily walks',
                        'Try different types of exercise to find what you enjoy',
                        'Set realistic fitness goals'
                    ]
                },
                {
                    'title': 'Improve Nutrition and Hydration',
                    'description': 'Fuel your body and mind properly',
                    'duration': '3-5 weeks',
                    'activities': [
                        'Plan balanced meals with local Kenyan foods',
                        'Increase water intake gradually',
                        'Reduce processed foods and sugar'
                    ]
                }
            ],
            'resources': [
                {
                    'type': 'book',
                    'title': 'The Body Keeps the Score',
                    'author': 'Bessel van der Kolk',
                    'description': 'Understanding the connection between body and mind'
                }
            ]
        }
    }
    
    # Map categories to solution templates
    category_mapping = {
        'relationships': 'relationships',
        'family': 'family',
        'work': 'work',
        'financial': 'financial',
        'personal': 'personal',
        'social': 'social',
        'health': 'health'
    }
    
    template_key = category_mapping.get(category.lower(), 'personal')
    template = solution_templates.get(template_key, solution_templates['personal'])
    
    # Customize based on user input (simplified analysis)
    customized_solution = template.copy()
    
    # Add personalized introduction based on user input
    if 'overwhelmed' in text.lower():
        customized_solution['personalized_intro'] = "I understand you're feeling overwhelmed. This is a common experience, and there are proven strategies that can help you regain control and find balance."
    elif 'anxious' in text.lower() or 'anxiety' in text.lower():
        customized_solution['personalized_intro'] = "Anxiety can be challenging, but it's manageable with the right tools and support. Let's work together on strategies that have helped many people in similar situations."
    elif 'stress' in text.lower():
        customized_solution['personalized_intro'] = "Stress is a natural response, but chronic stress can impact your well-being. These evidence-based techniques will help you develop healthier coping mechanisms."
    else:
        customized_solution['personalized_intro'] = "Thank you for sharing your experience. Here's a personalized plan designed to help you work through these challenges step by step."
    
    return customized_solution

@solutions_bp.route('/analyze', methods=['POST'])
def analyze_input():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    text = data.get('text', '')
    category = data.get('category', 'personal')
    
    if not text:
        return jsonify({'error': 'Text input is required'}), 400
    
    # Save journal entry
    journal_entry = JournalEntry(
        user_id=user_id,
        content=text,
        category=category
    )
    db.session.add(journal_entry)
    
    # Generate personalized solution
    solution_data = analyze_user_input(text, category)
    
    # Create or find existing solution
    solution = Solution.query.filter_by(
        title=solution_data['title'],
        category=category
    ).first()
    
    if not solution:
        solution = Solution(
            title=solution_data['title'],
            description=solution_data['description'],
            category=category,
            content=json.dumps(solution_data),
            estimated_time=solution_data['estimated_time'],
            difficulty_level='beginner',
            is_published=True
        )
        db.session.add(solution)
        db.session.flush()  # Get the ID
    
    # Increment views
    solution.views += 1
    
    # Create user-solution relationship
    user_solution = UserSolution(
        user_id=user_id,
        solution_id=solution.id
    )
    db.session.add(user_solution)
    
    db.session.commit()
    
    return jsonify({
        'solution': solution_data,
        'solution_id': solution.id,
        'journal_entry_id': journal_entry.id
    }), 200

@solutions_bp.route('/solutions', methods=['GET'])
def get_solutions():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get user's solutions
    user_solutions = db.session.query(UserSolution, Solution).join(
        Solution, UserSolution.solution_id == Solution.id
    ).filter(UserSolution.user_id == user_id).all()
    
    solutions_data = []
    for user_solution, solution in user_solutions:
        solution_dict = solution.to_dict()
        solution_dict['user_progress'] = user_solution.progress
        solution_dict['started_at'] = user_solution.started_at.isoformat() if user_solution.started_at else None
        solutions_data.append(solution_dict)
    
    return jsonify({'solutions': solutions_data}), 200

@solutions_bp.route('/solutions/<int:solution_id>/progress', methods=['PUT'])
def update_progress(solution_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    progress = data.get('progress', 0)
    notes = data.get('notes', '')
    
    user_solution = UserSolution.query.filter_by(
        user_id=user_id,
        solution_id=solution_id
    ).first()
    
    if not user_solution:
        return jsonify({'error': 'Solution not found for user'}), 404
    
    user_solution.progress = progress
    user_solution.notes = notes
    
    if progress >= 100 and not user_solution.completed_at:
        user_solution.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Progress updated',
        'user_solution': user_solution.to_dict()
    }), 200

@solutions_bp.route('/solutions/categories', methods=['GET'])
def get_categories():
    categories = [
        {'id': 'relationships', 'name': 'Relationships', 'icon': 'heart'},
        {'id': 'family', 'name': 'Family Issues', 'icon': 'users'},
        {'id': 'work', 'name': 'Work & Career', 'icon': 'briefcase'},
        {'id': 'financial', 'name': 'Financial Stress', 'icon': 'dollar-sign'},
        {'id': 'personal', 'name': 'Personal Growth', 'icon': 'trending-up'},
        {'id': 'social', 'name': 'Social Pressures', 'icon': 'user-friends'},
        {'id': 'health', 'name': 'Health & Lifestyle', 'icon': 'heart-pulse'}
    ]
    
    return jsonify({'categories': categories}), 200

