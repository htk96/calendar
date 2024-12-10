from flask import Blueprint, jsonify, request, render_template, current_app
from werkzeug.exceptions import BadRequest, NotFound
from .notion_client import NotionClient
from datetime import datetime
from .models import db, Event

bp = Blueprint('main', __name__)
notion = NotionClient()

def error_response(message, status_code):
    response = jsonify({"error": message})
    response.status_code = status_code
    return response

@bp.route('/')
def index():
    return render_template('intro.html')

@bp.route('/calendar')
def calendar():
    return render_template('index.html')

@bp.route('/api/projects', methods=['GET'])
def get_projects():
    projects = notion.get_projects()
    return jsonify(projects)

@bp.route('/api/projects', methods=['POST'])
def create_project():
    try:
        data = request.json
        if not data:
            raise BadRequest("No input data provided")
        
        required_fields = ['title', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")

        result = notion.create_project(
            title=data['title'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            status=data.get('status', '진행중')
        )
        return jsonify({"success": True, "data": result})
    except BadRequest as e:
        return error_response(str(e), 400)
    except Exception as e:
        current_app.logger.error(f"Error creating project: {str(e)}")
        return error_response("Internal server error", 500)

@bp.route('/api/projects/<page_id>', methods=['PATCH'])
def update_project(page_id):
    data = request.json
    result = notion.update_project(page_id, **data)
    return jsonify(result)

@bp.route('/api/projects/<page_id>', methods=['DELETE'])
def delete_project(page_id):
    result = notion.delete_project(page_id)
    return jsonify(result)

@bp.route('/api/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events])

@bp.route('/api/events', methods=['POST'])
def create_event():
    try:
        data = request.json
        new_event = Event(
            title=data['title'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            description=data.get('description', ''),
            status=data.get('status', '진행중'),
            assignee=data.get('assignee', ''),
            project=data.get('project', '')
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify(new_event.to_dict()), 201
    except Exception as e:
        current_app.logger.error(f"Error creating event: {str(e)}")
        return jsonify({"error": str(e)}), 400

@bp.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        data = request.json
        
        event.title = data.get('title', event.title)
        event.start_date = datetime.fromisoformat(data['start_date']) if 'start_date' in data else event.start_date
        event.end_date = datetime.fromisoformat(data['end_date']) if 'end_date' in data else event.end_date
        event.description = data.get('description', event.description)
        event.status = data.get('status', event.status)
        event.assignee = data.get('assignee', event.assignee)
        event.project = data.get('project', event.project)
        
        db.session.commit()
        return jsonify(event.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error updating event: {str(e)}")
        return jsonify({"error": str(e)}), 400

@bp.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "Event deleted successfully"})
    except Exception as e:
        current_app.logger.error(f"Error deleting event: {str(e)}")
        return jsonify({"error": str(e)}), 400