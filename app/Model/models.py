from ..extensions import db # Notice the relative import for db
from sqlalchemy import Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

cat_nevoi_association = db.Table('cat_nevoi', db.Model.metadata,
    db.Column('cat_id', db.Integer, db.ForeignKey('cats.id'), primary_key=True),
    db.Column('nevoi_id', db.Integer, db.ForeignKey('nevoi.id'), primary_key=True)
)

class Nevoi(db.Model):
    __tablename__ = 'nevoi'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    cats = relationship("Cat",
                        secondary=cat_nevoi_association,
                        back_populates="nevoi_list")

    def __repr__(self):
        return f"<Nevoi(id={self.id}, name='{self.name}')>"

class Cat(db.Model):
    __tablename__ = 'cats'

    id = db.Column(db.Integer, primary_key=True)
    nume = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    nevoi_list = relationship("Nevoi",
                              secondary=cat_nevoi_association,
                              back_populates="cats",
                              collection_class=list)

    def __repr__(self):
        return f"<Cat(id={self.id}, nume='{self.nume}')>"