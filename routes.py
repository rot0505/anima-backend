from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from datetime import datetime
import os

mongo_host = os.environ.get('MONGO_HOST')
db_name = os.environ.get('DB_NAME')
collection_name = os.environ.get('COLLECTION_NAME')

events_bp = Blueprint('events_bp', __name__)
client = MongoClient(mongo_host)
db = client[db_name]
collection = db[collection_name]

@events_bp.route('/api/events', methods=['GET'])
# Retrieve all events that occur on a specified date or today's date if none is provided in the request URL.
def get_events():
  date_str = request.args.get('date')
  if not date_str:
    date_str = str(datetime.today().strftime('%Y-%m-%d'))
  else:
    try:
      date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
      return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400
  year = date_obj.year
  month = int(date_obj.month)

  start_of_month = datetime(year=year, month=month, day=1).strftime('%Y-%m-%d')
  end_of_month = datetime(year=year, month=month+1, day=1).strftime('%Y-%m-%d')

  events_list = []
  for event in collection.find({'date': {'$gte': start_of_month, '$lt': end_of_month}}):
    events_list.append({
      'id': str(event['id']),
      'date': event['date'],
      'title': event['title']
    })
  return jsonify(events_list)

# Create a new event
@events_bp.route('/api/event', methods=['POST'])
def create_event():
  event_data = request.get_json()
  required_fields = ['id', 'date', 'title']
  missing_fields = [field for field in required_fields if field not in event_data]
  if missing_fields:
    return jsonify({'error': f'Missing required field(s): {", ".join(missing_fields)}'}), 400
  
  try:
    event_data['date'] = datetime.strptime(event_data['date'], '%Y-%m-%d').strftime('%Y-%m-%d')
  except ValueError:
    return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400
  
  event_id = collection.insert_one(event_data).inserted_id
  return jsonify({'id': str(event_id)})

# Update an existing event
@events_bp.route('/api/event/<id>', methods=['PUT'])
def update_event(id):
  event_data = request.get_json()
  result = collection.update_one({'id': int(id)}, {'$set': event_data})
  if result.modified_count == 1:
    return jsonify({'success': True})
  else:
    return jsonify({'error': 'No document was updated.'}), 404

# Delete an event by ID
@events_bp.route('/api/event/<id>', methods=['DELETE'])
def delete_event(id):
  result = collection.delete_one({'id': int(id)})
  if result.deleted_count == 1:
    return jsonify({'success': True})
  else:
    return jsonify({'error': 'No document was deleted.'}), 404
