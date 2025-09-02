#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
항생제 내성 시뮬레이터 웹 허브
Samsung Innovation Challenge 2025

모든 시뮬레이터를 웹 인터페이스로 통합 실행
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
from datetime import datetime
import time
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="🧬 항생제 내성 시뮬레이터 허브",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 메인 제목
st.title("🧬 완벽한 항생제 내성 진화 AI 시뮬레이터 허브")
st.subheader("Samsung Innovation Challenge 2025")

# 사이드바 - 시뮬레이터 선택
st.sidebar.title("🎯 시뮬레이터 선택")

simulator_options = {
    "🔬 과학적 정확도 시뮬레이터": "scientific",
    "🐍 Python 기본 시뮬레이터": "python",
    "⚡ JavaScript 시뮬레이터": "javascript", 
    "📊 R 시뮬레이터": "r",
    "🧮 MATLAB 시뮬레이터": "matlab",
    "📈 실시간 시각화": "realtime",
    "🎬 애니메이션 시각화": "animation"
}

selected_simulator = st.sidebar.selectbox(
    "실행할 시뮬레이터를 선택하세요:",
    options=list(simulator_options.keys())
)

# 시뮬레이션 파라미터
st.sidebar.markdown("---")
st.sidebar.title("⚙️ 시뮬레이션 설정")

# 환자 파라미터
st.sidebar.subheader("👤 환자 정보")
patient_weight = st.sidebar.slider("체중 (kg)", 40, 150, 70)
patient_age = st.sidebar.slider("나이", 18, 90, 35)
creatinine = st.sidebar.slider("크레아티닌 청소율 (mL/min)", 30, 150, 120)

# 약물 파라미터
st.sidebar.subheader("💊 투약 설정")
dose_amount = st.sidebar.slider("용량 (mg)", 100, 2000, 500)
dose_interval = st.sidebar.slider("투약 간격 (시간)", 6, 24, 12)
treatment_days = st.sidebar.slider("치료 기간 (일)", 3, 14, 7)

# 세균 파라미터
st.sidebar.subheader("🦠 세균 설정")
initial_sensitive = st.sidebar.number_input("초기 감수성균 (CFU/mL)", 
                                          value=1e8, format="%.0e")
initial_resistant = st.sidebar.number_input("초기 내성균 (CFU/mL)", 
                                          value=1e4, format="%.0e")

def run_simulator(simulator_type, params):
    """선택된 시뮬레이터 실행"""
    
    if simulator_type == "scientific":
        return run_scientific_simulator(params)
    elif simulator_type == "python":
        return run_python_simulator(params)
    elif simulator_type == "javascript":
        return run_javascript_simulator(params)
    elif simulator_type == "r":
        return run_r_simulator(params)
    elif simulator_type == "matlab":
        return run_matlab_simulator(params)
    elif simulator_type == "realtime":
        return run_realtime_visualizer(params)
    elif simulator_type == "animation":
        return run_animation_visualizer(params)

def run_scientific_simulator(params):
    """과학적 정확도 시뮬레이터 실행"""
    try:
        # scientific_simulator.py 임포트 및 실행
        from scientific_simulator import ScientificSimulator, PatientProfile, DrugProperties
        
        # 환자 프로필 생성
        patient = PatientProfile(
            weight=params['weight'],
            age=params['age'],
            creatinine_clearance=params['creatinine']
        )
        
        # 약물 특성
        drug = DrugProperties()
        
        # 시뮬레이터 생성
        simulator = ScientificSimulator(patient, drug)
        
        # 투약 스케줄 생성
        total_hours = params['treatment_days'] * 24
        dose_times = list(range(0, total_hours, params['interval']))
        dose_schedule = [(t, params['dose']) for t in dose_times]
        
        # 시뮬레이션 실행
        results = simulator.run_simulation(dose_schedule)
        
        return results, "과학적 정확도 시뮬레이션 완료!"
        
    except Exception as e:
        return None, f"오류: {str(e)}"

