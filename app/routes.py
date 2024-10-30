from datetime import datetime

from flask import Blueprint, jsonify, request
from .models import Medspa, db, ServiceProduct, ServiceProductSupplier, ServiceCategory, ServiceType, Appointment, AppointmentServiceSupplier

main = Blueprint('main', __name__)

@main.route('/medspas', methods=['GET'])
def get_medspas():
    medspas = Medspa.query.all()
    return jsonify([{"id": medspa.id, "name": medspa.name} for medspa in medspas])

@main.route('/medspas', methods=['POST'])
def create_medspa():
    data = request.get_json()
    new_medspa = Medspa(
        name=data['name'],
        address=data['address'],
        phone_number=data['phone_number'],
        email_address=data['email_address']
    )
    db.session.add(new_medspa)
    db.session.commit()
    return jsonify({"id": new_medspa.id, "name": new_medspa.name}), 201

service_bp = Blueprint('service', __name__)

@service_bp.route('/services', methods=['POST'])
def create_service():
    data = request.get_json()

    # when creating a service it is a requirement to specific which medspa it is associated with
    medspa_id = data.get('medspa_id')
    if not medspa_id:
        return jsonify({"error": "medspa_id is required"}), 400
    # medspa should exist
    medspa = Medspa.query.get(medspa_id)
    if not medspa:
        return jsonify({"error": "Medspa not found"}), 404

    # create service
    new_service = ServiceProduct(
        name=data.get('name'),
        description=data.get('description'),
        duration=data.get('duration'),
        medspa_id=medspa_id,
        service_type_id=data.get('service_type_id')
    )
    db.session.add(new_service)
    db.session.commit()

    # service_product_supplier
    supplier_name = data.get('supplier_name')
    price = data.get('price')

    if price is None:
        return jsonify({"error": "price is required"}), 400

    new_supplier = ServiceProductSupplier(
        product_id=new_service.id,
        supplier_name=supplier_name,
        price=price
    )
    db.session.add(new_supplier)
    db.session.commit()

    return jsonify({
        "id": new_service.id,
        "name": new_service.name,
        "description": new_service.description,
        "duration": new_service.duration,
        "medspa_id": new_service.medspa_id,
        "supplier_name": new_supplier.supplier_name,
        "price": str(new_supplier.price)
    }), 201

category_bp = Blueprint('category', __name__)

