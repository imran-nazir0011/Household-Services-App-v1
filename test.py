from werkzeug.security import generate_password_hash
from backend.models import db, Customer, ServiceProfessional, Service, ServiceRequest
from app import app   
import random
from datetime import datetime


def extract_city_from_address(address):
    for city in ["Delhi", "Mumbai", "Chennai"]:
        if city in address:
            return city
    return "Other"


def generate_sample_data():
     
    if Customer.query.first() or ServiceProfessional.query.first() or Service.query.first():
        print("Sample data already exists. Skipping generation.")
        return   

    print("Generating sample data...")

     
    secure_password = generate_password_hash("test@123")

     
    addresses_and_pincodes = {
        "Delhi": [("Connaught Place, Delhi", "110001"), ("Chandni Chowk, Delhi", "110002"),
                  ("Karol Bagh, Delhi", "110005"), ("Lajpat Nagar, Delhi", "110024"),
                  ("South Extension, Delhi", "110049")],
        "Mumbai": [("Andheri, Mumbai", "400053"), ("Bandra, Mumbai", "400050"),
                   ("Colaba, Mumbai", "400005"), ("Dadar, Mumbai", "400014"),
                   ("Juhu, Mumbai", "400049")],
        "Chennai": [("T Nagar, Chennai", "600017"), ("Adyar, Chennai", "600020"),
                    ("Velachery, Chennai", "600042"), ("Nungambakkam, Chennai", "600034"),
                    ("Egmore, Chennai", "600008")]
    }

     
    customer_names = [f"Customer {i+1}" for i in range(100)]
    customers = [
        Customer(
            name=customer_names[i],
            username=f"customer{i+1}",
            password=secure_password,
            email=f"customer{i+1}@example.com",
            phone=f"98765432{i % 100:02}",
            address=f"{random.choice(addresses_and_pincodes[city])[0]}, Pincode: {random.choice(addresses_and_pincodes[city])[1]}",
            verification_status=random.choice([True, False])   
        )
        for i, city in enumerate(random.choices(list(addresses_and_pincodes.keys()), k=100))
    ]

     
    services = [
        Service(
            name="Plumbing",
            price=100.0,
            description="Fixing leaks and plumbing issues",
            time_required=120,
            image=None
        ),
        Service(
            name="AC Repair",
            price=150.0,
            description="Air conditioner repair and maintenance",
            time_required=180,
            image=None
        ),
        Service(
            name="Electrician",
            price=80.0,
            description="Electrical repairs and installations",
            time_required=90,
            image=None
        ),
        Service(
            name="Carpentry",
            price=200.0,
            description="Furniture repairs and wooden fixtures",
            time_required=240,
            image=None
        ),
        Service(
            name="Painting",
            price=300.0,
            description="House and wall painting services",
            time_required=300,
            image=None
        ),
    ]

     
    db.session.add_all(services)
    db.session.commit()   

     
    service_names = [service.name for service in Service.query.all()]

     
    professional_names = [f"Professional {i+1}" for i in range(20)]
    professionals = [
        ServiceProfessional(
            name=professional_names[i],
            username=f"professional{i+1}",
            password=secure_password,
            email=f"professional{i+1}@example.com",
            phone=f"91234567{i % 100}",
            address=f"{random.choice(addresses_and_pincodes[city])[0]}, Pincode: {random.choice(addresses_and_pincodes[city])[1]}",
            service_type=service_names[i % len(service_names)],   
            experience=2 + i,   
            verified=True   
        )
        for i, city in enumerate(random.choices(list(addresses_and_pincodes.keys()), k=20))
    ]

     
    db.session.add_all(customers)
    db.session.add_all(professionals)

     
    db.session.commit()

     
    service_requests = []
    for _ in range(40):
        customer = random.choice(Customer.query.all())
        customer_city = extract_city_from_address(customer.address)
        service = random.choice(services)
        professional = ServiceProfessional.query.filter(
            ServiceProfessional.service_type == service.name,
            ServiceProfessional.address.like(f"%{customer_city}%")
        ).first()

        if professional:
            service_request = ServiceRequest(
                service_id=service.id,
                customer_id=customer.id,
                professional_id=professional.id,
                date_of_request=datetime.now(),
                service_status="assigned",   
                remarks="Service request assigned to the service professional."
            )
            service_requests.append(service_request)

     
    db.session.add_all(service_requests)
    db.session.commit()

    print("Sample data added successfully.")


 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()   
        generate_sample_data()
