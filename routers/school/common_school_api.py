from fastapi import APIRouter, Security, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, Response, FileResponse

from core.authentication.authorization_service import authorization_header, authorize_jwt
from core.jwt.jwt_service import get_sub, get_aud
from core.user import user_info_service
from core.user.user_info_service import get_identity_by_userid, role_to_school
from database.database import create_connection
from models.database_models.relational.schools import School

router = APIRouter(
    prefix='/api/school',
    tags=['school']
)

@router.get(
    path='',
    summary="Get one's verified school information",
)
def get_school_api(
  jwt: str = Security(authorization_header),
  db: Session = Depends(create_connection)
):
  token = authorize_jwt(jwt)
  sub = get_sub(token)

  identity = get_identity_by_userid(sub, db)
  if identity is None:
    raise HTTPException(status_code=400, detail="Identity not found")

  student_verified, neis_code = role_to_school(identity.role)
  if not student_verified:
    raise HTTPException(status_code=400, detail="User is not a student")

  school = db.query(School).filter_by(neis_code=neis_code).first()

  return JSONResponse(
    content={
      "name": school.school_name,
      "schoolUUID": str(school.school_id),
      "neisCode": school.neis_code,
      "grade": identity.grade,
      "classroom": identity.classroom,
      "studentNumber": identity.student_number,
      "homepage": school.homepage if school.homepage else None
    }
  )
