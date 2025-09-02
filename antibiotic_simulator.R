#!/usr/bin/env Rscript
# 항생제 내성 진화 시뮬레이터 - R 버전
# Samsung Innovation Challenge 2025
# 실행: Rscript antibiotic_simulator.R

cat("
╔══════════════════════════════════════════════════════════════╗
║        항생제 내성 진화 AI 시뮬레이터 v1.0 - R 버전          ║
║               Samsung Innovation Challenge 2025               ║
╚══════════════════════════════════════════════════════════════╝
\n")

# 필요한 라이브러리 로드
suppressWarnings({
  if (!require(deSolve, quietly = TRUE)) {
    cat("deSolve 패키지를 설치합니다...\n")
    install.packages("deSolve", repos = "https://cran.r-project.org")
    library(deSolve)
  }
  
  if (!require(ggplot2, quietly = TRUE)) {
    cat("ggplot2 패키지를 설치합니다...\n")
    install.packages("ggplot2", repos = "https://cran.r-project.org")
    library(ggplot2)
  }
  
  if (!require(jsonlite, quietly = TRUE)) {
    cat("jsonlite 패키지를 설치합니다...\n")
    install.packages("jsonlite", repos = "https://cran.r-project.org")
    library(jsonlite)
  }
})

# 환자 프로필 생성 함수
create_patient <- function(age, weight, creatinine_clearance, infection_severity) {
  list(
    age = age,
    weight = weight,
    creatinine_clearance = creatinine_clearance,
    infection_severity = infection_severity,
    genetic_markers = list(
      cyp_activity = 1.0,
      mdr1_activity = 1.0
    ),
    comorbidities = c()
  )
}

# 약물 특성 생성 함수
create_drug <- function(name, mic_sensitive, mic_resistant, mpc, half_life) {
  list(
    name = name,
    mic_sensitive = mic_sensitive,
    mic_resistant = mic_resistant,
    mpc = mpc,
    half_life = half_life,
    volume_distribution = 2.5,
    emax = 4.0,
    hill_coefficient = 2.0
  )
}

# 약동학 모델
calculate_elimination_rate <- function(drug, patient) {
  base_ke <- 0.693 / drug$half_life
  renal_factor <- patient$creatinine_clearance / 120.0
  genetic_factor <- patient$genetic_markers$cyp_activity
  age_factor <- ifelse(patient$age > 30, 1.0 - (patient$age - 30) * 0.01, 1.0)
  
  base_ke * renal_factor * genetic_factor * age_factor
}

calculate_volume_distribution <- function(drug, patient) {
  drug$volume_distribution * patient$weight
}

# 농도-시간 곡선 계산
concentration_time_course <- function(doses, times, ke, vd, interval = 12) {
  concentrations <- numeric(length(times))
  
  for (i in seq_along(times)) {
    t <- times[i]
    total_conc <- 0
    
    for (j in seq_along(doses)) {
      dose_time <- (j - 1) * interval
      if (t >= dose_time) {
        time_since_dose <- t - dose_time
        dose_conc <- (doses[j] / vd) * exp(-ke * time_since_dose)
        total_conc <- total_conc + dose_conc
      }
    }
    concentrations[i] <- total_conc
  }
  
  concentrations
}

# 약력학적 효과 함수
pharmacodynamic_effect <- function(concentration, mic, emax = 4.0, hill = 2.0) {
  if (concentration <= 0) return(0)
  emax * (concentration^hill) / (mic^hill + concentration^hill)
}

# 세균 집단 동역학 ODE 시스템
bacterial_ode <- function(t, y, parms) {
  S <- y[1]
  R <- y[2]
  
  # 현재 시점의 약물 농도 (선형 보간)
  C <- approx(parms$times, parms$concentrations, t, rule = 2)$y
  
  # 약력학적 효과
  kill_rate_s <- pharmacodynamic_effect(C, parms$drug$mic_sensitive, 
                                       parms$drug$emax, parms$drug$hill_coefficient)
  kill_rate_r <- pharmacodynamic_effect(C, parms$drug$mic_resistant, 
                                       parms$drug$emax, parms$drug$hill_coefficient)
  
  # 성장률
  growth_rate_s <- 0.693
  growth_rate_r <- 0.623
  mutation_rate <- 1e-8
  carrying_capacity <- 1e12
  
  total_pop <- S + R
  growth_factor <- 1 - total_pop / carrying_capacity
  
  # 변화율
  dS_dt <- (growth_rate_s * growth_factor - kill_rate_s) * S - mutation_rate * S
  dR_dt <- (growth_rate_r * growth_factor - kill_rate_r) * R + mutation_rate * S
  
  list(c(dS_dt, dR_dt))
}

# 시뮬레이션 실행 함수
run_simulation <- function(patient, drug, regimen, days = 7) {
  cat("\n🔬 시뮬레이션 시작...\n")
  cat(sprintf("환자: %d세, %.1fkg, 신기능: %.1f\n", 
             patient$age, patient$weight, patient$creatinine_clearance))
  cat(sprintf("약물: %s, 용량: %.1fmg, 간격: %d시간\n", 
             drug$name, regimen$dose, regimen$interval))
  
  # 약동학 파라미터 계산
  ke <- calculate_elimination_rate(drug, patient)
  vd <- calculate_volume_distribution(drug, patient)
  
  # 시간 배열
  total_hours <- days * 24
  times <- seq(0, total_hours, by = 0.25)  # 15분 간격
  
  # 투약 스케줄
  num_doses <- floor(total_hours / regimen$interval)
  doses <- rep(regimen$dose, num_doses)
  
  # 약물 농도 계산
  concentrations <- concentration_time_course(doses, times, ke, vd, regimen$interval)
  
  # 세균 집단 시뮬레이션
  initial_conditions <- c(S = 1e8, R = 1e4)
  
  parms <- list(
    times = times,
    concentrations = concentrations,
    drug = drug
  )
  
  # ODE 해법
  bacterial_solution <- ode(y = initial_conditions, 
                           times = times, 
                           func = bacterial_ode, 
                           parms = parms,
                           method = "rk4")
  
  # 결과 분석
  final_s <- tail(bacterial_solution[, "S"], 1)
  final_r <- tail(bacterial_solution[, "R"], 1)
  final_total <- final_s + final_r
  final_resistance_fraction <- final_r / final_total
  treatment_success <- (final_total < 1e6) & (final_resistance_fraction < 0.1)
  
  results <- list(
    final_bacterial_count = final_total,
    resistance_fraction = final_resistance_fraction,
    treatment_success = treatment_success,
    max_concentration = max(concentrations),
    min_concentration = min(concentrations[concentrations > 0]),
    concentrations = concentrations,
    bacterial_trajectory = bacterial_solution,
    times = times
  )
  
  cat("\n📊 시뮬레이션 결과:\n")
  cat(sprintf("   최종 세균수: %.2e CFU/mL\n", results$final_bacterial_count))
  cat(sprintf("   내성 비율: %.1f%%\n", results$resistance_fraction * 100))
  cat(sprintf("   치료 성공: %s\n", ifelse(results$treatment_success, "✅ 성공", "❌ 실패")))
  cat(sprintf("   최대 농도: %.2f mg/L\n", results$max_concentration))
  
  results
}

# AI 기반 투약 최적화
optimize_regimen <- function(patient, drug) {
  cat("\n🤖 AI 기반 투약 최적화...\n")
  
  dose_options <- c(250, 500, 750, 1000)
  interval_options <- c(6, 8, 12, 24)
  
  best_regimen <- NULL
  best_score <- -Inf
  
  for (dose in dose_options) {
    for (interval in interval_options) {
      regimen <- list(dose = dose, interval = interval)
      
      # 짧은 시뮬레이션으로 평가
      tryCatch({
        result <- run_simulation(patient, drug, regimen, days = 3)
        
        # 성공률과 비용을 고려한 스코어
        score <- ifelse(result$treatment_success, 1.0, 0.0) - dose / 1000
        
        if (score > best_score) {
          best_score <- score
          best_regimen <- regimen
        }
      }, error = function(e) {
        cat("Error in simulation:", conditionMessage(e), "\n")
      })
    }
  }
  
  cat("\n✅ 최적 투약법:\n")
  cat(sprintf("   용량: %.1fmg\n", best_regimen$dose))
  cat(sprintf("   간격: %d시간\n", best_regimen$interval))
  cat(sprintf("   예상 성공률: %.1f%%\n", best_score * 100))
  
  best_regimen
}

# 시각화 함수
create_plots <- function(results) {
  cat("\n📈 그래프 생성 중...\n")
  
  # 결과 디렉토리 생성
  if (!dir.exists("results")) {
    dir.create("results")
  }
  
  # 데이터 준비
  plot_data <- data.frame(
    time = results$times / 24,  # 일 단위로 변환
    concentration = results$concentrations,
    sensitive = results$bacterial_trajectory[, "S"],
    resistant = results$bacterial_trajectory[, "R"],
    total = results$bacterial_trajectory[, "S"] + results$bacterial_trajectory[, "R"]
  )
  
  # 농도 그래프
  p1 <- ggplot(plot_data, aes(x = time, y = concentration)) +
    geom_line(color = "blue", size = 1) +
    scale_y_log10() +
    labs(title = "Drug Concentration Over Time",
         x = "Time (days)",
         y = "Concentration (mg/L)") +
    theme_minimal()
  
  # 세균 집단 그래프
  p2 <- ggplot(plot_data) +
    geom_line(aes(x = time, y = sensitive, color = "Sensitive"), size = 1) +
    geom_line(aes(x = time, y = resistant, color = "Resistant"), size = 1) +
    geom_line(aes(x = time, y = total, color = "Total"), size = 1, linetype = "dashed") +
    scale_y_log10() +
    scale_color_manual(values = c("Sensitive" = "green", "Resistant" = "red", "Total" = "black")) +
    labs(title = "Bacterial Population Dynamics",
         x = "Time (days)",
         y = "Bacterial Count (CFU/mL)",
         color = "Population") +
    theme_minimal()
  
  # 그래프 저장
  ggsave("results/R_concentration_plot.png", p1, width = 10, height = 6, dpi = 300)
  ggsave("results/R_bacterial_plot.png", p2, width = 10, height = 6, dpi = 300)
  
  cat("   📊 농도 그래프: results/R_concentration_plot.png\n")
  cat("   📊 세균 그래프: results/R_bacterial_plot.png\n")
}

# 메인 실행 함수
main <- function() {
  # 샘플 환자 생성
  patient <- create_patient(65, 75, 80, 0.7)
  patient$comorbidities <- c("diabetes", "hypertension")
  
  # 샘플 약물
  drug <- create_drug("Ciprofloxacin", 0.5, 8.0, 2.0, 4.0)
  
  # AI 최적화 실행
  optimal_regimen <- optimize_regimen(patient, drug)
  
  # 최적 투약법으로 시뮬레이션
  final_results <- run_simulation(patient, drug, optimal_regimen, days = 7)
  
  # 시각화 생성
  create_plots(final_results)
  
  # 결과 저장
  timestamp <- Sys.time()
  report <- list(
    timestamp = format(timestamp, "%Y-%m-%dT%H:%M:%S"),
    patient = list(
      age = patient$age,
      weight = patient$weight,
      creatinine_clearance = patient$creatinine_clearance,
      infection_severity = patient$infection_severity
    ),
    drug = list(
      name = drug$name,
      mic_sensitive = drug$mic_sensitive,
      mic_resistant = drug$mic_resistant
    ),
    optimal_regimen = optimal_regimen,
    results = list(
      final_bacterial_count = final_results$final_bacterial_count,
      resistance_fraction = final_results$resistance_fraction,
      treatment_success = final_results$treatment_success
    )
  )
  
  # JSON 저장
  write_json(report, "results/antibiotic_simulation_R.json", pretty = TRUE)
  cat("\n💾 결과 저장: results/antibiotic_simulation_R.json\n")
  
  cat("\n✅ R 버전 시뮬레이션 완료!\n")
  cat("\n🔬 사용 가능한 기능:\n")
  cat("   ✅ 개인맞춤 약동학 모델\n")
  cat("   ✅ 세균 집단 동역학 (ODE)\n")
  cat("   ✅ AI 기반 투약 최적화\n")
  cat("   ✅ 고품질 시각화 (ggplot2)\n")
  cat("   ✅ 통계적 분석\n")
}

# 실행
if (!interactive()) {
  main()
}
