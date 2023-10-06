import asyncio
import websockets
import json

from connect4 import PLAYER1, PLAYER2, Connect4

class ValidationError(ValueError):
    pass

def validate(event):
    if event['type'] != 'play':
        raise ValidationError(f'Unexpected event type {event["type"]}')

async def handler(websocket):
    game = Connect4()
    PLAYERS = [PLAYER1, PLAYER2]
    turn = 0
    moves_sent = 0

    async for message in websocket:
        try:
            event = json.loads(message)
            validate(event)
            player = PLAYERS[turn % 2]
            turn += 1
            game.play(player, event['column'])
            while len(game.moves) > moves_sent:
                (player, column, row) = game.moves[moves_sent]
                moves_sent += 1

                await websocket.send(json.dumps({
                    'type': 'play',
                    'player': player,
                    'column': column,
                    'row': row
                }))

            if game.winner:
                await websocket.send(json.dumps({
                    'type': 'win',
                    'player': game.winner,
                }))

        except Exception as exception:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': repr(exception)
            }))


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
