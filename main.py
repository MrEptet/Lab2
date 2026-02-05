rom flask import Flask, Blueprint
from flask_restplus import Api, Resource, fields
from flasgger import Swagger

app = Flask(__name__)
# Инициализация Flasgger для отображения Swagger UI
swagger = Swagger(app) 
api = Api(app = app)

# --- НОВАЯ МОДЕЛЬ ДАННЫХ НЕДВИЖИМОСТИ ---
# Используем Float для общей площади и Integer для цены и комнат
property_model = api.model('Property', {
    'manager_name': fields.String(required=True, description='ФИО менеджера'),
    'address': fields.String(required=True, description='Адрес объекта'),
    'rooms_count': fields.Integer(required=True, description='Количество комнат'),
    'total_area': fields.Float(required=True, description='Общая площадь в кв.м.'),
    'price': fields.Integer(required=True, description='Цена объекта')
})

# Пример данных в оперативной памяти
all_properties_list = []

# --- Пространство /property ---
property_ns = api.namespace('property', description='API по управлению недвижимостью')
@property_ns.route("/")
class PropertyClass(Resource):
  @property_ns.doc("get_properties")
  @property_ns.marshal_with(property_model, as_list=True) # Маршалинг списка объектов
  def get(self):
    """Получение списка всех объектов недвижимости"""
    return all_properties_list

  @property_ns.doc("post_property")
  @property_ns.expect(property_model) # Ожидаем данные в соответствии с моделью property_model
  @property_ns.marshal_with(property_model) # Возвращаем созданный объект
  def post(self):
    """Создание нового объекта недвижимости"""
    new_property = api.payload
    all_properties_list.append(new_property)
    return new_property

api.add_namespace(property_ns)

if __name__ == "__main__":
  app.run(debug=True)
