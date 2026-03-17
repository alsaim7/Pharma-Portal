from sqlmodel import Session, create_engine


DATABASE_URL = "postgresql://postgres:sam@localhost:5432/pharma_portal_local"



engine = create_engine(DATABASE_URL, echo=True)


# get a seesion
def get_session():
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        # log error appropriately
        raise