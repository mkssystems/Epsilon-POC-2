@api.route('/game_sessions/<int:session_id>/join', methods=['POST'])
def join_game_session(session_id):
    data = request.json
    client_id = data.get('client_id')

    session = GameSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    existing_client = MobileClient.query.filter_by(client_id=client_id).first()
    if existing_client:
        return jsonify({'message': 'Client already connected'}), 200
    
    new_client = MobileClient(client_id=client_id, game_session_id=session.id)
    db.session.add(new_client)
    db.session.commit()
    
    return jsonify({
        'message': 'Connected successfully',
        'session_id': session.id,
        'map_seed': session.map_seed,
        'labyrinth_id': session.labyrinth_id
    }), 200

@api.route('/game_sessions/<int:session_id>/clients', methods=['GET'])
def get_connected_clients(session_id):
    session = GameSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    clients = [{
        'client_id': client.client_id,
        'connected_at': client.connected_at.isoformat()
    } for client in session.connected_clients]
    
    return jsonify({'clients': clients}), 200
