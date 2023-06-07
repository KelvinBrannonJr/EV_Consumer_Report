import sys
import mysql.connector

from PyQt6.QtWidgets import QApplication, QLabel, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QToolBar, QStatusBar, QMessageBox

from PyQt6.QtGui import QAction, QIcon

from PyQt6.QtCore import Qt


# Database connection class
class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="N0r5eV1k1ng", database="electric_vehicles"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        # Establish connection to database and create cursor
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        cursor = connection.cursor()

        # return connection and cursor, destructure variables in creation of instances
        return connection, cursor

    def close_connection(self, connection, cursor):

        # Commit changes to db and close connections, refresh app table
        return connection.commit(), cursor.close(), connection.close(), ev_consumer_report.load_data()


# App Main Window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Electric Vehicle Consumer Report")
        self.setMinimumSize(600, 400)

        # Menu items
        file_menu_item = self.menuBar().addMenu("&File")
        utility_menu_item = self.menuBar().addMenu("&Utility")
        help_menu_item = self.menuBar().addMenu("&Help")

        # Add vehicle menu item and action with toolbar icon binding to action
        add_ev_vehicle = QAction(QIcon("icons/add.png"), "Add Vehicle", self)
        add_ev_vehicle.triggered.connect(self.insert)
        file_menu_item.addAction(add_ev_vehicle)

        # About menu item and action
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        # SEARCH item and action with toolbar icon binding to action
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        utility_menu_item.addAction(search_action)

        # Toolbar widget and elements, toolbar is also movable
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_ev_vehicle)
        toolbar.addAction(search_action)

        # Statusbar widget and elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # QTableWidget attributes
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Make", "Model", "Range(miles)", "Cost(us)"))

        # To hide default vertical numbers not associated with SQL database
        self.table.verticalHeader().setVisible(False)

        # Detect if cell is clicked
        self.table.cellClicked.connect(self.cell_clicked)

        # Set a center layout widget to QTableWidget instance
        self.setCentralWidget(self.table)

    # Cell clicked method
    def cell_clicked(self):
        # Edit button
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        # Delete button
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Find children of statusbar widgets and remove appending children
        # Prevent duplications of widgets for every cell click
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        # Add widgets after cell is clicked
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    # Load MySQL Database data in PyQt
    def load_data(self):
        # Connect SQL database
        connection, cursor = DatabaseConnection().connect()
        results = connection.execute("SELECT * FROM electric_vehicles")

        # Initialize table number to 0
        self.table.setRowCount(0)

        # Iterate through row numbers
        for row_number, row_data in enumerate(results):

            # Every index insert a row cell with a row number
            self.table.insertRow(row_number)

            # Iterate through column numbers
            for column_number, column_data in enumerate(row_data):

                # Every index of a row number and column number add column data
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(column_data)))

        # Close the database connection
        connection.close()

    # Insert new data method call
    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        search_dialog = SearchDialog()
        search_dialog.exec()

    def edit(self):
        edit_dialog = EditDialog()
        edit_dialog.exec()

    def delete(self):
        delete_dialog = DeleteDialog()
        delete_dialog.exec()

    def about(self):
        about_dialog = AboutDialog()
        about_dialog.exec()


# Dialog Attributes for Insert
class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set Window Attributes
        self.setWindowTitle("Insert Electric Vehicle Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add a Make widget
        self.make = QLineEdit()
        self.make.setPlaceholderText("Make")
        layout.addWidget(self.make)

        # Add a Model widget
        self.model = QLineEdit()
        self.model.setPlaceholderText("Model")
        layout.addWidget(self.model)

        # Add Range Miles widget
        self.range_miles = QLineEdit()
        self.range_miles.setPlaceholderText("Range(miles)")
        layout.addWidget(self.range_miles)

        # Add Cost widget
        self.price = QLineEdit()
        self.price.setPlaceholderText("Price(us)")
        layout.addWidget(self.price)

        # Submit button
        submit_btn = QPushButton("Add EV")
        submit_btn.clicked.connect(self.add_vehicle)
        layout.addWidget(submit_btn)

        self.setLayout(layout)

    # Add Vehicle method
    def add_vehicle(self):
        # Reference to field values stored in variables
        make = self.make.text()
        model = self.model.text()
        range_miles = self.range_miles.text()
        price = self.price.text()

        # Connect to database and create cursor
        connection, cursor = DatabaseConnection().connect()

        # Use the cursor to destructure and INSERT reference variables into related db columns
        cursor.execute("INSERT INTO electric_vehicles (make, model, range_miles, cost_us) VALUES (?, ?, ?, ?)",
                       (make, model, range_miles, price))

        # Commit changes, Close connection to database and cursor
        DatabaseConnection().close_connection(connection, cursor)

        # Close window after entry
        self.close()


# Dialog Attributes for Search
class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set Window Attributes
        self.setWindowTitle("Search Vehicle")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        search_layout = QVBoxLayout()

        # Search Vehicle Name widget
        self.search_vehicle_name = QLineEdit()
        self.search_vehicle_name.setPlaceholderText("Vehicle Name")
        search_layout.addWidget(self.search_vehicle_name)

        # Search button
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_vehicle)
        search_layout.addWidget(search_btn)

        self.setLayout(search_layout)

    # Search Vehicle method
    def search_vehicle(self):
        # Reference to field values stored in variables
        name = self.search_vehicle_name.text()

        # Connect to database and create cursor
        connection, cursor = DatabaseConnection().connect()

        # Select all fields that contained query of vehicle name in database
        result = cursor.execute("SELECT * FROM electric_vehicles WHERE name = ?", (name, ))
        rows = list(result)
        print(rows)

        # Select all fields in Main window table and find match of vehicle name
        items = ev_consumer_report.table.findItems(name, Qt.MatchFlag.MatchFixedString)

        # Highlight all names that match query and print item row to console
        for item in items:
            print(item)
            ev_consumer_report.table.item(item.row(), 1).setSelected(True)

        # Close cursor and connection to db
        cursor.close()
        connection.close()

        # Close dialog after search
        self.close()


