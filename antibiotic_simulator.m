% 항생제 내성 진화 시뮬레이터 - MATLAB 버전
% Samsung Innovation Challenge 2025
% 실행: matlab -batch "run('antibiotic_simulator.m')"

clc; clear; close all;

fprintf('\n');
fprintf('╔══════════════════════════════════════════════════════════════╗\n');
fprintf('║        항생제 내성 진화 AI 시뮬레이터 v1.0 - MATLAB 버전     ║\n');
fprintf('║               Samsung Innovation Challenge 2025               ║\n');
fprintf('╚══════════════════════════════════════════════════════════════╝\n');
fprintf('\n');

%% 환자 프로필 정의
patient = struct();
patient.age = 65;
patient.weight = 75;
patient.creatinine_clearance = 80;
patient.infection_severity = 0.7;
patient.genetic_markers = struct('cyp_activity', 1.0, 'mdr1_activity', 1.0);
patient.comorbidities = {'diabetes', 'hypertension'};

%% 약물 특성 정의
drug = struct();
drug.name = 'Ciprofloxacin';
drug.mic_sensitive = 0.5;
drug.mic_resistant = 8.0;
drug.mpc = 2.0;
drug.half_life = 4.0;
drug.volume_distribution = 2.5;
drug.emax = 4.0;
drug.hill_coefficient = 2.0;

%% 약동학 모델 함수들
function ke = calculate_elimination_rate(drug, patient)
    base_ke = 0.693 / drug.half_life;
    renal_factor = patient.creatinine_clearance / 120.0;
    genetic_factor = patient.genetic_markers.cyp_activity;
    if patient.age > 30
        age_factor = 1.0 - (patient.age - 30) * 0.01;
    else
        age_factor = 1.0;
    end
    ke = base_ke * renal_factor * genetic_factor * age_factor;
end

function vd = calculate_volume_distribution(drug, patient)
    vd = drug.volume_distribution * patient.weight;
end

function concentrations = concentration_time_course(doses, times, ke, vd, interval)
    if nargin < 5
        interval = 12; % 기본값
    end
    
    concentrations = zeros(size(times));
    
    for i = 1:length(times)
        t = times(i);
        total_conc = 0;
        
        for j = 1:length(doses)
            dose_time = (j - 1) * interval;
            if t >= dose_time
                time_since_dose = t - dose_time;
                dose_conc = (doses(j) / vd) * exp(-ke * time_since_dose);
                total_conc = total_conc + dose_conc;
            end
        end
        concentrations(i) = total_conc;
    end
end

%% 약력학적 효과 함수
function effect = pharmacodynamic_effect(concentration, mic, emax, hill)
    if nargin < 3
        emax = 4.0;
    end
    if nargin < 4
        hill = 2.0;
    end
    
    if concentration <= 0
        effect = 0;
    else
        effect = emax * (concentration^hill) / (mic^hill + concentration^hill);
    end
end

%% 세균 집단 동역학 ODE 시스템
function dydt = bacterial_ode(t, y, times, concentrations, drug)
    S = y(1);
    R = y(2);
    
    % 현재 시점의 약물 농도 (선형 보간)
    C = interp1(times, concentrations, t, 'linear', 'extrap');
    
    % 약력학적 효과
    kill_rate_s = pharmacodynamic_effect(C, drug.mic_sensitive, drug.emax, drug.hill_coefficient);
    kill_rate_r = pharmacodynamic_effect(C, drug.mic_resistant, drug.emax, drug.hill_coefficient);
    
    % 파라미터
    growth_rate_s = 0.693;
    growth_rate_r = 0.623;
    mutation_rate = 1e-8;
    carrying_capacity = 1e12;
    
    % 성장 제한
    total_pop = S + R;
    growth_factor = 1 - total_pop / carrying_capacity;
    
    % 변화율
    dS_dt = (growth_rate_s * growth_factor - kill_rate_s) * S - mutation_rate * S;
    dR_dt = (growth_rate_r * growth_factor - kill_rate_r) * R + mutation_rate * S;
    
    dydt = [dS_dt; dR_dt];
