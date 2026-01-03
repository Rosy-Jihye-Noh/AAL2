"""
Scheduler Module - 자동화 작업 정의
백그라운드에서 주기적으로 실행되는 작업들
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Bidding, Shipment, Settlement, Contract, Notification, Customer, Forwarder
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    """Get database session for scheduler tasks"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def auto_expire_biddings():
    """
    마감일 지난 비딩 자동 expired 처리
    매 1시간마다 실행 권장
    """
    db = get_db()
    try:
        now = datetime.now()
        
        # 마감일 지난 open 상태 비딩 조회
        expired_biddings = db.query(Bidding).filter(
            Bidding.status == "open",
            Bidding.deadline < now,
            Bidding.deadline.isnot(None)
        ).all()
        
        count = 0
        for bidding in expired_biddings:
            bidding.status = "expired"
            
            # 관련 화주에게 알림
            quote_request = bidding.quote_request
            if quote_request and quote_request.customer_id:
                notification = Notification(
                    recipient_type="customer",
                    recipient_id=quote_request.customer_id,
                    notification_type="bidding_expired",
                    title="비딩이 마감되었습니다",
                    message=f"비딩번호 {bidding.bidding_no}의 입찰 마감 기한이 종료되었습니다.",
                    related_type="bidding",
                    related_id=bidding.id
                )
                db.add(notification)
            
            count += 1
        
        db.commit()
        logger.info(f"[Scheduler] Auto-expired {count} biddings")
        return count
        
    except Exception as e:
        db.rollback()
        logger.error(f"[Scheduler] Error in auto_expire_biddings: {e}")
        raise
    finally:
        db.close()


def check_delivery_reminders():
    """
    배송 확인 알림 처리
    - 7일 경과: 화주에게 알림 발송
    - 14일 경과: 자동 완료 처리
    매일 1회 실행 권장
    """
    db = get_db()
    try:
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)
        
        reminder_count = 0
        auto_complete_count = 0
        
        # === 7일 경과: 알림 발송 ===
        pending_7days = db.query(Shipment).filter(
            Shipment.current_status == "delivered",
            Shipment.delivery_confirmed == False,
            Shipment.actual_delivery <= seven_days_ago,
            Shipment.actual_delivery > fourteen_days_ago,
            Shipment.reminder_sent == False
        ).all()
        
        for shipment in pending_7days:
            # 화주에게 알림 발송
            contract = db.query(Contract).filter(Contract.id == shipment.contract_id).first()
            if contract:
                notification = Notification(
                    recipient_type="customer",
                    recipient_id=contract.customer_id,
                    notification_type="delivery_reminder",
                    title="배송 완료 확인 요청",
                    message=f"배송번호 {shipment.shipment_no}의 배송이 완료되었습니다. 7일 내 확인해주세요. 미확인 시 자동 완료 처리됩니다.",
                    related_type="shipment",
                    related_id=shipment.id
                )
                db.add(notification)
                
                # 알림 발송 표시
                shipment.reminder_sent = True
                shipment.reminder_sent_at = now
                reminder_count += 1
        
        # === 14일 경과: 자동 완료 ===
        pending_14days = db.query(Shipment).filter(
            Shipment.current_status == "delivered",
            Shipment.delivery_confirmed == False,
            Shipment.actual_delivery <= fourteen_days_ago
        ).all()
        
        for shipment in pending_14days:
            # 자동 완료 처리
            shipment.current_status = "completed"
            shipment.delivery_confirmed = True
            shipment.delivery_confirmed_at = now
            shipment.auto_confirmed = True
            
            # 계약 상태 업데이트
            contract = db.query(Contract).filter(Contract.id == shipment.contract_id).first()
            if contract:
                contract.status = "completed"
                
                # 정산 자동 생성 (없는 경우)
                existing_settlement = db.query(Settlement).filter(
                    Settlement.contract_id == contract.id
                ).first()
                
                if not existing_settlement:
                    settlement = Settlement(
                        settlement_no=f"ST-{now.strftime('%Y%m%d')}-{str(contract.id).zfill(3)}",
                        contract_id=contract.id,
                        forwarder_id=contract.forwarder_id,
                        customer_id=contract.customer_id,
                        total_amount_krw=contract.total_amount_krw,
                        service_fee=0,
                        net_amount=contract.total_amount_krw,
                        status="pending"
                    )
                    db.add(settlement)
                
                # 양측에게 알림
                notification_customer = Notification(
                    recipient_type="customer",
                    recipient_id=contract.customer_id,
                    notification_type="auto_delivery_confirmed",
                    title="배송이 자동 완료 처리되었습니다",
                    message=f"배송번호 {shipment.shipment_no}이 14일 경과로 자동 완료 처리되었습니다.",
                    related_type="shipment",
                    related_id=shipment.id
                )
                notification_forwarder = Notification(
                    recipient_type="forwarder",
                    recipient_id=contract.forwarder_id,
                    notification_type="auto_delivery_confirmed",
                    title="배송이 자동 완료 처리되었습니다",
                    message=f"배송번호 {shipment.shipment_no}이 14일 경과로 자동 완료 처리되었습니다. 정산을 진행해주세요.",
                    related_type="shipment",
                    related_id=shipment.id
                )
                db.add(notification_customer)
                db.add(notification_forwarder)
            
            auto_complete_count += 1
        
        db.commit()
        logger.info(f"[Scheduler] Sent {reminder_count} reminders, auto-completed {auto_complete_count} shipments")
        return {"reminders": reminder_count, "auto_completed": auto_complete_count}
        
    except Exception as e:
        db.rollback()
        logger.error(f"[Scheduler] Error in check_delivery_reminders: {e}")
        raise
    finally:
        db.close()


