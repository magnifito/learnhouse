from sqlmodel import Session, select, create_engine, SQLModel
from config.config import get_learnhouse_config
from src.db.users import User
from src.db.organizations import Organization

from src.db.user_organizations import UserOrganization
from src.db.roles import Role

def inspect_users():
    config = get_learnhouse_config()
    print(f"DB URL: {config.database_config.sql_connection_string}")
    engine = create_engine(config.database_config.sql_connection_string)
    
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        print(f"Found {len(users)} users.")
        user_map = {}
        for user in users:
            print(f"User: {user.username} (ID: {user.id}), Email: {user.email}")
            user_map[user.id] = user.username

        orgs = session.exec(select(Organization)).all()
        print(f"Found {len(orgs)} organizations.")
        org_map = {}
        for org in orgs:
            print(f"Org: {org.name} (ID: {org.id}), Slug: {org.slug}")
            org_map[org.id] = org.slug

        print("\\nRoles:")
        roles = session.exec(select(Role)).all()
        for role in roles:
            print(f"Role: {role.name} (ID: {role.id})")

        print("\\nUserOrganizations:")
        user_orgs = session.exec(select(UserOrganization)).all()
        print(f"Found {len(user_orgs)} links.")
        for uo in user_orgs:
            u_name = user_map.get(uo.user_id, "Unknown")
            o_slug = org_map.get(uo.org_id, "Unknown")
            print(f"Link: User {u_name} -> Org {o_slug} (Role ID: {uo.role_id})")

if __name__ == "__main__":
    inspect_users()
