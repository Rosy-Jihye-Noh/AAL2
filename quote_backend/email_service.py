"""
Email Service - 이메일 알림 서비스
실제 배포 시 SMTP 설정 필요
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import logging
import os

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수에서 SMTP 설정 로드
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@aallogistics.com")
FROM_NAME = os.getenv("FROM_NAME", "AAL Logistics Platform")

# 개발 모드 (실제 이메일 발송 안함)
DEV_MODE = os.getenv("EMAIL_DEV_MODE", "true").lower() == "true"


class EmailTemplate:
    """이메일 템플릿 정의"""
    
    @staticmethod
    def base_template(content: str, title: str = "AAL Logistics") -> str:
        """기본 이메일 템플릿"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
        .footer {{ background: #f9fafb; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; margin: 15px 0; }}
        .button:hover {{ background: #2563eb; }}
        .info-box {{ background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0; }}
        .warning-box {{ background: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; }}
        .success-box {{ background: #f0fdf4; border-left: 4px solid #22c55e; padding: 15px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            <p>본 메일은 AAL Logistics 플랫폼에서 자동 발송되었습니다.</p>
            <p>문의: support@aallogistics.com</p>
        </div>
    </div>
</body>
</html>
"""
    
    @staticmethod
    def bidding_created(customer_name: str, bidding_no: str, cargo_type: str, pol: str, pod: str, deadline: str) -> str:
        """비딩 생성 알림 (화주용)"""
        content = f"""
        <h2>견적 요청이 등록되었습니다</h2>
        <p>안녕하세요, {customer_name}님!</p>
        <p>귀하의 견적 요청이 성공적으로 등록되었습니다.</p>
        
        <div class="info-box">
            <p><strong>비딩 번호:</strong> {bidding_no}</p>
            <p><strong>화물 유형:</strong> {cargo_type}</p>
            <p><strong>출발지:</strong> {pol}</p>
            <p><strong>도착지:</strong> {pod}</p>
            <p><strong>입찰 마감:</strong> {deadline}</p>
        </div>
        
        <p>포워더들이 입찰에 참여하면 알림을 보내드립니다.</p>
        
        <a href="#" class="button">비딩 상세 보기</a>
        """
        return EmailTemplate.base_template(content, "견적 요청 등록 완료")
    
    @staticmethod
    def new_bid_received(customer_name: str, bidding_no: str, bid_count: int) -> str:
        """새 입찰 알림 (화주용)"""
        content = f"""
        <h2>새로운 입찰이 도착했습니다</h2>
        <p>안녕하세요, {customer_name}님!</p>
        
        <div class="success-box">
            <p><strong>비딩 번호:</strong> {bidding_no}</p>
            <p><strong>현재 입찰 수:</strong> {bid_count}건</p>
        </div>
        
        <p>마감 후 입찰 내역을 확인하고 운송사를 선정하실 수 있습니다.</p>
        
        <a href="#" class="button">비딩 현황 보기</a>
        """
        return EmailTemplate.base_template(content, "새 입찰 도착")
    
    @staticmethod
    def bid_awarded(forwarder_name: str, bidding_no: str, cargo_type: str, pol: str, pod: str, amount: str) -> str:
        """낙찰 알림 (포워더용)"""
        content = f"""
        <h2>🎉 축하합니다! 입찰에 선정되셨습니다</h2>
        <p>안녕하세요, {forwarder_name}님!</p>
        <p>귀사가 다음 운송 건에 선정되셨습니다.</p>
        
        <div class="success-box">
            <p><strong>비딩 번호:</strong> {bidding_no}</p>
            <p><strong>화물 유형:</strong> {cargo_type}</p>
            <p><strong>출발지:</strong> {pol}</p>
            <p><strong>도착지:</strong> {pod}</p>
            <p><strong>낙찰 금액:</strong> {amount}</p>
        </div>
        
        <p>계약 확인을 진행해주세요.</p>
        
        <a href="#" class="button">계약 확인하기</a>
        """
        return EmailTemplate.base_template(content, "입찰 선정 알림")
    
    @staticmethod
    def delivery_reminder(customer_name: str, shipment_no: str, delivered_date: str, days_left: int) -> str:
        """배송 완료 확인 요청 (화주용)"""
        content = f"""
        <h2>배송 완료 확인을 요청드립니다</h2>
        <p>안녕하세요, {customer_name}님!</p>
        
        <div class="warning-box">
            <p><strong>배송 번호:</strong> {shipment_no}</p>
            <p><strong>배송 완료일:</strong> {delivered_date}</p>
            <p><strong>자동 완료까지:</strong> {days_left}일</p>
        </div>
        
        <p>배송을 확인하시고 완료 처리해주세요. 미확인 시 14일 후 자동 완료 처리됩니다.</p>
        
        <a href="#" class="button">배송 확인하기</a>
        """
        return EmailTemplate.base_template(content, "배송 완료 확인 요청")
    
    @staticmethod
    def settlement_dispute(recipient_name: str, settlement_no: str, dispute_reason: str, is_forwarder: bool = True) -> str:
        """분쟁 알림"""
        if is_forwarder:
            content = f"""
            <h2>정산 분쟁이 제기되었습니다</h2>
            <p>안녕하세요, {recipient_name}님!</p>
            
            <div class="warning-box">
                <p><strong>정산 번호:</strong> {settlement_no}</p>
                <p><strong>분쟁 사유:</strong></p>
                <p>{dispute_reason}</p>
            </div>
            
            <p>7일 이내에 응답해주세요. 미응답 시 화주 주장이 인정됩니다.</p>
            
            <a href="#" class="button">분쟁 응답하기</a>
            """
        else:
            content = f"""
            <h2>분쟁이 접수되었습니다</h2>
            <p>안녕하세요, {recipient_name}님!</p>
            
            <div class="info-box">
                <p><strong>정산 번호:</strong> {settlement_no}</p>
                <p><strong>분쟁 사유:</strong></p>
                <p>{dispute_reason}</p>
            </div>
            
            <p>포워더의 응답을 기다려주세요. 진행 상황은 알림으로 안내드립니다.</p>
            
            <a href="#" class="button">분쟁 현황 보기</a>
            """
        return EmailTemplate.base_template(content, "정산 분쟁 알림")
    
    @staticmethod
    def dispute_resolved(recipient_name: str, settlement_no: str, resolution_type: str, resolution_note: str, final_amount: str) -> str:
        """분쟁 해결 알림"""
        resolution_labels = {
            "agreement": "양측 합의",
            "mediation": "관리자 중재",
            "auto_customer_favor": "자동 처리 (포워더 무응답)",
            "cancel": "취소"
        }
        
        content = f"""
        <h2>분쟁이 해결되었습니다</h2>
        <p>안녕하세요, {recipient_name}님!</p>
        
        <div class="success-box">
            <p><strong>정산 번호:</strong> {settlement_no}</p>
            <p><strong>해결 유형:</strong> {resolution_labels.get(resolution_type, resolution_type)}</p>
            <p><strong>해결 내용:</strong></p>
            <p>{resolution_note}</p>
            <p><strong>최종 정산 금액:</strong> {final_amount}</p>
        </div>
        
        <a href="#" class="button">정산 상세 보기</a>
        """
        return EmailTemplate.base_template(content, "분쟁 해결 알림")


class EmailService:
    """이메일 발송 서비스"""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        cc: Optional[List[str]] = None
    ) -> bool:
        """이메일 발송"""
        
        if DEV_MODE:
            logger.info(f"[DEV MODE] Email would be sent to: {to_email}")
            logger.info(f"[DEV MODE] Subject: {subject}")
            logger.debug(f"[DEV MODE] Content: {html_content[:200]}...")
            return True
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
            msg["To"] = to_email
            
            if cc:
                msg["Cc"] = ", ".join(cc)
            
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)
            
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                
                server.sendmail(FROM_EMAIL, recipients, msg.as_string())
            
            logger.info(f"Email sent successfully to: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    @classmethod
    def send_bidding_created(cls, to_email: str, customer_name: str, bidding_no: str, 
                              cargo_type: str, pol: str, pod: str, deadline: str) -> bool:
        """비딩 생성 알림 발송"""
        html = EmailTemplate.bidding_created(customer_name, bidding_no, cargo_type, pol, pod, deadline)
        return cls.send_email(to_email, f"[AAL] 견적 요청 등록 완료 - {bidding_no}", html)
    
    @classmethod
    def send_new_bid_notification(cls, to_email: str, customer_name: str, 
                                   bidding_no: str, bid_count: int) -> bool:
        """새 입찰 알림 발송"""
        html = EmailTemplate.new_bid_received(customer_name, bidding_no, bid_count)
        return cls.send_email(to_email, f"[AAL] 새 입찰 도착 - {bidding_no}", html)
    
    @classmethod
    def send_bid_awarded(cls, to_email: str, forwarder_name: str, bidding_no: str,
                          cargo_type: str, pol: str, pod: str, amount: str) -> bool:
        """낙찰 알림 발송"""
        html = EmailTemplate.bid_awarded(forwarder_name, bidding_no, cargo_type, pol, pod, amount)
        return cls.send_email(to_email, f"[AAL] 🎉 입찰 선정 알림 - {bidding_no}", html)
    
    @classmethod
    def send_delivery_reminder(cls, to_email: str, customer_name: str, 
                                shipment_no: str, delivered_date: str, days_left: int) -> bool:
        """배송 확인 요청 발송"""
        html = EmailTemplate.delivery_reminder(customer_name, shipment_no, delivered_date, days_left)
        return cls.send_email(to_email, f"[AAL] 배송 완료 확인 요청 - {shipment_no}", html)
    
    @classmethod
    def send_dispute_notification(cls, to_email: str, recipient_name: str,
                                   settlement_no: str, dispute_reason: str, 
                                   is_forwarder: bool = True) -> bool:
        """분쟁 알림 발송"""
        html = EmailTemplate.settlement_dispute(recipient_name, settlement_no, dispute_reason, is_forwarder)
        subject = f"[AAL] 정산 분쟁 {'제기' if is_forwarder else '접수'} - {settlement_no}"
        return cls.send_email(to_email, subject, html)
    
    @classmethod
    def send_dispute_resolved(cls, to_email: str, recipient_name: str,
                               settlement_no: str, resolution_type: str,
                               resolution_note: str, final_amount: str) -> bool:
        """분쟁 해결 알림 발송"""
        html = EmailTemplate.dispute_resolved(recipient_name, settlement_no, resolution_type, resolution_note, final_amount)
        return cls.send_email(to_email, f"[AAL] 분쟁 해결 완료 - {settlement_no}", html)


# 테스트
if __name__ == "__main__":
    # 개발 모드 테스트
    print("Testing Email Templates...")
    
    # 템플릿 테스트
    html = EmailTemplate.bidding_created(
        "홍길동", "BID-20260103-001", "FCL", "KRPUS", "USLAX", "2026-01-10"
    )
    print("Bidding Created Template Generated")
    
    html = EmailTemplate.delivery_reminder(
        "홍길동", "SH-20260103-001", "2025-12-27", 7
    )
    print("Delivery Reminder Template Generated")
    
    html = EmailTemplate.settlement_dispute(
        "AAL물류", "ST-20260103-001", "화물 파손 발생. 검수 보고서 첨부.", True
    )
    print("Dispute Notification Template Generated")
    
    print("\nAll templates generated successfully!")