def run_python_simulator(params):
    """Python 기본 시뮬레이터 실행"""
    try:
        # 간단한 Python 시뮬레이션
        times = np.arange(0, params['treatment_days'] * 24, 0.5)
        concentrations = []
        sensitive_pop = [params['initial_sensitive']]
        resistant_pop = [params['initial_resistant']]
        
        for t in times:
            # 간단한 농도 계산
            dose_times = np.arange(0, len(times) * 0.5, params['interval'])
            conc = 0
            for dt in dose_times:
                if t >= dt:
                    conc += (params['dose'] / 175) * np.exp(-0.173 * (t - dt))
            concentrations.append(conc)
            
            # 세균 동역학
            if len(sensitive_pop) > 0:
                s_current = sensitive_pop[-1]
                r_current = resistant_pop[-1]
                
                # 성장 및 사멸
                kill_s = 4.0 * (conc ** 2) / (0.5 ** 2 + conc ** 2)
                kill_r = 4.0 * (conc ** 2) / (8.0 ** 2 + conc ** 2)
                
                s_new = max(0, s_current * (1 + (0.693 - kill_s) * 0.5))
                r_new = max(0, r_current * (1 + (0.623 - kill_r) * 0.5))
                
                sensitive_pop.append(s_new)
                resistant_pop.append(r_new)
        
        results = {
            'times': times.tolist(),
            'concentrations': concentrations,
            'sensitive_populations': sensitive_pop,
            'resistant_populations': resistant_pop,
            'total_populations': [s + r for s, r in zip(sensitive_pop, resistant_pop)],
            'resistance_fractions': [r/(s+r)*100 if s+r > 0 else 0 
                                   for s, r in zip(sensitive_pop, resistant_pop)]
        }
        
        return results, "Python 기본 시뮬레이션 완료!"
        
    except Exception as e:
        return None, f"오류: {str(e)}"

