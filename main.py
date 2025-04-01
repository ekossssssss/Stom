import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog,
                            QMessageBox, QLineEdit, QWidget, QTableView)
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QPixmap, QImage
from PyQt6.QtCore import Qt
from autoriz import  Ui_Autoriz
from untitled import Ui_Form
from new_pas import Ui_Password
from LKUser import Ui_LKUser
from prosmotr import Ui_Prosmotr
from otmena_zakaza import Ui_Otmena
from db import Database


class LoginWindow(QDialog, Ui_Autoriz):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Авторизация")
        self.setFixedSize(579, 383)
        pixmap = QPixmap("logo-01.jpg")
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

        self.pushButton.clicked.connect(self.authenticate_customer)
        self.password_input = self.lineEdit_2
        self.login_input = self.lineEdit
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def authenticate_customer(self):
        db = Database()
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        customer_id = db.check_customer_login(login, password)
        if customer_id:
            self.open_customer_window(customer_id)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверные учетные данные")


    def open_customer_window(self, customer_id):
        self.customer_window = LKUser(customer_id)
        self.customer_window.show()
        self.close()


class LKUser(QMainWindow, Ui_LKUser):
    def __init__(self, customer_id):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Домашняя страница")
        self.customer_id = customer_id
        self.db = Database()
        self.pushButton.clicked.connect(self.zakaz_window)
        self.pushButton_2.clicked.connect(self.my_zakaz)
        self.pushButton_3.clicked.connect(self.otmena_zakaza)
        self.pushButton_4.clicked.connect(self.new_password_w)
        pixmap = QPixmap("logo-01.jpg")
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.model = QStandardItemModel()  # Создаем модель как атрибут класса
        self.tableView.setModel(self.model)
        self.my_zakazi()



    def showEvent(self, event):
        self.my_zakazi()
        super().showEvent(event)

    def zakaz_window(self):
        self.zakaz_w = WindowUser(self.customer_id, self)
        self.zakaz_w.show()
        self.hide()

    def my_zakazi(self):
        try:
            data = self.db.my_orders(self.customer_id)
            self.model.clear()
            self.model.setHorizontalHeaderLabels(
                ["Номер заказа", "Продукт", "Материал", "Статус", "Цена", "Дата заказа"]
            )

            for row in data:
                try:
                    # Извлекаем значения из словаря по ключу
                    order_id = row['order_id']
                    product_name = row['product_name']
                    material_name = row['material_name']
                    status = row['status']
                    total_price=row['total_price']
                    date_z  = row['date']

                    # Создаем элементы QStandardItem
                    item_order_id = QStandardItem(str(order_id))
                    item_product_name = QStandardItem(product_name)
                    item_material_name = QStandardItem(material_name)
                    item_status = QStandardItem(status)
                    item_price = QStandardItem(str(total_price))
                    item_date = QStandardItem(str(date_z))


                    # Добавляем элементы в строку
                    items = [item_order_id, item_product_name, item_material_name, item_status, item_price, item_date]
                    self.model.appendRow(items)

                except Exception as e:
                    print(f"Ошибка при обработке строки: {row}. Ошибка: {e}")
                    continue  # Пропускаем строку с ошибкой

            self.tableView.setModel(self.model)


        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")
            print(f"Ошибка в my_zakazi: {str(e)}")

    def otmena_zakaza(self):
        self.otmena_win = Otmena_zakaza(self.customer_id, self)  # Передаем self как parent_window
        self.otmena_win.show()
        self.hide()
    def new_password_w(self):
        self.new_p_win = NewPassword(self.customer_id, self)  # Передаем self как parent_window
        self.new_p_win.show()
        self.hide()

    def my_zakaz(self):
        self.zakaz_window = My_Zakaz(self.customer_id, self)
        self.zakaz_window.show()
        self.hide()

class My_Zakaz(QMainWindow, Ui_Prosmotr ):
    def __init__(self, customer_id, parent_window):
        super().__init__()
        self.setupUi(self)
        self.customer_id = customer_id
        self.parent_window = parent_window
        self.setWindowTitle("Просмотр заказа")
        self.db = Database()
        pixmap = QPixmap("logo-01.jpg")
        self.label_2.setPixmap(pixmap)
        self.label_2.setScaledContents(True)
        self.pushButton.clicked.connect(self.get_my_zakaz)
        self.pushButton_2.clicked.connect(self.get_close)

    def get_my_zakaz(self):
        try:
            order_id = int(self.lineEdit.text())
            data = self.db.get_order_details(order_id)  # Используем исправленный метод

            if data is None:
                QMessageBox.critical(self, "Ошибка", "Произошла ошибка при запросе к БД")
                return

            if not data:
                QMessageBox.information(self, "Инфо", "Заказ не найден")
                return

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(
                ["Номер заказа", "Продукт", "Материал", "Статус"]
            )
            for row in data:
                items = [
                    QStandardItem(str(row['order_id'])),
                    QStandardItem(row['product_name']),
                    QStandardItem(row['material_name']),
                    QStandardItem(row['status'])
                ]
                model.appendRow(items)

                # Отображение изображения, если оно есть
                if row['image_data']:
                    image = QImage.fromData(row['image_data'])
                    if not image.isNull():
                        pixmap = QPixmap.fromImage(image)
                        self.label_4.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                    else:
                        self.label_4.clear()
                else:
                    self.label_4.clear()

            self.tableView.setModel(model)

        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Введите корректный номер заказа")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def get_close(self):
            self.parent_window.show()
            self.hide()

