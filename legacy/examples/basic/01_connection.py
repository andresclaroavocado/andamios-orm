"""
Example 01: Database Connection and Engine Setup

This example demonstrates how to:
- Create a DuckDB engine with proper configuration
- Set up async session management
- Handle connection lifecycle
- Use uvloop for optimal performance

Expected behavior:
- Successfully connect to DuckDB
- Create and close sessions properly
- No resource leaks or connection issues
"""

import asyncio
import uvloop
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from andamios_orm import create_engine, sessionmaker, AsyncSession


async def basic_connection_example():
    """Basic database connection example."""
    print("🔌 Setting up database connection...")
    
    # Create async engine for DuckDB
    # Connection string format: duckdb:///path/to/file.db
    # Use in-memory database for this example
    engine = create_engine(
        "duckdb:///:memory:",
        echo=True,  # Log SQL statements for debugging
        pool_size=10,  # Connection pool size
        max_overflow=20,  # Maximum overflow connections
    )
    
    # Create session factory
    SessionLocal = sessionmaker(
        engine, 
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    print("✅ Engine created successfully")
    
    # Test basic session creation and cleanup
    async with SessionLocal() as session:
        print("📖 Session created")
        
        # Execute a simple query to test connection
        result = await session.execute("SELECT 'Hello from DuckDB!' as message")
        message = result.scalar()
        print(f"📨 Message from database: {message}")
        
        # Session automatically closed here
        print("🔒 Session closed")
    
    # Clean shutdown
    await engine.dispose()
    print("🛑 Engine disposed")


@asynccontextmanager
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.
    
    This pattern ensures proper resource cleanup and is the recommended
    way to handle database sessions in production code.
    """
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    await engine.dispose()


async def session_context_manager_example():
    """Example using the session context manager."""
    print("\n🎯 Using session context manager...")
    
    async with get_database_session() as session:
        # Your database operations here
        result = await session.execute("SELECT 42 as answer")
        answer = result.scalar()
        print(f"🧮 The answer is: {answer}")
    
    print("✅ Session automatically managed")


async def multiple_sessions_example():
    """Example showing multiple concurrent sessions."""
    print("\n🔄 Multiple concurrent sessions...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    async def worker(worker_id: int, session_factory) -> str:
        """Worker function that uses its own session."""
        async with session_factory() as session:
            result = await session.execute(f"SELECT 'Worker {worker_id}' as worker")
            return result.scalar()
    
    # Run multiple workers concurrently
    tasks = [
        worker(i, SessionLocal) 
        for i in range(1, 4)
    ]
    
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(f"👷 {result} completed")
    
    await engine.dispose()
    print("✅ All workers completed")


async def error_handling_example():
    """Example showing proper error handling with database connections."""
    print("\n⚠️  Error handling example...")
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    try:
        async with SessionLocal() as session:
            # This will cause an error (invalid SQL)
            await session.execute("INVALID SQL STATEMENT")
    except Exception as e:
        print(f"🚨 Caught expected error: {type(e).__name__}: {e}")
        print("✅ Error handled properly, session cleaned up")
    
    await engine.dispose()


async def performance_monitoring_example():
    """Example showing how to monitor connection performance."""
    print("\n📊 Performance monitoring example...")
    
    import time
    
    start_time = time.perf_counter()
    
    engine = create_engine("duckdb:///:memory:", echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession)
    
    setup_time = time.perf_counter() - start_time
    print(f"⚡ Engine setup took: {setup_time:.4f} seconds")
    
    # Test session creation performance
    session_times = []
    
    for i in range(5):
        start = time.perf_counter()
        
        async with SessionLocal() as session:
            await session.execute("SELECT 1")
        
        end = time.perf_counter()
        session_times.append(end - start)
    
    avg_time = sum(session_times) / len(session_times)
    print(f"📈 Average session time: {avg_time:.4f} seconds")
    
    await engine.dispose()


async def main():
    """Main example runner."""
    print("🚀 Andamios ORM Connection Examples")
    print("=" * 50)
    
    await basic_connection_example()
    await session_context_manager_example()
    await multiple_sessions_example()
    await error_handling_example()
    await performance_monitoring_example()
    
    print("\n✨ All connection examples completed successfully!")


if __name__ == "__main__":
    # Use uvloop for optimal async performance
    uvloop.run(main())