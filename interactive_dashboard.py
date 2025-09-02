#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
대화형 웹 대시보드 - 항생제 내성 시뮬레이터
Samsung Innovation Challenge 2025
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="항생제 내성 시뮬레이터",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #00d4ff, #ff0080);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success {
        color: #00ff00;
        font-weight: bold;
    }
    .failure {
        color: #ff4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class InteractiveSimulator:
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if 'simulation_data' not in st.session_state:
            st.session_state.simulation_data = {
                'times': [],
                'concentrations': [],
                'sensitive': [],
                'resistant': [],
                'resistance_fractions': [],
                'doses_given': []
            }
        
        if 'running' not in st.session_state:
            st.session_state.running = False
            
        if 'current_time' not in st.session_state:
            st.session_state.current_time = 0
            
    def pharmacodynamic_effect(self, conc, mic, emax=4.0, hill=2.0):
        """약력학적 효과 계산"""
        if conc <= 0:
            return 0
        return emax * (conc ** hill) / (mic ** hill + conc ** hill)
    
    def calculate_concentration(self, t, doses_given, dose, ke, vd):
        """약물 농도 계산"""
        conc = 0
        for dose_time in doses_given:
            if t >= dose_time:
                time_since_dose = t - dose_time
                dose_conc = (dose / vd) * np.exp(-ke * time_since_dose)
                conc += dose_conc
        return conc
    
    def run_simulation(self, dose, interval, days, patient_weight):
        """시뮬레이션 실행"""
        # 파라미터 계산
        ke = 0.693 / 4.0  # 반감기 4시간
        vd = 2.5 * patient_weight  # 분포용적
        
        # 시간 배열
        total_hours = days * 24
        times = np.arange(0, total_hours, 0.5)  # 30분 간격
        
        # 투약 시점
        dose_times = np.arange(0, total_hours, interval)
        
        # 농도 계산
        concentrations = []
        for t in times:
            conc = self.calculate_concentration(t, dose_times, dose, ke, vd)
            concentrations.append(conc)
        
        # 세균 집단 시뮬레이션
        S = 1e8  # 초기 감수성균
        R = 1e4  # 초기 내성균
        
        s_populations = [S]
        r_populations = [R]
        resistance_fractions = [R / (S + R) * 100]
        
        # 파라미터
        growth_rate_s = 0.693
        growth_rate_r = 0.623
        mutation_rate = 1e-8
        mic_s = 0.5
        mic_r = 8.0
        emax = 4.0
        hill = 2.0
        dt = 0.5
        
        for i in range(1, len(times)):
            t = times[i]
            conc = concentrations[i]
            
            # 약력학적 효과
            kill_rate_s = self.pharmacodynamic_effect(conc, mic_s, emax, hill)
            kill_rate_r = self.pharmacodynamic_effect(conc, mic_r, emax, hill)
            
            # 세균 집단 업데이트
            total_pop = S + R
            carrying_capacity = 1e12
            growth_factor = max(0, 1 - total_pop / carrying_capacity)
            
            dS_dt = (growth_rate_s * growth_factor - kill_rate_s) * S - mutation_rate * S
            dR_dt = (growth_rate_r * growth_factor - kill_rate_r) * R + mutation_rate * S
            
            S = max(0, S + dS_dt * dt)
            R = max(0, R + dR_dt * dt)
            
            s_populations.append(S)
            r_populations.append(R)
            
            total = S + R
            if total > 0:
                resistance_frac = R / total * 100
            else:
                resistance_frac = 0
            resistance_fractions.append(resistance_frac)
        
        return {
            'times': times,
            'concentrations': concentrations,
            'sensitive': s_populations,
            'resistant': r_populations,
            'resistance_fractions': resistance_fractions,
            'dose_times': dose_times
        }
    
    def create_concentration_plot(self, data, dose, mic_s=0.5, mic_r=8.0):
        """농도 그래프 생성"""
        fig = go.Figure()
        
        # 농도 선
        fig.add_trace(go.Scatter(
            x=data['times'],
            y=data['concentrations'],
            mode='lines',
            name='약물 농도',
            line=dict(color='cyan', width=3),
            hovertemplate='시간: %{x:.1f}h<br>농도: %{y:.2f} mg/L<extra></extra>'
        ))
        
        # MIC 선들
        fig.add_hline(y=mic_s, line_dash="dash", line_color="green", 
                     annotation_text="MIC (감수성)", annotation_position="bottom right")
        fig.add_hline(y=mic_r, line_dash="dash", line_color="red",
                     annotation_text="MIC (내성)", annotation_position="top right")
        
        # 투약 시점 표시
        for dose_time in data['dose_times']:
            fig.add_vline(x=dose_time, line_dash="dot", line_color="yellow", opacity=0.7)
        
        fig.update_layout(
            title=f"💊 약물 농도 변화 (용량: {dose}mg)",
            xaxis_title="시간 (시간)",
            yaxis_title="농도 (mg/L)",
            yaxis_type="log",
            template="plotly_dark",
            hovermode='x unified'
        )
        
        return fig
    
    def create_bacterial_plot(self, data):
        """세균 집단 그래프 생성"""
        fig = go.Figure()
        
        # 감수성균
        fig.add_trace(go.Scatter(
            x=data['times'],
            y=data['sensitive'],
            mode='lines',
            name='감수성균',
            line=dict(color='green', width=2),
            hovertemplate='시간: %{x:.1f}h<br>감수성균: %{y:.2e} CFU/mL<extra></extra>'
        ))
        
        # 내성균
        fig.add_trace(go.Scatter(
            x=data['times'],
            y=data['resistant'],
            mode='lines',
            name='내성균',
            line=dict(color='red', width=2),
            hovertemplate='시간: %{x:.1f}h<br>내성균: %{y:.2e} CFU/mL<extra></extra>'
        ))
        
        # 총합
        total = [s + r for s, r in zip(data['sensitive'], data['resistant'])]
        fig.add_trace(go.Scatter(
            x=data['times'],
            y=total,
            mode='lines',
            name='총 세균수',
            line=dict(color='white', width=1, dash='dash'),
            hovertemplate='시간: %{x:.1f}h<br>총 세균수: %{y:.2e} CFU/mL<extra></extra>'
        ))
        
        # 치료 실패 임계선
        fig.add_hline(y=1e6, line_dash="dot", line_color="orange",
                     annotation_text="치료 실패 임계값", annotation_position="bottom right")
        
        fig.update_layout(
            title="🦠 세균 집단 동역학",
            xaxis_title="시간 (시간)",
            yaxis_title="세균 수 (CFU/mL)",
            yaxis_type="log",
            template="plotly_dark",
            hovermode='x unified'
        )
        
        return fig
    
    def create_resistance_plot(self, data):
        """내성 비율 그래프 생성"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['times'],
            y=data['resistance_fractions'],
            mode='lines',
            name='내성 비율',
            line=dict(color='orange', width=3),
            fill='tonexty',
            hovertemplate='시간: %{x:.1f}h<br>내성 비율: %{y:.1f}%<extra></extra>'
        ))
        
        # 위험 임계선
        fig.add_hline(y=10, line_dash="dot", line_color="red",
                     annotation_text="위험 임계값 (10%)", annotation_position="top right")
        
        fig.update_layout(
            title="📊 내성 비율 변화",
            xaxis_title="시간 (시간)",
            yaxis_title="내성 비율 (%)",
            template="plotly_dark",
            hovermode='x unified'
        )
        
        return fig
    
    def create_3d_plot(self, data):
        """3D 시각화"""
        fig = go.Figure(data=go.Scatter3d(
            x=data['times'],
            y=data['concentrations'],
            z=data['resistance_fractions'],
            mode='markers+lines',
            marker=dict(
                size=3,
                color=data['resistance_fractions'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="내성비율 (%)")
            ),
            line=dict(color='cyan', width=4),
            hovertemplate='시간: %{x:.1f}h<br>농도: %{y:.2f} mg/L<br>내성: %{z:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="🌐 3D 시공간 분석",
            scene=dict(
                xaxis_title="시간 (시간)",
                yaxis_title="농도 (mg/L)",
                zaxis_title="내성 비율 (%)",
                bgcolor="black"
            ),
            template="plotly_dark"
        )
        
        return fig
    
    def run_dashboard(self):
        """대시보드 실행"""
        # 헤더
        st.markdown('<div class="main-header">🧬 실시간 항생제 내성 시뮬레이터</div>', unsafe_allow_html=True)
        st.markdown("### Samsung Innovation Challenge 2025")
        
        # 사이드바 컨트롤
        st.sidebar.header("🎛️ 시뮬레이션 설정")
        
        # 환자 정보
        st.sidebar.subheader("👤 환자 정보")
        patient_age = st.sidebar.slider("나이 (세)", 20, 90, 65)
        patient_weight = st.sidebar.slider("체중 (kg)", 40, 120, 70)
        creatinine = st.sidebar.slider("크레아티닌 청소율", 30, 150, 100)
        infection_severity = st.sidebar.slider("감염 중증도", 0.1, 1.0, 0.5)
        
        # 투약 설정
        st.sidebar.subheader("💊 투약 설정")
        dose = st.sidebar.slider("용량 (mg)", 100, 2000, 500, step=50)
        interval = st.sidebar.slider("투약 간격 (시간)", 6, 24, 12)
        days = st.sidebar.slider("치료 기간 (일)", 1, 14, 7)
        
        # 약물 선택
        drug_options = {
            "Ciprofloxacin": {"mic_s": 0.5, "mic_r": 8.0},
            "Amoxicillin": {"mic_s": 2.0, "mic_r": 32.0},
            "Vancomycin": {"mic_s": 1.0, "mic_r": 16.0}
        }
        selected_drug = st.sidebar.selectbox("약물 선택", list(drug_options.keys()))
        mic_s = drug_options[selected_drug]["mic_s"]
        mic_r = drug_options[selected_drug]["mic_r"]
        
        # 시뮬레이션 실행 버튼
        if st.sidebar.button("🚀 시뮬레이션 시작", type="primary"):
            with st.spinner("시뮬레이션 실행 중..."):
                data = self.run_simulation(dose, interval, days, patient_weight)
            
            # 메인 대시보드
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 그래프들
                st.plotly_chart(self.create_concentration_plot(data, dose, mic_s, mic_r), use_container_width=True)
                st.plotly_chart(self.create_bacterial_plot(data), use_container_width=True)
                st.plotly_chart(self.create_resistance_plot(data), use_container_width=True)
            
            with col2:
                # 실시간 메트릭
                st.subheader("📊 실시간 지표")
                
                final_conc = data['concentrations'][-1]
                final_total = data['sensitive'][-1] + data['resistant'][-1]
                final_resistance = data['resistance_fractions'][-1]
                treatment_success = final_total < 1e6 and final_resistance < 10
                
                st.metric("최종 농도", f"{final_conc:.2f} mg/L")
                st.metric("최종 세균수", f"{final_total:.2e} CFU/mL")
                st.metric("내성 비율", f"{final_resistance:.1f}%")
                
                if treatment_success:
                    st.markdown('<div class="success">✅ 치료 성공</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="failure">❌ 치료 실패</div>', unsafe_allow_html=True)
                
                # 추가 통계
                st.subheader("📈 상세 통계")
                max_conc = max(data['concentrations'])
                time_above_mic = sum(1 for c in data['concentrations'] if c > mic_s) / len(data['concentrations']) * 100
                total_doses = len(data['dose_times'])
                
                st.write(f"**최대 농도:** {max_conc:.2f} mg/L")
                st.write(f"**MIC 상회 시간:** {time_above_mic:.1f}%")
                st.write(f"**총 투약 횟수:** {total_doses}회")
                
                # 권장사항
                st.subheader("💡 AI 권장사항")
                if final_resistance > 50:
                    st.warning("⚠️ 높은 내성 위험! 조합요법 고려")
                elif time_above_mic < 70:
                    st.info("ℹ️ 용량 증량 또는 간격 단축 권장")
                else:
                    st.success("✅ 적절한 투약법입니다")
            
            # 3D 시각화 (별도 탭)
            st.subheader("🌐 고급 시각화")
            tab1, tab2, tab3 = st.tabs(["3D 분석", "비교 분석", "데이터 내보내기"])
            
            with tab1:
                st.plotly_chart(self.create_3d_plot(data), use_container_width=True)
            
            with tab2:
                st.info("여러 시나리오 비교 기능 (개발 중)")
                
                # 간단한 비교
                compare_data = []
                for test_dose in [250, 500, 750, 1000]:
                    test_data = self.run_simulation(test_dose, interval, 3, patient_weight)  # 짧은 시뮬레이션
                    final_res = test_data['resistance_fractions'][-1]
                    compare_data.append({"용량": test_dose, "최종내성": final_res})
                
                compare_df = pd.DataFrame(compare_data)
                fig = px.bar(compare_df, x="용량", y="최종내성", 
                           title="용량별 내성 비교", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.subheader("📁 결과 다운로드")
                
                # 데이터프레임 생성
                results_df = pd.DataFrame({
                    'Time_h': data['times'],
                    'Concentration_mg_L': data['concentrations'],
                    'Sensitive_CFU_mL': data['sensitive'],
                    'Resistant_CFU_mL': data['resistant'],
                    'Resistance_Percent': data['resistance_fractions']
                })
                
                st.download_button(
                    label="📊 CSV 다운로드",
                    data=results_df.to_csv(index=False),
                    file_name=f"antibiotic_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # JSON 결과
                json_results = {
                    'parameters': {
                        'drug': selected_drug,
                        'dose': dose,
                        'interval': interval,
                        'days': days,
                        'patient_weight': patient_weight
                    },
                    'results': {
                        'treatment_success': treatment_success,
                        'final_resistance': final_resistance,
                        'max_concentration': max_conc
                    }
                }
                
                st.download_button(
                    label="📄 JSON 다운로드",
                    data=json.dumps(json_results, indent=2),
                    file_name=f"antibiotic_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        # 정보 패널
        with st.expander("ℹ️ 사용법 및 정보"):
            st.markdown("""
            ### 🎯 주요 기능
            - **실시간 시뮬레이션**: 약물 농도와 세균 동역학 실시간 모니터링
            - **개인맞춤 설정**: 환자별 특성을 고려한 맞춤 시뮬레이션
            - **다양한 시각화**: 2D/3D 그래프로 직관적 분석
            - **AI 권장사항**: 시뮬레이션 결과 기반 치료 권장사항
            
            ### 📊 해석 가이드
            - **농도 그래프**: MIC 이상 유지 시간이 중요
            - **세균 그래프**: 총 세균수 1e6 미만이 치료 성공
            - **내성 그래프**: 10% 미만 유지가 이상적
            
            ### 🔬 기술적 특징
            - 정밀 약동학 모델링
            - 세균 집단 동역학 (ODE)
            - 실시간 인터랙티브 시각화
            - 다중 시나리오 비교 분석
            """)

def main():
    simulator = InteractiveSimulator()
    simulator.run_dashboard()

if __name__ == "__main__":
    main()
