#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
항생제 내성 진화 AI 시뮬레이터 - 메인 프로그램
Samsung Innovation Challenge 2025

완벽한 실시간 시각화 및 비선형 모델링
"""

import os
import sys
import locale
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, CheckButtons
import seaborn as sns
import pandas as pd
import time
import threading
import json
from datetime import datetime
import warnings
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 로케일 설정
try:
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Korean_Korea.949')
    except:
        pass

warnings.filterwarnings('ignore')

class PerfectAntibioticSimulator:
    def __init__(self):
        """완벽한 항생제 시뮬레이터 초기화"""
        
        # 스타일 설정
        plt.style.use('dark_background')
        sns.set_style("darkgrid")
        
        # 시뮬레이션 파라미터
        self.reset_parameters()
        
        # GUI 상태
        self.running = False
        self.paused = False
        self.animation = None
        
        # 모델 선택
        self.model_type = "nonlinear"  # linear, nonlinear, stochastic
        
        # 결과 저장 디렉토리
        os.makedirs("results", exist_ok=True)
        os.makedirs("figs", exist_ok=True)
        
        print("🧬 완벽한 항생제 내성 진화 AI 시뮬레이터 초기화 완료!")
        
    def reset_parameters(self):
        """파라미터 초기화"""
        # 시간 파라미터
        self.current_time = 0
        self.max_time = 168  # 7일 = 168시간
        self.dt = 0.1  # 시간 단계
        
        # 환자 파라미터 (비선형 개인맞춤)
        self.patient = {
            'age': 65,
            'weight': 70,
            'creatinine_clearance': 100,
            'genetic_polymorphism': 1.0,  # CYP450 활성도
            'comorbidity_factor': 0.8,    # 동반질환 영향
            'immune_status': 1.0          # 면역 상태
        }
        
        # 비선형 약동학 파라미터
        self.pk_params = {
            'dose': 500,
            'interval': 12,
            'ka': 1.5,      # 흡수율 상수
            'ke': 0.173,    # 제거율 상수
            'vd': 175,      # 분포용적
            'f': 0.85,      # 생체이용률
            'protein_binding': 0.3,  # 단백질 결합률
            'saturation_conc': 50    # 포화 농도
        }
        
        # 비선형 세균 동역학 파라미터
        self.pd_params = {
            'S0': 1e8,      # 초기 감수성균
            'R0': 1e4,      # 초기 내성균
            'growth_rate_s': 0.693,
            'growth_rate_r': 0.623,
            'mutation_rate': 1e-8,
            'mic_s': 0.5,
            'mic_r': 8.0,
            'mpc': 2.0,
            'emax': 4.0,
            'hill': 2.0,
            'carrying_capacity': 1e12,
            'competition_factor': 0.1,  # 경쟁 인자
            'adaptive_resistance': 0.01  # 적응 내성
        }
        
        # 현재 상태
        self.S = self.pd_params['S0']
        self.R = self.pd_params['R0']
        self.depot_amount = 0  # 저장고 약물량
        
        # 데이터 저장
        self.data = {
            'times': [],
            'concentrations': [],
            'free_concentrations': [],  # 유리 농도
            'depot_amounts': [],
            's_populations': [],
            'r_populations': [],
            'total_populations': [],
            'resistance_fractions': [],
            'growth_rates_s': [],
            'growth_rates_r': [],
            'kill_rates_s': [],
            'kill_rates_r': [],
            'dose_events': [],
            'efficacy_index': [],  # 치료 효과 지수
            'resistance_pressure': []  # 내성 압력
        }
        
    def calculate_personalized_pk(self, patient):
        """개인맞춤 약동학 파라미터 계산"""
        # 나이에 따른 신기능 보정
        age_factor = 1.0 - (patient['age'] - 30) * 0.005 if patient['age'] > 30 else 1.0
        
        # 신기능에 따른 제거율 보정
        renal_factor = patient['creatinine_clearance'] / 120.0
        
        # 유전자 다형성 보정
        genetic_factor = patient['genetic_polymorphism']
        
        # 동반질환 보정
        comorbidity_factor = patient['comorbidity_factor']
        
        # 개인맞춤 파라미터
        ke_personal = self.pk_params['ke'] * renal_factor * genetic_factor * age_factor
        vd_personal = self.pk_params['vd'] * patient['weight'] / 70.0 * comorbidity_factor
        
        return ke_personal, vd_personal
    
    def nonlinear_pk_model(self, t, depot, dose_times):
        """비선형 약동학 모델 (Michaelis-Menten 동역학)"""
        ke_personal, vd_personal = self.calculate_personalized_pk(self.patient)
        
        # 투약 확인
        recent_dose = 0
        for dose_time in dose_times:
            if abs(t - dose_time) < self.dt:
                recent_dose = self.pk_params['dose'] * self.pk_params['f']
                break
        
        # 흡수 (1차 동역학)
        absorption = self.pk_params['ka'] * depot
        
        # 분포용적에서의 농도
        if vd_personal > 0:
            plasma_conc = (depot / vd_personal) if depot > 0 else 0
        else:
            plasma_conc = 0
        
        # 비선형 제거 (Michaelis-Menten)
        km = self.pk_params['saturation_conc']
        elimination = (ke_personal * plasma_conc) / (1 + plasma_conc / km)
        
        # 저장고 변화율
        ddepot_dt = recent_dose - absorption - elimination
        
        # 유리 농도 (단백질 결합 고려)
        free_conc = plasma_conc * (1 - self.pk_params['protein_binding'])
        
        return ddepot_dt, plasma_conc, free_conc
    
    def sigmoid_kill_curve(self, conc, mic, emax, hill, adaptive_factor=1.0):
        """시그모이드 살균 곡선 (Hill equation with adaptation)"""
        if conc <= 0:
            return 0
        
        # 적응 내성 고려
        effective_mic = mic * adaptive_factor
        
        # Hill equation with sigmoidicity
        kill_rate = emax * (conc ** hill) / (effective_mic ** hill + conc ** hill)
        
        # 농도가 매우 높을 때 포화 효과
        saturation_factor = 1 / (1 + conc / (10 * mic))
        
        return kill_rate * saturation_factor
    
    def nonlinear_pd_model(self, conc_free, S, R):
        """비선형 약력학 모델"""
        # 현재 집단 크기
        total_pop = S + R
        
        # 운반 용량 효과 (로지스틱 성장)
        carrying_effect = 1 - total_pop / self.pd_params['carrying_capacity']
        carrying_effect = max(0, carrying_effect)
        
        # 경쟁 효과 (종간 경쟁)
        competition_s = 1 - self.pd_params['competition_factor'] * R / (S + R + 1)
        competition_r = 1 - self.pd_params['competition_factor'] * S / (S + R + 1)
        
        # 적응 내성 인자 (시간에 따른 MIC 증가)
        adaptive_factor_s = 1.0
        adaptive_factor_r = 1 + self.pd_params['adaptive_resistance'] * (conc_free / self.pd_params['mic_r'])
        
        # 성장률 (영양소 제한 고려)
        growth_s = self.pd_params['growth_rate_s'] * carrying_effect * competition_s
        growth_r = self.pd_params['growth_rate_r'] * carrying_effect * competition_r
        
        # 살균률 (비선형 효과)
        kill_s = self.sigmoid_kill_curve(
            conc_free, self.pd_params['mic_s'], 
            self.pd_params['emax'], self.pd_params['hill'], 
            adaptive_factor_s
        )
        
        kill_r = self.sigmoid_kill_curve(
            conc_free, self.pd_params['mic_r'], 
            self.pd_params['emax'], self.pd_params['hill'], 
            adaptive_factor_r
        )
        
        # 돌연변이 (농도 의존적)
        mutation_pressure = 1 + (conc_free / self.pd_params['mpc']) ** 2
        mutation_rate = self.pd_params['mutation_rate'] * mutation_pressure
        
        # 면역 반응 (환자 의존적)
        immune_kill_s = 0.01 * self.patient['immune_status'] * S / (1 + S / 1e9)
        immune_kill_r = 0.005 * self.patient['immune_status'] * R / (1 + R / 1e9)
        
        # 변화율 계산
        dS_dt = growth_s * S - kill_s * S - mutation_rate * S - immune_kill_s
        dR_dt = growth_r * R - kill_r * R + mutation_rate * S - immune_kill_r
        
        # 음수 방지
        dS_dt = dS_dt if S + dS_dt * self.dt > 0 else -S / self.dt
        dR_dt = dR_dt if R + dR_dt * self.dt > 0 else -R / self.dt
        
        return dS_dt, dR_dt, growth_s, growth_r, kill_s, kill_r
    
    def update_simulation_step(self):
        """시뮬레이션 한 스텝 업데이트"""
        t = self.current_time
        
        # 투약 시점 확인
        dose_times = np.arange(0, self.max_time, self.pk_params['interval'])
        
        # 약동학 계산
        ddepot_dt, plasma_conc, free_conc = self.nonlinear_pk_model(t, self.depot_amount, dose_times)
        
        # 저장고 업데이트
        self.depot_amount = max(0, self.depot_amount + ddepot_dt * self.dt)
        
        # 약력학 계산
        dS_dt, dR_dt, growth_s, growth_r, kill_s, kill_r = self.nonlinear_pd_model(
            free_conc, self.S, self.R
        )
        
        # 세균 집단 업데이트
        self.S = max(0, self.S + dS_dt * self.dt)
        self.R = max(0, self.R + dR_dt * self.dt)
        
        # 데이터 저장
        total_pop = self.S + self.R
        resistance_frac = (self.R / total_pop * 100) if total_pop > 0 else 0
        
        # 치료 효과 지수 계산
        initial_total = self.pd_params['S0'] + self.pd_params['R0']
        log_reduction = np.log10(initial_total / max(total_pop, 1))
        efficacy = log_reduction - resistance_frac / 10  # 내성 패널티
        
        # 내성 압력 계산
        if self.pd_params['mpc'] > 0:
            resistance_pressure = (free_conc / self.pd_params['mpc']) ** 2
        else:
            resistance_pressure = 0
        
        self.data['times'].append(t)
        self.data['concentrations'].append(plasma_conc)
        self.data['free_concentrations'].append(free_conc)
        self.data['depot_amounts'].append(self.depot_amount)
        self.data['s_populations'].append(self.S)
        self.data['r_populations'].append(self.R)
        self.data['total_populations'].append(total_pop)
        self.data['resistance_fractions'].append(resistance_frac)
        self.data['growth_rates_s'].append(growth_s)
        self.data['growth_rates_r'].append(growth_r)
        self.data['kill_rates_s'].append(kill_s)
        self.data['kill_rates_r'].append(kill_r)
        self.data['efficacy_index'].append(efficacy)
        self.data['resistance_pressure'].append(resistance_pressure)
        
        # 투약 이벤트 기록
        if any(abs(t - dt) < self.dt for dt in dose_times):
            self.data['dose_events'].append(t)
        
        self.current_time += self.dt
        
    def setup_perfect_gui(self):
        """완벽한 GUI 설정"""
        # 큰 figure 생성
        self.fig = plt.figure(figsize=(20, 14))
        self.fig.patch.set_facecolor('black')
        
        # 한글 제목
        title_text = "🧬 완벽한 항생제 내성 진화 AI 시뮬레이터 v2.0\n" + \
                    "Samsung Innovation Challenge 2025 - 비선형 모델링"
        self.fig.suptitle(title_text, fontsize=18, fontweight='bold', color='cyan')
        
        # 복잡한 레이아웃
        gs = self.fig.add_gridspec(4, 4, hspace=0.4, wspace=0.3)
        
        # 1. 약물 농도 (상단 좌측 2칸)
        self.ax1 = self.fig.add_subplot(gs[0, :2])
        self.setup_concentration_plot()
        
        # 2. 세균 동역학 (상단 우측 2칸)
        self.ax2 = self.fig.add_subplot(gs[0, 2:])
        self.setup_bacterial_plot()
        
        # 3. 내성 분석 (중간 좌측)
        self.ax3 = self.fig.add_subplot(gs[1, 0])
        self.setup_resistance_plot()
        
        # 4. 치료 효과 (중간 중앙)
        self.ax4 = self.fig.add_subplot(gs[1, 1])
        self.setup_efficacy_plot()
        
        # 5. 3D 공간 (중간 우측 2칸)
        self.ax5 = self.fig.add_subplot(gs[1, 2:], projection='3d')
        self.setup_3d_plot()
        
        # 6. 실시간 통계 (하단 좌측)
        self.ax6 = self.fig.add_subplot(gs[2, 0])
        self.setup_stats_plot()
        
        # 7. 환자 상태 (하단 중앙)
        self.ax7 = self.fig.add_subplot(gs[2, 1])
        self.setup_patient_plot()
        
        # 8. AI 예측 (하단 우측 2칸)
        self.ax8 = self.fig.add_subplot(gs[2, 2:])
        self.setup_prediction_plot()
        
        # 9. 컨트롤 패널 (최하단)
        self.setup_control_panel(gs)
        
    def setup_concentration_plot(self):
        """농도 그래프 설정"""
        self.ax1.set_title('💊 실시간 약물 농도 (비선형 PK)', fontweight='bold', color='cyan')
        self.ax1.set_xlabel('시간 (시간)')
        self.ax1.set_ylabel('농도 (mg/L)')
        self.ax1.set_yscale('log')
        self.ax1.grid(True, alpha=0.3)
        
        # 여러 선 초기화
        self.line_total_conc, = self.ax1.plot([], [], 'cyan', linewidth=3, label='총 농도')
        self.line_free_conc, = self.ax1.plot([], [], 'yellow', linewidth=2, label='유리 농도')
        
        # MIC/MPC 선
        self.ax1.axhline(y=self.pd_params['mic_s'], color='green', linestyle='--', alpha=0.7, label='MIC (감수성)')
        self.ax1.axhline(y=self.pd_params['mic_r'], color='red', linestyle='--', alpha=0.7, label='MIC (내성)')
        self.ax1.axhline(y=self.pd_params['mpc'], color='orange', linestyle=':', alpha=0.7, label='MPC')
        
        self.ax1.legend(loc='upper right')
        
    def setup_bacterial_plot(self):
        """세균 동역학 그래프 설정"""
        self.ax2.set_title('🦠 비선형 세균 집단 동역학', fontweight='bold', color='lightgreen')
        self.ax2.set_xlabel('시간 (시간)')
        self.ax2.set_ylabel('세균 수 (CFU/mL)')
        self.ax2.set_yscale('log')
        self.ax2.grid(True, alpha=0.3)
        
        self.line_s, = self.ax2.plot([], [], 'green', linewidth=3, label='감수성균')
        self.line_r, = self.ax2.plot([], [], 'red', linewidth=3, label='내성균')
        self.line_total, = self.ax2.plot([], [], 'white', linewidth=2, linestyle='--', label='총 세균수')
        
        # 임계선
        self.ax2.axhline(y=1e6, color='orange', linestyle=':', alpha=0.7, label='치료 실패 임계값')
        
        self.ax2.legend()
        
    def setup_resistance_plot(self):
        """내성 분석 그래프"""
        self.ax3.set_title('📊 내성 비율', fontweight='bold', color='orange')
        self.ax3.set_xlabel('시간 (시간)')
        self.ax3.set_ylabel('내성 비율 (%)')
        self.ax3.grid(True, alpha=0.3)
        
        self.line_resistance, = self.ax3.plot([], [], 'orange', linewidth=3)
        self.ax3.axhline(y=10, color='red', linestyle=':', alpha=0.7, label='위험 임계값')
        self.ax3.set_ylim(0, 100)
        
    def setup_efficacy_plot(self):
        """치료 효과 그래프"""
        self.ax4.set_title('🎯 치료 효과 지수', fontweight='bold', color='lightblue')
        self.ax4.set_xlabel('시간 (시간)')
        self.ax4.set_ylabel('효과 지수')
        self.ax4.grid(True, alpha=0.3)
        
        self.line_efficacy, = self.ax4.plot([], [], 'lightblue', linewidth=3)
        self.ax4.axhline(y=0, color='white', linestyle='-', alpha=0.5)
        
    def setup_3d_plot(self):
        """3D 시각화"""
        self.ax5.set_title('🌐 3D 시공간 분석', fontweight='bold', color='magenta')
        self.ax5.set_xlabel('시간 (h)')
        self.ax5.set_ylabel('농도 (mg/L)')
        self.ax5.set_zlabel('내성률 (%)')
        
    def setup_stats_plot(self):
        """통계 패널"""
        self.ax6.set_title('📈 실시간 통계', fontweight='bold', color='white')
        self.ax6.axis('off')
        
    def setup_patient_plot(self):
        """환자 상태 패널"""
        self.ax7.set_title('👤 환자 상태', fontweight='bold', color='lightcoral')
        self.ax7.axis('off')
        
    def setup_prediction_plot(self):
        """AI 예측 패널"""
        self.ax8.set_title('🤖 AI 예측 및 권장사항', fontweight='bold', color='gold')
        self.ax8.set_xlabel('시간 (시간)')
        self.ax8.set_ylabel('예측값')
        self.ax8.grid(True, alpha=0.3)
        
    def setup_control_panel(self, gs):
        """컨트롤 패널 설정"""
        # 슬라이더들
        ax_dose = plt.axes([0.1, 0.02, 0.2, 0.03])
        self.slider_dose = Slider(ax_dose, '용량 (mg)', 100, 2000, valinit=self.pk_params['dose'], valfmt='%0.0f')
        self.slider_dose.on_changed(self.update_dose)
        
        ax_interval = plt.axes([0.35, 0.02, 0.2, 0.03])
        self.slider_interval = Slider(ax_interval, '간격 (h)', 6, 24, valinit=self.pk_params['interval'], valfmt='%0.0f')
        self.slider_interval.on_changed(self.update_interval)
        
        ax_age = plt.axes([0.6, 0.02, 0.15, 0.03])
        self.slider_age = Slider(ax_age, '나이', 20, 90, valinit=self.patient['age'], valfmt='%0.0f')
        self.slider_age.on_changed(self.update_age)
        
        # 버튼들
        ax_start = plt.axes([0.8, 0.02, 0.08, 0.03])
        self.btn_start = Button(ax_start, '시작')
        self.btn_start.on_clicked(self.toggle_simulation)
        
        ax_reset = plt.axes([0.9, 0.02, 0.08, 0.03])
        self.btn_reset = Button(ax_reset, '리셋')
        self.btn_reset.on_clicked(self.reset_simulation)
        
    def update_dose(self, val):
        self.pk_params['dose'] = self.slider_dose.val
        
    def update_interval(self, val):
        self.pk_params['interval'] = self.slider_interval.val
        
    def update_age(self, val):
        self.patient['age'] = self.slider_age.val
        
    def toggle_simulation(self, event):
        if self.running:
            self.running = False
            self.btn_start.label.set_text('시작')
        else:
            self.running = True
            self.btn_start.label.set_text('정지')
            
    def reset_simulation(self, event):
        self.running = False
        self.reset_parameters()
        self.btn_start.label.set_text('시작')
        self.clear_plots()
        
    def clear_plots(self):
        """그래프 초기화"""
        for line in [self.line_total_conc, self.line_free_conc, self.line_s, 
                    self.line_r, self.line_total, self.line_resistance, self.line_efficacy]:
            line.set_data([], [])
        
    def update_plots(self):
        """모든 그래프 업데이트"""
        if not self.data['times']:
            return
            
        times = self.data['times']
        
        # 1. 농도 그래프
        self.line_total_conc.set_data(times, self.data['concentrations'])
        self.line_free_conc.set_data(times, self.data['free_concentrations'])
        
        # 투약 시점 표시
        for dose_time in self.data['dose_events']:
            if dose_time in times[-50:]:  # 최근 50개 포인트만
                self.ax1.axvline(x=dose_time, color='yellow', alpha=0.6, linewidth=1)
        
        # 2. 세균 그래프
        self.line_s.set_data(times, self.data['s_populations'])
        self.line_r.set_data(times, self.data['r_populations'])
        self.line_total.set_data(times, self.data['total_populations'])
        
        # 3. 내성 그래프
        self.line_resistance.set_data(times, self.data['resistance_fractions'])
        
        # 4. 효과 그래프
        self.line_efficacy.set_data(times, self.data['efficacy_index'])
        
        # 축 범위 자동 조정
        self.auto_scale_axes()
        
        # 5. 3D 그래프 업데이트
        self.update_3d_plot()
        
        # 6. 통계 업데이트
        self.update_stats()
        
        # 7. 환자 상태 업데이트
        self.update_patient_status()
        
        # 8. AI 예측 업데이트
        self.update_ai_prediction()
        
    def auto_scale_axes(self):
        """축 범위 자동 조정"""
        if len(self.data['times']) < 2:
            return
            
        # 시간 범위 (최근 48시간)
        current_time = self.data['times'][-1]
        time_window = max(48, current_time * 0.3)
        time_start = max(0, current_time - time_window)
        
        # 농도 그래프
        self.ax1.set_xlim(time_start, current_time + 12)
        if self.data['concentrations']:
            conc_data = self.data['concentrations'][-200:]
            if any(c > 0 for c in conc_data):
                self.ax1.set_ylim(0.01, max(conc_data) * 2)
        
        # 세균 그래프
        self.ax2.set_xlim(time_start, current_time + 12)
        if self.data['total_populations']:
            total_data = self.data['total_populations'][-200:]
            min_pop = min([p for p in total_data if p > 0]) if any(p > 0 for p in total_data) else 1
            max_pop = max(total_data)
            self.ax2.set_ylim(min_pop / 10, max_pop * 10)
        
        # 내성 그래프
        self.ax3.set_xlim(time_start, current_time + 12)
        
        # 효과 그래프
        self.ax4.set_xlim(time_start, current_time + 12)
        if self.data['efficacy_index']:
            eff_data = self.data['efficacy_index'][-200:]
            self.ax4.set_ylim(min(eff_data) - 1, max(eff_data) + 1)
        
    def update_3d_plot(self):
        """3D 그래프 업데이트"""
        self.ax5.clear()
        self.ax5.set_title('🌐 3D 시공간 분석', fontweight='bold', color='magenta')
        
        if len(self.data['times']) > 10:
            # 최근 데이터만 사용
            n_points = min(100, len(self.data['times']))
            times_3d = self.data['times'][-n_points:]
            conc_3d = self.data['free_concentrations'][-n_points:]
            resist_3d = self.data['resistance_fractions'][-n_points:]
            
            # 색상 맵핑 (시간에 따라)
            colors = plt.cm.viridis(np.linspace(0, 1, len(times_3d)))
            
            # 3D 산점도
            self.ax5.scatter(times_3d, conc_3d, resist_3d, c=colors, s=30)
            
            # 궤적 선
            self.ax5.plot(times_3d, conc_3d, resist_3d, 'white', alpha=0.6, linewidth=1)
            
            self.ax5.set_xlabel('시간 (h)')
            self.ax5.set_ylabel('유리농도 (mg/L)')
            self.ax5.set_zlabel('내성률 (%)')
        
    def update_stats(self):
        """실시간 통계 업데이트"""
        self.ax6.clear()
        self.ax6.set_title('📈 실시간 통계', fontweight='bold', color='white')
        self.ax6.axis('off')
        
        if self.data['times']:
            current_time = self.data['times'][-1]
            current_conc = self.data['free_concentrations'][-1]
            current_total = self.data['total_populations'][-1]
            current_resistance = self.data['resistance_fractions'][-1]
            current_efficacy = self.data['efficacy_index'][-1]
            
            # 투약 횟수
            dose_count = len(self.data['dose_events'])
            
            # 평균 내성 압력
            avg_pressure = np.mean(self.data['resistance_pressure'][-10:]) if self.data['resistance_pressure'] else 0
            
            # 치료 성공 예측
            success_prob = 1 / (1 + np.exp(-(current_efficacy - 0.5))) * 100
            
            stats_text = f"""
