from app.models.Role import Role
from app.models.RoleDAOInterface import RoleDAOInterface
from app.extensions import db

class RoleDAO(RoleDAOInterface):
    def create(self, role):
        db.session.add(role)
        db.session.commit()
        return role

    def get_by_id(self, id_role):
        return Role.query.get(id_role)

    def get_all(self):
        return Role.query.all()

    def update(self, role):
        db.session.commit()
        return role

    def delete(self, id_role):
        role = self.get_by_id(id_role)
        if role:
            db.session.delete(role)
            db.session.commit()
