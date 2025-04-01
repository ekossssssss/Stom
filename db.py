import pymysql

class Database:
    def __init__(self):
        self.connection_params = {
            "host": "fatima6p.beget.tech",
            "user": "fatima6p_factory",
            "password": "Babaeva2025",
            "db": "fatima6p_factory",
            "cursorclass": pymysql.cursors.DictCursor
        }

    def _get_connection(self):
        return pymysql.connect(**self.connection_params)

    # Общие методы
    def check_customer_login(self, login, password):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT id FROM customer WHERE login = %s AND password = %s",
                        (login, password))
                    result = cursor.fetchone()
                    return result['id'] if result else None
                except Exception as e:
                    print(f"Customer auth error: {e}")
                    return None

    def check_manager_login(self, login, password):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT id FROM employee WHERE login = %s AND password = %s",
                        (login, password))
                    result = cursor.fetchone()
                    return result['id'] if result else None
                except Exception as e:
                    print(f"Manager auth error: {e}")
                    return None

    # Методы для клиентов
    def get_products(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM product")
                return [row['name'] for row in cursor.fetchall()]

    def get_materials(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT sc.material_id, m.name, m.image_data
                    FROM supply_composition sc
                    JOIN material m ON sc.material_id = m.id
                """)
                materials = cursor.fetchall()

                # Используем словарь для хранения уникальных материалов
                unique_materials = {}
                for row in materials:
                    material_id = row['material_id']
                    if material_id not in unique_materials:
                        unique_materials[material_id] = {
                            'material_id': material_id,
                            'name': row['name'],
                            'image_data': row['image_data']
                        }

                # Преобразуем словарь обратно в список
                materials = list(unique_materials.values())

                fabrics = []
                accessories = []

                for material in materials:
                    if material['material_id'] in {1, 2, 9, 13}:
                        fabrics.append(material)
                    elif material['material_id'] in {3, 4, 5}:
                        accessories.append(material)

                return fabrics, accessories

    def create_order(self, customer_id, order_data):
        with self._get_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    for order in order_data:
                        self.validate_order_data(cursor, order)
                        cursor.callproc(
                            'CreateOrderWithMaterialsAndFurnitura2',
                            [customer_id, *order.values()]
                        )
                    connection.commit()
                    return True, "Заказ успешно создан"
            except pymysql.Error as e:
                connection.rollback()
                return False, f"Ошибка БД: {e.args[1]}"
            except ValueError as e:
                return False, str(e)
            except Exception as e:
                return False, f"Неизвестная ошибка: {str(e)}"

    # Методы для менеджеров
    def get_zakazi(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                sql = """SELECT orq.id, c.organization_name AS customer, 
                        orq.status, orq.date 
                        FROM order_request orq 
                        JOIN customer c ON orq.customer_id = c.id"""
                cursor.execute(sql)
                return cursor.fetchall()

    def get_customers(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                sql = """SELECT	id,organization_name,inn,organization_type_id,
                director_first_name,director_last_name,director_middle_name,
                kpp,ogrn,email,address FROM customer"""
                cursor.execute(sql)
                return cursor.fetchall()

    def update_customer(self, data):
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    sql = """
                    UPDATE customer
                    SET 
                        login = %s,
                        password = %s,
                        organization_name = %s,
                        inn = %s,
                        organization_type_id = %s,
                        director_first_name = %s,
                        director_last_name = %s,
                        director_middle_name = %s,
                        kpp = %s,
                        ogrn = %s,
                        email = %s,
                        address = %s
                    WHERE id = %s  
                    """
                    cursor.execute(sql, (
                        data["Логин"],
                        data["Пароль"],
                        data["Имя организации"],
                        data["ИНН"],
                        data["Тип"],
                        data["Имя"],
                        data["Фамилия"],
                        data["Отчество"],
                        data["КПП"],
                        data["ОРГН"],
                        data["Почта"],
                        data["Адрес"],
                        data["Номер"]  # id записи
                    ))
                    connection.commit()
        except Exception as e:
            print(f"Ошибка при обновлении заказчика: {e}")
            raise

    def get_sebestoimoste(self, id_customer):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.callproc('CheckCustomerReadyOrders', (id_customer,))
                return cursor.fetchall()

    def odobrenie(self, id_o):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.callproc('InsertOrderRequest', (id_o,))
                    connection.commit()
                    return True
                except Exception as e:
                    print(f"Ошибка одобрения: {e}")
                    return False

    def otkaz(self, id_o):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.callproc('InsertOrderRequest2', (id_o,))
                    connection.commit()
                    return True
                except Exception as e:
                    print(f"Ошибка отказа: {e}")
                    return False

    # Валидация
    def validate_order_data(self, cursor, data):
        try:
            float(data['width'])
            float(data['length'])
            int(data['quantity'])
        except ValueError:
            raise ValueError("Некорректные числовые значения")

        if not self.check_exists(cursor, 'product', data['product']):
            raise ValueError("Продукт не найден")
        if not self.check_exists(cursor, 'material', data['material']):
            raise ValueError("Материал не найден")
        if not self.check_exists(cursor, 'material', data['furnitura']):
            raise ValueError("Фурнитура не найдена")

    def check_exists(self, cursor, table, name):
        cursor.execute(f"SELECT id FROM {table} WHERE name = %s", (name,))
        return cursor.fetchone() is not None

    def my_orders(self, customer_id):
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    sql = """
                        SELECT
        orc.order_id,
        p.name AS product_name,
        m.name AS material_name,
        org.status,
        org.total_price,
        org.date
    FROM order_composition orc
    LEFT JOIN product_materials pm ON orc.id = pm.order_composition_id
    LEFT JOIN supply_composition sc ON pm.supply_composition_id = sc.id
    LEFT JOIN material m ON sc.material_id = m.id
    LEFT JOIN product p ON orc.product_id = p.id
    LEFT JOIN order_request org ON org.id = orc.order_id
    WHERE org.customer_id =  %s
                    """
                    cursor.execute(sql, (customer_id,))
                    return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении заказов: {e}")
            return []

    def get_order_details(self, order_id):
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    sql = """SELECT
                        orc.order_id,
                        p.name AS product_name,
                        m.name AS material_name,
                        orc.status,
                        orc.image_data  
                    FROM order_composition orc
                    LEFT JOIN product_materials pm ON orc.id = pm.order_composition_id
                    LEFT JOIN product p ON orc.product_id = p.id
                    LEFT JOIN material m ON pm.supply_composition_id = m.id
                    WHERE orc.order_id = %s;"""
                    cursor.execute(sql, (order_id,))
                    data = cursor.fetchall()
                    return data

        except Exception as e:
            print(f"Ошибка при получении заказа: {e}")
            return None

    def otmena(self, id_order):
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    sql = 'call otmena_zakaza(%s)'
                    cursor.execute(sql, (id_order,))
                    connection.commit()
                    if cursor.rowcount > 0:
                        return True
                    else:
                        return False

        except Exception as e:
            print(f"Ошибка при отмене заказа: {e}")
            return False

    def get_organization_types(self):
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    sql = """SELECT id, name FROM organization_type;"""
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    print(f"Данные из базы данных: {data}")  # Отладочный вывод
                    return data  # Возвращает список словарей [{'id': 1, 'name': 'ООО'}, ...]
        except Exception as e:
            print(f"Ошибка при получении типов организаций: {e}")
            return []  # Возвращаем пустой список в случае ошибки

    def new_customer(self, login, password, name, inn, type_id, name_d, fam_d, ot_d, kpp, orgn, email, address):
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO customer (login,password,organization_name,inn,
                    organization_type_id,director_first_name,director_last_name,
                    director_middle_name,kpp,ogrn,email,address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        login, password, name, inn, type_id,
                        name_d, fam_d, ot_d, kpp, orgn, email, address
                    ))
                    connection.commit()
                    return True
        except Exception as e:
            print(f"Ошибка при добавлении заказчика: {e}")
            return False


    def new_p(self, id_customer, password):
        try:
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    sql = 'call new_password(%s, %s)'
                    cursor.execute(sql, (id_customer, password,))
                    connection.commit()
                    if cursor.rowcount > 0:
                        return True
                    else:
                        return False

        except Exception as e:
            print(f"Ошибка при отмене заказа: {e}")
            return False

    def raschot(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                try:
                    # Вызов процедуры без параметров
                    sql = "CALL UpdateOrderRequestTotalPrice()"
                    cursor.execute(sql)
                    # Фиксация изменений, если процедура изменяет данные
                    connection.commit()
                except Exception as e:
                    # Откат изменений в случае ошибки
                    connection.rollback()
                    raise e  # Повторно выбрасываем исключение для обработки в вызывающем коде





