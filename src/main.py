import asyncio
import os.path
import sys

from src.queries.core import SyncCore
from src.queries.orm import SyncORM

sys.path.insert(1, os.path.join(sys.path[0], '..'))


async def main():
    # ========== SYNC ==========
    # CORE
    # SyncCore.create_tables()
    # SyncCore.insert_workers()
    # SyncCore.select_workers()
    # SyncCore.update_worker()
    # #SyncCore.insert_resumes()
    # #SyncCore.select_resumes_avg_compensation()
    # #SyncCore.insert_additional_resumes()
    # #SyncCore.join_cte_subquery_window_func()

    # ORM
    SyncORM.create_tables()
    SyncORM.insert_workers()
    SyncORM.select_workers()
    SyncORM.update_worker()
    SyncORM.insert_resumes()
    # SyncORM.select_resumes()
    # SyncORM.select_resumes_avg_compensation()
    #SyncORM.insert_additional_resumes()
    #SyncORM.join_cte_subquery_window_func()
    #SyncORM.select_workers_with_lazy_relationship()
    #SyncORM.select_workers_with_joined_relationship()
    #SyncORM.select_workers_with_selectin_relationship()
    #SyncORM.select_workers_with_condition_relationship()
    #SyncORM.select_workers_with_condition_relationship_contains_eager()
    SyncORM.select_workers_with_relationship_contains_eager_with_limit()
    #SyncORM.convert_workers_to_dto()
    #SyncORM.add_vacancies_and_replies()
    #SyncORM.select_resumes_with_all_relationships()


if __name__ == "__main__":
    asyncio.run(main())