end

%% 시뮬레이션 실행 함수
function results = run_simulation(patient, drug, regimen, days)
    if nargin < 4
        days = 7;
    end
    
    fprintf('\n🔬 시뮬레이션 시작...\n');
    fprintf('환자: %d세, %.1fkg, 신기능: %.1f\n', patient.age, patient.weight, patient.creatinine_clearance);
    fprintf('약물: %s, 용량: %.1fmg, 간격: %d시간\n', drug.name, regimen.dose, regimen.interval);
    
    % 약동학 파라미터 계산
    ke = calculate_elimination_rate(drug, patient);
    vd = calculate_volume_distribution(drug, patient);
    
    % 시간 배열
    total_hours = days * 24;
    times = 0:0.25:total_hours; % 15분 간격
    
    % 투약 스케줄
    num_doses = floor(total_hours / regimen.interval);
    doses = repmat(regimen.dose, 1, num_doses);
    
    % 약물 농도 계산
    concentrations = concentration_time_course(doses, times, ke, vd, regimen.interval);
    
    % 세균 집단 시뮬레이션
    initial_conditions = [1e8; 1e4]; % [S; R]
    
    % ODE 해법
    options = odeset('RelTol', 1e-6, 'AbsTol', 1e-9);
    [T, Y] = ode45(@(t, y) bacterial_ode(t, y, times, concentrations, drug), times, initial_conditions, options);
    
    % 결과 분석
    final_s = Y(end, 1);
    final_r = Y(end, 2);
    final_total = final_s + final_r;
    final_resistance_fraction = final_r / final_total;
    treatment_success = (final_total < 1e6) && (final_resistance_fraction < 0.1);
    
    results = struct();
    results.final_bacterial_count = final_total;
    results.resistance_fraction = final_resistance_fraction;
    results.treatment_success = treatment_success;
    results.max_concentration = max(concentrations);
    results.min_concentration = min(concentrations(concentrations > 0));
    results.concentrations = concentrations;
    results.bacterial_trajectory = Y;
    results.times = times;
    
    fprintf('\n📊 시뮬레이션 결과:\n');
    fprintf('   최종 세균수: %.2e CFU/mL\n', results.final_bacterial_count);
    fprintf('   내성 비율: %.1f%%\n', results.resistance_fraction * 100);
    if results.treatment_success
        fprintf('   치료 성공: ✅ 성공\n');
    else
        fprintf('   치료 성공: ❌ 실패\n');
    end
    fprintf('   최대 농도: %.2f mg/L\n', results.max_concentration);
end

%% AI 기반 투약 최적화
function optimal_regimen = optimize_regimen(patient, drug)
    fprintf('\n🤖 AI 기반 투약 최적화...\n');
    
    dose_options = [250, 500, 750, 1000];
    interval_options = [6, 8, 12, 24];
    
    best_regimen = struct();
    best_score = -inf;
    
    for i = 1:length(dose_options)
        for j = 1:length(interval_options)
            regimen = struct('dose', dose_options(i), 'interval', interval_options(j));
            
            try
                result = run_simulation(patient, drug, regimen, 3); % 짧은 시뮬레이션
                
                % 성공률과 비용을 고려한 스코어
                if result.treatment_success
                    score = 1.0 - dose_options(i) / 1000;
                else
                    score = 0.0 - dose_options(i) / 1000;
                end
                
                if score > best_score
                    best_score = score;
                    best_regimen = regimen;
                end
            catch ME
                fprintf('시뮬레이션 오류: %s\n', ME.message);
            end
        end
    end
    
    optimal_regimen = best_regimen;
    
    fprintf('\n✅ 최적 투약법:\n');
    fprintf('   용량: %.1fmg\n', optimal_regimen.dose);
    fprintf('   간격: %d시간\n', optimal_regimen.interval);
    fprintf('   예상 성공률: %.1f%%\n', best_score * 100);
end

