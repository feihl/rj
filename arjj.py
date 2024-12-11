from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests

# Backend API URL
BASE_URL = "http://127.0.0.1:8000"

# Home Screen
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Welcome to Room Scheduler!", font_size=24))

        btn_users = Button(text="Manage Users")
        btn_users.bind(on_press=self.go_to_users)
        layout.add_widget(btn_users)

        btn_rooms = Button(text="Manage Rooms")
        btn_rooms.bind(on_press=self.go_to_rooms)
        layout.add_widget(btn_rooms)

        btn_appointments = Button(text="Manage Appointments")
        btn_appointments.bind(on_press=self.go_to_appointments)
        layout.add_widget(btn_appointments)

        self.add_widget(layout)

    def go_to_users(self, instance):
        self.manager.current = 'users'

    def go_to_rooms(self, instance):
        self.manager.current = 'rooms'

    def go_to_appointments(self, instance):
        self.manager.current = 'appointments'

# User Management Screen
class UserScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        self.layout.add_widget(Label(text="Manage Users", font_size=24))

        # List Users Button
        btn_list_users = Button(text="List Users")
        btn_list_users.bind(on_press=self.list_users)
        self.layout.add_widget(btn_list_users)

        # Add User Button
        btn_add_user = Button(text="Add User")
        btn_add_user.bind(on_press=self.add_user)
        self.layout.add_widget(btn_add_user)

        btn_back = Button(text="Back to Home")
        btn_back.bind(on_press=self.go_back_home)
        self.layout.add_widget(btn_back)

        self.add_widget(self.layout)

    def list_users(self, instance):
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            users = response.json()
            for user in users:
                self.layout.add_widget(Label(text=f"ID: {user['id']} Name: {user['name']} Email: {user['email']}"))
        else:
            self.layout.add_widget(Label(text="Failed to fetch users."))

    def add_user(self, instance):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Add New User", font_size=24))
        
        name_input = TextInput(hint_text="Name")
        email_input = TextInput(hint_text="Email")
        self.layout.add_widget(name_input)
        self.layout.add_widget(email_input)

        btn_submit = Button(text="Submit")
        btn_submit.bind(on_press=lambda x: self.submit_user(name_input.text, email_input.text))
        self.layout.add_widget(btn_submit)

        # Always keep the back button present
        btn_back = Button(text="Back")
        btn_back.bind(on_press=self.go_back_home)
        self.layout.add_widget(btn_back)

    def go_back_home(self, instance):
        self.manager.current = 'home'

    def submit_user(self, name, email):
        if not name or not email:
            self.layout.add_widget(Label(text="Please provide both name and email."))
            return
        response = requests.post(f"{BASE_URL}/users", json={"name": name, "email": email})
        if response.status_code == 200:
            self.layout.add_widget(Label(text="User added successfully!"))
        else:
            self.layout.add_widget(Label(text="Failed to add user."))

