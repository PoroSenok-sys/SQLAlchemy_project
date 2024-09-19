from sqlalchemy import Integer, and_, cast, func, insert, inspect, or_, select, text
from sqlalchemy.orm import aliased, contains_eager, joinedload, selectinload

from src.database import Base, async_engine, async_session_factory, sync_session_factory, sync_engine
from src.models import WorkersOrm, Workload, ResumesOrm


class SyncORM:
    @staticmethod
    def create_tables():
        sync_engine.echo = True
        Base.metadata.drop_all(sync_engine)
        Base.metadata.create_all(sync_engine)
        print(1234)
        sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with sync_session_factory() as session:
            worker_jack = WorkersOrm(username="Jack")
            worker_michael = WorkersOrm(username="Michael")
            session.add_all([worker_jack, worker_michael])
            # flush отправляет запрос в базу данных
            # После flush каждый из работников получает первичный ключ id, который отдала БД
            session.flush()
            session.commit()

    @staticmethod
    def select_workers():
        with sync_session_factory() as session:
            query = select(WorkersOrm) # SELECT * FROM workers;
            result = session.execute(query)
            workers = result.scalars().all()
            for worker in workers:
                print(f'id: {worker.id}, username: {worker.username}')
            #print(f'{workers=}')

    @staticmethod
    def update_worker(worker_id: int = 2, new_username: str = "Misha"):
        with sync_session_factory() as session:
            search_worker = session.get(WorkersOrm, worker_id)
            search_worker.username = new_username
            session.commit()

    @staticmethod
    def select_resumes():
        with sync_session_factory() as session:
            query = select(ResumesOrm)
            result = session.execute(query)
            resumes = result.scalars().all()
            for resume in resumes:
                print(f'id: {resume.id}, title: {resume.title}, compensation: {resume.compensation},'
                      f' workload: {resume.workload}, worker_id: {resume.worker_id}')
            #print(f'{workers=}')

    @staticmethod
    def insert_resumes():
        with sync_session_factory() as session:
            resume_jack_1 = ResumesOrm(
                title="Python Junior Developer", compensation=50000, workload=Workload.fulltime, worker_id=1)
            resume_jack_2 = ResumesOrm(
                title="Python Разработчик", compensation=150000, workload=Workload.fulltime, worker_id=1)
            resume_michael_1 = ResumesOrm(
                title="Python Data Engineer", compensation=250000, workload=Workload.parttime, worker_id=2)
            resume_michael_2 = ResumesOrm(
                title="Data Scientist", compensation=300000, workload=Workload.fulltime, worker_id=2)
            session.add_all([resume_jack_1, resume_jack_2,
                             resume_michael_1, resume_michael_2])
            session.commit()

    @staticmethod
    def select_resumes_avg_compensation(like_language: str = "Python"):
        """
        select workload, avg(compensation)::int as avg_compensation
        from resumes
        where title like '%Python%' and compensation > 40000
        group by workload
        having avg(compensation) > 70000
        """
        with sync_session_factory() as session:
            query = (
                select(
                    ResumesOrm.workload,
                    # 1 вариант использования cast
                    # cast(func.avg(ResumesOrm.compensation), Integer).label("avg_compensation"),
                    # 2 вариант использования cast (предпочтительный способ)
                    func.avg(ResumesOrm.compensation).cast(Integer).label("avg_compensation"),
                )
                .select_from(ResumesOrm)
                .filter(and_(
                    ResumesOrm.title.contains(like_language),
                    ResumesOrm.compensation > 40000,
                ))
                .group_by(ResumesOrm.workload)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = session.execute(query)
            result = res.all()
            print(result[0].avg_compensation)

    @staticmethod
    def insert_additional_resumes():
        with sync_session_factory() as session:
            workers = [
                {"username": "Artem"},  # id 3
                {"username": "Roman"},  # id 4
                {"username": "Petr"},   # id 5
            ]
            resumes = [
                {"title": "Python программист", "compensation": 60000, "workload": "fulltime", "worker_id": 3},
                {"title": "Machine Learning Engineer", "compensation": 70000, "workload": "parttime", "worker_id": 3},
                {"title": "Python Data Scientist", "compensation": 80000, "workload": "parttime", "worker_id": 4},
                {"title": "Python Analyst", "compensation": 90000, "workload": "fulltime", "worker_id": 4},
                {"title": "Python Junior Developer", "compensation": 100000, "workload": "fulltime", "worker_id": 5},
            ]
            insert_workers = insert(WorkersOrm).values(workers)
            insert_resumes = insert(ResumesOrm).values(resumes)
            session.execute(insert_workers)
            session.execute(insert_resumes)
            session.commit()

    @staticmethod
    def join_cte_subquery_window_func():
        """
        Запрос на языке SQL:
        WITH helper2 AS (
            SELECT *, compensation-avg_workload_compensation AS compensation_diff
            FROM
            (SELECT
                w.id,
                w.username,
                r.compensation,
                r.workload,
                avg(r.compensation) OVER (PARTITION BY workload)::int AS avg_workload_compensation
            FROM resumes r
            JOIN workers w ON r.worker_id = w.id) helper1
        )
        SELECT * FROM helper2
        ORDER BY compensation_diff DESC;
        """
        with sync_session_factory() as session:
            r = aliased(ResumesOrm)
            w = aliased(WorkersOrm)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.compensation).over(partition_by=r.workload).cast(Integer).label("avg_workload_compensation"),
                )
                # .select_from(r)
                .join(r, r.worker_id == w.id).subquery("helper1")
            )
            cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.compensation,
                    subq.c.workload,
                    subq.c.avg_workload_compensation,
                    (subq.c.compensation - subq.c.avg_workload_compensation).label("compensation_diff"),
                )
                .cte("helper2")
            )
            query = (
                select(cte)
                .order_by(cte.c.compensation_diff.desc())
            )

            res = session.execute(query)
            result = res.all()
            print(f"{len(result)=}. {result=}")

    @staticmethod
    def select_workers_with_joined_relationship():
        with sync_session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(joinedload(WorkersOrm.resumes))
            )

            res = session.execute(query)
            result = res.unique().scalars().all()

            worker_1_resumes = result[0].resumes
            print(worker_1_resumes)

            worker_2_resumes = result[1].resumes
            print(worker_2_resumes)

    @staticmethod
    def select_workers_with_selectin_relationship():
        with sync_session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(selectinload(WorkersOrm.resumes))
            )

            res = session.execute(query)
            result = res.scalars().all()

            worker_1_resumes = result[0].resumes
            # print(worker_1_resumes)

            worker_2_resumes = result[1].resumes
            # print(worker_2_resumes)
