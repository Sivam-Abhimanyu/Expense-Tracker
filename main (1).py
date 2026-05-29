import datetime
import sqlite3
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp

# ANDROID SAFE DATABASE PATH
DB_PATH = os.path.join(
    App.get_running_app().user_data_dir
    if App.get_running_app()
    else ".",
    "expenses.db"
)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mode TEXT,
            reason TEXT,
            quantity TEXT,
            price REAL
        )
    ''')

    conn.commit()
    conn.close()

# --- UI DESIGN (KV Language) ---
KV = '''
ScreenManager:
    WelcomeScreen:
    ExpenseScreen:
    ViewScreen:

<WelcomeScreen>:
    name: 'welcome'

    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)
        md_bg_color: 0.95, 0.95, 0.95, 1

        MDLabel:
            text: "Welcome by AVSK"
            font_style: "H4"
            halign: "center"

        MDRaisedButton:
            text: "Expense"
            size_hint_x: 0.8
            pos_hint: {"center_x": 0.5}
            on_release: root.manager.current = 'expense'

        MDRaisedButton:
            text: "View"
            size_hint_x: 0.8
            pos_hint: {"center_x": 0.5}
            on_release:
                root.manager.current = 'view'
                root.manager.get_screen('view').clear_table()

        Widget:

<ExpenseScreen>:
    name: 'expense'

    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Add Expense"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        ScrollView:

            MDBoxLayout:
                orientation: 'vertical'
                adaptive_height: True
                padding: dp(15)
                spacing: dp(15)

                MDRaisedButton:
                    id: date_btn
                    text: "Select Date"
                    on_release: root.show_date_picker()

                MDTextField:
                    id: mode_input
                    hint_text: "Mode of Payment"
                    readonly: True
                    on_focus:
                        if self.focus: root.open_mode_menu()

                MDTextField:
                    id: mode_other
                    hint_text: "Specify Payment Mode"
                    opacity: 0
                    disabled: True

                MDTextField:
                    id: reason_input
                    hint_text: "Reason for Expense"
                    readonly: True
                    on_focus:
                        if self.focus: root.open_reason_menu()

                MDTextField:
                    id: reason_other
                    hint_text: "Specify Reason"
                    opacity: 0
                    disabled: True

                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(60)

                    MDTextField:
                        id: qty_val
                        hint_text: "Quantity"
                        input_filter: 'float'

                    MDTextField:
                        id: qty_unit
                        hint_text: "Unit"
                        readonly: True
                        on_focus:
                            if self.focus: root.open_unit_menu()

                MDTextField:
                    id: price_input
                    hint_text: "Price"
                    input_filter: 'float'

                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(10)

                    MDRaisedButton:
                        text: "Submit"
                        on_release: root.submit_data()

                    MDFlatButton:
                        text: "Clear"
                        on_release: root.clear_fields()

                    MDFlatButton:
                        text: "Back"
                        on_release: root.go_back()

<ViewScreen>:
    name: 'view'

    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        MDTopAppBar:
            title: "View Expenses"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(5)
            size_hint_y: None
            height: dp(50)

            MDRaisedButton:
                id: from_date_btn
                text: "From Date"
                on_release: root.show_date_picker('from')

            MDRaisedButton:
                id: to_date_btn
                text: "To Date"
                on_release: root.show_date_picker('to')

        MDTextField:
            id: filter_reason
            hint_text: "Filter by Reason"
            readonly: True
            on_focus:
                if self.focus: root.open_filter_menu()

        MDRaisedButton:
            text: "View"
            on_release: root.fetch_and_display_data()

        MDBoxLayout:
            id: table_container
            orientation: 'vertical'
            size_hint_y: 0.7

        MDLabel:
            id: total_label
            text: "Total: ₹0.00"
            halign: "right"
            font_style: "H6"