# Dialog Attributes for Edit
class EditDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set Window Attributes
        self.setWindowTitle("Update Electric Vehicle Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get table row and column of vehicle to edit
        index = ev_consumer_report.table.currentRow()

        # Get ID from selected Row
        self.vehicle_id = ev_consumer_report.table.item(index, 0).text()

        # Get Vehicle Make
        vehicle_make = ev_consumer_report.table.item(index, 1).text()

        # Get Vehicle Model name
        vehicle_model = ev_consumer_report.table.item(index, 2).text()

        # Get Vehicle Range Miles
        vehicle_range = ev_consumer_report.table.item(index, 3).text()

        # Get Vehicle Price
        vehicle_price = ev_consumer_report.table.item(index, 3).text()

        # Add Vehicle Make widget
        self.make = QLineEdit(vehicle_make)
        self.make.setPlaceholderText("Vehicle Make")
        layout.addWidget(self.make)

        # Add Vehicle Model widget
        self.model = QLineEdit(vehicle_model)
        self.model.setPlaceholderText("Vehicle Model")
        layout.addWidget(self.model)

        # Add Range Miles widget
        self.range_miles = QLineEdit(vehicle_range)
        self.range_miles.setPlaceholderText("Range Miles")
        layout.addWidget(self.range_miles)

        # Add Price widget
        self.price = QLineEdit(vehicle_price)
        self.price.setPlaceholderText("Vehicle Price")
        layout.addWidget(self.range_miles)

        # Submit button
        submit_btn = QPushButton("Update")
        submit_btn.clicked.connect(self.update_vehicle)
        layout.addWidget(submit_btn)

        self.setLayout(layout)

    # Update method
    def update_vehicle(self):
        connection, cursor = DatabaseConnection().connect()

        # Destructure table rows and UPDATE with new values from references in edit fields
        cursor.execute("UPDATE electric_vehicles SET make = ?, model = ?, range_miles = ?, cost_us = ? WHERE id = ?",
                       (self.make.text(),
                        self.model.text(),
                        self.range_miles.text(),
                        self.price.text(),
                        self.vehicle_id))

        # Commit changes, Close connection to database and cursor
        DatabaseConnection().close_connection(connection, cursor)

        # Close dialog after update
        self.close()


# Dialog Attributes for Delete
class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set Window Attributes
        self.setWindowTitle("Delete Vehicle Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_vehicle)
        no.clicked.connect(self.close)

    # Delete Method
    def delete_vehicle(self):
        # Connect to database
        connection, cursor = DatabaseConnection().connect()

        # Get table row and column of vehicle to edit
        index = ev_consumer_report.table.currentRow()

        # Get ID from selected Row
        vehicle_id = ev_consumer_report.table.item(index, 0).text()

        # Execute SQL DELETE query using vehicle ID
        cursor.execute("DELETE FROM electric_vehicles WHERE id = ?", (vehicle_id, ))

        # Commit changes, Close connection to database and cursor
        DatabaseConnection().close_connection(connection, cursor)

        # Create a message box to relay deletion was successful
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The Record Deleted Successfully!")
        confirmation_widget.exec()

        # Close delete dialog window
        self.close()


# About Inheriting from 'QMessageBox' simple child version of a QDialog
class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")

        # Content for about section
        content = "This is a 2023 self interest comparison study in 'EV' or Electric Vehicle market." \
                  "I used PyQt6 and it's component libraries to build the UI" \
                  "I used object oriented architecture to keep my code organized and scalable." \
                  " A MySQL server database was used store findings and to managed it's contents."

        # Use set text to content
        self.setText(content)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ev_consumer_report = MainWindow()
    ev_consumer_report.show()
    ev_consumer_report.load_data()
    sys.exit(app.exec())
