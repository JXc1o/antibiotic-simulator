#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 시뮬레이터 통합 실행기
Samsung Innovation Challenge 2025

한 번에 모든 언어의 시뮬레이터를 실행하는 런처
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path
import json

def print_banner():
    """시작 배너 출력"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🧬 항생제 내성 진화 AI 시뮬레이터 허브              ║
║                Samsung Innovation Challenge 2025              ║
║                                                              ║
║  🎯 모든 언어 지원 | 🌐 웹 인터페이스 | 📊 실시간 시각화      ║
╚══════════════════════════════════════════════════════════════╝

🚀 통합 실행 시작...
    """)

def check_requirements():
    """필요한 도구들 확인"""
    print("🔍 환경 확인 중...")
    
    requirements = {}
    
    # Python 확인
    requirements['python'] = sys.executable is not None
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}" if requirements['python'] else "   ❌ Python")
    
    # Node.js 확인
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        requirements['nodejs'] = result.returncode == 0
        if requirements['nodejs']:
            print(f"   ✅ Node.js {result.stdout.strip()}")
        else:
            print("   ❌ Node.js")
    except:
        requirements['nodejs'] = False
        print("   ❌ Node.js (미설치)")
    
    # R 확인
    try:
        result = subprocess.run(['Rscript', '--version'], capture_output=True, text=True)
        requirements['r'] = result.returncode == 0
        print("   ✅ R" if requirements['r'] else "   ❌ R")
    except:
        requirements['r'] = False
        print("   ❌ R (미설치)")
    
    # MATLAB 확인  
    try:
        result = subprocess.run(['matlab', '-help'], capture_output=True, text=True, timeout=5)
        requirements['matlab'] = result.returncode == 0
        print("   ✅ MATLAB" if requirements['matlab'] else "   ❌ MATLAB")
    except:
        requirements['matlab'] = False
        print("   ❌ MATLAB (미설치)")
    
    return requirements

