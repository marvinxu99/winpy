"""SQLAlchemy TUtorial:
https://docs.sqlalchemy.org/en/14/tutorial/data.html
To create, select and manipulate data within a relational database
"""

from sqlalchemy import create_engine
from sqlalchemy import insert, select, bindparam, update
from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy import ForeignKey


# Establish connectivity - the Engine
# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
engine = create_engine("sqlite+pysqlite:///:memory:", echo=False, future=True)

"""
Setting up MetaData with Table objects (SQLAlchemy Core)
"""
# MetaData object
metadata = MetaData()

# user_account
user_table = Table(
        "user_account",
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(30)),
        Column('fullname', String)
    )

address_table = Table(
        "address",
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', ForeignKey('user_account.id'), nullable=False),
        Column('email_address', String, nullable=False)
    )

# Create the database
metadata.create_all(engine)

""" Insert Rows with Core"""
stmt = insert(user_table).values(name='spongebob', fullname="Spongebob Squarepants")
with engine.connect() as conn:
    result = conn.execute(stmt)
    conn.commit()
    print(result.inserted_primary_key)


# INSERT usually generates the “values” clause automatically
with engine.connect() as conn:
    result = conn.execute(
        insert(user_table),
        [
            {"name": "sandy", "fullname": "Sandy Cheeks"},
            {"name": "patrick", "fullname": "Patrick Star"}
        ]
    )
    conn.commit()
    result = conn.execute(select(user_table))
    print(result.all())

# Below is some slightly deeper alchemy just so that we can add related rows 
# without fetching the primary key identifiers from the user_table operation 
# into the application. Most Alchemists will simply use the ORM which takes 
# care of things like this for us.
scalar_subquery = (
    select(user_table.c.id)
    .where(user_table.c.name==bindparam('username'))
    .scalar_subquery()
)

with engine.connect() as conn:
    result = conn.execute(
        insert(address_table).values(user_id=scalar_subquery),
        [
            {"username": 'spongebob', "email_address": "spongebob@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@sqlalchemy.org"},
            {"username": 'sandy', "email_address": "sandy@squirrelpower.org"},
        ]
    )
    conn.commit()
    result = conn.execute(
            select(
                    user_table.c.id, 
                    user_table.c.fullname, 
                    address_table.c.email_address
                )
            .where(user_table.c.id==address_table.c.user_id)
        )
    print(result.all())

# Update 
# The update() SQL Expression Construct
stmt = (
    update(user_table).where(user_table.c.name == 'patrick').
    values(fullname='Patrick ITi')
)
with engine.connect() as conn:
    conn.execute(stmt)
    conn.commit()
    result = conn.execute(select(user_table))
    print(result.all())


# Update executemany():
stmt = (
    update(user_table).
    where(user_table.c.name == bindparam('oldname')).
    values(fullname=bindparam('newname'))
)
print(stmt)
with engine.connect() as conn:
    conn.execute(
        stmt,
        [
            {'oldname':'patrick', 'newname':'ed'},
            {'oldname':'spongebob', 'newname':'mary'},
            {'oldname':'jim', 'newname':'jake'},
        ]
    )
    conn.commit()
    result = conn.execute(select(user_table))
    print(result.all())