def check_dispute_deadlines():
    """
    분쟁 자동 처리
    - 분쟁 제기 후 7일간 포워더 무응답 시 화주 주장 인정
    - 분쟁 제기 후 30일간 미해결 시 관리자 알림
    매일 1회 실행 권장
    """
    db = get_db()
    try:
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        
        auto_resolve_count = 0
        admin_alert_count = 0
        
        # === 7일 무응답: 화주 주장 인정 ===
        no_response_disputes = db.query(Settlement).filter(
            Settlement.status == "disputed",
            Settlement.disputed_at <= seven_days_ago,
            Settlement.forwarder_response.is_(None),
            Settlement.resolved_at.is_(None)
        ).all()
        
        for settlement in no_response_disputes:
            # 화주 주장 인정 - 자동 해결
            settlement.status = "completed"
            settlement.resolved_at = now
            settlement.resolution_type = "auto_customer_favor"
            settlement.resolution_note = "포워더 7일 무응답으로 화주 주장 인정"
            
            # 양측 알림
            notification_customer = Notification(
                recipient_type="customer",
                recipient_id=settlement.customer_id,
                notification_type="dispute_auto_resolved",
                title="분쟁이 자동 해결되었습니다",
                message=f"정산번호 {settlement.settlement_no}의 분쟁이 포워더 무응답으로 귀하의 주장대로 해결되었습니다.",
                related_type="settlement",
                related_id=settlement.id
            )
            notification_forwarder = Notification(
                recipient_type="forwarder",
                recipient_id=settlement.forwarder_id,
                notification_type="dispute_auto_resolved",
                title="분쟁이 자동 해결되었습니다",
                message=f"정산번호 {settlement.settlement_no}의 분쟁이 7일 무응답으로 화주 주장대로 해결되었습니다.",
                related_type="settlement",
                related_id=settlement.id
            )
            db.add(notification_customer)
            db.add(notification_forwarder)
            auto_resolve_count += 1
        
        # === 30일 미해결: 관리자 알림 ===
        # (관리자 시스템이 있다면 여기서 알림)
        long_disputes = db.query(Settlement).filter(
            Settlement.status == "disputed",
            Settlement.disputed_at <= thirty_days_ago,
            Settlement.resolved_at.is_(None)
        ).count()
        
        if long_disputes > 0:
            logger.warning(f"[Scheduler] {long_disputes} disputes pending for over 30 days - admin attention needed")
            admin_alert_count = long_disputes
        
        db.commit()
        logger.info(f"[Scheduler] Auto-resolved {auto_resolve_count} disputes, {admin_alert_count} need admin attention")
        return {"auto_resolved": auto_resolve_count, "need_admin": admin_alert_count}
        
    except Exception as e:
        db.rollback()
        logger.error(f"[Scheduler] Error in check_dispute_deadlines: {e}")
        raise
    finally:
        db.close()


def run_all_scheduled_tasks():
    """모든 스케줄 작업 실행 (테스트/수동 실행용)"""
    logger.info("[Scheduler] Running all scheduled tasks...")
    
    results = {
        "expired_biddings": auto_expire_biddings(),
        "delivery_reminders": check_delivery_reminders(),
        "dispute_checks": check_dispute_deadlines()
    }
    
    logger.info(f"[Scheduler] All tasks completed: {results}")
    return results


if __name__ == "__main__":
    # 수동 실행 테스트
    run_all_scheduled_tasks()
