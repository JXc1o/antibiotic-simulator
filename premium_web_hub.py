#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 Premium 항생제 내성 시뮬레이터 - D5 Render 스타일
Samsung Innovation Challenge 2025

D5 Render처럼 전문적이고 멋진 디자인의 웹 허브
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
import subprocess
import sys
import time
import threading
from datetime import datetime
import base64
from pathlib import Path
import io
import zipfile

# 페이지 설정
st.set_page_config(
    page_title="🧬 항생제 내성 진화 AI 시뮬레이터",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 한국어 폰트 및 고급 CSS 스타일
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    
    * {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    .main-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 4rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .feature-desc {
        color: #666;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    .premium-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 50px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
        margin: 1rem 0;
    }
    
    .premium-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.6);
    }
    
    .stats-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 2rem 0;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 900;
        display: block;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    .monitoring-panel {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border-left: 5px solid #667eea;
    }
    
    .monitor-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .monitor-status {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    .status-running {
        background-color: #10b981;
    }
    
    .status-stopped {
        background-color: #ef4444;
    }
    
    .status-pending {
        background-color: #f59e0b;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .progress-modern {
        background: #e5e7eb;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-bar-modern {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    .sidebar {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    
    .tab-container {
        background: white;
        border-radius: 15px;
        padding: 0;
        margin: 2rem 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    .korean-text {
        font-family: 'Noto Sans KR', sans-serif !important;
        font-weight: 400;
    }
    
    .metric-card-premium {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'simulation_status' not in st.session_state:
    st.session_state.simulation_status = {}
if 'active_processes' not in st.session_state:
    st.session_state.active_processes = {}
if 'monitoring_data' not in st.session_state:
    st.session_state.monitoring_data = []

# 메인 히어로 섹션
st.markdown("""
<div class="main-hero">
    <div class="hero-title korean-text">🧬 항생제 내성 진화 AI 시뮬레이터</div>
    <div class="hero-subtitle korean-text">Samsung Innovation Challenge 2025 - 삼성을 뛰어넘는 혁신</div>
    <div style="margin-top: 2rem;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.5rem; display: inline-block;">🔬 과학적 정확성</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.5rem; display: inline-block;">🤖 AI 최적화</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.5rem; display: inline-block;">📊 실시간 분석</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.5rem; display: inline-block;">🌐 웹 인터페이스</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 실시간 시스템 모니터링 함수
def get_system_status():
    """실시간 시스템 상태 확인"""
    status = {}
    
    # Python 상태
    status['Python'] = {
        'name': 'Python 엔진',
        'status': 'running',
        'version': f"{sys.version_info.major}.{sys.version_info.minor}",
        'description': '메인 시뮬레이션 엔진'
    }
    
    # Node.js 상태
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=3)
        status['NodeJS'] = {
            'name': 'JavaScript 엔진',
            'status': 'running' if result.returncode == 0 else 'stopped',
            'version': result.stdout.strip() if result.returncode == 0 else 'N/A',
            'description': 'JavaScript 시뮬레이터'
        }
    except:
        status['NodeJS'] = {
            'name': 'JavaScript 엔진',
            'status': 'stopped',
            'version': '미설치',
            'description': 'JavaScript 시뮬레이터'
        }
    
    # R 상태
    try:
        result = subprocess.run(['R', '--version'], capture_output=True, text=True, timeout=3)
        status['R'] = {
            'name': 'R 통계 엔진',
            'status': 'running' if result.returncode == 0 else 'stopped',
            'version': '4.5+' if result.returncode == 0 else '미설치',
            'description': '통계 분석 엔진'
        }
    except:
        status['R'] = {
            'name': 'R 통계 엔진',
            'status': 'stopped',
            'version': '미설치',
            'description': '통계 분석 엔진'
        }
    
    return status

def run_simulation_with_monitoring(sim_type, params):
    """모니터링과 함께 시뮬레이션 실행"""
    simulation_id = f"{sim_type}_{datetime.now().strftime('%H%M%S')}"
    
    # 모니터링 데이터 초기화
    st.session_state.simulation_status[simulation_id] = {
        'type': sim_type,
        'status': 'starting',
        'progress': 0,
        'start_time': datetime.now(),
        'params': params
    }
    
    try:
        if sim_type == 'korean_perfect':
            # 한글 완벽 시뮬레이터 실행
            st.session_state.simulation_status[simulation_id]['status'] = 'running'
            st.session_state.simulation_status[simulation_id]['progress'] = 25
            
            result = subprocess.run([
                sys.executable, 'perfect_korean_simulator.py'
            ], capture_output=True, text=True, timeout=60)
            
            st.session_state.simulation_status[simulation_id]['progress'] = 75
            
            if result.returncode == 0:
                st.session_state.simulation_status[simulation_id]['status'] = 'completed'
                st.session_state.simulation_status[simulation_id]['progress'] = 100
                return True, "한글 시뮬레이션 완료!"
            else:
                st.session_state.simulation_status[simulation_id]['status'] = 'error'
                return False, f"오류: {result.stderr}"
                
        elif sim_type == 'javascript':
            # JavaScript 시뮬레이터 실행
            st.session_state.simulation_status[simulation_id]['status'] = 'running'
            st.session_state.simulation_status[simulation_id]['progress'] = 30
            
            result = subprocess.run([
                'node', 'antibiotic_simulator.js'
            ], capture_output=True, text=True, timeout=45)
            
            st.session_state.simulation_status[simulation_id]['progress'] = 90
            
            if result.returncode == 0:
                st.session_state.simulation_status[simulation_id]['status'] = 'completed'
                st.session_state.simulation_status[simulation_id]['progress'] = 100
                return True, "JavaScript 시뮬레이션 완료!"
            else:
                st.session_state.simulation_status[simulation_id]['status'] = 'error'
                return False, f"오류: {result.stderr}"
                
        elif sim_type == 'r_stats':
            # R 시뮬레이터 실행
            st.session_state.simulation_status[simulation_id]['status'] = 'running'
            st.session_state.simulation_status[simulation_id]['progress'] = 20
            
            result = subprocess.run([
                'Rscript', 'antibiotic_simulator.R'
            ], capture_output=True, text=True, timeout=60)
            
            st.session_state.simulation_status[simulation_id]['progress'] = 85
            
            if result.returncode == 0:
                st.session_state.simulation_status[simulation_id]['status'] = 'completed'
                st.session_state.simulation_status[simulation_id]['progress'] = 100
                return True, "R 통계 분석 완료!"
            else:
                st.session_state.simulation_status[simulation_id]['status'] = 'error'
                return False, f"오류: {result.stderr}"
        
    except subprocess.TimeoutExpired:
        st.session_state.simulation_status[simulation_id]['status'] = 'timeout'
        return False, "실행 시간 초과"
    except Exception as e:
        st.session_state.simulation_status[simulation_id]['status'] = 'error'
        return False, f"오류: {str(e)}"

# 실시간 모니터링 패널
st.markdown("""
<div class="monitoring-panel">
    <h3 class="korean-text" style="margin-bottom: 2rem; color: #333; font-weight: 700;">📊 실시간 시스템 모니터링</h3>
</div>
""", unsafe_allow_html=True)

# 시스템 상태 표시
col1, col2 = st.columns(2)

with col1:
    system_status = get_system_status()
    
    for key, info in system_status.items():
        status_class = "status-running" if info['status'] == 'running' else "status-stopped"
        status_text = "실행 중" if info['status'] == 'running' else "중지됨"
        status_icon = "🟢" if info['status'] == 'running' else "🔴"
        
        st.markdown(f"""
        <div class="monitor-item korean-text">
            <div class="monitor-status">
                <div class="status-indicator {status_class}"></div>
                <div>
                    <div style="font-weight: 600; font-size: 1.1rem;">{status_icon} {info['name']}</div>
                    <div style="color: #666; font-size: 0.9rem;">{info['description']} (v{info['version']})</div>
                </div>
            </div>
            <div style="font-weight: 600; color: #667eea;">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    # 활성 시뮬레이션 모니터링
    st.markdown('<div class="korean-text" style="font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem;">🔄 활성 시뮬레이션</div>', unsafe_allow_html=True)
    
    if st.session_state.simulation_status:
        for sim_id, sim_info in st.session_state.simulation_status.items():
            if sim_info['status'] in ['running', 'starting']:
                elapsed = (datetime.now() - sim_info['start_time']).seconds
                
                st.markdown(f"""
                <div class="monitor-item korean-text">
                    <div>
                        <div style="font-weight: 600;">{sim_info['type']} 시뮬레이션</div>
                        <div style="color: #666; font-size: 0.9rem;">실행 시간: {elapsed}초</div>
                        <div class="progress-modern">
                            <div class="progress-bar-modern" style="width: {sim_info['progress']}%"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="monitor-item korean-text" style="text-align: center; color: #666;">
            현재 실행 중인 시뮬레이션이 없습니다
        </div>
        """, unsafe_allow_html=True)

# 주요 기능 카드들
st.markdown('<div style="margin: 3rem 0;"></div>', unsafe_allow_html=True)

# 기능 섹션
features_col1, features_col2, features_col3 = st.columns(3)

with features_col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🧬</div>
        <div class="feature-title korean-text">완벽한 한글 시뮬레이터</div>
        <div class="feature-desc korean-text">
            과학적으로 정확한 모델링과 완벽한 한국어 지원으로
            의료진이 쉽게 사용할 수 있는 시뮬레이터입니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 한글 시뮬레이터 실행", key="korean_sim", use_container_width=True):
        with st.spinner("한글 시뮬레이션 실행 중..."):
            success, message = run_simulation_with_monitoring('korean_perfect', {})
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)

with features_col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-title korean-text">JavaScript 시뮬레이터</div>
        <div class="feature-desc korean-text">
            웹 개발자를 위한 고성능 JavaScript 엔진으로
            빠르고 효율적인 시뮬레이션을 제공합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⚡ JavaScript 실행", key="js_sim", use_container_width=True):
        with st.spinner("JavaScript 시뮬레이션 실행 중..."):
            success, message = run_simulation_with_monitoring('javascript', {})
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)

with features_col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title korean-text">R 통계 분석</div>
        <div class="feature-desc korean-text">
            전문적인 통계 분석과 고급 데이터 시각화를
            위한 R 기반 분석 도구입니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📊 R 분석 실행", key="r_sim", use_container_width=True):
        with st.spinner("R 통계 분석 실행 중..."):
            success, message = run_simulation_with_monitoring('r_stats', {})
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)

# 통계 대시보드
st.markdown('<div style="margin: 3rem 0;"></div>', unsafe_allow_html=True)

stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

# 결과 파일 개수
results_dir = Path("results")
total_files = len(list(results_dir.glob("*"))) if results_dir.exists() else 0

with stats_col1:
    st.markdown(f"""
    <div class="metric-card-premium">
        <div class="metric-value korean-text">{total_files}</div>
        <div class="metric-label korean-text">생성된 결과</div>
    </div>
    """, unsafe_allow_html=True)

with stats_col2:
    completed_sims = sum(1 for sim in st.session_state.simulation_status.values() if sim['status'] == 'completed')
    st.markdown(f"""
    <div class="metric-card-premium">
        <div class="metric-value korean-text">{completed_sims}</div>
        <div class="metric-label korean-text">완료된 시뮬레이션</div>
    </div>
    """, unsafe_allow_html=True)

with stats_col3:
    running_sims = sum(1 for sim in st.session_state.simulation_status.values() if sim['status'] == 'running')
    st.markdown(f"""
    <div class="metric-card-premium">
        <div class="metric-value korean-text">{running_sims}</div>
        <div class="metric-label korean-text">실행 중</div>
    </div>
    """, unsafe_allow_html=True)

with stats_col4:
    system_health = sum(1 for status in system_status.values() if status['status'] == 'running')
    st.markdown(f"""
    <div class="metric-card-premium">
        <div class="metric-value korean-text">{system_health}/3</div>
        <div class="metric-label korean-text">시스템 상태</div>
    </div>
    """, unsafe_allow_html=True)

# 결과 표시 및 다운로드 섹션
st.markdown('<div style="margin: 3rem 0;"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
    <h3 class="korean-text" style="color: #333; font-weight: 700; margin-bottom: 2rem;">📁 생성된 결과 파일</h3>
</div>
""", unsafe_allow_html=True)

if results_dir.exists():
    result_files = list(results_dir.glob("*"))
    
    if result_files:
        # 파일 타입별 분류
        html_files = [f for f in result_files if f.suffix == '.html']
        json_files = [f for f in result_files if f.suffix == '.json']
        image_files = [f for f in result_files if f.suffix in ['.png', '.gif', '.jpg']]
        
        tab1, tab2, tab3 = st.tabs(["📊 시각화", "📋 데이터", "🖼️ 이미지"])
        
        with tab1:
            if html_files:
                for html_file in html_files[:3]:  # 최대 3개 표시
                    st.markdown(f"**{html_file.name}**")
                    try:
                        with open(html_file, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        st.components.v1.html(html_content, height=400, scrolling=True)
                    except Exception as e:
                        st.error(f"파일 로드 오류: {e}")
            else:
                st.info("아직 생성된 시각화가 없습니다.")
        
        with tab2:
            if json_files:
                selected_json = st.selectbox("데이터 파일 선택", [f.name for f in json_files])
                if selected_json:
                    try:
                        with open(results_dir / selected_json, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        st.json(data)
                    except Exception as e:
                        st.error(f"파일 로드 오류: {e}")
            else:
                st.info("아직 생성된 데이터가 없습니다.")
        
        with tab3:
            if image_files:
                cols = st.columns(3)
                for i, img_file in enumerate(image_files[:6]):
                    with cols[i % 3]:
                        st.image(str(img_file), caption=img_file.name, use_container_width=True)
            else:
                st.info("아직 생성된 이미지가 없습니다.")
        
        # 전체 다운로드
        if st.button("📥 모든 결과 ZIP 다운로드", use_container_width=True):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in result_files:
                    if file_path.is_file():
                        zip_file.write(file_path, file_path.name)
            
            zip_buffer.seek(0)
            st.download_button(
                label="📥 다운로드 시작",
                data=zip_buffer.getvalue(),
                file_name=f"antibiotic_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )

# 푸터
st.markdown('<div style="margin: 4rem 0;"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem 2rem; border-radius: 20px; text-align: center; color: white;">
    <h2 class="korean-text" style="margin-bottom: 1rem; font-weight: 700;">🏆 Samsung Innovation Challenge 2025</h2>
    <h3 class="korean-text" style="margin-bottom: 2rem; font-weight: 300;">삼성을 뛰어넘는 혁신적 솔루션</h3>
    <div style="margin-bottom: 2rem;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.5rem; display: inline-block;">🔬 과학적 정확성</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.5rem; display: inline-block;">🤖 AI 최적화</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.5rem; display: inline-block;">📊 실시간 분석</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.5rem; display: inline-block;">🌐 웹 인터페이스</span>
    </div>
    <p class="korean-text" style="opacity: 0.9; font-size: 1.1rem;">개발팀: AI 기반 정밀의학 연구팀</p>
</div>
""", unsafe_allow_html=True)

# 자동 새로고침 (실시간 모니터링용)
time.sleep(1)
st.rerun()
