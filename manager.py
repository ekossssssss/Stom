from db import Database
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QMessageBox, QLineEdit, QWidget, QTableView)
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QPixmap, QImage
from PyQt6.QtCore import Qt
from manager_window import Ui_ManagerWindow
from sebestoimost import Ui_Sebes
from autariz import Ui_Emploie
from register import  Ui_AddingCustomer
from red_customer import Ui_RedZakaz

class LoginManagerWindow(QWidget, Ui_Emploie):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Авторизация менеджера")
        pixmap = QPixmap("logo-01.jpg" )
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

        self.pushButton.clicked.connect(self.authenticate_manager)
        self.password_input = self.lineEdit_2
        self.login_input = self.lineEdit
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def authenticate_manager(self):
        db = Database()
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        manager_id = db.check_manager_login(login, password)
        if manager_id:
            self.open_manager_window(manager_id)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверные учетные данные")

    def open_manager_window(self, manager_id):
        self.manager_window = ManagerWindow(manager_id)
        self.manager_window.show()
        self.close()

class ManagerWindow(QMainWindow, Ui_ManagerWindow):
    def __init__(self, manager_id):
        super().__init__()
        self.setupUi(self)
        self.manager_id = manager_id
        self.db = Database()
        self.initialize_ui()

    def initialize_ui(self):
        self.setWindowTitle("Менеджер заказов")
        pixmap = QPixmap("logo-01.jpg")
        self.label_3.setPixmap(pixmap)
        self.label_3.setScaledContents(True)
        self.pushButton.clicked.connect(self.sebes_win)
        self.pushButton_2.clicked.connect(self.new_customer)
        self.pushButton_3.clicked.connect(self.red_cust_win)
        self.pushButton_4.clicked.connect(self.raschot)
        self.load_data()

    def load_data(self):
        try:
            data = self.db.get_zakazi()
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(
                ["Номер заказа", "Заказчик", "Статус", "Дата"]
            )
            for row in data:
                items = [QStandardItem(str(row[key])) for key in row]
                model.appendRow(items)
            self.tableView.setModel(model)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def sebes_win(self):
        try:
            self.sebes_window = Sebestoimost(self.manager_id)
            self.sebes_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка открытия: {str(e)}")
    def new_customer(self):
        try:
            self.cust_window = NewCustomer(self.manager_id)
            self.cust_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка открытия: {str(e)}")

    def red_cust_win(self):
        try:
            self.red_window = Redaktirovanie(self.manager_id)
            self.red_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка открытия: {str(e)}")

    def raschot(self):
        try:
            # Вызов метода raschot из вашего класса базы данных
            self.db.raschot()
            QMessageBox.information(self, "Успех", "Расчет выполнен успешно!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при выполнении расчета: {str(e)}")

class Redaktirovanie(QMainWindow, Ui_RedZakaz):
    def __init__(self, manager_id):
        super().__init__()
        self.setupUi(self)
        self.manager_id = manager_id
        self.db = Database()
        self.setWindowTitle("Редактирование заказчика")
        pixmap = QPixmap("logo-01.jpg")
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.pushButton.clicked.connect(self.nazad)
        self.load_data()

    def load_data(self):
        try:
            data = self.db.get_customers()
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(
                ["Номер", "Имя организации", "ИНН", "Тип", "Имя", "Фамилия", "Отчество", "КПП",
                 "ОРГН", "Почта", "Адрес"]
            )
            for row in data:
                items = [QStandardItem(str(row[key])) for key in row]
                model.appendRow(items)
            self.tableView.setModel(model)
            self.tableView.setEditTriggers(QTableView.EditTrigger.AllEditTriggers)  # Разрешить редактирование
            model.dataChanged.connect(self.on_data_changed)  # Подключить сигнал
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def on_data_changed(self, top_left, bottom_right):
        try:
            model = self.tableView.model()
            for row in range(top_left.row(), bottom_right.row() + 1):
                # Получаем данные из строки
                row_data = {}
                for column in range(model.columnCount()):
                    index = model.index(row, column)
                    row_data[model.headerData(column, Qt.Orientation.Horizontal)] = model.data(index)

                # Обновляем данные в базе данных
                self.db.update_customer(row_data)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления данных: {str(e)}")

    def nazad(self):
        self.manager_window = ManagerWindow(self.manager_id)
        self.manager_window.show()
        self.hide()


