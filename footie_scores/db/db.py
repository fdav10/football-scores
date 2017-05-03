if __name__ == '__main__':
    import datetime as dt
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    import munch
    from footie_scores.apis.football_api import FootballAPI

    engine = create_engine('sqlite:///:memory:', echo=True)
    session = sessionmaker(bind=engine)()
    Base = declarative_base()

    class Fixture(Base):
        __tablename__ = 'fixtures'

        id = Column(Integer, primary_key=True)
        team_home = Column(String)
        team_away = Column(String)
        score_home = Column(String)
        score_away = Column(String)
        date = Column(String)
        time_kickoff = Column(String)
        time_elapsed = Column(String)

        def __repr__(self):
            return "<Fixture(team_home='%s', team_away='%s', date='%s)" %(
                self.team_home, self.team_away, self.date)


    class FromDict():
        def __init__(self, **entries):
            import ipdb; ipdb.set_trace()
            self.__dict__.update(entries)

    fapi = FootballAPI()
    cl = fapi.get_competitions()['data'][0]
    yesterday = dt.date.today() - dt.timedelta(days=1)
    fixtures = fapi.page_ready_fixtures_for_date(yesterday, cl)
    for f in fixtures:
        serialised_f = munch.munchify(f)
        import ipdb; ipdb.set_trace()
