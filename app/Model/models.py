from ..extensions import db
from sqlalchemy import Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

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

class MetNeed(db.Model):
    __tablename__ = 'met_need'

    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('cats.id'), nullable=False)
    nevoi_id = db.Column(db.Integer, db.ForeignKey('nevoi.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    cat = relationship("Cat", backref="met_needs")
    nevoi = relationship("Nevoi", backref="met_needs")

    def __repr__(self):
        return f"<MetNeed(id={self.id}, cat_id={self.cat_id}, nevoi_id={self.nevoi_id}, timestamp={self.timestamp})>"

    @classmethod
    def was_met_recently(cls, cat_id, nevoi_id, hours=24):
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return cls.query.filter(
            cls.cat_id == cat_id,
            cls.nevoi_id == nevoi_id,
            cls.timestamp >= cutoff_time
        ).first() is not None