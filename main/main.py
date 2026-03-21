from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

connections = []
usernames = {}
rooms = {}

app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve HTML
@app.get("/")
async def home():
    with open("templates/index.html") as f:
        return HTMLResponse(f.read())

# Broadcast message to room
async def broadcast(room,data):

    for conn in connections:
        if rooms.get(conn)==room:
            await conn.send_json(data)

# Send online users list
async def send_user_list(room):

    users=[]

    for ws in usernames:
        if rooms.get(ws)==room:
            users.append(usernames[ws])

    for ws in connections:
        if rooms.get(ws)==room:
            await ws.send_json({
                "type":"users",
                "users":users
            })

# WebSocket
@app.websocket("/ws")
async def websocket(ws: WebSocket):

    await ws.accept()

    try:

        data=await ws.receive_json()

        username=data["username"]
        room=data["room"]

        connections.append(ws)
        usernames[ws]=username
        rooms[ws]=room

        await broadcast(room,{
        "type":"system",
        "message":f"{username} joined {room}"
        })

        await send_user_list(room)

        while True:

            data=await ws.receive_json()

            if data["type"]=="chat":

                await broadcast(rooms[ws],{
                "type":"chat",
                "username":username,
                "message":data["message"]
                })

            if data["type"]=="typing":

                await broadcast(rooms[ws],{
                "type":"typing",
                "username":username
                })

            if data["type"]=="stop_typing":

                await broadcast(rooms[ws],{
                "type":"stop_typing"
                })

            if data["type"]=="change_room":

                old_room=rooms[ws]
                new_room=data["room"]

                rooms[ws]=new_room

                await broadcast(old_room,{
                "type":"system",
                "message":f"{username} left {old_room}"
                })

                await broadcast(new_room,{
                "type":"system",
                "message":f"{username} joined {new_room}"
                })

                await send_user_list(old_room)
                await send_user_list(new_room)

    except WebSocketDisconnect:

        user=usernames.get(ws)
        room=rooms.get(ws)

        if ws in connections:
            connections.remove(ws)

        usernames.pop(ws,None)
        rooms.pop(ws,None)

        await broadcast(room,{
        "type":"system",
        "message":f"{user} left {room}"
        })

        await send_user_list(room)

if __name__=="__main__":
    uvicorn.run("main:app",host="localhost",port=8000,reload=True)