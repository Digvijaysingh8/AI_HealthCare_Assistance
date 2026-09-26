import os

from app.agent.appointment_flow import (
    find_doctor_node,
    check_availability_node,
    prepare_appointment_node,
    book_appointment_node
)


os.environ["ODASHA_USER_ID"] = "2"


state = {
    "user_id": 2,
    "doctor_name": "Dr. Sharma",
    "doctor_id": None,
    "appointment_date": "2026-09-30",
    "appointment_time": "11:00",
    "confirmed": False,
    "response": None
}
print("\nTesting booking without confirmation:")

result = book_appointment_node(state)

print(result)

state.update(find_doctor_node(state))

print("After find doctor:")
print(state)

state.update(check_availability_node(state))

print("\nAfter availability check:")
print(state)

state.update(prepare_appointment_node(state))

print("\nAfter preparation:")
print(state)