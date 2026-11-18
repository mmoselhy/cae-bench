# Coverage -- profile `opensource`

CAE-bench-TN is an unofficial, tool-neutral derivative of CAE-bench (svd-ai-lab/cae-bench, Apache-2.0). Its scores are not CAE-bench scores.

Profile status: **tested**. Open-source solvers as in CAE-bench: OpenFOAM v2412, CalculiX 2.17 + Gmsh, Cantera 3.2.0, PyBaMM 26.7.1.0

77 of 77 neutral tasks covered.

| task | domain | portability | covered | missing capabilities |
|---|---|---|---|---|
| `battery/cells/a123_lfp_discharge_1p15c_298k` | battery | portable-after-calibration | yes | - |
| `battery/cells/a123_lfp_energy_0p88c_300k` | battery | portable-after-calibration | yes | - |
| `battery/cells/a123_lfp_mean_voltage_1p52c_297k` | battery | portable-after-calibration | yes | - |
| `battery/cells/ecker_graphite_discharge_0p62c_293k` | battery | portable-after-calibration | yes | - |
| `battery/cells/ecker_graphite_energy_1p12c_298k` | battery | portable-after-calibration | yes | - |
| `battery/cells/ecker_graphite_mean_voltage_0p84c_292k` | battery | portable-after-calibration | yes | - |
| `battery/cells/kokam_lco_discharge_0p71c_302k` | battery | portable-after-calibration | yes | - |
| `battery/cells/lco_graphite_discharge_1p27c_295k` | battery | portable-after-calibration | yes | - |
| `battery/cells/lco_graphite_energy_1p73c_296k` | battery | portable-after-calibration | yes | - |
| `battery/cells/lgm50_fast_charge_current_limit_45c` | battery | portable-after-calibration | yes | - |
| `battery/cells/lgm50_nmc811_discharge_2p3c_288k` | battery | portable-after-calibration | yes | - |
| `battery/cells/lgm50_nmc811_energy_1p6c_301k` | battery | portable-after-calibration | yes | - |
| `battery/cells/lgm50_nmc811_mean_voltage_0p78c_294k` | battery | portable-after-calibration | yes | - |
| `battery/cells/nca_graphite_discharge_0p93c_299k` | battery | portable-after-calibration | yes | - |
| `battery/cells/nmc_pouch_discharge_1p8c_303k` | battery | portable-after-calibration | yes | - |
| `battery/cells/nmc_pouch_energy_2p4c_299k` | battery | portable-after-calibration | yes | - |
| `battery/characterization/a123_cccv_charge_1p1c_from_soc0p26` | battery | portable-after-calibration | yes | - |
| `battery/characterization/a123_pulse_resistance_1p8a_soc0p51` | battery | portable-after-calibration | yes | - |
| `battery/characterization/kokam_cccv_charge_0p64c_from_soc0p31` | battery | portable-after-calibration | yes | - |
| `battery/characterization/kokam_pulse_resistance_1p2a_soc0p47` | battery | portable-after-calibration | yes | - |
| `battery/characterization/lco_graphite_pulse_resistance_0p9a_soc0p66` | battery | portable-after-calibration | yes | - |
| `battery/characterization/lgm50_cccv_charge_1p52c_from_soc0p12` | battery | portable-after-calibration | yes | - |
| `battery/characterization/lgm50_pulse_resistance_5a_soc0p62` | battery | portable-after-calibration | yes | - |
| `battery/characterization/nca_cccv_charge_0p79c_from_soc0p35` | battery | portable-after-calibration | yes | - |
| `battery/characterization/nca_pulse_resistance_0p6a_soc0p74` | battery | portable-after-calibration | yes | - |
| `battery/characterization/nmc_pouch_cccv_charge_1p3c_from_soc0p23` | battery | portable-after-calibration | yes | - |
| `battery/characterization/nmc_pouch_pulse_resistance_4p1a_soc0p55` | battery | portable-after-calibration | yes | - |
| `battery/degradation/lgm50_plating_fade_9_cycles_1p3c` | battery | portable-after-calibration | yes | - |
| `battery/degradation/lgm50_sei_fade_12_cycles_1c` | battery | portable-after-calibration | yes | - |
| `battery/degradation/lgm50_sei_plating_fade_10_cycles_1p5c` | battery | portable-after-calibration | yes | - |
| `battery/thermal/lco_graphite_thermal_rise_2p35c_299k` | battery | portable-after-calibration | yes | - |
| `battery/thermal/lgm50_okane_thermal_rise_1p85c_292k` | battery | portable-after-calibration | yes | - |
| `battery/thermal/lgm50_thermal_rise_0p91c_303k` | battery | portable-after-calibration | yes | - |
| `battery/thermal/nmc_pouch_thermal_rise_2p7c_305k` | battery | portable-after-calibration | yes | - |
| `cfd/fluids/backstep_laminar_armaly_re389` | cfd | portable-after-calibration | yes | - |
| `cfd/fluids/bump_in_channel_2d` | cfd | portable | yes | - |
| `cfd/fluids/channel_developing_entry` | cfd | portable-after-calibration | yes | - |
| `cfd/fluids/channel_retau395_repair_closure` | cfd | native-only | yes | - |
| `cfd/fluids/cylinder_schafer_turek_2d1_cd` | cfd | portable | yes | - |
| `cfd/fluids/de_vahl_davis_natural_convection_ra1e4` | cfd | portable | yes | - |
| `cfd/fluids/flatplate_zpg_subsonic` | cfd | portable-after-calibration | yes | - |
| `cfd/fluids/kovasznay_flow_re40` | cfd | portable | yes | - |
| `cfd/fluids/lid_driven_cavity_ghia_re1000` | cfd | portable | yes | - |
| `cfd/fluids/naca0012_subsonic` | cfd | portable-after-calibration | yes | - |
| `cfd/fluids/plane_poiseuille_friction_factor` | cfd | portable | yes | - |
| `cfd/fluids/taylor_green_vortex_2d_re100` | cfd | portable | yes | - |
| `cfd/fluids/turbulent_channel_flow_retau590` | cfd | portable | yes | - |
| `combustion/flames/c2h4_air_flame_speed_phi1p14_1p2atm_309k` | combustion | portable-after-calibration | yes | - |
| `combustion/flames/c2h6_air_flame_speed_phi1p09_1p3atm_316k` | combustion | portable-after-calibration | yes | - |
| `combustion/flames/c3h8_air_flame_speed_phi1p11_1p3atm_313k` | combustion | portable-after-calibration | yes | - |
| `combustion/flames/ch3oh_air_flame_speed_phi1p16_1p3atm_337k` | combustion | portable-after-calibration | yes | - |
| `combustion/flames/ch4_air_flame_speed_meet_resolution_spec` | combustion | portable-after-calibration | yes | - |
| `combustion/flames/ch4_air_flame_speed_phi1p24_1p6atm_306k` | combustion | portable-after-calibration | yes | - |
| `combustion/flames/h2_air_flame_speed_phi1p12_1p2atm_312k` | combustion | portable-after-calibration | yes | - |
| `combustion/flames/nh3_air_flame_speed_phi1p12_1p4atm_319k` | combustion | portable-after-calibration | yes | - |
| `combustion/flames/nh3_flame_speed_repair_mechanism` | combustion | native-only | yes | - |
| `combustion/kinetics/c2h2_air_idt_phi0p74_1462k_6p4atm` | combustion | portable | yes | - |
| `combustion/kinetics/c2h4_air_idt_phi0p68_1641k_11p8atm` | combustion | portable | yes | - |
| `combustion/kinetics/c2h6_air_idt_phi0p63_1547k_7p3atm` | combustion | portable | yes | - |
| `combustion/kinetics/c3h8_air_idt_phi0p59_1568k_8p1atm` | combustion | portable | yes | - |
| `combustion/kinetics/ch3oh_air_idt_phi0p66_1583k_6p8atm` | combustion | portable | yes | - |
| `combustion/kinetics/ch4_air_idt_phi0p55_1633k_9p2atm` | combustion | portable | yes | - |
| `combustion/kinetics/ch4_air_idt_resume_interrupted_run` | combustion | native-only | yes | - |
| `combustion/kinetics/ch4_air_idt_sensitivity_ch3ho2_phi0p87_1390k` | combustion | portable | yes | - |
| `combustion/kinetics/h2_air_idt_phi0p57_1246k_5p4atm` | combustion | portable | yes | - |
| `combustion/kinetics/ndodecane_air_idt_phi0p83_1319k_14p2atm` | combustion | portable | yes | - |
| `combustion/kinetics/nh3_air_idt_phi0p72_1521k_5p1atm` | combustion | portable | yes | - |
| `combustion/kinetics/nhexane_air_idt_phi0p79_1442k_4p6atm` | combustion | portable | yes | - |
| `packaging/thermal/pkg25d_thermal_tim118um_k4p7_h22600` | packaging | portable-after-calibration | yes | - |
| `packaging/thermal/pkg25d_thermal_tim142um_k3p6_h14200` | packaging | portable-after-calibration | yes | - |
| `packaging/thermal/pkg25d_thermal_tim32um_k8p4_h19000` | packaging | portable-after-calibration | yes | - |
| `packaging/thermal/pkg25d_thermal_tim58um_k9p1_h9400` | packaging | portable-after-calibration | yes | - |
| `packaging/thermal/pkg25d_thermal_tim85um_k6p2_h11500` | packaging | portable-after-calibration | yes | - |
| `packaging/thermal/pkg25d_thermal_tim_delta_118to32_h22600` | packaging | portable-after-calibration | yes | - |
| `packaging/thermomechanical/pkg25d_warpage_tim126um_k3p9_h8700` | packaging | portable-after-calibration | yes | - |
| `packaging/thermomechanical/pkg25d_warpage_tim41um_k9p8_h24500` | packaging | portable-after-calibration | yes | - |
| `packaging/thermomechanical/pkg25d_warpage_tim72um_k6p6_h16300` | packaging | portable-after-calibration | yes | - |
