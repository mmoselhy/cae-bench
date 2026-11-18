# Coverage -- profile `altair`

CAE-bench-TN is an unofficial, tool-neutral derivative of CAE-bench (svd-ai-lab/cae-bench, Apache-2.0). Its scores are not CAE-bench scores.

Profile status: **stub**. Altair OptiStruct (thermal, thermo-mechanical) -- adapter untested

9 of 39 neutral tasks covered.

| task | domain | portability | covered | missing capabilities |
|---|---|---|---|---|
| `cfd/fluids/backstep_laminar_armaly_re389` | cfd | portable-after-calibration | no | `domain:cfd` |
| `cfd/fluids/bump_in_channel_2d` | cfd | portable | no | `domain:cfd` |
| `cfd/fluids/channel_developing_entry` | cfd | portable-after-calibration | no | `domain:cfd` |
| `cfd/fluids/channel_retau395_repair_closure` | cfd | native-only | no | `domain:cfd` |
| `cfd/fluids/cylinder_schafer_turek_2d1_cd` | cfd | portable | no | `domain:cfd` |
| `cfd/fluids/de_vahl_davis_natural_convection_ra1e4` | cfd | portable | no | `domain:cfd` |
| `cfd/fluids/flatplate_zpg_subsonic` | cfd | portable-after-calibration | no | `domain:cfd` |
| `cfd/fluids/kovasznay_flow_re40` | cfd | portable | no | `domain:cfd` |
| `cfd/fluids/lid_driven_cavity_ghia_re1000` | cfd | portable | no | `domain:cfd` |
| `cfd/fluids/naca0012_subsonic` | cfd | portable-after-calibration | no | `domain:cfd` |
| `cfd/fluids/plane_poiseuille_friction_factor` | cfd | portable | no | `domain:cfd` |
| `cfd/fluids/taylor_green_vortex_2d_re100` | cfd | portable | no | `domain:cfd` |
| `cfd/fluids/turbulent_channel_flow_retau590` | cfd | portable | no | `domain:cfd` |
| `combustion/flames/c2h4_air_flame_speed_phi1p14_1p2atm_309k` | combustion | portable-after-calibration | no | `domain:combustion` |
| `combustion/flames/c2h6_air_flame_speed_phi1p09_1p3atm_316k` | combustion | portable-after-calibration | no | `domain:combustion` |
| `combustion/flames/c3h8_air_flame_speed_phi1p11_1p3atm_313k` | combustion | portable-after-calibration | no | `domain:combustion` |
| `combustion/flames/ch3oh_air_flame_speed_phi1p16_1p3atm_337k` | combustion | portable-after-calibration | no | `domain:combustion` |
| `combustion/flames/ch4_air_flame_speed_phi1p24_1p6atm_306k` | combustion | portable-after-calibration | no | `domain:combustion` |
| `combustion/flames/h2_air_flame_speed_phi1p12_1p2atm_312k` | combustion | portable-after-calibration | no | `domain:combustion` |
| `combustion/flames/nh3_air_flame_speed_phi1p12_1p4atm_319k` | combustion | portable-after-calibration | no | `domain:combustion` |
| `combustion/kinetics/c2h2_air_idt_phi0p74_1462k_6p4atm` | combustion | portable | no | `domain:combustion` |
| `combustion/kinetics/c2h4_air_idt_phi0p68_1641k_11p8atm` | combustion | portable | no | `domain:combustion` |
| `combustion/kinetics/c2h6_air_idt_phi0p63_1547k_7p3atm` | combustion | portable | no | `domain:combustion` |
| `combustion/kinetics/c3h8_air_idt_phi0p59_1568k_8p1atm` | combustion | portable | no | `domain:combustion` |
| `combustion/kinetics/ch3oh_air_idt_phi0p66_1583k_6p8atm` | combustion | portable | no | `domain:combustion` |
| `combustion/kinetics/ch4_air_idt_phi0p55_1633k_9p2atm` | combustion | portable | no | `domain:combustion` |
| `combustion/kinetics/h2_air_idt_phi0p57_1246k_5p4atm` | combustion | portable | no | `domain:combustion` |
| `combustion/kinetics/ndodecane_air_idt_phi0p83_1319k_14p2atm` | combustion | portable | no | `domain:combustion` |
| `combustion/kinetics/nh3_air_idt_phi0p72_1521k_5p1atm` | combustion | portable | no | `domain:combustion` |
| `combustion/kinetics/nhexane_air_idt_phi0p79_1442k_4p6atm` | combustion | portable | no | `domain:combustion` |
| `packaging/thermal/pkg25d_thermal_tim118um_k4p7_h22600` | packaging | portable-after-calibration | yes | - |
| `packaging/thermal/pkg25d_thermal_tim142um_k3p6_h14200` | packaging | portable-after-calibration | yes | - |
| `packaging/thermal/pkg25d_thermal_tim32um_k8p4_h19000` | packaging | portable-after-calibration | yes | - |
| `packaging/thermal/pkg25d_thermal_tim58um_k9p1_h9400` | packaging | portable-after-calibration | yes | - |
| `packaging/thermal/pkg25d_thermal_tim85um_k6p2_h11500` | packaging | portable-after-calibration | yes | - |
| `packaging/thermal/pkg25d_thermal_tim_delta_118to32_h22600` | packaging | portable-after-calibration | yes | - |
| `packaging/thermomechanical/pkg25d_warpage_tim126um_k3p9_h8700` | packaging | portable-after-calibration | yes | - |
| `packaging/thermomechanical/pkg25d_warpage_tim41um_k9p8_h24500` | packaging | portable-after-calibration | yes | - |
| `packaging/thermomechanical/pkg25d_warpage_tim72um_k6p6_h16300` | packaging | portable-after-calibration | yes | - |