class NewPassword(QMainWindow, Ui_Password):
    def __init__(self, customer_id, parent_window):
        super().__init__()
        self.setupUi(self)
        self.customer_id = customer_id
        self.parent_window = parent_window
        self.setWindowTitle("Смена пароля")
        self.pushButton.clicked.connect(self.new_password)
        self.pushButton_2.clicked.connect(self.open_customer_window)
        self.db = Database()
        pixmap = QPixmap("logo-01.jpg")
        self.label_2.setPixmap(pixmap)
        self.label_2.setScaledContents(True)

    def new_password(self):
        try:
            password = self.lineEdit.text().strip()
            if not password:
                self.label_4.setText("Введите новый пароль!")
                return

            success = self.db.new_p(self.customer_id, password)
            if success:
                self.label_4.setText("Пароль изменен!")
            else:
                self.label_4.setText("Ошибка изменения пароля!")
                self.open_customer_window()

        except Exception as e:
            self.label_4.setText("Ошибка!")
            print(f"Ошибка: {e}")

    def open_customer_window(self):
        self.parent_window.show()
        self.hide()

class Otmena_zakaza(QMainWindow, Ui_Otmena):
    def __init__(self, customer_id, parent_window):  # Добавляем parent_window
        super().__init__()
        self.setupUi(self)
        self.customer_id = customer_id
        self.parent_window = parent_window
        self.setWindowTitle("Отмена заказа")
        self.pushButton.clicked.connect(self.otmenit)
        self.pushButton_2.clicked.connect(self.nazad)
        self.db = Database()
        pixmap = QPixmap("logo-01.jpg")
        self.label_2.setPixmap(pixmap)
        self.label_2.setScaledContents(True)

    def otmenit(self):
        try:
            order_id = int(self.lineEdit.text())
            data = self.db.otmena(order_id)
            if data:
                self.label_4.setText("Заказ отменен!")
            else:
                self.label_4.setText("Ошибка: заказ не найден!")
        except ValueError:
            self.label_4.setText("Неверный ID заказа!")

    def nazad(self):
        self.parent_window.show()
        self.hide()

class WindowUser(QMainWindow, Ui_Form):
    def __init__(self, customer_id, parent_window):
        super().__init__()
        self.setupUi(self)
        self.customer_id = customer_id
        self.parent_window = parent_window
        self.db = Database()
        self.orders = []  # Список для хранения заказов
        self.initialize_ui()

    def initialize_ui(self):
        self.setWindowTitle("Заказ изделий")
        pixmap = QPixmap("logo-01.jpg")
        self.label_4.setPixmap(pixmap)
        self.label_4.setScaledContents(True)
        self.load_combobox_data()
        self.zakaz_button.clicked.connect(self.process_order)
        self.zakaz_button_2.clicked.connect(self.add_additional_order)
        self.close_button.clicked.connect(self.open_customer_window)

    def load_combobox_data(self):
        try:
            products = self.db.get_products()
            fabrics, accessories = self.db.get_materials()

            # Добавляем материалы в комбобоксы
            self.comboBox_2.addItems(products)
            self.comboBox.addItems([material['name'] for material in fabrics])
            self.comboBox_3.addItems([material['name'] for material in accessories])

            # Сохраняем данные изображений для использования в обработчике
            self.fabrics_data = fabrics
            self.accessories_data = accessories

            # Настраиваем обработчики выбора элементов в комбобоксах
            self.comboBox.currentIndexChanged.connect(self.update_material_image)
            self.comboBox_3.currentIndexChanged.connect(self.update_material_image)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")
            self.close()

    def update_material_image(self):
        # Определяем, какой комбобокс вызвал событие
        sender = self.sender()

        if sender == self.comboBox:
            materials = self.fabrics_data
            index = self.comboBox.currentIndex()
        elif sender == self.comboBox_3:
            materials = self.accessories_data
            index = self.comboBox_3.currentIndex()
        else:
            return

        # Получаем данные изображения для выбранного материала
        if 0 <= index < len(materials):
            image_data = materials[index]['image_data']
            if image_data:
                image = QImage.fromData(image_data)
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    self.label_4.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                else:
                    self.label_4.clear()
            else:
                self.label_4.clear()

    def process_order(self):
        try:
            order_data = self.get_order_data()
            if self.validate_inputs(order_data):
                self.orders.append(order_data)
                success, message = self.db.create_order(self.customer_id, self.orders)

                if success:
                    QMessageBox.information(self, "Успех", message)
                    self.clear_fields()
                    self.orders = []
                else:
                    QMessageBox.critical(self, "Ошибка", message)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_additional_order(self):
        try:
            # Добавляем текущий заказ в список
            order_data = self.get_order_data()
            if self.validate_inputs(order_data):
                self.orders.append(order_data)
                QMessageBox.information(self, "Добавлено", "Заказ добавлен. Можете оформить еще один.")
                self.clear_fields()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def get_order_data(self):
        return {
            'product': self.comboBox_2.currentText(),
            'material': self.comboBox.currentText(),
            'furnitura': self.comboBox_3.currentText(),
            'width': self.lineEdit.text().strip(),
            'length': self.lineEdit_2.text().strip(),
            'quantity': self.lineEdit1.text().strip(),
            'quantity_2': self.lineEdit1_2.text().strip()

        }

    def validate_inputs(self, data):
        if not all(data.values()):
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return False
        return True

    def clear_fields(self):
        self.comboBox_2.setCurrentIndex(0)
        self.comboBox.setCurrentIndex(0)
        self.comboBox_3.setCurrentIndex(0)
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit1.clear()
        self.lineEdit1_2.clear()

    def open_customer_window(self):
        self.parent_window.show()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())

