#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Epic 항생제 내성 시뮬레이터 실행 스크립트
"""

import subprocess
import sys
import os

def install_requirements():
    """필요한 패키지 설치"""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'scikit-learn'
    ]
    
    print("📦 필요한 패키지를 설치하는 중...")
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} 설치 완료")
        except subprocess.CalledProcessError:
            print(f"❌ {package} 설치 실패")
            return False
    return True

def run_streamlit_app():
    """Streamlit 애플리케이션 실행"""
    print("\n🚀 Epic 항생제 내성 시뮬레이터를 시작합니다...")
    print("📱 브라우저에서 http://localhost:8501 로 접속하세요")
    print("⏹️  종료하려면 Ctrl+C를 누르세요\n")
    
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'epic_web_hub.py'])
    except KeyboardInterrupt:
        print("\n👋 애플리케이션을 종료합니다.")
    except FileNotFoundError:
        print("❌ epic_web_hub.py 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    print("🏆 Epic 항생제 내성 시뮬레이터 런처")
    print("=" * 50)
    
    # 패키지 설치
    if install_requirements():
        print("\n✅ 모든 패키지 설치 완료!")
        # Streamlit 앱 실행
        run_streamlit_app()
    else:
        print("\n❌ 패키지 설치에 실패했습니다.")
        sys.exit(1)