📅 시간: {current_time:.1f} / {self.max_time} h
💊 유리농도: {current_conc:.3f} mg/L
🦠 총 세균수: {current_total:.2e}
📊 내성률: {current_resistance:.1f}%
🎯 효과지수: {current_efficacy:.2f}
💉 투약횟수: {dose_count}회
⚡ 내성압력: {avg_pressure:.3f}
🎲 성공확률: {success_prob:.1f}%

📈 진행률: {current_time/self.max_time*100:.1f}%
            """
            
            self.ax6.text(0.05, 0.95, stats_text, transform=self.ax6.transAxes,
                         fontsize=9, verticalalignment='top', fontfamily='monospace',
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="navy", alpha=0.8))
        
    def update_patient_status(self):
        """환자 상태 업데이트"""
        self.ax7.clear()
        self.ax7.set_title('👤 환자 상태', fontweight='bold', color='lightcoral')
        self.ax7.axis('off')
        
        # 개인맞춤 파라미터 표시
        ke_personal, vd_personal = self.calculate_personalized_pk(self.patient)
        
        patient_text = f"""
👤 환자정보:
   나이: {self.patient['age']:.0f}세
   체중: {self.patient['weight']:.0f}kg
   신기능: {self.patient['creatinine_clearance']:.0f}
   유전형: {self.patient['genetic_polymorphism']:.2f}
   동반질환: {self.patient['comorbidity_factor']:.2f}
   면역상태: {self.patient['immune_status']:.2f}