# Room Management Screen
class RoomScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(Label(text="Manage Rooms", font_size=24))

        # List Rooms Button
        btn_list_rooms = Button(text="List Rooms")
        btn_list_rooms.bind(on_press=self.list_rooms)
        self.layout.add_widget(btn_list_rooms)

        # Add Room Button
        btn_add_room = Button(text="Add Room")
        btn_add_room.bind(on_press=self.add_room)
        self.layout.add_widget(btn_add_room)

        # Back to Home Button
        btn_back = Button(text="Back to Home")
        btn_back.bind(on_press=self.go_back_home)
        self.layout.add_widget(btn_back)

        self.add_widget(self.layout)

    def list_rooms(self, instance):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Room List", font_size=24))

        response = requests.get(f"{BASE_URL}/rooms")
        if response.status_code == 200:
            rooms = response.json()
            for room in rooms:
                room_box = BoxLayout(orientation='horizontal')
                room_box.add_widget(Label(
                    text=f"ID: {room['id']}, Name: {room['name']}, Location: {room['location']}, Capacity: {room['capacity']}"
                ))
                # Edit Button
                btn_edit = Button(text="Edit")
                btn_edit.bind(on_press=lambda x, r=room: self.edit_room(r))
                room_box.add_widget(btn_edit)

                # Delete Button
                btn_delete = Button(text="Delete")
                btn_delete.bind(on_press=lambda x, r=room: self.delete_room(r['id']))
                room_box.add_widget(btn_delete)

                self.layout.add_widget(room_box)
        else:
            self.layout.add_widget(Label(text="Failed to fetch rooms."))

        # Back Button
        btn_back = Button(text="Back")
        btn_back.bind(on_press=lambda x: self.show_main_screen())
        self.layout.add_widget(btn_back)

    def add_room(self, instance):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Add New Room", font_size=24))

        # Input Fields
        name_input = TextInput(hint_text="Room Name")
        location_input = TextInput(hint_text="Location")
        capacity_input = TextInput(hint_text="Capacity")
        self.layout.add_widget(name_input)
        self.layout.add_widget(location_input)
        self.layout.add_widget(capacity_input)

        # Submit Button
        btn_submit = Button(text="Submit")
        btn_submit.bind(on_press=lambda x: self.submit_room(name_input.text, location_input.text, capacity_input.text))
        self.layout.add_widget(btn_submit)

        # Back Button
        btn_back = Button(text="Back")
        btn_back.bind(on_press=lambda x: self.show_main_screen())
        self.layout.add_widget(btn_back)

    def edit_room(self, room):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text=f"Edit Room ID: {room['id']}", font_size=24))

        # Input Fields with pre-filled values
        name_input = TextInput(text=room['name'], hint_text="Room Name")
        location_input = TextInput(text=room['location'], hint_text="Location")
        capacity_input = TextInput(text=str(room['capacity']), hint_text="Capacity")
        self.layout.add_widget(name_input)
        self.layout.add_widget(location_input)
        self.layout.add_widget(capacity_input)

        # Submit Button
        btn_submit = Button(text="Update")
        btn_submit.bind(on_press=lambda x: self.update_room(room['id'], name_input.text, location_input.text, capacity_input.text))
        self.layout.add_widget(btn_submit)

        # Back Button
        btn_back = Button(text="Back")
        btn_back.bind(on_press=lambda x: self.show_main_screen())
        self.layout.add_widget(btn_back)

    def update_room(self, room_id, name, location, capacity):
        try:
            response = requests.put(f"{BASE_URL}/rooms/{room_id}", json={
                "name": name,
                "location": location,
                "capacity": int(capacity)
            })
            if response.status_code == 200:
                self.layout.add_widget(Label(text="Room updated successfully!"))
            else:
                self.layout.add_widget(Label(text="Failed to update room."))
        except ValueError:
            self.layout.add_widget(Label(text="Invalid capacity value. Please enter a number."))

    def delete_room(self, room_id):
        response = requests.delete(f"{BASE_URL}/rooms/{room_id}")
        if response.status_code == 200:
            self.layout.add_widget(Label(text="Room deleted successfully!"))
            self.list_rooms(None)  # Refresh the room list
        else:
            self.layout.add_widget(Label(text="Failed to delete room."))

    def submit_room(self, name, location, capacity):
        try:
            response = requests.post(f"{BASE_URL}/rooms", json={
                "name": name,
                "location": location,
                "capacity": int(capacity)
            })
            if response.status_code == 200:
                self.layout.add_widget(Label(text="Room added successfully!"))
            else:
                self.layout.add_widget(Label(text="Failed to add room."))
        except ValueError:
            self.layout.add_widget(Label(text="Invalid capacity value. Please enter a number."))

    def show_main_screen(self):
        self.layout.clear_widgets()
        self.__init__()

    def go_back_home(self, instance):
        self.manager.current = 'home'



# Appointment Management Screen
class AppointmentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Manage Appointments", font_size=24))

        btn_back = Button(text="Back to Home")
        btn_back.bind(on_press=self.go_back_home)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def go_back_home(self, instance):
        self.manager.current = 'home'

# Screen Manager
class RoomSchedulerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(UserScreen(name='users'))
        sm.add_widget(RoomScreen(name='rooms'))
        sm.add_widget(AppointmentScreen(name='appointments'))
        return sm

if __name__ == "__main__":
    RoomSchedulerApp().run()
