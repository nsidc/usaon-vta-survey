import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import DateTime, Enum, Integer, SmallInteger, String

from usaon_vta_survey import db
from usaon_vta_survey._types import ObservingSystemType

# Workaround for missing type stubs for flask-sqlalchemy:
#     https://github.com/dropbox/sqlalchemy-stubs/issues/76#issuecomment-595839159
BaseModel: DeclarativeMeta = db.Model


class Survey(BaseModel):
    __tablename__ = 'survey'
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    response_id = Column(
        Integer,
        ForeignKey('response.id'),
        nullable=True,
    )

    created_timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
    notes = Column(
        String(512),
        nullable=True,
    )

    response = relationship(
        'Response',
        back_populates='survey',
    )


class Response(BaseModel):
    __tablename__ = 'response'
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    created_timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )
    updated_timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    survey = relationship(
        'Survey',
        back_populates='response',
    )


class ResponseObservingSystem(BaseModel):
    __tablename__ = 'response_observing_system'
    __table_args__ = (UniqueConstraint('name', 'response_id'),)
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String(256),
        nullable=False,
    )
    response_id = Column(
        Integer,
        ForeignKey('response.id'),
        nullable=False,
    )

    type = Column(
        Enum(ObservingSystemType),
        nullable=False,
    )

    __mapper_args__ = {
        'polymorphic_identity': ObservingSystemType.other,
        'polymorphic_on': type,
    }

    url = Column(String(256), nullable=False)
    author_name = Column(String(256), nullable=False)
    author_email = Column(String(256), nullable=False)
    funding_country = Column(String(256), nullable=False)
    funding_agency = Column(String(256), nullable=False)
    references_citations = Column(String(512), nullable=False)
    notes = Column(String(512), nullable=False)


class ResponseObservingSystemObservational(BaseModel):
    __tablename__ = 'response_observing_system_observational'
    __mapper_args__ = {
        'polymorphic_identity': ObservingSystemType.observational,
    }

    response_observing_system_id = Column(
        Integer,
        ForeignKey('response_observing_system.id'),
        primary_key=True,
    )

    platform = Column(String(256), nullable=False)
    sensor = Column(String(256), nullable=False)


class ResponseObservingSystemResearch(BaseModel):
    __tablename__ = 'response_observing_system_research'
    __mapper_args__ = {
        'polymorphic_identity': ObservingSystemType.research,
    }

    response_observing_system_id = Column(
        Integer,
        ForeignKey('response_observing_system.id'),
        primary_key=True,
    )

    intermediate_product = Column(String(256), nullable=False)


class ResponseDataProduct(BaseModel):
    __tablename__ = 'response_data_product'
    __table_args__ = (UniqueConstraint('name', 'response_id'),)
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String(256),
        nullable=False,
    )
    response_id = Column(
        Integer,
        ForeignKey('response.id'),
        nullable=False,
    )

    # TODO: Constrain to 0-100
    satisfaction_rating = Column(
        SmallInteger,
        nullable=False,
    )


class ResponseApplication(BaseModel):
    __tablename__ = 'response_application'
    __table_args__ = (UniqueConstraint('name', 'response_id'),)
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String(256),
        nullable=False,
    )
    response_id = Column(
        Integer,
        ForeignKey('response.id'),
        nullable=False,
    )


# Association tables
class ResponseObservingSystemDataProduct(BaseModel):
    __tablename__ = 'response_observing_system_data_product'
    response_observing_system_id = Column(
        Integer,
        ForeignKey('response_observing_system.id'),
        primary_key=True,
    )
    response_data_product_id = Column(
        Integer,
        ForeignKey('response_data_product.id'),
        primary_key=True,
    )

    # TODO: Constrain 0-100
    observing_system_contribution_to_data_product_rating = Column(
        SmallInteger,
        nullable=False,
    )
    # TODO: Constraint 0-100
    satisfaction_rating = Column(SmallInteger, nullable=False)
    rationale = Column(String(512), nullable=True)
    needed_improvements = Column(String(512), nullable=True)


class ResponseDataProductApplication(BaseModel):
    __tablename__ = 'response_data_product_application'
    response_data_product_id = Column(
        Integer,
        ForeignKey('response_data_product.id'),
        primary_key=True,
    )
    response_application_id = Column(
        Integer,
        ForeignKey('response_application.id'),
        primary_key=True,
    )

    # TODO: Constrain 0-100
    data_product_contribution_to_application_rating = Column(
        SmallInteger,
        nullable=False,
    )
    # TODO: Constraint 0-100
    satisfaction_rating = Column(SmallInteger, nullable=False)
    rationale = Column(String(512), nullable=True)
    needed_improvements = Column(String(512), nullable=True)


class ResponseApplicationSocietalBenefitArea(BaseModel):
    __tablename__ = 'response_application_societal_benefit_area'
    response_application_id = Column(
        Integer,
        ForeignKey('response_application.id'),
        primary_key=True,
    )
    societal_benefit_area_id = Column(
        String(256),
        ForeignKey('societal_benefit_area.id'),
        primary_key=True,
    )


# Reference tables
class SocietalBenefitArea(BaseModel):
    __tablename__ = 'societal_benefit_area'
    id = Column(
        String(256),
        primary_key=True,
    )


class SocietalBenefitSubArea(BaseModel):
    __tablename__ = 'societal_benefit_subarea'
    id = Column(
        String(256),
        primary_key=True,
    )
    societal_benefit_area_id = Column(
        String(256),
        ForeignKey('societal_benefit_area.id'),
        nullable=False,
    )


class SocietalBenefitKeyObjective(BaseModel):
    __tablename__ = 'societal_benefit_key_objective'
    id = Column(
        String(256),
        primary_key=True,
    )
    societal_benefit_subarea_id = Column(
        String(256),
        ForeignKey('societal_benefit_subarea.id'),
        nullable=False,
    )
