from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

# Apna password yahan zaroor update karein agar alag hai toh
MYSQL_URL = "mysql+pymysql://root:yes@localhost:3306/exam_analytics"

engine = create_engine(MYSQL_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. Database Schema (Table Design)
class ExamTrend(Base):
    __tablename__ = "exam_trends"

    id = Column(Integer, primary_key=True, index=True)
    exam_year = Column(Integer, nullable=False)
    exam_stage = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    cut_off_marks = Column(Float)
    total_vacancies = Column(Integer)
    difficulty_level = Column(String(50))

# 2. Database mein Table Create karna
def init_db():
    print("⏳ Creating tables in database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

# 3. Sample Data Insert karna
def seed_data():
    db = SessionLocal()
    
    # Check karein ki kya data pehle se hai
    if db.query(ExamTrend).first():
        print("⚡ Data already exists in the database. Skipping seed.")
        db.close()
        return

    print("⏳ Inserting sample historical data...")
    sample_data = [
        ExamTrend(exam_year=2020, exam_stage="Prelims", category="General", cut_off_marks=92.51, total_vacancies=796, difficulty_level="Moderate-Tough"),
        ExamTrend(exam_year=2021, exam_stage="Prelims", category="General", cut_off_marks=87.54, total_vacancies=712, difficulty_level="Tough"),
        ExamTrend(exam_year=2022, exam_stage="Prelims", category="General", cut_off_marks=88.22, total_vacancies=1011, difficulty_level="Moderate"),
        ExamTrend(exam_year=2023, exam_stage="Prelims", category="General", cut_off_marks=75.41, total_vacancies=1105, difficulty_level="Very Tough"),
        ExamTrend(exam_year=2020, exam_stage="Prelims", category="OBC", cut_off_marks=89.12, total_vacancies=796, difficulty_level="Moderate-Tough"),
        ExamTrend(exam_year=2023, exam_stage="Prelims", category="OBC", cut_off_marks=74.75, total_vacancies=1105, difficulty_level="Very Tough"),
    ]
    
    db.add_all(sample_data)
    db.commit()
    print("✅ Sample data inserted successfully!")
    db.close()

if __name__ == "__main__":
    init_db()
    seed_data()