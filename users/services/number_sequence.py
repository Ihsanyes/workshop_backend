from django.db import transaction

def generate_employee_id(workshop):
    from ..models import EmployeeIdSequence

    with transaction.atomic():
        seq, _ = EmployeeIdSequence.objects.select_for_update().get_or_create(
            workshop=workshop
        )

        seq.last_number += 1
        seq.save()

    return f"W{workshop.id}-EMP{str(seq.last_number).zfill(4)}"