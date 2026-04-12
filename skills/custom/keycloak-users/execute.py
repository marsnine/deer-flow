#!/usr/bin/env python3
"""
Keycloak 사용자 조회 스킬 실행 코드
"""

import subprocess
import sys
from datetime import datetime

def execute_keycloak_users_query():
    """
    Keycloak에 등록된 사용자 목록을 조회합니다.
    """
    
    # SQL 쿼리
    sql_query = """
    SELECT 
        username, 
        email, 
        first_name, 
        last_name, 
        enabled, 
        to_char(to_timestamp(created_timestamp/1000), 'YYYY-MM-DD HH24:MI:SS') as created_date 
    FROM user_entity 
    ORDER BY created_timestamp;
    """
    
    # 요약 정보 쿼리
    summary_queries = [
        "SELECT '총 사용자 수: ' || COUNT(*) || '명' FROM user_entity;",
        "SELECT '활성 사용자: ' || COUNT(*) || '명' FROM user_entity WHERE enabled = true;",
        "SELECT '비활성 사용자: ' || COUNT(*) || '명' FROM user_entity WHERE enabled = false;",
        "SELECT '가장 최근 생성: ' || username || ' (' || to_char(to_timestamp(created_timestamp/1000), 'YYYY-MM-DD HH24:MI:SS') || ')' FROM user_entity ORDER BY created_timestamp DESC LIMIT 1;"
    ]
    
    print("🔍 Keycloak에 등록된 사용자 목록 조회 중...\n")
    
    try:
        # 메인 쿼리 실행
        result = subprocess.run(
            ["docker", "exec", "startcloud-postgres", "psql", "-U", "startcloud", "-d", "keycloak", "-c", sql_query],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(result.stdout)
        
        # 요약 정보 출력
        print("📊 요약 정보")
        print("-----------")
        
        for query in summary_queries:
            summary_result = subprocess.run(
                ["docker", "exec", "startcloud-postgres", "psql", "-U", "startcloud", "-d", "keycloak", "-t", "-c", query],
                capture_output=True,
                text=True,
                check=True
            )
            print(summary_result.stdout.strip())
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 오류 발생: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def format_user_list():
    """
    사용자 목록을 보기 좋은 형식으로 포맷팅합니다.
    """
    
    # SQL 쿼리 - 포맷팅된 결과를 위한 쿼리
    sql_query = """
    SELECT 
        ROW_NUMBER() OVER (ORDER BY created_timestamp) as 번호,
        username as 사용자명, 
        COALESCE(email, '-') as 이메일, 
        COALESCE(first_name, '-') as 이름, 
        COALESCE(last_name, '-') as 성, 
        CASE WHEN enabled THEN '활성' ELSE '비활성' END as 상태, 
        to_char(to_timestamp(created_timestamp/1000), 'YYYY-MM-DD HH24:MI:SS') as 생성일 
    FROM user_entity 
    ORDER BY created_timestamp;
    """
    
    print("🔍 Keycloak에 등록된 사용자 목록\n")
    
    try:
        # 포맷팅된 쿼리 실행
        result = subprocess.run(
            ["docker", "exec", "startcloud-postgres", "psql", "-U", "startcloud", "-d", "keycloak", "-c", sql_query],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(result.stdout)
        
        # 추가 정보
        print("\n📋 사용자 계정 상세 정보")
        print("=" * 50)
        
        # 각 사용자별 상세 정보 조회
        detail_query = """
        SELECT 
            username,
            COALESCE(email, '없음') as email,
            COALESCE(first_name, '없음') as first_name,
            COALESCE(last_name, '없음') as last_name,
            CASE WHEN enabled THEN '활성화됨 ✅' ELSE '비활성화됨 ❌' END as status,
            to_char(to_timestamp(created_timestamp/1000), 'YYYY년 MM월 DD일 HH24시 MI분 SS초') as created_date_korean
        FROM user_entity 
        ORDER BY created_timestamp;
        """
        
        detail_result = subprocess.run(
            ["docker", "exec", "startcloud-postgres", "psql", "-U", "startcloud", "-d", "keycloak", "-t", "-c", detail_query],
            capture_output=True,
            text=True,
            check=True
        )
        
        users = detail_result.stdout.strip().split('\n')
        user_count = 1
        
        for user in users:
            if user.strip():
                parts = user.strip().split('|')
                if len(parts) >= 6:
                    username, email, first_name, last_name, status, created_date = [part.strip() for part in parts]
                    
                    print(f"\n{user_count}. **{username}**")
                    print(f"   - **이메일**: {email}")
                    print(f"   - **이름**: {first_name}")
                    print(f"   - **성**: {last_name}")
                    print(f"   - **상태**: {status}")
                    print(f"   - **생성일**: {created_date}")
                    
                    # 계정 유형 판별
                    if 'service-account' in username:
                        print(f"   - **계정 유형**: 서비스 계정 🔧")
                    elif username == 'admin':
                        print(f"   - **계정 유형**: 관리자 계정 👑")
                    else:
                        print(f"   - **계정 유형**: 일반 사용자 계정 👤")
                    
                    user_count += 1
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 오류 발생: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def main():
    """
    메인 함수
    """
    print("=" * 60)
    print("Keycloak 사용자 조회 스킬 실행")
    print("=" * 60)
    
    # 실행 옵션 확인
    if len(sys.argv) > 1 and sys.argv[1] == "--format":
        success = format_user_list()
    else:
        success = execute_keycloak_users_query()
    
    if success:
        print("\n✅ Keycloak 사용자 조회가 완료되었습니다.")
    else:
        print("\n❌ Keycloak 사용자 조회 중 오류가 발생했습니다.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())