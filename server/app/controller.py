from service import lifespan
from fastapi import FastAPI, status, Depends, WebSocket
from service import Service
from models.token import Token
from models.user import User, SpotifyUser
from models.session import Session
from starlette.middleware.cors import CORSMiddleware
from typing import Annotated

service = Service()
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.post("/auth-codes", status_code=status.HTTP_201_CREATED)
async def authorize_spotify(user: SpotifyUser) -> Token:
    # TODO: replace the spotify token getting with spotipy
    # global spotify_token
    # spotify_token = exchange_code_for_token(user.auth_code)
    user = await service.create_user(user)
    return service.generate_token(user)


@app.post("/token", status_code=status.HTTP_201_CREATED)
async def authorize(user: User) -> Token:
    user = await service.create_user(user)
    return service.generate_token(user)


@app.get("/", status_code=status.HTTP_200_OK)
async def read_root(user_id: Annotated[str, Depends(service.verify_token)]) -> dict:
    await service.validate_user(user_id)
    user = await service.get_user(user_id)
    return {"Hello World": "User. Your details are:", "user_id": user.id, "username": user.username}


@app.post("/sessions", status_code=status.HTTP_201_CREATED, response_model=Session)
async def create_new_session(user_id: Annotated[str, Depends(service.verify_token)], session: Session) -> Session:
    await service.validate_user(user_id)
    return await service.create_session(user_id, session)


@app.get("/sessions", status_code=status.HTTP_200_OK, response_model=list[Session])
async def get_session() -> list[Session]:
    return await service.get_all_sessions()


# TODO: delete if onboarding using session_ids is not required
@app.post("/sessions/{session_id}/guests", status_code=status.HTTP_200_OK, response_model=Session)
async def add_guest(guest_id: Annotated[str, Depends(service.verify_token)], session_id: str) -> Session:
    await service.validate_session(session_id)
    return await service.add_guest_to_session(guest_id, session_id, "")


@app.post("/sessions/join/{invite_token}", status_code=status.HTTP_200_OK, response_model=Session)
async def join_session(guest_id: Annotated[str, Depends(service.verify_token)], invite_token: str) -> Session:
    await service.validate_user(guest_id)
    await service.validate_invite(invite_token)
    return await service.add_guest_to_session(guest_id, "", invite_token)


@app.delete("/sessions/{session_id}/guests/{guest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_guest(host_id: Annotated[str, Depends(service.verify_token)], session_id: str, guest_id: str) -> None:
    await service.validate_user(host_id)
    await service.validate_session(session_id)
    await service.remove_guest_from_session(host_id, guest_id, session_id)


@app.delete("/sessions/{session_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_session(guest_id: Annotated[str, Depends(service.verify_token)], session_id: str) -> None:
    await service.validate_user(guest_id)
    await service.validate_session(session_id)
    await service.remove_guest_from_session("", guest_id, session_id)


@app.websocket("/ws/{session_id}")
async def websocket_session(websocket: WebSocket, session_id: str):
    await websocket.accept()
    await service.establish_ws_connection_to_session(websocket, session_id)


# This WS code is inspired by the encode/broadcaster package.
# If something needs to be fixed or changed, look at their GitHub repo.
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     # This endpoint only serves a simplex operation.
#     # If the future desires duplex operations, look at the encode/broadcaster example.
#     await websocket.accept()
#
#     async with manager.subscribe(channel="test") as subscriber:
#         try:
#             async for event in subscriber:
#                 await websocket.send_text(event.message)
#         except WebSocketDisconnect:
#             pass
#
#
# async def test_websocket():
#     event = asyncio.Event()
#     asyncio.create_task(set_websocket_test_task(event))
#     await handle_test_event(event)
#
#
# async def set_websocket_test_task(event):
#     while True:
#         await asyncio.sleep(2)
#         event.set()
#         event.clear()
#
#
# async def handle_test_event(event):
#     while True:
#         await event.wait()
#         await manager.publish(channel="test", message="WEBSOCKET TEST MESSAGE")