def run_javascript_simulator(params):
    """JavaScript 시뮬레이터 실행"""
    try:
        # Node.js로 JavaScript 실행
        result = subprocess.run([
            'node', 'antibiotic_simulator.js'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # 결과 파일 읽기
            if os.path.exists('results/antibiotic_simulation_js.json'):
                with open('results/antibiotic_simulation_js.json', 'r') as f:
                    results = json.load(f)
                return results, "JavaScript 시뮬레이션 완료!"
            else:
                return None, "결과 파일을 찾을 수 없습니다."
        else:
            return None, f"JavaScript 실행 오류: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return None, "JavaScript 실행 시간 초과"
    except FileNotFoundError:
        return None, "Node.js가 설치되지 않았습니다."
    except Exception as e:
        return None, f"오류: {str(e)}"

def run_r_simulator(params):
    """R 시뮬레이터 실행"""
    try:
        result = subprocess.run([
            'Rscript', 'antibiotic_simulator.R'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {"message": "R 시뮬레이션 실행됨"}, "R 시뮬레이션 완료!"
        else:
            return None, f"R 실행 오류: {result.stderr}"
            
    except FileNotFoundError:
        return None, "R이 설치되지 않았습니다."
    except Exception as e:
        return None, f"오류: {str(e)}"

def run_matlab_simulator(params):
    """MATLAB 시뮬레이터 실행"""
    try:
        result = subprocess.run([
            'matlab', '-batch', 'antibiotic_simulator'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {"message": "MATLAB 시뮬레이션 실행됨"}, "MATLAB 시뮬레이션 완료!"
        else:
            return None, f"MATLAB 실행 오류: {result.stderr}"
            
    except FileNotFoundError:
        return None, "MATLAB이 설치되지 않았습니다."
    except Exception as e:
        return None, f"오류: {str(e)}"

def run_realtime_visualizer(params):
    """실시간 시각화 실행"""
    try:
        # 백그라운드에서 실행
        subprocess.Popen([
            sys.executable, 'realtime_visualizer.py'
        ])
        return {"message": "실시간 시각화 시작됨"}, "실시간 시각화가 별도 창에서 실행됩니다!"
        
    except Exception as e:
        return None, f"오류: {str(e)}"

def run_animation_visualizer(params):
    """애니메이션 시각화 실행"""
    try:
        subprocess.Popen([
            sys.executable, 'animated_visualizer.py'
        ])
        return {"message": "애니메이션 시작됨"}, "애니메이션 시각화가 별도 창에서 실행됩니다!"
        
    except Exception as e:
        return None, f"오류: {str(e)}"

def create_plotly_charts(results):
    """Plotly 차트 생성"""
    if not results or 'times' not in results:
        return None
    
    # 서브플롯 생성
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            '💊 약물 농도',
            '🦠 세균 집단',
            '📊 내성 비율',
            '📈 치료 효과'
        ],
        specs=[[{"secondary_y": False}, {"secondary_y": True}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    times = results['times']
    
    # 1. 약물 농도
    fig.add_trace(
        go.Scatter(x=times, y=results['concentrations'],
                  mode='lines', name='농도', line=dict(color='blue')),
        row=1, col=1
    )
    
    # 2. 세균 집단
    fig.add_trace(
        go.Scatter(x=times, y=results['sensitive_populations'],
                  mode='lines', name='감수성균', line=dict(color='green')),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=times, y=results['resistant_populations'],
                  mode='lines', name='내성균', line=dict(color='red')),
        row=1, col=2
    )
    
    # 3. 내성 비율
    fig.add_trace(
        go.Scatter(x=times, y=results['resistance_fractions'],
                  mode='lines', name='내성 비율', line=dict(color='orange')),
        row=2, col=1
    )
    
    # 4. 치료 효과
    if 'total_populations' in results:
        fig.add_trace(
            go.Scatter(x=times, y=results['total_populations'],
                      mode='lines', name='총 세균 수', line=dict(color='purple')),
            row=2, col=2
        )
    
    # 축 설정
    fig.update_yaxes(type="log", title_text="농도 (mg/L)", row=1, col=1)
    fig.update_yaxes(type="log", title_text="세균 수 (CFU/mL)", row=1, col=2)
    fig.update_yaxes(title_text="내성 비율 (%)", range=[0, 100], row=2, col=1)
    fig.update_yaxes(type="log", title_text="총 세균 수", row=2, col=2)
    
    fig.update_xaxes(title_text="시간 (시간)")
    
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="🧬 항생제 내성 시뮬레이션 결과"
    )
    
    return fig

# 메인 컨텐츠
st.markdown("---")

# 시뮬레이션 실행 버튼
if st.button(f"▶️ {selected_simulator} 실행", key="run_sim"):
    
    # 파라미터 수집
    params = {
        'weight': patient_weight,
        'age': patient_age,
        'creatinine': creatinine,
        'dose': dose_amount,
        'interval': dose_interval,
        'treatment_days': treatment_days,
        'initial_sensitive': initial_sensitive,
        'initial_resistant': initial_resistant
    }
    
    # 프로그레스 바
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("시뮬레이션 초기화 중...")
    progress_bar.progress(25)
    
    # 시뮬레이터 실행
    simulator_type = simulator_options[selected_simulator]
    results, message = run_simulator(simulator_type, params)
    
    progress_bar.progress(75)
    status_text.text("결과 처리 중...")
    
    if results:
        progress_bar.progress(100)
        status_text.text(message)
        
        # 결과 표시
        st.success(message)
        
        # 차트 생성 및 표시
        if isinstance(results, dict) and 'times' in results:
            chart = create_plotly_charts(results)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            
            # 통계 요약
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 시뮬레이션 시간", f"{max(results['times']):.1f} 시간")
            
            with col2:
                final_conc = results['concentrations'][-1] if results['concentrations'] else 0
                st.metric("최종 약물 농도", f"{final_conc:.3f} mg/L")
            
            with col3:
                final_resistance = results['resistance_fractions'][-1] if results['resistance_fractions'] else 0
                st.metric("최종 내성 비율", f"{final_resistance:.1f}%")
            
            with col4:
                total_doses = len(range(0, treatment_days * 24, dose_interval))
                st.metric("총 투약 횟수", f"{total_doses}회")
            
            # 결과 다운로드
            if st.button("📥 결과 다운로드"):
                json_str = json.dumps(results, indent=2, ensure_ascii=False)
                st.download_button(
                    label="JSON 파일 다운로드",
                    data=json_str,
                    file_name=f"simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        else:
            st.info("시뮬레이션이 완료되었지만 그래프 데이터가 없습니다.")
    
    else:
        progress_bar.progress(100)
        st.error(message)

# 사용 가능한 시뮬레이터 상태 체크
st.markdown("---")
st.subheader("🔧 시뮬레이터 상태")

status_col1, status_col2 = st.columns(2)

with status_col1:
    st.markdown("### 설치된 언어/도구")
    
    # Python 체크
    python_status = "✅" if sys.executable else "❌"
    st.text(f"{python_status} Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Node.js 체크
    try:
        node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        node_status = "✅" if node_result.returncode == 0 else "❌"
        node_version = node_result.stdout.strip() if node_result.returncode == 0 else "미설치"
    except:
        node_status = "❌"
        node_version = "미설치"
    st.text(f"{node_status} Node.js {node_version}")
    
    # R 체크
    try:
        r_result = subprocess.run(['R', '--version'], capture_output=True, text=True)
        r_status = "✅" if r_result.returncode == 0 else "❌"
    except:
        r_status = "❌"
    st.text(f"{r_status} R")
    
    # MATLAB 체크
    try:
        matlab_result = subprocess.run(['matlab', '-help'], capture_output=True, text=True)
        matlab_status = "✅" if matlab_result.returncode == 0 else "❌"
    except:
        matlab_status = "❌"
    st.text(f"{matlab_status} MATLAB")

with status_col2:
    st.markdown("### 시뮬레이터 파일")
    
    files_to_check = [
        "scientific_simulator.py",
        "antibiotic_simulator_clean.py",
        "antibiotic_simulator.js",
        "antibiotic_simulator.R",
        "antibiotic_simulator.m",
        "realtime_visualizer.py"
    ]
    
    for file in files_to_check:
        file_status = "✅" if os.path.exists(file) else "❌"
        st.text(f"{file_status} {file}")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
<h4>🧬 Samsung Innovation Challenge 2025</h4>
<p>항생제 내성 진화 시뮬레이터 - 과학적으로 정확하고 포괄적인 모델링</p>
<p>개발: AI 기반 정밀의학 팀</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    st.markdown("웹 허브가 실행 중입니다! 사이드바에서 시뮬레이터를 선택하세요.")
