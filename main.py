from flask import Flask, Blueprint, request
from flask_restplus import Api, Resource, fields
from flasgger import Swagger #

app = Flask(__name__)
swagger = Swagger(app) 
api = Api(app=app)

property_model = api.model('Property', {
    'id': fields.Integer(readOnly=True, description='Уникальный идентификатор объекта'),
    'manager_name': fields.String(required=True, description='ФИО менеджера'),
    'address': fields.String(required=True, description='Адрес объекта'),
    'rooms_count': fields.Integer(required=True, description='Количество комнат'),
    'total_area': fields.Float(required=True, description='Общая площадь в кв.м.'),
    'price': fields.Integer(required=True, description='Цена объекта')
})

# Пример данных в оперативной памяти с добавлением ID
all_properties_list = [
    {'id': 1, 'manager_name': 'Иванов И.И.', 'address': 'ул. Ленина, д. 1', 'rooms_count': 2, 'total_area': 55.5, 'price': 5000000},
    {'id': 2, 'manager_name': 'Петров П.П.', 'address': 'пр-т Мира, д. 10', 'rooms_count': 3, 'total_area': 80.0, 'price': 8500000}
]
current_id = 2

# --- ПРОСТРАНСТВО ИМЕН /property ---
property_ns = api.namespace('property', description='API по управлению недвижимостью')

@property_ns.route("/")
class PropertyListClass(Resource):
  @property_ns.doc("list_properties")
  @property_ns.marshal_list_with(property_model)
  def get(self):
    """Получение списка всех объектов недвижимости с возможностью сортировки"""
    global all_properties_list
    # Реализация сортировки по параметру запроса 'sort_by'
    sort_by = request.args.get('sort_by', 'id') # Сортировка по умолчанию по id
    if sort_by in property_model.keys():
        # Используем sorted() с lambda-функцией для сортировки списка словарей
        all_properties_list = sorted(all_properties_list, key=lambda x: x[sort_by], reverse=request.args.get('order') == 'desc')
    return all_properties_list

  @property_ns.doc("create_property")
  @property_ns.expect(property_model)
  @property_ns.marshal_with(property_model, code=201)
  def post(self):
    """Создание нового объекта недвижимости"""
    global current_id
    new_property = api.payload
    current_id += 1
    new_property['id'] = current_id
    all_properties_list.append(new_property)
    return new_property, 201

@property_ns.route("/<int:id>")
@property_ns.param('id', 'Идентификатор объекта недвижимости')
@property_ns.response(404, 'Объект не найден')
class PropertyClass(Resource):
    @property_ns.doc("get_property")
    @property_ns.marshal_with(property_model)
    def get(self, id):
        """Получение информации об объекте по ID"""
        item = next((item for item in all_properties_list if item['id'] == id), None)
        if item:
            return item
        property_ns.abort(404, f"Объект с ID {id} не найден")

    @property_ns.doc("update_property")
    @property_ns.expect(property_model)
    @property_ns.marshal_with(property_model)
    def put(self, id):
        """Обновление записи по ID"""
        item = next((item for item in all_properties_list if item['id'] == id), None)
        if item:
            item.update(api.payload) # Обновляем данные объекта
            return item
        property_ns.abort(404, f"Объект с ID {id} не найден")

    @property_ns.doc("delete_property")
    @property_ns.response(204, 'Объект удален')
    def delete(self, id):
        """Удаление записи по ID"""
        global all_properties_list
        item = next((item for item in all_properties_list if item['id'] == id), None)
        if item:
            all_properties_list.remove(item) #
            return '', 204
        property_ns.abort(404, f"Объект с ID {id} не найден")

@property_ns.route("/stats")
class PropertyStatsClass(Resource):
    @property_ns.doc("get_property_stats")
    def get(self):
        """Вычисление среднего, максимального и минимального значения по числовым полям"""
        if not all_properties_list:
            return {"message": "Список объектов пуст"}, 404

        stats = {}
        numeric_fields = ['rooms_count', 'total_area', 'price']

        for field in numeric_fields:
            # Извлекаем значения для числовых полей
            values = [item[field] for item in all_properties_list if isinstance(item[field], (int, float))]
            if values:
                # Используем встроенные функции Python для расчетов
                stats[field + '_avg'] = sum(values) / len(values)
                stats[field + '_max'] = max(values)
                stats[field + '_min'] = min(values)
        return stats

api.add_namespace(property_ns)

if __name__ == "__main__":
  app.run(debug=True)
