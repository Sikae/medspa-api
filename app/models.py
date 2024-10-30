from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()
from . import db

class ServiceCategory(db.Model):
    __tablename__ = 'service_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class ServiceType(db.Model):
    __tablename__ = 'service_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('service_category.id'), nullable=False)
    category = db.relationship("ServiceCategory", backref="types")

class ServiceProduct(db.Model):
    __tablename__ = 'service_product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)
    service_type_id = db.Column(db.Integer, db.ForeignKey('service_type.id'), nullable=False)
    type = db.relationship("ServiceType", backref="products")
    medspa_id = db.Column(db.Integer, db.ForeignKey('medspa.id'), nullable=False)
    medspa = db.relationship("Medspa", backref="services")

class ServiceProductSupplier(db.Model):
    __tablename__ = 'service_product_supplier'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('service_product.id'), nullable=False)
    supplier_name = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Numeric, nullable=False)
    product = db.relationship("ServiceProduct", backref="suppliers")

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    total_duration = db.Column(db.Integer)
    total_price = db.Column(db.Numeric)
    status = db.Column(db.String(20), nullable=False)
    medspa_id = db.Column(db.Integer, db.ForeignKey('medspa.id'), nullable=False)
    medspa = db.relationship("Medspa", backref="appointments")

class AppointmentServiceSupplier(db.Model):
    __tablename__ = 'appointment_service_supplier'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    service_product_supplier_id = db.Column(db.Integer, db.ForeignKey('service_product_supplier.id'), nullable=False)
    appointment = db.relationship("Appointment", backref="services")
    service = db.relationship("ServiceProductSupplier", backref="appointments")

class Medspa(db.Model):
    __tablename__ = 'medspa'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email_address = db.Column(db.String(100), nullable=False)
