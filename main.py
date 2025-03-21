import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, db
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from threading import Thread
import time
import urllib.request  # ✅ Used to check internet connectivity

# ✅ Step 1: Secure Firebase Setup
firebase_config_json = base64.b64decode(os.getenv("FIREBASE_CONFIG", "")).decode()
firebase_config = json.loads(firebase_config_json)

# Initialize Firebase only if credentials are valid
if firebase_config and "private_key" in firebase_config:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred, {"databaseURL": "https://messanger-e687d-default-rtdb.firebaseio.com"})
else:
    print("⚠️ Firebase configuration missing! Check environment variables.")

# ✅ Step 2: Kivy UI Design
KV = '''
ScreenManager:
    ChatScreen:

<ChatScreen>:
    name: "chat"

    MDLabel:
        id: internet_status
        text: "✅ Connected"
        halign: "center"
        pos_hint: {"center_x": 0.5, "center_y": 0.95}  # Topmost position
        theme_text_color: "Custom"
        text_color: 0, 1, 0, 1  # Green when online

    MDLabel:
        id: notification_label
        text: ""
        halign: "center"
        pos_hint: {"center_x": 0.5, "center_y": 0.9}  # Notification below status

    MDTextField:
        id: message_input
        hint_text: "Type your message"
        pos_hint: {"center_x": 0.5, "center_y": 0.8}
        size_hint_x: 0.8

    MDRaisedButton:
        text: "Send"
        pos_hint: {"center_x": 0.5, "center_y": 0.7}
        on_release: app.send_message()

    MDLabel:
        id: chat_output
        text: "Chat History"
        pos_hint: {"center_x": 0.5, "center_y": 0.4}
        size_hint_x: 0.9
'''

# ✅ Step 3: Define Screens
class ChatScreen(Screen):
    pass

# ✅ Step 4: App Logic
class ChatApp(MDApp):
    last_message = ""  # Store last message to prevent duplicate notifications

    def build(self):
        self.sm = ScreenManager()
        Builder.load_string(KV)
        self.chat_screen = ChatScreen(name="chat")
        self.sm.add_widget(self.chat_screen)
        self.start_message_listener()  # Start real-time updates
        self.start_internet_checker()  # Start internet check loop
        return self.sm

    def check_internet(self):
        """Checks if the internet is available"""
        try:
            urllib.request.urlopen("http://www.google.com", timeout=2)  # Try to connect
            return True
        except:
            return False

    def update_internet_status(self):
        """Updates the internet connection label"""
        chat_screen = self.sm.get_screen("chat")
        internet_status_label = chat_screen.ids.internet_status

        if self.check_internet():
            internet_status_label.text = "✅ Connected"
            internet_status_label.text_color = (0, 1, 0, 1)  # Green
        else:
            internet_status_label.text = "❌ No Internet"
            internet_status_label.text_color = (1, 0, 0, 1)  # Red

    def start_internet_checker(self):
        """Runs a background thread to check internet status"""
        def check_loop():
            while True:
                self.update_internet_status()
                time.sleep(3)  # Check every 3 seconds

        Thread(target=check_loop, daemon=True).start()

    def send_message(self):
        """Sends a message to Firebase"""
        if not self.check_internet():
            return  # Don't send if no internet

        chat_screen = self.sm.get_screen("chat")
        msg_input = chat_screen.ids.message_input
        if msg_input.text:
            db.reference("messages").push({"text": msg_input.text})
            msg_input.text = ""  # Clear input field

    def update_messages(self):
        """Fetch messages from Firebase and update UI"""
        if not self.check_internet():
            return  # Don't fetch if no internet

        messages = db.reference("messages").get()
        chat_screen = self.sm.get_screen("chat")
        chat_output = chat_screen.ids.chat_output
        notification_label = chat_screen.ids.notification_label  # Get the top label

        if messages:
            chat_history = "\n".join(msg["text"] for msg in messages.values())
            last_msg = list(messages.values())[-1]["text"]
        else:
            chat_history = "No messages"
            last_msg = ""

        chat_output.text = chat_history  # Update chat history

        # ✅ Show Notification at the Top Instead of Snackbar
        if last_msg and last_msg != self.last_message:
            self.last_message = last_msg
            notification_label.text = f"📢 New Message: {last_msg}"  # Show new message

    def start_message_listener(self):
        """Listens for real-time Firebase updates"""
        def listen_for_updates():
            while True:
                self.update_messages()
                time.sleep(2)  # Refresh every 2 seconds

        Thread(target=listen_for_updates, daemon=True).start()

# ✅ Step 5: Run the App
if __name__ == "__main__":
    ChatApp().run()