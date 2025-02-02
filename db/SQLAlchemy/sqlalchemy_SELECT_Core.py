"""Selecting Rows with Core or ORM
https://docs.sqlalchemy.org/en/14/tutorial/data_select.html

For both Core and ORM, the select() function generates a Select construct 
which is used for all SELECT queries. Passed to methods like 
Connection.execute() in Core and Session.execute() in ORM, a SELECT statement 
is emitted in the current transaction and the result rows available via 
the returned Result object.
"""

from sqlalchemy import create_engine
from sqlalchemy import insert, select, bindparam
from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy import text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base, relationship


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
# print(repr(user_table.c.name))
# print(user_table.c.keys())
# print(user_table.primary_key)

# Primary Key & Foreign Key
# When using the ForeignKey object within a Column definition, we can omit 
# the datatype for that Column; it is automatically inferred from that 
# of the related column, in the above example the Integer datatype of 
# the user_account.id column
address_table = Table(
        "address",
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', ForeignKey('user_account.id'), nullable=False),
        Column('email_address', String, nullable=False)
    )

# Create the database
metadata.create_all(engine)

##########################################
# Define Tables using ORM
Base = declarative_base()
print(Base)

class User(Base):
    __tablename__ = 'user_account'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)

    addresses = relationship("Address", back_populates="user")

    def __repr__(self):
       return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user_account.id'))

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


""" Insert Rows with Core"""
stmt = insert(user_table).values(name='spongebob', fullname="Spongebob Squarepants")
# print(stmt)
# compiled = stmt.compile()
# print(compiled.params)
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

""" INSERT...FROM SELECT """
print("----INSERT...FROM SELECT ---")
# select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
# insert_stmt = insert(address_table).from_select(
#     ["user_id", "email_address"], select_stmt
# )
# # print(insert_stmt)
# with engine.connect() as conn:
#     result = conn.execute(insert_stmt)
#     conn.commit()
#     result = conn.execute(select(address_table))
#     for r in result:
#         print(r)


#########################################
""" 
Selecting Rows with Core
"""
print("----Selecting Rows with Core ----")
stmt = select(user_table).where(user_table.c.name=='spongebob')
stmt2 = select(user_table.c.name, user_table.c.fullname).where(user_table.c.name=='spongebob')
# print(stmt)
with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(row)

    for row in conn.execute(stmt2):
        # print(type(row))
        print(row)
'''
(1, 'spongebob', 'Spongebob Squarepants')
('spongebob', 'Spongebob Squarepants')
'''

# Selecting from Labeled SQL Expressions
print("---Selecting from Labeled SQL Expressions---")
stmt = (
    select(
        ("Username: " + user_table.c.name).label('username'),
        user_table.c.fullname,
    ).order_by(user_table.c.name)
)
with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(f"{row.username} {row.fullname}")

# Selecting with Textual Column Expressions
print("--- Selecting with Textual Column Expressions ---")
stmt = (
    select(
        text("'some phrase'"), user_table.c.name
    ).order_by(user_table.c.name)
)
with engine.connect() as conn:
    print(conn.execute(stmt).all())

# In this common case we can get more functionality out of our textual 
# fragment using the literal_column() construct instead. This object is 
# similar to text() except that instead of representing arbitrary SQL of 
# any form, it explicitly represents a single “column” and can then be 
# labeled and referred towards in subqueries and other expressions
from sqlalchemy import literal_column
stmt = (
    select(
        literal_column("'some phrase'").label("p"), user_table.c.name
    ).order_by(user_table.c.name)
)
with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(f"{row.p}, {row.name}")


# The WHERE clause
# (1) To produce expressions joined by AND, where() method maybe invoked any number of times:
print(
    select(address_table.c.email_address).
    where(user_table.c.name == 'squidward').
    where(address_table.c.user_id == user_table.c.id)
)
'''
SELECT address.email_address 
FROM address, user_account
WHERE user_account.name = :name_1 AND address.user_id = user_account.id
'''
#(2) A single call to Select.where() also accepts multiple expressions with the same effect:
print(
    select(address_table.c.email_address).
    where(
        user_table.c.name == 'squidward',
        address_table.c.user_id == user_table.c.id
    )
)
'''
SELECT address.email_address
FROM address, user_account
WHERE user_account.name = :name_1 AND address.user_id = user_account.id 
'''
# (3) “AND” and “OR” conjunctions are both available directly using the and_() 
# and or_() functions, illustrated below in terms of ORM entities:
from sqlalchemy import and_, or_
print(
    select(address_table.c.email_address)
    .where(
        and_(
            or_(
                user_table.c.name == 'squidward', 
                user_table.c.name == 'sandy'
            ),
            address_table.c.user_id == user_table.c.id
        )
    )
)
"""
SELECT address.email_address
FROM address, user_account
WHERE (user_account.name = :name_1 OR user_account.name = :name_2) AND address.user_id = user_account.id
"""
#(4) select().filter_by()
print(
    select(user_table.c.name).filter_by(name='spongebob', fullname='Spongebob Squarepants')
)
"""
SELECT user_account.id, user_account.name, user_account.fullname
FROM user_account
WHERE user_account.name = :name_1 AND user_account.fullname = :fullname_1 
"""

# Explicit FROM clauses and JOINs
print("--- Explicit FROM clauses and JOINs ---")
# (1) select().join_from()
print(
    select(user_table.c.name, address_table.c.email_address)
    .join_from(user_table, address_table)
) 
"""
SELECT user_account.name, address.email_address
FROM user_account JOIN address ON user_account.id = address.user_id 
"""

