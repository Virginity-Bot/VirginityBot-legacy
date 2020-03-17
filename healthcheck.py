# import asyncio
# import socket
# import os
# from sanic import Sanic

# app = Sanic(__name__)
# server_socket = '/tmp/sanic.sock'
# sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)


# @app.route('/healthcheck')
# def healthcheck(req):
#   return 'Healthy'


# def start_server():
#   try:
#     os.remove(server_socket)
#   finally:
#     sock.bind(server_socket)

#   loop = asyncio.get_event_loop()
#   server_coro = app.create_server(
#       sock=sock,
#       return_asyncio_server=True,
#       asyncio_server_kwargs=dict(start_serving=False)
#   )
#   server = loop.run_until_complete(server_coro)

#   try:
#     assert server.is_serving() is False
#     loop.run_until_complete(server.start_serving())
#     assert server.is_serving() is True
#     loop.run_until_complete(server.serve_forever())
#   except KeyboardInterrupt:
#     server.close()
#     loop.close()


# def stop_server():
#   app.shutdown()


from aiohttp import web


async def handle(request):
  name = request.match_info.get('name', "Anonymous")
  text = "Hello, " + name
  return web.Response(text=text)


async def wshandle(request):
  ws = web.WebSocketResponse()
  await ws.prepare(request)

  async for msg in ws:
    if msg.type == web.WSMsgType.text:
      await ws.send_str("Hello, {}".format(msg.data))
    elif msg.type == web.WSMsgType.binary:
      await ws.send_bytes(msg.data)
    elif msg.type == web.WSMsgType.close:
      break

  return ws


app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/echo', wshandle),
                web.get('/{name}', handle)])


def start_server():
  web.run_app(app)
