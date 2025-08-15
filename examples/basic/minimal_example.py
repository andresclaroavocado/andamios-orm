"""
Minimal Example - As Simple As Possible

This is the "simplest example" that addresses all of Grok's points:
- No engine/session setup visible to user
- No async complexity  
- Focused on one core operation
- Self-contained
- Minimal output
"""

from sqlalchemy import Column, String
from andamios_orm import SimpleModel, save, create_tables

class Repository(SimpleModel):
    __tablename__ = "repositories"
    name = Column(String(255), nullable=False)

# Setup (one line)
create_tables()

# Use (two lines) 
repo = Repository(name="backend-api")
saved_repo = save(repo)

print(f"Created repository: {saved_repo.name} (ID: {saved_repo.id})")