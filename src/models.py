import datetime
import enum
from typing import Annotated

from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, text, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from src.database import Base, str_256

type_intpk = Annotated[int, mapped_column(primary_key=True)]
type_created_at = Annotated[datetime.datetime, mapped_column(server_default=text("now()"))]
type_updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("now()"),
        onupdate=datetime.datetime.now(datetime.UTC))]


class WorkersOrm(Base):
    """Создание объекта в Декларативном стиле"""
    __tablename__ = "workers"

    id: Mapped[type_intpk]
    username: Mapped[str_256]

    resumes: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="worker",
    )

    resumes_parttime: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="worker",
        primaryjoin="and_(WorkersOrm.id == ResumesOrm.worker_id, ResumesOrm.workload == 'parttime')",
        order_by="ResumesOrm.id.desc()",
    )


class Workload(enum.Enum):
    parttime = "parttime"
    fulltime = "fulltime"


class ResumesOrm(Base):
    __tablename__ = "resumes"

    id: Mapped[type_intpk]
    title: Mapped[str_256]
    compensation: Mapped[int]
    workload: Mapped[Workload]
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id", ondelete="CASCADE"))
    created_at: Mapped[type_created_at]
    updated_at: Mapped[type_updated_at]

    worker: Mapped["WorkersOrm"] = relationship(
        back_populates="resumes",
    )

    repr_cols_num = 2
    repr_cols = ("created_at", )

    __table_args__ = (
        Index("title_index", "title"),
        CheckConstraint("compensation > 0", name="check_compensation_positive"),
    )














metadata_obj = MetaData()

"""Создание объекта в Императивном стиле"""
workers_table = Table(
    "workers",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String),
)