@service_bp.route('/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    data = request.get_json()
    service = ServiceProduct.query.get(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404

    service.name = data.get('name', service.name)
    service.description = data.get('description', service.description)
    service.duration = data.get('duration', service.duration)

    # price is in ServiceProductSupplier table
    price = data.get('price')
    if price is not None:
        # assuming there's only one supplier record per service for simplicity
        supplier_record = service.suppliers[0] if service.suppliers else None
        if supplier_record:
            supplier_record.price = price
        else:
            # create a supplier record if none exists
            new_supplier = ServiceProductSupplier(
                product_id=service.id,
                price=price
            )
            db.session.add(new_supplier)

    db.session.commit()

    response = {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "duration": service.duration,
        "price": str(supplier_record.price if supplier_record else price)
    }
    
    return jsonify(response), 200

# get service by ID
@service_bp.route('/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    # Find the service by its ID
    service = ServiceProduct.query.get(service_id)
    if not service:
        return jsonify({"error": "Service not found"}), 404

    # Fetch supplier data (assuming one supplier per service for simplicity)
    supplier = service.suppliers[0] if service.suppliers else None
    price = str(supplier.price) if supplier else None
    supplier_name = supplier.supplier_name if supplier else None

    # Prepare the response
    response = {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "duration": service.duration,
        "medspa_id": service.medspa_id,
        "price": price,
        "supplier_name": supplier_name
    }
    
    return jsonify(response), 200

@service_bp.route('/medspas/<int:medspa_id>/services', methods=['GET'])
def get_services_for_medspa(medspa_id):
    # Check if the medspa exists
    medspa = Medspa.query.get(medspa_id)
    if not medspa:
        return jsonify({"error": "Medspa not found"}), 404

    # Get all services for the medspa
    services = ServiceProduct.query.filter_by(medspa_id=medspa_id).all()

    # Format the response with service and supplier details
    result = []
    for service in services:
        # Assume one supplier per service for simplicity
        supplier = service.suppliers[0] if service.suppliers else None
        result.append({
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "duration": service.duration,
            "price": str(supplier.price) if supplier else None,
            "supplier_name": supplier.supplier_name if supplier else None
        })

    return jsonify(result), 200

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()

    # validate fields
    start_time = data.get('start_time')
    medspa_id = data.get('medspa_id')
    service_ids = data.get('service_ids')  # list of IDs
    if not start_time or not medspa_id or not service_ids:
        return jsonify({"error": "start_time, medspa_id, and service_ids are required"}), 400

    medspa = Medspa.query.get(medspa_id)
    if not medspa:
        return jsonify({"error": "Medspa not found"}), 404

    total_duration = 0
    total_price = 0

    # calculate total duration and price for services
    valid_service_ids = []
    for service_id in service_ids:
        service = ServiceProductSupplier.query.get(service_id)
        if service:
            total_duration += service.product.duration
            total_price += service.price
            valid_service_ids.append(service_id)

    new_appointment = Appointment(
        start_time=datetime.fromisoformat(start_time),
        total_duration=total_duration,
        total_price=total_price,
        status="scheduled",
        medspa_id=medspa_id
    )
    db.session.add(new_appointment)
    db.session.commit()

    # associate services with the appointment
    for service_id in valid_service_ids:
        appointment_service = AppointmentServiceSupplier(
            appointment_id=new_appointment.id,
            service_product_supplier_id=service_id
        )
        db.session.add(appointment_service)

    db.session.commit()

    response = {
        "id": new_appointment.id,
        "start_time": new_appointment.start_time.isoformat(),
        "total_duration": new_appointment.total_duration,
        "total_price": str(new_appointment.total_price),
        "status": new_appointment.status,
        "medspa_id": new_appointment.medspa_id,
        "services": valid_service_ids
    }

    return jsonify(response), 201

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    # get associated services
    services = []
    for association in appointment.services:
        service = association.service
        services.append({
            "id": service.product_id,
            "name": service.product.name,
            "description": service.product.description,
            "duration": service.product.duration,
            "price": str(service.price),
            "supplier_name": service.supplier_name
        })

    response = {
        "id": appointment.id,
        "start_time": appointment.start_time.isoformat(),
        "total_duration": appointment.total_duration,
        "total_price": str(appointment.total_price),
        "status": appointment.status,
        "medspa_id": appointment.medspa_id,
        "services": services
    }
    
    return jsonify(response), 200

@appointment_bp.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
def update_appointment_status(appointment_id):
    data = request.get_json()

    new_status = data.get('status')
    if new_status not in ["scheduled", "completed", "canceled"]:
        return jsonify({"error": "Invalid status. Allowed values are: 'scheduled', 'completed', 'canceled'"}), 400

    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    appointment.status = new_status
    db.session.commit()

    response = {
        "id": appointment.id,
        "status": appointment.status,
        "start_time": appointment.start_time.isoformat(),
        "total_duration": appointment.total_duration,
        "total_price": str(appointment.total_price),
        "medspa_id": appointment.medspa_id
    }

    return jsonify(response), 200

@appointment_bp.route('/appointments', methods=['GET'])
def list_appointments():
    # filters
    status = request.args.get('status')
    start_date = request.args.get('start_date')  # in YYYY-MM-DD format

    query = Appointment.query
    if status:
        query = query.filter(Appointment.status == status)

    if start_date:
        try:
            # create date representing the start of the day
            date = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(
                db.func.date(Appointment.start_time) == date  # compare only the date part
            )
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    appointments = query.all()

    result = []
    for appointment in appointments:
        result.append({
            "id": appointment.id,
            "status": appointment.status,
            "start_time": appointment.start_time.isoformat(),
            "total_duration": appointment.total_duration,
            "total_price": str(appointment.total_price),
            "medspa_id": appointment.medspa_id
        })

    return jsonify(result), 200



# create service category
@category_bp.route('/service-categories', methods=['POST'])
def create_service_category():
    data = request.get_json()

    name = data.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400

    new_category = ServiceCategory(name=name)
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify({
        "id": new_category.id,
        "name": new_category.name
    }), 201


# create service type
@category_bp.route('/service-types', methods=['POST'])
def create_service_type():
    data = request.get_json()
    name = data.get('name')
    category_id = data.get('category_id')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    if not category_id:
        return jsonify({"error": "Category ID is required"}), 400

    category = ServiceCategory.query.get(category_id)
    if not category:
        return jsonify({"error": "Service Category not found"}), 404

    new_service_type = ServiceType(name=name, category_id=category_id)
    db.session.add(new_service_type)
    db.session.commit()
    
    return jsonify({
        "id": new_service_type.id,
        "name": new_service_type.name,
        "category_id": new_service_type.category_id
    }), 201


service_type_bp = Blueprint('service_type', __name__)

# Route to get all service types
@service_type_bp.route('/service-types', methods=['GET'])
def get_all_service_types():
    service_types = ServiceType.query.all()

    # Format the response to include each service type's category details
    result = [
        {
            "id": service_type.id,
            "name": service_type.name,
            "category": {
                "id": service_type.category.id,
                "name": service_type.category.name
            }
        } for service_type in service_types
    ]

    return jsonify(result), 200