🧬 개인맞춤 PK:
   제거율: {ke_personal:.3f} /h
   분포용적: {vd_personal:.0f} L
   
💊 현재 투약:
   용량: {self.pk_params['dose']:.0f} mg
   간격: {self.pk_params['interval']:.0f} h
        """
        
        self.ax7.text(0.05, 0.95, patient_text, transform=self.ax7.transAxes,
                     fontsize=9, verticalalignment='top', fontfamily='monospace',
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="darkred", alpha=0.8))
        
    def update_ai_prediction(self):
        """AI 예측 및 권장사항"""
        self.ax8.clear()
        self.ax8.set_title('🤖 AI 예측 및 권장사항', fontweight='bold', color='gold')
        self.ax8.axis('off')
        
        if len(self.data['times']) > 10:
            # 간단한 선형 예측
            recent_resistance = self.data['resistance_fractions'][-10:]
            recent_times = self.data['times'][-10:]
            
            if len(recent_resistance) > 1:
                # 내성 변화율 계산
                resistance_slope = (recent_resistance[-1] - recent_resistance[0]) / (recent_times[-1] - recent_times[0])
                
                # 예측 시간 (다음 24시간)
                future_times = np.linspace(recent_times[-1], recent_times[-1] + 24, 50)
                predicted_resistance = recent_resistance[-1] + resistance_slope * (future_times - recent_times[-1])
                
                # 예측 그래프
                self.ax8.plot(recent_times, recent_resistance, 'gold', linewidth=2, label='실제')
                self.ax8.plot(future_times, predicted_resistance, 'orange', linestyle='--', linewidth=2, label='예측')
                self.ax8.axhline(y=10, color='red', linestyle=':', alpha=0.7, label='위험선')
                
                self.ax8.set_xlabel('시간 (h)')
                self.ax8.set_ylabel('내성률 (%)')
                self.ax8.legend()
                self.ax8.grid(True, alpha=0.3)
                
                # AI 권장사항
                if resistance_slope > 1:  # 내성이 빠르게 증가
                    recommendation = "⚠️ 내성 급증! 조합요법 권장"
                elif recent_resistance[-1] > 50:
                    recommendation = "🔴 높은 내성! 약물 변경 고려"
                elif self.data['free_concentrations'][-1] < self.pd_params['mic_s']:
                    recommendation = "📈 용량 증량 권장"
                else:
                    recommendation = "✅ 현재 치료법 유지"
                
                self.ax8.text(0.02, 0.98, f"🤖 AI 권장: {recommendation}", 
                             transform=self.ax8.transAxes, fontsize=12, fontweight='bold',
                             bbox=dict(boxstyle="round,pad=0.3", facecolor="gold", alpha=0.8),
                             verticalalignment='top')
        
    def animate(self, frame):
        """애니메이션 프레임"""
        if self.running and self.current_time < self.max_time:
            self.update_simulation_step()
            self.update_plots()
            
        if self.current_time >= self.max_time:
            self.running = False
            self.btn_start.label.set_text('완료')
            self.save_results()
            
        return []
    
    def save_results(self):
        """결과 저장"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'model_type': self.model_type,
            'parameters': {
                'patient': self.patient,
                'pk_params': self.pk_params,
                'pd_params': self.pd_params
            },
            'final_results': {
                'final_time': self.current_time,
                'final_concentration': self.data['free_concentrations'][-1] if self.data['free_concentrations'] else 0,
                'final_total_bacteria': self.data['total_populations'][-1] if self.data['total_populations'] else 0,
                'final_resistance_fraction': self.data['resistance_fractions'][-1] if self.data['resistance_fractions'] else 0,
                'final_efficacy': self.data['efficacy_index'][-1] if self.data['efficacy_index'] else 0,
                'treatment_success': (self.data['total_populations'][-1] < 1e6 and 
                                    self.data['resistance_fractions'][-1] < 10) if self.data['total_populations'] else False
            },
            'time_series_data': self.data
        }
        
        # JSON 저장
        with open('results/perfect_simulation_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # CSV 저장
        df = pd.DataFrame({
            'Time_h': self.data['times'],
            'Total_Concentration_mg_L': self.data['concentrations'],
            'Free_Concentration_mg_L': self.data['free_concentrations'],
            'Sensitive_CFU_mL': self.data['s_populations'],
            'Resistant_CFU_mL': self.data['r_populations'],
            'Total_CFU_mL': self.data['total_populations'],
            'Resistance_Percent': self.data['resistance_fractions'],
            'Efficacy_Index': self.data['efficacy_index'],
            'Resistance_Pressure': self.data['resistance_pressure']
        })
        
        df.to_csv('results/perfect_simulation_data.csv', index=False, encoding='utf-8-sig')
        
        print("\n✅ 완벽한 시뮬레이션 완료!")
        print(f"📊 결과 저장: results/perfect_simulation_results.json")
        print(f"📊 데이터 저장: results/perfect_simulation_data.csv")
        
        # 최종 요약
        final_success = results['final_results']['treatment_success']
        final_resistance = results['final_results']['final_resistance_fraction']
        final_efficacy = results['final_results']['final_efficacy']
        
        print(f"\n🎯 최종 결과:")
        print(f"   치료 성공: {'✅' if final_success else '❌'}")
        print(f"   최종 내성률: {final_resistance:.1f}%")
        print(f"   치료 효과: {final_efficacy:.2f}")
        
    def run_perfect_simulation(self):
        """완벽한 시뮬레이션 실행"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║           🧬 완벽한 항생제 내성 진화 AI 시뮬레이터            ║
║                Samsung Innovation Challenge 2025              ║
║                                                              ║
║  🎯 비선형 개인맞춤 모델링 | 🤖 AI 예측 시스템               ║
║  📊 실시간 다차원 시각화   | 🔬 3D 시공간 분석               ║
╚══════════════════════════════════════════════════════════════╝

🚀 혁신적 기능:
   ✅ 비선형 Michaelis-Menten 약동학
   ✅ 시그모이드 살균 곡선 모델
   ✅ 개인맞춤 유전자형 고려
   ✅ 적응 내성 및 경쟁 효과
   ✅ 실시간 8차원 시각화
   ✅ AI 기반 예측 및 권장
   ✅ 3D 시공간 궤적 분석
   ✅ 완벽한 한글 지원

💡 사용법:
   - 슬라이더: 실시간 파라미터 조정
   - '시작' 버튼: 시뮬레이션 시작/정지
   - '리셋' 버튼: 완전 초기화
   - 모든 그래프: 실시간 인터랙티브
        """)
        
        # GUI 설정
        self.setup_perfect_gui()
        
        # 애니메이션 시작
        self.animation = animation.FuncAnimation(
            self.fig, self.animate, 
            interval=50, blit=False, 
            repeat=True, cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()

def main():
    """메인 실행 함수"""
    print("🧬 완벽한 항생제 내성 진화 AI 시뮬레이터 초기화 중...")
    
    # 시뮬레이터 생성
    simulator = PerfectAntibioticSimulator()
    
    # 실행
    simulator.run_perfect_simulation()

if __name__ == "__main__":
    main()
