#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실시간 모니터링 백엔드 서비스
Samsung Innovation Challenge 2025

시뮬레이션 진행 상황을 실시간으로 추적하고 업데이트
"""

import json
import time
import threading
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
import psutil

class RealTimeMonitor:
    def __init__(self):
        self.monitoring_data = {
            'simulations': {},
            'system_status': {},
            'performance': {},
            'last_updated': None
        }
        self.monitoring_active = True
        
    def start_monitoring(self):
        """모니터링 시작"""
        print("🔄 실시간 모니터링 시작...")
        
        # 별도 스레드에서 모니터링 실행
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return monitor_thread
    
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 시스템 상태 업데이트
                self._update_system_status()
                
                # 성능 지표 업데이트
                self._update_performance()
                
                # 파일 시스템 체크
                self._check_results()
                
                # 데이터 저장
                self._save_monitoring_data()
                
                # 5초 간격으로 업데이트
                time.sleep(5)
                
            except Exception as e:
                print(f"모니터링 오류: {e}")
                time.sleep(10)
    
    def _update_system_status(self):
        """시스템 상태 업데이트"""
        status = {}
        
        # Python 상태
        status['python'] = {
            'status': 'running',
            'version': f"{sys.version_info.major}.{sys.version_info.minor}",
            'memory_usage': psutil.virtual_memory().percent
        }
        
        # Node.js 체크
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=3)
            status['nodejs'] = {
                'status': 'running' if result.returncode == 0 else 'stopped',
                'version': result.stdout.strip() if result.returncode == 0 else 'N/A'
            }
        except:
            status['nodejs'] = {'status': 'stopped', 'version': 'N/A'}
        
        # R 체크
        try:
            result = subprocess.run(['R', '--version'], capture_output=True, text=True, timeout=3)
            status['r'] = {
                'status': 'running' if result.returncode == 0 else 'stopped',
                'version': 'R 4.5+' if result.returncode == 0 else 'N/A'
            }
        except:
            status['r'] = {'status': 'stopped', 'version': 'N/A'}
        
        self.monitoring_data['system_status'] = status
    
    def _update_performance(self):
        """성능 지표 업데이트"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            
            self.monitoring_data['performance'] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
            
        except Exception as e:
            print(f"성능 모니터링 오류: {e}")
    
    def _check_results(self):
        """결과 파일 체크"""
        results_dir = Path("results")
        if results_dir.exists():
            files = list(results_dir.glob("*"))
            
            # 파일 타입별 분류
            file_stats = {
                'total_files': len(files),
                'html_files': len([f for f in files if f.suffix == '.html']),
                'json_files': len([f for f in files if f.suffix == '.json']),
                'image_files': len([f for f in files if f.suffix in ['.png', '.gif', '.jpg']]),
                'latest_file': None
            }
            
            # 최신 파일 찾기
            if files:
                latest_file = max(files, key=lambda f: f.stat().st_mtime)
                file_stats['latest_file'] = {
                    'name': latest_file.name,
                    'modified': datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
                }
            
            self.monitoring_data['file_stats'] = file_stats
    
    def _save_monitoring_data(self):
        """모니터링 데이터 저장"""
        self.monitoring_data['last_updated'] = datetime.now().isoformat()
        
        # JSON 파일로 저장
        os.makedirs('monitoring', exist_ok=True)
        with open('monitoring/realtime_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.monitoring_data, f, indent=2, ensure_ascii=False)
    
    def add_simulation(self, sim_id, sim_type, status='starting'):
        """시뮬레이션 추가"""
        self.monitoring_data['simulations'][sim_id] = {
            'type': sim_type,
            'status': status,
            'start_time': datetime.now().isoformat(),
            'progress': 0
        }
    
    def update_simulation(self, sim_id, status=None, progress=None):
        """시뮬레이션 상태 업데이트"""
        if sim_id in self.monitoring_data['simulations']:
            if status:
                self.monitoring_data['simulations'][sim_id]['status'] = status
            if progress is not None:
                self.monitoring_data['simulations'][sim_id]['progress'] = progress
            
            self.monitoring_data['simulations'][sim_id]['last_updated'] = datetime.now().isoformat()
    
    def get_status(self):
        """현재 상태 반환"""
        return self.monitoring_data
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        print("🛑 모니터링 중지됨")

def main():
    """메인 실행 함수"""
    print("🚀 실시간 모니터링 서비스 시작...")
    
    monitor = RealTimeMonitor()
    
    try:
        # 모니터링 시작
        monitor_thread = monitor.start_monitoring()
        
        print("✅ 모니터링 서비스가 실행 중입니다.")
        print("📊 모니터링 데이터: ./monitoring/realtime_data.json")
        print("⏹️ Ctrl+C로 중지할 수 있습니다.")
        
        # 메인 스레드 유지
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단됨")
        monitor.stop_monitoring()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()
