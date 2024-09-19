from sqlalchemy import insert, select, text, update
from sqlalchemy.orm import aliased

from src.database import async_engine, sync_engine
from src.models import Workload, metadata_obj, workers_table


def get_123_sync():
    with sync_engine.connect() as conn:
        res = conn.execute(text("SELECT 1,2,3 union select 4,5,6"))
        print(f"{res.first()=}")


async def get_123_async():
    async with async_engine.connect() as conn:
        res = await conn.execute(text("SELECT 1,2,3 union select 4,5,6"))
        print(f"{res.first()=}")


class SyncCore:
    @staticmethod
    def create_tables():
        sync_engine.echo = True
        metadata_obj.drop_all(sync_engine)
        metadata_obj.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with sync_engine.connect() as conn:
            # stmt = """INSERT INTO workers (username) VALUES
            #     ('Jack'),
            #     ('Michael');"""
            stmt = insert(workers_table).values(
                [
                    {"username": "Jack"},
                    {"username": "Michael"},
                ]
            )
            conn.execute(stmt)
            conn.commit()

    @staticmethod
    def select_workers():
        with sync_engine.connect() as conn:
            query = select(workers_table) # SELECT * FROM workers;
            result = conn.execute(query)
            workers = result.all()
            print(f'{workers=}')

    @staticmethod
    def update_worker(worker_id: int = 2, new_username: str = "Misha"):
        with sync_engine.connect() as conn:
            stmt = (
                update(workers_table)
                .values(username=new_username)
                .filter_by(id=worker_id) # where(workers_table.c.id==worker_id)
            )
            conn.execute(stmt)
            conn.commit()

            #stmt = update(workers_table).where(id=1).values()
