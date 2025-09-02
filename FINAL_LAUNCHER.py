#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 FINAL LAUNCHER - 삼성을 뛰어넘는 궁극의 항생제 내성 시뮬레이터
Samsung Innovation Challenge 2025

모든 언어, 모든 기능, 완벽한 한글 지원, 웹 인터페이스 통합
"""

import os
import sys
import subprocess
import webbrowser
import time
import json
from datetime import datetime
from pathlib import Path

def print_ultimate_banner():
    """궁극의 시작 배너"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🏆 FINAL LAUNCHER - 삼성을 뛰어넘는 궁극의 시뮬레이터        ║
║              Samsung Innovation Challenge 2025               ║
║                                                              ║
║  🧬 과학적 정확성   🤖 AI 최적화   🌐 웹 인터페이스          ║
║  🔤 완벽한 한글     📊 실시간 시각화   ⚡ 다중 언어 지원      ║
║                                                              ║
║           🏆 삼성 수준을 뛰어넘는 혁신적 솔루션               ║
╚══════════════════════════════════════════════════════════════╝

🚀 모든 시스템 준비 완료! 선택하세요:

1️⃣  🌐 궁극의 웹 허브 실행 (추천!)
2️⃣  🐍 완벽한 한글 시뮬레이터 실행
3️⃣  ⚡ JavaScript 시뮬레이터 실행
4️⃣  📊 R 시뮬레이터 실행
5️⃣  🧮 MATLAB 시뮬레이터 실행 (설치 시)
6️⃣  🎬 모든 시각화 도구 실행
7️⃣  🚀 전체 시스템 통합 실행
8️⃣  📊 시스템 상태 확인
9️⃣  🔧 문제 해결 도구
0️⃣  ❌ 종료