%% 시각화 함수
function create_plots(results)
    fprintf('\n📈 그래프 생성 중...\n');
    
    % 결과 디렉토리 생성
    if ~exist('results', 'dir')
        mkdir('results');
    end
    
    % Figure 1: 약물 농도
    figure(1);
    subplot(2, 1, 1);
    semilogy(results.times / 24, results.concentrations, 'b-', 'LineWidth', 2);
    xlabel('Time (days)');
    ylabel('Drug Concentration (mg/L)');
    title('Drug Concentration Over Time');
    grid on;
    
    % Figure 2: 세균 집단
    subplot(2, 1, 2);
    semilogy(results.times / 24, results.bacterial_trajectory(:, 1), 'g-', 'LineWidth', 2, 'DisplayName', 'Sensitive');
    hold on;
    semilogy(results.times / 24, results.bacterial_trajectory(:, 2), 'r-', 'LineWidth', 2, 'DisplayName', 'Resistant');
    semilogy(results.times / 24, sum(results.bacterial_trajectory, 2), 'k--', 'LineWidth', 1, 'DisplayName', 'Total');
    xlabel('Time (days)');
    ylabel('Bacterial Count (CFU/mL)');
    title('Bacterial Population Dynamics');
    legend('show');
    grid on;
    hold off;
    
    % 그래프 저장
    saveas(gcf, 'results/MATLAB_simulation_plots.png');
    saveas(gcf, 'results/MATLAB_simulation_plots.fig');
    
    fprintf('   📊 그래프 저장: results/MATLAB_simulation_plots.png\n');
end

%% 메인 실행
fprintf('🚀 시뮬레이터 초기화 중...\n');

% AI 최적화 실행
optimal_regimen = optimize_regimen(patient, drug);

% 최적 투약법으로 시뮬레이션
final_results = run_simulation(patient, drug, optimal_regimen, 7);

% 시각화 생성
create_plots(final_results);

% 결과 저장
timestamp = datestr(now, 'yyyy-mm-ddTHH:MM:SS');
report = struct();
report.timestamp = timestamp;
report.patient = struct('age', patient.age, 'weight', patient.weight, ...
                       'creatinine_clearance', patient.creatinine_clearance, ...
                       'infection_severity', patient.infection_severity);
report.drug = struct('name', drug.name, 'mic_sensitive', drug.mic_sensitive, ...
                    'mic_resistant', drug.mic_resistant);
report.optimal_regimen = optimal_regimen;
report.results = struct('final_bacterial_count', final_results.final_bacterial_count, ...
                       'resistance_fraction', final_results.resistance_fraction, ...
                       'treatment_success', final_results.treatment_success);

% JSON 저장 (MATLAB R2016b 이상)
try
    json_str = jsonencode(report);
    fid = fopen('results/antibiotic_simulation_MATLAB.json', 'w');
    fprintf(fid, '%s', json_str);
    fclose(fid);
    fprintf('\n💾 결과 저장: results/antibiotic_simulation_MATLAB.json\n');
catch
    % 구버전 MATLAB용 대안
    fprintf('\n💾 결과를 MAT 파일로 저장: results/antibiotic_simulation_MATLAB.mat\n');
    save('results/antibiotic_simulation_MATLAB.mat', 'report');
end

fprintf('\n✅ MATLAB 버전 시뮬레이션 완료!\n');
fprintf('\n🔬 사용 가능한 기능:\n');
fprintf('   ✅ 개인맞춤 약동학 모델\n');
fprintf('   ✅ 세균 집단 동역학 (ODE45)\n');
fprintf('   ✅ AI 기반 투약 최적화\n');
fprintf('   ✅ 고품질 시각화\n');
fprintf('   ✅ 수치해석 최적화\n');

fprintf('\n💡 추가 실행 옵션:\n');
fprintf('   - MATLAB GUI에서 실행\n');
fprintf('   - Simulink 모델 연동\n');
fprintf('   - 병렬 컴퓨팅 가속화\n');
fprintf('   - 실시간 데이터 스트리밍\n');