class NewCustomer(QMainWindow, Ui_AddingCustomer):
    def __init__(self, manager_id):
        super().__init__()
        self.setupUi(self)
        self.manager_id = manager_id
        self.db = Database()
        self.initialize_ui()

    def initialize_ui(self):
        self.setWindowTitle("Добавление нового заказчика")
        self.back.clicked.connect(self.close_window)
        self.register_2.clicked.connect(self.get_new_customer)
        self.load_organization_types()

    def load_organization_types(self):
        try:
            organization_types = self.db.get_organization_types()  # Получаем список словарей [{'id': 1, 'name': 'ООО'}, ...]
            self.comboBox.clear()  # Очищаем комбобокс перед заполнением

            for org in organization_types:  # org — это словарь, например {'id': 1, 'name': 'ООО'}
                org_id = org['id']  # Извлекаем id
                org_name = org['name']  # Извлекаем name
                self.comboBox.addItem(org_name, org_id)  # Добавляем элемент с текстом org_name и данными org_id

            # Проверка, что комбобокс заполнен
            print(f"Заполнен комбобокс: {[self.comboBox.itemText(i) for i in range(self.comboBox.count())]}")
        except Exception as e:
            print(f"Ошибка при загрузке типов организаций: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить типы организаций")
    def get_new_customer(self):
        try:
            login = str(self.login.text())
            password = str(self.Password.text())
            name = str(self.Name_organization.text())
            inn = str(self.INN.text())
            type_id = self.comboBox.currentData()  # Получаем ID из комбобокса
            name_d = str(self.Name.text())
            fam_d = str(self.last_name.text())
            ot_d = str(self.Middle_name.text())
            kpp = str(self.KPP.text())
            orgn = str(self.OGRN.text())
            email = str(self.email.text())
            address = str(self.Adress.text())

            # Проверка на пустые поля
            if not all([login, password, name, inn, type_id, name_d, fam_d, kpp, orgn, email, address]):
                QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
                return

            if self.db.new_customer(login, password, name, inn, type_id, name_d, fam_d, ot_d, kpp, orgn, email,
                                    address):
                QMessageBox.information(self, "Успех", "Заказчик успешно добавлен!")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось выполнить операцию")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")

    def close_window(self):
        self.manager_window = ManagerWindow(self.manager_id)
        self.manager_window.show()
        self.hide()


class Sebestoimost(QMainWindow, Ui_Sebes):
        def __init__(self, manager_id):
            super().__init__()
            self.setupUi(self)
            self.manager_id = manager_id
            self.db = Database()
            self.initialize_ui()

        def initialize_ui(self):
            self.setWindowTitle("Расчет себестоимости")
            pixmap = QPixmap("logo-01.jpg")
            self.label_3.setPixmap(pixmap)
            self.label_3.setScaledContents(True)
            self.pushButton_2.clicked.connect(self.close_window)
            self.pushButton_3.clicked.connect(self.get_sebestoimost)
            self.pushButton.clicked.connect(self.get_odobrenie)
            self.pushButton_4.clicked.connect(self.get_otkaz)

        def get_sebestoimost(self):
            try:
                id_order = int(self.lineEdit.text())
                data = self.db.get_sebestoimoste(id_order)
                if data:
                    model = QStandardItemModel()
                    model.setHorizontalHeaderLabels(
                        ["Заказчик", "Выполненные заказы", "Сообщение"]
                    )
                    for row in data:
                        items = [QStandardItem(str(row[key])) for key in row]
                        model.appendRow(items)
                    self.tableView.setModel(model)
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите числовой ID заказа")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")

        def get_odobrenie(self):
            try:
                id_o = int(self.lineEdit_2.text())
                if self.db.odobrenie(id_o):
                    QMessageBox.information(self, "Успех", "Заказ одобрен!")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось выполнить операцию")
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректный ID заказа")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")

        def get_otkaz(self):
            try:
                id_o = int(self.lineEdit_2.text())
                if self.db.otkaz(id_o):
                    QMessageBox.information(self, "Успех", "Заказ отклонен!")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось выполнить операцию")
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректный ID заказа")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")

        def close_window(self):
            self.manager_window = ManagerWindow(self.manager_id)
            self.manager_window.show()
            self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginManagerWindow()
    login_window.show()
    sys.exit(app.exec())