# (2) Select.join() method, which indicates only the right side of the JOIN, 
# the left hand-side is inferred:
print(
    select(user_table.c.name, address_table.c.email_address).
    join(address_table)
)
"""
SELECT user_account.name, address.email_address
FROM user_account JOIN address ON user_account.id = address.user_id  
"""
# (3) Select.from() method - used if the columns clause does not
print(
    select(user_table.c.name, address_table.c.email_address).
    select_from(user_table).join(address_table)
)

# Select.from() method is used if the columns clause does not have enough info 
# to provide for a FROM clause.
from sqlalchemy import func
print (
    select(func.count('*')).select_from(user_table)
)
"""
SELECT count(:count_2) AS count_1
FROM user_account
"""

# Setting on the ON Clause
# Both Select.join() and Select.join_from() accept an additional argument 
# for the ON clause, which is stated using the same SQL Expression mechanics 
# as we saw about in The WHERE clause
print(
    select(address_table.c.email_address)
    .select_from(user_table)
    .join(address_table, user_table.c.id == address_table.c.user_id)
)

# OUTER and FULL join
# Both the Select.join() and Select.join_from() methods accept keyword 
# arguments Select.join.isouter and Select.join.full which will render 
# LEFT OUTER JOIN and FULL OUTER JOIN, respectively:
print("--- OUTER and FULL join ---")
stmt1 = select(user_table.c.name, address_table.c.email_address).join(address_table, isouter=True)
#stmt1 = select(user_table.c.name, address_table.c.email_address).outerjoin(address_table)
print(stmt1)
"""
SELECT user_account.id, user_account.name, user_account.fullname
FROM user_account LEFT OUTER JOIN address ON user_account.id = address.user
"""
stmt2 = select(user_table).join(address_table, full=True)
print(stmt2)
"""
SELECT user_account.id, user_account.name, user_account.fullname
FROM user_account FULL OUTER JOIN address ON user_account.id = address.user_id
"""
with engine.connect() as conn:
    print(conn.execute(stmt1).all())
    # print(session.execute(stmt2).all())   # FULL and RIGHT Outer join not suppored in sqllite3

# ORDER BY, GROUP BY, HAVING
print(" --- ORDER BY, GROUP BY, HAVING ---")
stmt = select(user_table).order_by(user_table.c.name.asc())
#stmt = select(user_table).order_by(user_table.c.name.desc())
with engine.connect() as conn:
    print(conn.execute(stmt).all())


# Aggregate functions with GROUP BY / HAVING
# SQLAlchemy provides for SQL functions in an open-ended 
# way using a namespace known as func
print("--- Aggregate functions with GROUP BY / HAVING ---")
from sqlalchemy import func
# count_fn = func.count(user_table.c.id)
# print(count_fn)
with engine.connect() as conn:
    result = conn.execute(
        select(User.name, func.count(Address.id).label("count")).
        join(Address).
        group_by(User.name).
        having(func.count(Address.id) > 1)
    )
    print(result.all())

# rdering or Grouping by a Label
from sqlalchemy import func, desc
stmt = select(Address.user_id, User.name,
        func.count(Address.id).label('num_addresses')). \
        join(Address). \
        group_by("user_id").order_by("user_id", desc("num_addresses"))
print(stmt)
with engine.connect() as conn:
    result = conn.execute(stmt)
    print(result.all())

# Using Alias
print("--- Using Alias ---")
# user_alias_1 = user_table.alias()
# user_alias_2 = user_table.alias()
# print(
#     select(user_alias_1.c.name, user_alias_2.c.name).
#     join_from(user_alias_1, user_alias_2, user_alias_1.c.id > user_alias_2.c.id)
# )
u1 = user_table.alias()
u2 = user_table.alias()
print(
    select(u1.c.name, u2.c.name).
    join_from(u1, u2, u1.c.id > u2.c.id)
)

# Subqueries and CTEs
print("--- Subqueries and CTEs ---")
subq = select(
    func.count(address_table.c.id).label("count"),
    address_table.c.user_id
).group_by(address_table.c.user_id).subquery()
stmt = select(
    user_table.c.name,
    user_table.c.fullname,
    subq.c.count
).join_from(user_table, subq)
print(stmt)

# CTE: Select.cte()

#Scalar and Correlated Subqueries
# A scalar subquery is a subquery that returns exactly zero or one row 
# and exactly one column.

# UNION, UNION ALL and other set operations
print("--- UNION, UNION ALL and other set operations ---")
from sqlalchemy import union_all
stmt1 = select(user_table).where(user_table.c.name == 'sandy')
stmt2 = select(user_table).where(user_table.c.name == 'spongebob')
u = union_all(stmt1, stmt2)
with engine.connect() as conn:
    result = conn.execute(u)
    print(result.all())


#EXISTS subqueries
print("--- EXISTS subqueries ---")
subq = (
    select(func.count(address_table.c.id)).
    where(user_table.c.id == address_table.c.user_id).
    group_by(address_table.c.user_id).
    having(func.count(address_table.c.id) > 1)
).exists()
with engine.connect() as conn:
    result = conn.execute(
        select(user_table.c.name).where(subq)
    )
    print(result.all())

# Not exists
print("---- NOT EXISTS ---") 
subq = (
    select(address_table.c.id).
    where(user_table.c.id == address_table.c.user_id)
).exists()
with engine.connect() as conn:
    result = conn.execute(
        select(user_table.c.name).where(~subq)
    )
    print(result.all())


#Working with SQL Functions
print("--- Working with SQL Functions ---")
# count()
# max(), min()
# now()
# concat(), lower(), upper()

from sqlalchemy.dialects import postgresql
print(select(func.now()).compile(dialect=postgresql.dialect()))
"""
SELECT now() AS now_1
"""

from sqlalchemy.dialects import oracle
print(select(func.now()).compile(dialect=oracle.dialect()))
"""
SELECT CURRENT_TIMESTAMP AS now_1 FROM DUAL
"""
