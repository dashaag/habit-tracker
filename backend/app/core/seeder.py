import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.role import RoleRepository
from app.db import SessionLocal  # Import SessionLocal directly

logger = logging.getLogger(__name__)

DEFAULT_ROLES = ["Admin", "User"]

async def init_roles() -> None:
    """Initializes the default roles in the database."""
    logger.info("Initializing default roles...")
    
    session: AsyncSession | None = None
    try:
        # Create a new session for the seeder
        session = SessionLocal()
        
        role_repo = RoleRepository(session)
        for role_name in DEFAULT_ROLES:
            role = await role_repo.get_role_by_name(name=role_name)
            if not role:
                await role_repo.create_role(role_name=role_name)
                logger.info(f"Role '{role_name}' created.")
            else:
                logger.info(f"Role '{role_name}' already exists.")
        await session.commit() # Commit changes after all roles are processed
    except Exception as e:
        logger.error(f"Error initializing roles: {e}")
        if session:
            await session.rollback() # Rollback on error
    finally:
        if session:
            await session.close() # Ensure the session is closed
    logger.info("Role initialization process finished.")

if __name__ == "__main__":
    # This allows running the seeder directly, e.g., for initial setup or testing.
    # You'd need to configure logging and asyncio.run properly for this.
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_roles())
