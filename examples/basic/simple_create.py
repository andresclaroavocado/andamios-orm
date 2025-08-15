"""
Simple CREATE Example - The Simplest Possible

This is what Grok recommended: minimal setup, focus on one operation,
no session management, no async complexity.
"""

from sqlalchemy import Column, String
from andamios_orm import SimpleModel, save, create_tables

# Define a simple model
class Repository(SimpleModel):
    __tablename__ = "repositories"
    
    name = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"Repository(id={self.id}, name='{self.name}')"

# One-time setup (in real apps, do this at startup)
create_tables()

# CREATE - Ultra simple!
repo = Repository(name="MyProject")
saved_repo = save(repo)

print(f"Created: {saved_repo}")
print(f"ID assigned: {saved_repo.id}")