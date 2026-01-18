"""
사용자 관리 스크립트
"""
import hashlib
import json
import os

USER_FILE = "users.json"

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """사용자 로드"""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """사용자 저장"""
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def add_user(username: str, password: str, role: str = "user"):
    """사용자 추가"""
    users = load_users()
    
    if username in users:
        print(f"⚠️  사용자 '{username}'이 이미 존재합니다.")
        response = input("덮어쓰시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("취소되었습니다.")
            return
    
    users[username] = {
        "password_hash": hash_password(password),
        "role": role,
        "created_at": str(datetime.now())
    }
    save_users(users)
    print(f"✅ 사용자 '{username}' ({role}) 추가 완료")

def remove_user(username: str):
    """사용자 삭제"""
    users = load_users()
    
    if username not in users:
        print(f"❌ 사용자 '{username}'을 찾을 수 없습니다.")
        return
    
    del users[username]
    save_users(users)
    print(f"✅ 사용자 '{username}' 삭제 완료")

def list_users():
    """사용자 목록"""
    users = load_users()
    
    if not users:
        print("📋 등록된 사용자가 없습니다.")
        return
    
    print("\n📋 등록된 사용자:")
    print("-" * 50)
    for username, info in users.items():
        role = info.get('role', 'user')
        created = info.get('created_at', 'N/A')
        print(f"  👤 {username:15} | 역할: {role:10} | 생성: {created[:10]}")
    print("-" * 50)
    print(f"총 {len(users)}명\n")

def change_password(username: str, new_password: str):
    """비밀번호 변경"""
    users = load_users()
    
    if username not in users:
        print(f"❌ 사용자 '{username}'을 찾을 수 없습니다.")
        return
    
    users[username]["password_hash"] = hash_password(new_password)
    save_users(users)
    print(f"✅ 사용자 '{username}'의 비밀번호가 변경되었습니다.")

if __name__ == "__main__":
    import sys
    from datetime import datetime
    
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════╗
║           이광수 AI - 사용자 관리 도구                    ║
╚══════════════════════════════════════════════════════════╝

사용법:
  python manage_users.py add <username> <password> [role]
    → 새 사용자 추가 (role: admin 또는 user, 기본값: user)
    
  python manage_users.py remove <username>
    → 사용자 삭제
    
  python manage_users.py list
    → 전체 사용자 목록 보기
    
  python manage_users.py passwd <username> <new_password>
    → 비밀번호 변경

예시:
  python manage_users.py add teacher1 secure_pass admin
  python manage_users.py add student1 pass1234
  python manage_users.py list
  python manage_users.py passwd student1 new_pass
  python manage_users.py remove student1
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "add":
            if len(sys.argv) < 4:
                print("❌ 사용법: python manage_users.py add <username> <password> [role]")
                sys.exit(1)
            username = sys.argv[2]
            password = sys.argv[3]
            role = sys.argv[4] if len(sys.argv) > 4 else "user"
            add_user(username, password, role)
            
        elif command == "remove":
            if len(sys.argv) < 3:
                print("❌ 사용법: python manage_users.py remove <username>")
                sys.exit(1)
            username = sys.argv[2]
            remove_user(username)
            
        elif command == "list":
            list_users()
            
        elif command == "passwd":
            if len(sys.argv) < 4:
                print("❌ 사용법: python manage_users.py passwd <username> <new_password>")
                sys.exit(1)
            username = sys.argv[2]
            new_password = sys.argv[3]
            change_password(username, new_password)
            
        else:
            print(f"❌ 알 수 없는 명령: {command}")
            print("사용 가능한 명령: add, remove, list, passwd")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