def run_python_simulators():
    """Python 시뮬레이터들 실행"""
    print("\n🐍 Python 시뮬레이터 실행 중...")
    
    python_scripts = [
        ("과학적 정확도 시뮬레이터", "scientific_simulator.py"),
        ("기본 시뮬레이터", "antibiotic_simulator_clean.py"),
        ("고급 시뮬레이터", "antibiotic_simulator_full.py")
    ]
    
    processes = []
    
    for name, script in python_scripts:
        if os.path.exists(script):
            print(f"   ▶️ {name} 시작...")
            try:
                # 백그라운드에서 실행
                process = subprocess.Popen([
                    sys.executable, script
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                processes.append((name, process))
                time.sleep(1)  # 순차적 시작
            except Exception as e:
                print(f"   ❌ {name} 실행 실패: {e}")
        else:
            print(f"   ⚠️ {script} 파일이 없습니다.")
    
    return processes

def run_javascript_simulator():
    """JavaScript 시뮬레이터 실행"""
    print("\n⚡ JavaScript 시뮬레이터 실행 중...")
    
    if os.path.exists("antibiotic_simulator.js"):
        try:
            print("   ▶️ Node.js 시뮬레이터 시작...")
            result = subprocess.run([
                'node', 'antibiotic_simulator.js'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("   ✅ JavaScript 시뮬레이션 완료!")
                return True
            else:
                print(f"   ❌ JavaScript 실행 오류: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("   ⏰ JavaScript 실행 시간 초과")
            return False
        except FileNotFoundError:
            print("   ❌ Node.js가 설치되지 않았습니다.")
            return False
    else:
        print("   ⚠️ antibiotic_simulator.js 파일이 없습니다.")
        return False

def run_r_simulator():
    """R 시뮬레이터 실행"""
    print("\n📊 R 시뮬레이터 실행 중...")
    
    if os.path.exists("antibiotic_simulator.R"):
        try:
            print("   ▶️ R 시뮬레이터 시작...")
            result = subprocess.run([
                'Rscript', 'antibiotic_simulator.R'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("   ✅ R 시뮬레이션 완료!")
                return True
            else:
                print(f"   ❌ R 실행 오류: {result.stderr}")
                return False
        except FileNotFoundError:
            print("   ❌ R이 설치되지 않았습니다.")
            return False
    else:
        print("   ⚠️ antibiotic_simulator.R 파일이 없습니다.")
        return False

def run_matlab_simulator():
    """MATLAB 시뮬레이터 실행"""
    print("\n🧮 MATLAB 시뮬레이터 실행 중...")
    
    if os.path.exists("antibiotic_simulator.m"):
        try:
            print("   ▶️ MATLAB 시뮬레이터 시작...")
            result = subprocess.run([
                'matlab', '-batch', 'antibiotic_simulator'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("   ✅ MATLAB 시뮬레이션 완료!")
                return True
            else:
                print(f"   ❌ MATLAB 실행 오류: {result.stderr}")
                return False
        except FileNotFoundError:
            print("   ❌ MATLAB이 설치되지 않았습니다.")
            return False
    else:
        print("   ⚠️ antibiotic_simulator.m 파일이 없습니다.")
        return False

def launch_web_hub():
    """웹 허브 실행"""
    print("\n🌐 웹 허브 실행 중...")
    
    try:
        print("   ▶️ Streamlit 웹 서버 시작...")
        
        # Streamlit 실행
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'web_hub.py',
            '--server.port', '8501',
            '--server.headless', 'true'
        ])
        
        # 서버 시작 대기
        time.sleep(3)
        
        # 브라우저에서 열기
        url = "http://localhost:8501"
        print(f"   🌐 웹 브라우저에서 열기: {url}")
        webbrowser.open(url)
        
        return process
        
    except Exception as e:
        print(f"   ❌ 웹 허브 실행 실패: {e}")
        return None

def launch_visualizations():
    """시각화 도구들 실행"""
    print("\n📊 시각화 도구 실행 중...")
    
    visualization_scripts = [
        ("실시간 시각화", "realtime_visualizer.py"),
        ("애니메이션 시각화", "animated_visualizer.py")
    ]
    
    processes = []
    
    for name, script in visualization_scripts:
        if os.path.exists(script):
            try:
                print(f"   ▶️ {name} 시작...")
                process = subprocess.Popen([
                    sys.executable, script
                ])
                processes.append((name, process))
                time.sleep(2)  # 순차적 시작
            except Exception as e:
                print(f"   ❌ {name} 실행 실패: {e}")
        else:
            print(f"   ⚠️ {script} 파일이 없습니다.")
    
    return processes

def create_status_report(requirements, results):
    """상태 보고서 생성"""
    print("\n📋 실행 결과 요약:")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": requirements,
        "execution_results": results,
        "summary": {
            "total_simulators": len(results),
            "successful": sum(1 for r in results.values() if r),
            "failed": sum(1 for r in results.values() if not r)
        }
    }
    
    # 콘솔 출력
    print(f"   ✅ 성공: {report['summary']['successful']}개")
    print(f"   ❌ 실패: {report['summary']['failed']}개")
    print(f"   📊 총계: {report['summary']['total_simulators']}개")
    
    # JSON 저장
    os.makedirs('results', exist_ok=True)
    with open('results/launch_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("   💾 상세 보고서: results/launch_report.json")
    
    return report

def main():
    """메인 실행 함수"""
    print_banner()
    
    # 환경 확인
    requirements = check_requirements()
    
    # 결과 디렉토리 생성
    os.makedirs('results', exist_ok=True)
    
    # 실행 결과 추적
    results = {}
    all_processes = []
    
    # 1. Python 시뮬레이터들 실행
    if requirements['python']:
        python_processes = run_python_simulators()
        all_processes.extend(python_processes)
        results['python_simulators'] = len(python_processes) > 0
    
    # 2. JavaScript 시뮬레이터 실행
    if requirements['nodejs']:
        results['javascript_simulator'] = run_javascript_simulator()
    else:
        results['javascript_simulator'] = False
    
    # 3. R 시뮬레이터 실행
    if requirements['r']:
        results['r_simulator'] = run_r_simulator()
    else:
        results['r_simulator'] = False
    
    # 4. MATLAB 시뮬레이터 실행
    if requirements['matlab']:
        results['matlab_simulator'] = run_matlab_simulator()
    else:
        results['matlab_simulator'] = False
    
    # 5. 시각화 도구들 실행
    if requirements['python']:
        viz_processes = launch_visualizations()
        all_processes.extend(viz_processes)
        results['visualizations'] = len(viz_processes) > 0
    
    # 6. 웹 허브 실행
    if requirements['python']:
        web_process = launch_web_hub()
        if web_process:
            all_processes.append(("웹 허브", web_process))
            results['web_hub'] = True
        else:
            results['web_hub'] = False
    
    # 상태 보고서 생성
    report = create_status_report(requirements, results)
    
    print(f"""
🎉 통합 실행 완료!

📱 접속 방법:
   🌐 웹 허브: http://localhost:8501
   📊 실시간 시각화: 별도 창에서 실행
   📈 애니메이션: 별도 창에서 실행

💡 사용법:
   - 웹 브라우저에서 http://localhost:8501 접속
   - 사이드바에서 원하는 시뮬레이터 선택
   - 파라미터 조정 후 실행 버튼 클릭
   - 결과를 실시간으로 확인

⚡ 실행 중인 프로세스: {len(all_processes)}개
📊 생성된 결과 파일: results/ 폴더 확인

Ctrl+C로 모든 프로세스를 중단할 수 있습니다.
    """)
    
    try:
        # 메인 프로세스 대기
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단됨")
        print("모든 프로세스를 종료합니다...")
        
        # 모든 프로세스 종료
        for name, process in all_processes:
            try:
                process.terminate()
                print(f"   ✅ {name} 종료")
            except:
                pass
        
        print("👋 프로그램 종료")

if __name__ == "__main__":
    main()