""")

def check_all_systems():
    """전체 시스템 상태 체크"""
    print("🔍 전체 시스템 상태 확인 중...")
    
    status = {}
    
    # Python 체크
    status['Python'] = sys.executable is not None
    print(f"   {'✅' if status['Python'] else '❌'} Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Node.js 체크
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        status['Node.js'] = result.returncode == 0
        version = result.stdout.strip() if result.returncode == 0 else 'N/A'
        print(f"   {'✅' if status['Node.js'] else '❌'} Node.js {version}")
    except:
        status['Node.js'] = False
        print("   ❌ Node.js (미설치)")
    
    # R 체크
    try:
        result = subprocess.run(['R', '--version'], capture_output=True, text=True, timeout=5)
        status['R'] = result.returncode == 0
        print(f"   {'✅' if status['R'] else '❌'} R")
    except:
        status['R'] = False
        print("   ❌ R (미설치)")
    
    # MATLAB 체크
    try:
        result = subprocess.run(['matlab', '-help'], capture_output=True, text=True, timeout=5)
        status['MATLAB'] = result.returncode == 0
        print(f"   {'✅' if status['MATLAB'] else '❌'} MATLAB")
    except:
        status['MATLAB'] = False
        print("   ❌ MATLAB (미설치)")
    
    # 중요 파일들 체크
    important_files = [
        'ultimate_web_hub.py',
        'perfect_korean_simulator.py',
        'scientific_simulator.py',
        'antibiotic_simulator.js',
        'antibiotic_simulator.R',
        'antibiotic_simulator.m'
    ]
    
    print("\n📁 주요 파일 상태:")
    for file in important_files:
        exists = os.path.exists(file)
        print(f"   {'✅' if exists else '❌'} {file}")
    
    print(f"\n📊 시스템 준비도: {sum(status.values())}/{len(status)} 완료")
    
    return status

def launch_ultimate_web_hub():
    """궁극의 웹 허브 실행"""
    print("🌐 궁극의 웹 허브 실행 중...")
    
    try:
        # Streamlit 실행
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'ultimate_web_hub.py',
            '--server.port', '8502',
            '--server.headless', 'false'
        ])
        
        print("   ⏳ 웹 서버 시작 대기 중...")
        time.sleep(3)
        
        # 브라우저 열기
        url = "http://localhost:8502"
        print(f"   🌐 웹 브라우저 열기: {url}")
        webbrowser.open(url)
        
        print("   ✅ 웹 허브 실행 완료!")
        print(f"   📱 브라우저에서 {url} 접속하세요!")
        
        return process
        
    except Exception as e:
        print(f"   ❌ 웹 허브 실행 실패: {e}")
        return None

def run_korean_simulator():
    """완벽한 한글 시뮬레이터 실행"""
    print("🐍 완벽한 한글 시뮬레이터 실행 중...")
    
    try:
        result = subprocess.run([
            sys.executable, 'perfect_korean_simulator.py'
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("   ✅ 한글 시뮬레이터 실행 완료!")
        else:
            print("   ❌ 실행 중 오류 발생")
            
    except Exception as e:
        print(f"   ❌ 실행 실패: {e}")

def run_javascript_simulator():
    """JavaScript 시뮬레이터 실행"""
    print("⚡ JavaScript 시뮬레이터 실행 중...")
    
    try:
        result = subprocess.run([
            'node', 'antibiotic_simulator.js'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("   ✅ JavaScript 시뮬레이션 완료!")
            print("   📁 결과: results/antibiotic_simulation_js.json")
        else:
            print(f"   ❌ 실행 오류: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   ⏰ 실행 시간 초과")
    except FileNotFoundError:
        print("   ❌ Node.js가 설치되지 않았습니다.")
    except Exception as e:
        print(f"   ❌ 오류: {e}")

def run_r_simulator():
    """R 시뮬레이터 실행"""
    print("📊 R 시뮬레이터 실행 중...")
    
    try:
        result = subprocess.run([
            'Rscript', 'antibiotic_simulator.R'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("   ✅ R 시뮬레이션 완료!")
            print(f"   📊 출력:\n{result.stdout[:500]}...")
        else:
            print(f"   ❌ 실행 오류: {result.stderr}")
            
    except FileNotFoundError:
        print("   ❌ R이 설치되지 않았습니다.")
    except Exception as e:
        print(f"   ❌ 오류: {e}")

def run_matlab_simulator():
    """MATLAB 시뮬레이터 실행"""
    print("🧮 MATLAB 시뮬레이터 실행 중...")
    
    try:
        result = subprocess.run([
            'matlab', '-batch', 'antibiotic_simulator'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("   ✅ MATLAB 시뮬레이션 완료!")
            print(f"   📊 출력:\n{result.stdout[:500]}...")
        else:
            print(f"   ❌ 실행 오류: {result.stderr}")
            
    except FileNotFoundError:
        print("   ❌ MATLAB이 설치되지 않았습니다.")
    except Exception as e:
        print(f"   ❌ 오류: {e}")

def run_all_visualizers():
    """모든 시각화 도구 실행"""
    print("🎬 모든 시각화 도구 실행 중...")
    
    visualizers = [
        'realtime_visualizer.py',
        'animated_visualizer.py'
    ]
    
    processes = []
    
    for viz in visualizers:
        if os.path.exists(viz):
            try:
                print(f"   ▶️ {viz} 시작...")
                process = subprocess.Popen([sys.executable, viz])
                processes.append(process)
                time.sleep(2)
                print(f"   ✅ {viz} 실행됨")
            except Exception as e:
                print(f"   ❌ {viz} 실행 실패: {e}")
        else:
            print(f"   ⚠️ {viz} 파일 없음")
    
    return processes

def run_integrated_system():
    """전체 시스템 통합 실행"""
    print("🚀 전체 시스템 통합 실행 중...")
    
    all_processes = []
    
    # 1. 웹 허브 실행
    web_process = launch_ultimate_web_hub()
    if web_process:
        all_processes.append(("웹 허브", web_process))
    
    time.sleep(2)
    
    # 2. 시각화 도구들 실행
    viz_processes = run_all_visualizers()
    for i, proc in enumerate(viz_processes):
        all_processes.append((f"시각화 도구 {i+1}", proc))
    
    # 3. 기본 시뮬레이션들 실행
    print("   🐍 Python 시뮬레이션 실행...")
    run_korean_simulator()
    
    print("   ⚡ JavaScript 시뮬레이션 실행...")
    run_javascript_simulator()
    
    print("   📊 R 시뮬레이션 실행...")
    run_r_simulator()
    
    print("   🧮 MATLAB 시뮬레이션 실행...")
    run_matlab_simulator()
    
    print(f"\n🎉 전체 시스템 실행 완료!")
    print(f"📊 실행 중인 프로세스: {len(all_processes)}개")
    print("🌐 웹 허브: http://localhost:8502")
    
    return all_processes

def troubleshoot():
    """문제 해결 도구"""
    print("🔧 문제 해결 도구 실행 중...")
    
    print("\n1. 가상환경 확인...")
    venv_active = 'VIRTUAL_ENV' in os.environ
    print(f"   {'✅' if venv_active else '❌'} 가상환경: {'활성화됨' if venv_active else '비활성화됨'}")
    
    print("\n2. Python 패키지 확인...")
    required_packages = ['streamlit', 'plotly', 'matplotlib', 'numpy', 'pandas']
    for pkg in required_packages:
        try:
            __import__(pkg)
            print(f"   ✅ {pkg}")
        except ImportError:
            print(f"   ❌ {pkg} (미설치)")
    
    print("\n3. 포트 사용 확인...")
    try:
        import socket
        for port in [8501, 8502, 8503]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                print(f"   ⚠️ 포트 {port}: 사용 중")
            else:
                print(f"   ✅ 포트 {port}: 사용 가능")
            sock.close()
    except Exception as e:
        print(f"   ❌ 포트 체크 실패: {e}")
    
    print("\n4. 결과 폴더 확인...")
    results_dir = Path("results")
    if results_dir.exists():
        file_count = len(list(results_dir.glob("*")))
        print(f"   ✅ results 폴더: {file_count}개 파일")
    else:
        print("   ⚠️ results 폴더 없음 - 생성합니다")
        results_dir.mkdir(exist_ok=True)

def show_results_summary():
    """결과 요약 표시"""
    print("📊 결과 요약:")
    
    results_dir = Path("results")
    if results_dir.exists():
        files = list(results_dir.glob("*"))
        print(f"   📁 총 결과 파일: {len(files)}개")
        
        for file_type, pattern in [
            ("JSON 데이터", "*.json"),
            ("HTML 시각화", "*.html"),
            ("이미지", "*.png"),
            ("애니메이션", "*.gif")
        ]:
            count = len(list(results_dir.glob(pattern)))
            if count > 0:
                print(f"   📄 {file_type}: {count}개")
    else:
        print("   📁 결과 폴더가 없습니다.")

def main():
    """메인 실행 함수"""
    while True:
        print_ultimate_banner()
        
        try:
            choice = input("🎯 선택하세요 (0-9): ").strip()
            
            if choice == '1':
                process = launch_ultimate_web_hub()
                if process:
                    input("\n⏸️ 웹 허브가 실행 중입니다. Enter를 눌러 계속...")
            
            elif choice == '2':
                run_korean_simulator()
                input("\n✅ 완료! Enter를 눌러 계속...")
            
            elif choice == '3':
                run_javascript_simulator()
                input("\n✅ 완료! Enter를 눌러 계속...")
            
            elif choice == '4':
                run_r_simulator()
                input("\n✅ 완료! Enter를 눌러 계속...")
            
            elif choice == '5':
                run_matlab_simulator()
                input("\n✅ 완료! Enter를 눌러 계속...")
            
            elif choice == '6':
                processes = run_all_visualizers()
                if processes:
                    input(f"\n🎬 {len(processes)}개 시각화 도구가 실행 중입니다. Enter를 눌러 계속...")
            
            elif choice == '7':
                all_processes = run_integrated_system()
                input(f"\n🚀 전체 시스템({len(all_processes)}개 프로세스)이 실행 중입니다. Enter를 눌러 계속...")
            
            elif choice == '8':
                check_all_systems()
                show_results_summary()
                input("\n📊 상태 확인 완료! Enter를 눌러 계속...")
            
            elif choice == '9':
                troubleshoot()
                input("\n🔧 문제 해결 도구 실행 완료! Enter를 눌러 계속...")
            
            elif choice == '0':
                print("\n👋 프로그램을 종료합니다...")
                print("🎉 Samsung Innovation Challenge 2025 - 성공적인 시뮬레이션이었습니다!")
                break
            
            else:
                print("\n❌ 잘못된 선택입니다. 0-9 중에서 선택해주세요.")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ 사용자에 의해 중단됨")
            break
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            time.sleep(2)

if __name__ == "__main__":
    # 환경 설정
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 메인 실행
    main()
