import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json

# Global out-of-office flag
IS_OUT = True  # Set to False when you're back

# Your user ID or username
YOUR_FEISHU_USERNAME = "martin.guinto"

# Register event handler
def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    if not IS_OUT:
        return  # You're not out, don't auto-reply

    # Get sender and receiver info
    sender_id = data.event.sender.sender_id.user_id
    receiver_id = data.event.message.mentions[0].id.user_id if data.event.message.mentions else ""

    # Prevent replying to yourself or wrong recipient
    if data.event.sender.sender_id.union_id == data.event.message.sender_id.union_id:
        return  # Do not respond to own messages

    # Optional: check if this message is for you
    if data.event.message.chat_type != "p2p":
        return  # Only handle private messages

    # Compose reply
    content = json.dumps({
        "text": "Hi, this is an automated message. Martin Guinto is currently unavailable or on leave. He will get back to you once he's back. Thank you!"
    })

    request = (
        CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(data.event.message.chat_id)
            .msg_type("text")
            .content(content)
            .build()
        )
        .build()
    )

    response = client.im.v1.chat.create(request)

    if not response.success():
        raise Exception(
            f"client.im.v1.chat.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )

# Register event handler
event_handler = (
    lark.EventDispatcherHandler.builder("", "")
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)
    .build()
)

# Initialize Lark client and WebSocket
client = lark.Client.builder().app_id(lark.APP_ID).app_secret(lark.APP_SECRET).build()
wsClient = lark.ws.Client(
    lark.APP_ID,
    lark.APP_SECRET,
    event_handler=event_handler,
    log_level=lark.LogLevel.DEBUG,
)

def main():
    wsClient.start()

if __name__ == "__main__":
    main()