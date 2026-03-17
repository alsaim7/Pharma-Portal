from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select

from database import get_session
from schemas.pharmacy_schemas import (
    MedicineRequestResponseStatusChange,
)
from schemas.request_schemas import (
    MedicineRequestPaginatedResponse,
)

from models.request_models import MedicineRequest, MedicineRequestItem
from models.pharmacy_models import medicine_model
from sqlalchemy.orm import selectinload


router = APIRouter(
    tags=["Pharmacy Dashboard"],
)


@router.get("/pharmacy", response_model=MedicineRequestPaginatedResponse)
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
    

    
@router.patch("/pharmacy/{request_id}/status", response_model=MedicineRequestResponseStatusChange)
def update_request_status(
    request_id: int,
    data: MedicineRequestResponseStatusChange,
    session: Session = Depends(get_session)
):
    try:

        request = session.get(MedicineRequest, request_id)

        if not request:
            raise HTTPException(
                status_code=404,
                detail="Request not found"
            )

        allowed_status = ["pending", "delivered", "out_of_stock"]

        if data.status not in allowed_status:
            raise HTTPException(
                status_code=400,
                detail="Invalid status"
            )

        if request.status != "pending":
            raise HTTPException(
                status_code=400,
                detail="Request already processed"
            )

        # handle out of stock medicines
        if data.status == "out_of_stock":

            if not data.out_of_stock_items:
                raise HTTPException(
                    status_code=400,
                    detail="Out of stock medicines must be provided"
                )

            request.out_of_stock_items = data.out_of_stock_items

        else:
            request.out_of_stock_items = None

        request.status = data.status

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
            detail=f"Error updating status: {str(e)}"
        )