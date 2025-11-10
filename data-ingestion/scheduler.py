"""
데이터 수집 배치 스케줄러

APScheduler를 사용하여 정해진 시간에 시장 데이터를 자동 수집합니다.
- 스케줄: 08:30, 11:30, 15:30 (환경변수로 설정 가능)
- 개별 어댑터 실패 시 다른 어댑터 계속 실행
- 성공/실패 로그 기록
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import logging
import os
import sys
from typing import List

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('data_ingestion.log')
    ]
)
logger = logging.getLogger(__name__)


class DataIngestionScheduler:
    """데이터 수집 스케줄러"""
    
    def __init__(self, adapters: List, normalizer, repository):
        """
        Args:
            adapters: MarketAdapter 리스트
            normalizer: DataNormalizer 인스턴스
            repository: PriceRepository 인스턴스
        """
        self.adapters = adapters
        self.normalizer = normalizer
        self.repository = repository
        self.collection_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0
        }
    
    def run_collection(self):
        """
        모든 어댑터에서 데이터 수집
        
        1. 각 어댑터에서 raw 데이터 수집
        2. 정규화 (품목명 매핑, 단위 변환)
        3. DB 저장
        4. 성공/실패 로그 기록
        
        개별 어댑터 실패 시에도 다른 어댑터는 계속 실행됩니다.
        """
        self.collection_stats['total_runs'] += 1
        
        logger.info("=" * 60)
        logger.info(f"Starting data collection run #{self.collection_stats['total_runs']}")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        total_success = 0
        total_failed = 0
        total_records = 0
        
        for adapter in self.adapters:
            adapter_name = adapter.__class__.__name__
            
            try:
                logger.info(f"Processing {adapter_name}...")
                
                # 1. 데이터 수집
                raw_data = adapter.fetch_data(datetime.now())
                logger.info(f"{adapter_name}: Fetched {len(raw_data)} raw records")
                
                if not raw_data:
                    logger.warning(f"{adapter_name}: No data fetched")
                    continue
                
                # 2. 데이터 정규화
                normalized = self.normalizer.normalize(
                    raw_data, 
                    adapter.get_market_id()
                )
                logger.info(f"{adapter_name}: Normalized {len(normalized)} records")
                
                if not normalized:
                    logger.warning(f"{adapter_name}: No records after normalization")
                    continue
                
                # 3. DB 저장
                inserted_count = self.repository.bulk_insert(normalized)
                logger.info(f"{adapter_name}: Inserted {inserted_count} records")
                
                total_success += 1
                total_records += inserted_count
                
                logger.info(
                    f"✓ Success: {adapter_name} - "
                    f"{inserted_count} records inserted"
                )
                
            except Exception as e:
                total_failed += 1
                logger.error(
                    f"✗ Failed: {adapter_name} - "
                    f"Error: {str(e)}",
                    exc_info=True
                )
                # 개별 어댑터 실패 시에도 계속 진행
                continue
        
        # 수집 결과 요약
        logger.info("-" * 60)
        logger.info("Collection Summary:")
        logger.info(f"  Total adapters: {len(self.adapters)}")
        logger.info(f"  Successful: {total_success}")
        logger.info(f"  Failed: {total_failed}")
        logger.info(f"  Total records inserted: {total_records}")
        logger.info("-" * 60)
        
        if total_success > 0:
            self.collection_stats['successful_runs'] += 1
        else:
            self.collection_stats['failed_runs'] += 1
    
    def get_stats(self) -> dict:
        """
        스케줄러 통계 반환
        
        Returns:
            통계 딕셔너리
        """
        return self.collection_stats.copy()


def initialize_components():
    """
    컴포넌트 초기화
    
    Returns:
        (adapters, normalizer, repository) 튜플
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 어댑터 임포트
    from adapters.garak import GarakAdapter
    from adapters.noryangjin import NoryangjinAdapter
    from normalizer import DataNormalizer
    
    # Core Service의 AliasMatcher와 Repository 임포트
    # 실제 구현 시 경로 조정 필요
    try:
        sys.path.append('../core-service')
        from app.aliases.matcher import AliasMatcher
        from app.database.price_repository import PriceRepository
    except ImportError as e:
        logger.error(f"Failed to import core-service modules: {e}")
        raise
    
    # 데이터베이스 연결
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://user:pass@localhost:5432/seafood"
    )
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # AliasMatcher 초기화
    alias_matcher = AliasMatcher(db)
    
    # DataNormalizer 초기화
    normalizer = DataNormalizer(alias_matcher)
    
    # PriceRepository 초기화
    repository = PriceRepository(db)
    
    # 어댑터 초기화
    adapters = []
    
    # 가락시장 어댑터
    garak_api_key = os.getenv("GARAK_API_KEY")
    if garak_api_key:
        adapters.append(GarakAdapter(garak_api_key))
        logger.info("Initialized GarakAdapter")
    else:
        logger.warning("GARAK_API_KEY not set, skipping GarakAdapter")
    
    # 노량진 어댑터
    noryangjin_url = os.getenv("NORYANGJIN_URL")
    adapters.append(NoryangjinAdapter(noryangjin_url))
    logger.info("Initialized NoryangjinAdapter")
    
    if not adapters:
        raise ValueError("No adapters initialized")
    
    return adapters, normalizer, repository


def main():
    """스케줄러 실행"""
    logger.info("Initializing Data Ingestion Scheduler...")
    
    try:
        # 컴포넌트 초기화
        adapters, normalizer, repository = initialize_components()
        
        # 스케줄러 생성
        scheduler = DataIngestionScheduler(adapters, normalizer, repository)
        
        # APScheduler 설정
        sched = BlockingScheduler()
        
        # 스케줄 시간 설정 (08:30, 11:30, 15:30)
        schedule_times = os.getenv("SCHEDULE_TIMES", "08:30,11:30,15:30").split(",")
        
        for time_str in schedule_times:
            time_str = time_str.strip()
            hour, minute = map(int, time_str.split(":"))
            sched.add_job(
                scheduler.run_collection,
                'cron',
                hour=hour,
                minute=minute,
                id=f'collection_{time_str.replace(":", "")}'
            )
            logger.info(f"Scheduled data collection at {time_str}")
        
        # 즉시 한 번 실행 (테스트용)
        if os.getenv("RUN_IMMEDIATELY", "false").lower() == "true":
            logger.info("Running collection immediately (RUN_IMMEDIATELY=true)")
            scheduler.run_collection()
        
        logger.info("Scheduler started successfully")
        logger.info("Press Ctrl+C to exit")
        sched.start()
        
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