'''

# --- WELCOME SCREEN ---
class WelcomeScreen(Screen):
    pass

# --- EXPENSE SCREEN ---
class ExpenseScreen(Screen):

    def on_enter(self):
        self.clear_fields()

    def clear_fields(self):
        self.selected_date = datetime.date.today().strftime("%Y-%m-%d")

        self.ids.date_btn.text = f"Date: {self.selected_date}"

        self.ids.mode_input.text = ""
        self.ids.mode_other.text = ""

        self.ids.reason_input.text = ""
        self.ids.reason_other.text = ""

        self.ids.qty_val.text = ""
        self.ids.qty_unit.text = ""

        self.ids.price_input.text = ""

        self.toggle_other_field('mode', False)
        self.toggle_other_field('reason', False)

    def go_back(self):
        self.manager.current = 'welcome'

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self.selected_date = value.strftime("%Y-%m-%d")
        self.ids.date_btn.text = f"Date: {self.selected_date}"

    def toggle_other_field(self, field_type, show):

        target = (
            self.ids.mode_other
            if field_type == 'mode'
            else self.ids.reason_other
        )

        if show:
            target.opacity = 1
            target.disabled = False
        else:
            target.opacity = 0
            target.disabled = True
            target.text = ""

    # PAYMENT MODE MENU
    def open_mode_menu(self):

        items = ["Cash", "UPI", "Card", "Others"]

        menu_items = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=i: self.set_mode(x)
            }
            for i in items
        ]

        self.mode_menu = MDDropdownMenu(
            caller=self.ids.mode_input,
            items=menu_items,
            width_mult=4
        )

        self.mode_menu.open()

    def set_mode(self, text):
        self.ids.mode_input.text = text
        self.mode_menu.dismiss()

        self.toggle_other_field('mode', text == "Others")

    # REASON MENU
    def open_reason_menu(self):

        items = [
            "Bill payment",
            "Grocery",
            "Fuel",
            "Buy Products",
            "Others"
        ]

        menu_items = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=i: self.set_reason(x)
            }
            for i in items
        ]

        self.reason_menu = MDDropdownMenu(
            caller=self.ids.reason_input,
            items=menu_items,
            width_mult=4
        )

        self.reason_menu.open()

    def set_reason(self, text):
        self.ids.reason_input.text = text
        self.reason_menu.dismiss()

        self.toggle_other_field('reason', text == "Others")

    # UNIT MENU
    def open_unit_menu(self):

        items = ["kg", "ltr", "nos"]

        menu_items = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=i: self.set_unit(x)
            }
            for i in items
        ]

        self.unit_menu = MDDropdownMenu(
            caller=self.ids.qty_unit,
            items=menu_items,
            width_mult=2
        )

        self.unit_menu.open()

    def set_unit(self, text):
        self.ids.qty_unit.text = text
        self.unit_menu.dismiss()

    # SUBMIT DATA
    def submit_data(self):

        final_mode = (
            self.ids.mode_other.text
            if self.ids.mode_input.text == "Others"
            else self.ids.mode_input.text
        )

        final_reason = (
            self.ids.reason_other.text
            if self.ids.reason_input.text == "Others"
            else self.ids.reason_input.text
        )

        qty = f"{self.ids.qty_val.text} {self.ids.qty_unit.text}".strip()

        price = self.ids.price_input.text

        if not final_mode or not final_reason or not price:
            self.show_alert(
                "Error",
                "Please fill Mode, Reason and Price"
            )
            return

        try:
            conn = sqlite3.connect(DB_PATH)

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO expenses
                (date, mode, reason, quantity, price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    self.selected_date,
                    final_mode,
                    final_reason,
                    qty,
                    float(price)
                )
            )

            conn.commit()
            conn.close()

            self.show_alert(
                "Success",
                "Expense Saved Successfully!"
            )

            self.clear_fields()

        except Exception as e:
            self.show_alert("Error", str(e))

    # ALERT DIALOG
    def show_alert(self, title, text):

        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )

        dialog.open()

# --- VIEW SCREEN ---
class ViewScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.from_date = ""
        self.to_date = ""

        self.data_table = None

    def go_back(self):
        self.manager.current = 'welcome'

    def clear_table(self):

        self.ids.table_container.clear_widgets()

        self.ids.total_label.text = "Total: ₹0.00"

        self.ids.from_date_btn.text = "From Date"
        self.ids.to_date_btn.text = "To Date"

        self.ids.filter_reason.text = "All"

        self.from_date = ""
        self.to_date = ""

    # DATE PICKER
    def show_date_picker(self, target):

        date_dialog = MDDatePicker()

        date_dialog.bind(
            on_save=lambda instance, value, range:
            self.on_date_save(target, value)
        )

        date_dialog.open()

    def on_date_save(self, target, value):

        date_str = value.strftime("%Y-%m-%d")

        if target == 'from':
            self.from_date = date_str
            self.ids.from_date_btn.text = f"From: {date_str}"

        else:
            self.to_date = date_str
            self.ids.to_date_btn.text = f"To: {date_str}"

    # FILTER MENU
    def open_filter_menu(self):

        items = [
            "All",
            "Bill payment",
            "Grocery",
            "Fuel",
            "Buy Products"
        ]

        menu_items = [
            {
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=i: self.set_filter(x)
            }
            for i in items
        ]

        self.filter_menu = MDDropdownMenu(
            caller=self.ids.filter_reason,
            items=menu_items,
            width_mult=4
        )

        self.filter_menu.open()

    def set_filter(self, text):
        self.ids.filter_reason.text = text
        self.filter_menu.dismiss()

    # FETCH DATA
    def fetch_and_display_data(self):

        if not self.from_date or not self.to_date:
            self.ids.total_label.text = "Select both Dates!"
            return

        reason_filter = self.ids.filter_reason.text or "All"

        conn = sqlite3.connect(DB_PATH)

        cursor = conn.cursor()

        if reason_filter == "All":

            cursor.execute(
                """
                SELECT date, mode, reason, quantity, price
                FROM expenses
                WHERE date BETWEEN ? AND ?
                """,
                (self.from_date, self.to_date)
            )

        else:

            cursor.execute(
                """
                SELECT date, mode, reason, quantity, price
                FROM expenses
                WHERE (date BETWEEN ? AND ?)
                AND reason = ?
                """,
                (
                    self.from_date,
                    self.to_date,
                    reason_filter
                )
            )

        rows = cursor.fetchall()

        conn.close()

        self.ids.table_container.clear_widgets()

        table_data = []

        total_sum = 0.0

        for r in rows:

            table_data.append(
                (
                    r[0],
                    r[1],
                    r[2],
                    r[3],
                    f"₹{r[4]:.2f}"
                )
            )

            total_sum += r[4]

        self.data_table = MDDataTable(
            size_hint=(1, 1),

            use_pagination=True,

            column_data=[
                ("Date", dp(25)),
                ("Mode", dp(20)),
                ("Reason", dp(25)),
                ("Qty", dp(15)),
                ("Price", dp(20)),
            ],

            row_data=table_data
        )

        self.ids.table_container.add_widget(self.data_table)

        self.ids.total_label.text = (
            f"Total Sum: ₹{total_sum:.2f}"
        )

# --- MAIN APP ---
class ExpenseTrackerApp(MDApp):

    def build(self):

        self.theme_cls.primary_palette = "Blue"

        init_db()

        return Builder.load_string(KV)

# --- RUN APP ---
if __name__ == '__main__':
    ExpenseTrackerApp().run()
