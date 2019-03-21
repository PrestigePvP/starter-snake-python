import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response


@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''


@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')


@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()


@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    # print(json.dumps(data))

    color = "#FF00FF"

    return start_response(color)


board_score = {}
body_map = {}
directions = ['up', 'down', 'left', 'right']


@bottle.post('/move')
def move():
    data = bottle.request.json

    food = data['board']['food']
    body = data['you']['body']
    head_loc = body[0]
    head_x = head_loc['x']
    head_y = head_loc['y']

    for x in range(16):
        body_map[x] = {}
        for y in range(16):
            body_map[x][y] = False
            for bod in body:
                if bod['x'] == x and bod['y'] == y:
                    body_map[x][y] = True

    for x in range(15):
        board_score[x] = {}
        for y in range(15):
            board_score[x][y] = {'food': False, 'x': x, 'y': y, 'distance': abs(head_x - x) + abs(head_y - y),
                                 'body': body_map[x][y]}

    for x in food:
        x_score = x['x']
        y_score = x['y']
        board_score[x_score][y_score] = {'food': True, 'x': x_score, 'y': y_score,
                                         'distance': abs(head_x - x_score) + abs(head_y - y_score),
                                         'body': body_map[x_score][y_score]}

    smallest = 1000
    board_piece = None

    for x in board_score:
        for y in board_score[x]:
            score = board_score[x][y]
            if not score['food']:
                continue
            if score['body']:
                continue
            if score['distance'] < smallest:
                smallest = score['distance']
                board_piece = score

    if board_piece is None:
        return move_response('down')

    if board_piece['y'] != head_y:
        if board_piece['y'] > head_y:
            return move_response(get_move_direction('down', head_x, head_y))
        else:
            return move_response(get_move_direction('up', head_x, head_y))

    if board_piece['x'] != head_x:
        if board_piece['x'] > head_x:
            return move_response(get_move_direction('right', head_x, head_y))
        else:
            return move_response(get_move_direction('left', head_x, head_y))

    return move_response(get_move_direction('up', head_x, head_y))


def get_move_direction(attempt, head_x, head_y):
    adjusted_head_x = get_adjusted_x(head_x, attempt)
    adjusted_head_y = get_adjusted_y(head_y, attempt)
    if not body_map[adjusted_head_x][adjusted_head_y] and 0 <= adjusted_head_x <= 15 and 0 <= adjusted_head_y <= 15:
        return attempt
    for direction in directions:
        adj_x = get_adjusted_x(head_x, direction)
        adj_y = get_adjusted_y(head_y, direction)
        if adj_x < 0 or adj_x > 15:
            continue
        if adj_y < 0 or adj_y > 15:
            continue
        if not body_map[adj_x][adj_y]:
            return direction
    return attempt


def get_adjusted_y(head_y, direction):
    if direction == 'down':
        return head_y + 1
    if direction == 'up':
        return head_y - 1
    return head_y


def get_adjusted_x(head_x, direction):
    if direction == 'right':
        return head_x + 1
    if direction == 'left':
        return head_x - 1
    return head_x

@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    # print(json.dumps(data))

    return end_response()


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
