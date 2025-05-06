import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from lark_oapi.api.contact.v3 import *
import json

# Set this to your Feishu email
YOUR_EMAIL = "martin.guinto@example.com"  # Replace with your actual Feishu email

# Global flag for out-of-office mode
IS_OUT = True

# Placeholder for your Feishu user ID (will be fetched via API)
YOUR_USER_ID = None


def get_user_id_by_email(email: str) -> str:
    """Fetch Feishu user ID by email"""
    request = BatchGetIdRequest.builder().emails([email]).build()
    response = client.contact.v3.user.batch_get_id(request)

    if response.success() and response.data and email in response.data.email_users:
        return response.data.email_users[email][0].user_id
    else:
        raise Exception(f"Failed to fetch user ID for {email}: {response.msg}")


def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    if not IS_OUT or YOUR_USER_ID is None:
        return

    # Check if message is p2p and sent to your chat
    if data.event.message.chat_type != "p2p":
        return

    # Skip messages not sent to you
    if data.event.message.chat_id != YOUR_USER_ID:
        return

    # Skip responding to yourself
    if data.event.sender.sender_id.user_id == YOUR_USER_ID:
        return

    # Compose auto-reply
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

# Initialize client
client = lark.Client.builder().app_id(lark.APP_ID).app_secret(lark.APP_SECRET).build()

# Initialize WebSocket
wsClient = lark.ws.Client(
    lark.APP_ID,
    lark.APP_SECRET,
    event_handler=event_handler,
    log_level=lark.LogLevel.DEBUG,
)


def main():
    global YOUR_USER_ID
    # Fetch your own user ID by email
    YOUR_USER_ID = get_user_id_by_email(YOUR_EMAIL)
    # Start WebSocket
    wsClient.start()


if __name__ == "__main__":
    main()