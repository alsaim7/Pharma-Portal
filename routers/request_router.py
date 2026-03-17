from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, func, select

from database import get_session
from models.user_models import User
from schemas.request_schemas import (
    MedicineRequestCreate,
    MedicineRequestResponse,
    MedicineRequestResponseCancel,
    MedicineRequestPaginatedResponse,
)

from models.request_models import MedicineRequest, MedicineRequestItem
from models.pharmacy_models import medicine_model
from sqlalchemy.orm import selectinload
from fastapi import Query

from security.oauth2 import get_current_user
from security.permissions import require_roles


router = APIRouter(
    tags=["Requested By"],
    dependencies=[
        Depends(get_current_user),
        Depends(require_roles(["admin", "nurse"]))
    ]
)



@router.post("/requests", response_model=MedicineRequestResponse)
def create_request(
    data: MedicineRequestCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        request_data = data.model_dump(exclude={"medicines"})
        request_data["created_by_user_id"] = current_user.id

        request = MedicineRequest(**request_data)

        session.add(request)
        session.commit()
        session.refresh(request)

        # Merge duplicate medicines
        merged_medicines = {}

        for med in data.medicines:
            med_data = med.model_dump()
            med_id = med_data["medicine_id"]

            if med_id in merged_medicines:
                merged_medicines[med_id]["quantity"] += med_data["quantity"]
            else:
                merged_medicines[med_id] = med_data

        # Insert merged medicines
        for med in merged_medicines.values():
            item = MedicineRequestItem(
                request_id=request.id,
                **med
            )
            session.add(item)

        session.commit()

        return request

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating request: {str(e)}"
        )
    




@router.get("/requests", response_model=MedicineRequestPaginatedResponse)
def get_all_requests(
    page: int = Query(1, ge=1, le=1000),
    limit: int = Query(50, ge=1, le=50),
    session: Session = Depends(get_session)
):
    try:
        offset = (page - 1) * limit

        # Count total rows
        total_count = session.exec(
            select(func.count()).select_from(MedicineRequest)
        ).one()

        # Fetch paginated rows
        statement = (
            select(MedicineRequest)
            .options(
                selectinload(MedicineRequest.items)
                .selectinload(MedicineRequestItem.medicine)
            )
            .order_by(MedicineRequest.id.desc())
            .offset(offset)
            .limit(limit)
        )

        requests = session.exec(statement).all()

        return {
            "data": requests,
            "total": total_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching requests: {str(e)}"
        )


@router.get("/requests/{request_id}", response_model=MedicineRequestResponse)
def get_request_by_id(
    request_id: int,
    session: Session = Depends(get_session)
):
    try:

        statement = (
            select(MedicineRequest)
            .where(MedicineRequest.id == request_id)
            .options(
                selectinload(MedicineRequest.items)
                .selectinload(MedicineRequestItem.medicine)
            )
        )

        request = session.exec(statement).first()

        if not request:
            raise HTTPException(
                status_code=404,
                detail="Request not found"
            )

        return request

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching request: {str(e)}"
        )
    



@router.patch("/requests/{request_id}/cancel", response_model=MedicineRequestResponseCancel)
def cancel_request(
    request_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:

        request = session.get(MedicineRequest, request_id)

        if not request:
            raise HTTPException(
                status_code=404,
                detail="Request not found"
            )

        if request.status != "pending":
            raise HTTPException(
                status_code=400,
                detail="Only pending requests can be cancelled"
            )

        request.status = "cancelled"
        request.cancelled_by_user_id= current_user.id

        session.add(request)
        session.commit()
        session.refresh(request)

        return request

    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error cancelling request: {str(e)}"
        )
    



