from models import Base
from database import engine
# Import all models to ensure they're registered with Base.metadata
from models.user import User
from models.health_profile import HealthProfile
from models.activity_log import ActivityLog
from models.metrics_history import MetricsHistory
from models.consent import DataConsent
from models.goal import Goal

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!") 